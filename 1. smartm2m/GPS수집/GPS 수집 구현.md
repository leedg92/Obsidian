# GPS 수집 시스템 — 현재 구현 상태 정리 ver

## 1. 시스템 구성

```
App → Bctrans/Allcone backend (바이패스) → Proxy → Cloud 서버 (검증 + ClickHouse 직접 INSERT)
```

| 컴포넌트 | 역할 |
|---------|------|
| App (모바일) | GPS 수집, `isMoving==0` 제외, 배치 전송 (최대 500건/배치) |
| Bctrans/Allcone backend | 바이패스 (리버스프록시로 전달) |
| Proxy | nginx 리버스프록시, 클라우드로 라우팅 |
| Cloud 서버 (Spring Boot 3.2.5 / Java 21) | 2단계 검증 + ClickHouse 직접 INSERT |
| ClickHouse | GPS 데이터 저장 + 설정 메타데이터 + 분석용 뷰 |

> Kafka는 인프라에 구성되어 있으나, 현재 애플리케이션 코드에서는 사용하지 않음. Cloud 서버가 검증 후 ClickHouse에 직접 INSERT하는 구조.

---

## 2. API 스펙

### 수집 엔드포인트

`POST /api/gps/collect`

**요청 (JSON)**

```json
{
  "userId": "user001",
  "truckNo": "12가3456",
  "points": [
    {
      "latitude": 35.0802,
      "longitude": 128.8039,
      "speed": 15.5,
      "accuracy": 10,
      "batteryLevel": 85,
      "networkType": "LTE",
      "isMoving": true,
      "collectedAt": "2026-04-08T10:30:00.000Z"
    }
  ]
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| userId | String | O | 사용자 ID |
| truckNo | String | O | 차량번호 |
| points | Array | O | GPS 포인트 배열 (최대 500건, 초과 시 413) |
| points[].latitude | Double | O | 위도 |
| points[].longitude | Double | O | 경도 |
| points[].speed | Double | - | 속도 (km/h) |
| points[].accuracy | Integer | - | GPS 정확도 (m) |
| points[].batteryLevel | Integer | - | 배터리 잔량 (%) |
| points[].networkType | String | - | 네트워크 타입 (LTE, 5G 등) |
| points[].isMoving | Boolean | - | 이동 여부 |
| points[].collectedAt | String | - | 수집 시각 (ISO 8601) |

**응답 (JSON)**

```json
{
  "result": "success",
  "data": {
    "requested": 50,
    "saved": 45,
    "rejected": 5
  }
}
```

| 필드 | 설명 |
|------|------|
| requested | 요청된 전체 포인트 수 |
| saved | 검증 통과하여 저장된 포인트 수 |
| rejected | 검증 실패하여 제외된 포인트 수 |

### 설정 리로드 엔드포인트

`POST /api/gps/config/reload` — ClickHouse 설정 테이블을 메모리에 다시 로드

---

## 3. 서버 검증 로직 (2단계)

### 1단계: 한반도 바운딩 박스

| 설정키           | 값     | 설명    |
| ------------- | ----- | ----- |
| KOREA_MIN_LAT | 33.0  | 최소 위도 |
| KOREA_MAX_LAT | 39.0  | 최대 위도 |
| KOREA_MIN_LON | 124.0 | 최소 경도 |
| KOREA_MAX_LON | 132.0 | 최대 경도 |

- 범위 밖이면 GPS 튐으로 간주, 즉시 reject

### 2단계: 속도 임계값

- Haversine 공식으로 포인트가 터미널 구역 내인지 판단
- **구역 내** → 해당 구역의 속도 임계값 적용 (5 km/h)
- **구역 밖** → 기본 속도 임계값 적용 (3 km/h)
- 속도가 임계값 미만이면 reject (정지/저속 데이터 제외)

**터미널 구역 설정:**

| 구역명 | 중심 위도 | 중심 경도 | 반경 | 속도 임계값 |
|--------|----------|----------|------|-----------|
| 신항 | 35.0802408 | 128.8039779 | 5 km | 5 km/h |
| 신항 배후단지 | 35.1347164 | 128.8638059 | 3.5 km | 5 km/h |
| 북항 | 35.1160086 | 129.0540030 | 3.5 km | 5 km/h |

설정값은 `@PostConstruct`로 기동 시 메모리 캐싱, `POST /api/gps/config/reload`로 수동 갱신 가능.

---

## 4. 데이터베이스 (ClickHouse)

데이터베이스명: `gps_collect`

### 4-1. gps_warehouse — 원본 GPS 데이터

| 컬럼 | 타입 | 설명 |
|------|------|------|
| USER_ID | String | 사용자 ID |
| TRUCK_NO | String | 차량번호 |
| TRUCKER_ID | String | 운송사 ID |
| LATITUDE | Float64 | 위도 (원본 정밀도) |
| LONGITUDE | Float64 | 경도 (원본 정밀도) |
| SPEED | Float32 | 속도 (km/h) |
| ACCURACY | Float32 | GPS 정확도 (m) |
| BATTERY_LEVEL | Nullable(Float32) | 배터리 잔량 |
| NETWORK_TYPE | Nullable(String) | 네트워크 타입 |
| IS_MOVING | UInt8 | 이동 여부 (1=이동중) |
| COLLECTED_AT | DateTime64(3) | 수집 시각 (밀리초 정밀도) |
| CREATED_AT | DateTime | 서버 수신 시각 |

- ORDER BY: `(TRUCK_NO, COLLECTED_AT)`
- 엔진: MergeTree

### 4-2. gps_mart — 밀도 분석용

`gps_warehouse` INSERT 시 Materialized View(`gps_mart_mv`)가 자동으로 위경도를 정수부/소수부 분리하여 적재.

| 컬럼 | 타입 | 설명 | 예시 (35.14349, 128.80397) |
|------|------|------|--------------------------|
| LAT_INT | UInt8 (1byte) | 위도 정수부 | 35 |
| LAT_DEC | UInt32 (4bytes) | 위도 소수부 (5자리, ~1m 정밀도) | 14349 |
| LON_INT | UInt8 (1byte) | 경도 정수부 | 128 |
| LON_DEC | UInt32 (4bytes) | 경도 소수부 (5자리, ~1m 정밀도) | 80397 |

- 좌표 복원: `LAT_INT + LAT_DEC / 100000.0`
- 10m 그리드 집계: `LAT_DEC / 10`으로 4자리 단위 GROUP BY
- 행당 10 bytes, 정수부는 부산항 일대 거의 상수 → 사실상 0 바이트로 압축

### 4-3. gps_validation_config — 글로벌 설정 (KEY-VALUE)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| CONFIG_KEY | String | 설정 키 (PK) |
| CONFIG_VALUE | String | 설정 값 |
| DESCRIPTION | String | 설명 |

**초기 데이터:**

| CONFIG_KEY | CONFIG_VALUE | DESCRIPTION |
|------------|-------------|-------------|
| DEFAULT_SPEED_THRESHOLD_KMH | 3.0 | 구역 밖 기본 속도 임계값 (km/h) |
| KOREA_MIN_LAT | 33.0 | 한반도 바운딩 박스 최소 위도 |
| KOREA_MAX_LAT | 39.0 | 한반도 바운딩 박스 최대 위도 |
| KOREA_MIN_LON | 124.0 | 한반도 바운딩 박스 최소 경도 |
| KOREA_MAX_LON | 132.0 | 한반도 바운딩 박스 최대 경도 |

### 4-4. terminal_zone_config — 터미널 구역 설정

| 컬럼 | 타입 | 설명 |
|------|------|------|
| ZONE_ID | UInt32 | 구역 ID (PK) |
| ZONE_NAME | String | 구역명 |
| CENTER_LAT | Float64 | 중심 위도 |
| CENTER_LON | Float64 | 중심 경도 |
| RADIUS_KM | Float32 | 반경 (km) |
| SPEED_THRESHOLD_KMH | Float32 | 속도 임계값 (km/h) |
| DESCRIPTION | String | 설명 |

### 4-5. 분석용 뷰

| 뷰 | 유형 | 용도 |
|----|------|------|
| gps_mart_mv | Materialized View | warehouse INSERT 시 mart 자동 적재 |
| gps_warehouse_view_zone | View | warehouse 포인트별 소속 터미널 구역 판정 (Haversine) |
| gps_warehouse_view_heatmap | View | 구역별 위경도 그리드 히트맵 집계 |

---

## 5. 실제 데이터 현황

| 항목      | 수치             | 용량       |
| ------- | -------------- | -------- |
| 일평균 적재량 | **약 119만 건/일** | **30MB** |


### 계획 대비 비교

| 항목 | 계획 (현실적 산정) | 실제 |
|------|-------------------|------|
| 일일 건수 | 약 10.8억 건/일 | 약 119만 건/일 (**계획의 약 0.1%**) |
| 산정 근거 | 2만명 동시, 9시간, 30초마다 50건 | 현재 실 사용자 수/전송 빈도가 계획 대비 극히 적음 |

### 디스크 사용량 추정 (현재 실적 기반)

| 기간 | 예상 warehouse 크기 | 예상 mart 추가분 |
|------|---------------------|-----------------|
| 1개월 | ~900 MB | ~300 MB |
| 6개월 | ~5.4 GB | ~1.8 GB |
| 1년 | ~10.8 GB | ~3.6 GB |


---

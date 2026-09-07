# 인근도로 혼잡도 API (CHENH-88 / 설계 CHENH-94)

> 앱이 호출하는 인스턴스는 **allcone**, context-path 는 `/allcone-api` — 예) `/allcone-api/mobile/traffic/road`

## 엔드포인트 목록

| #   | 메서드    | 경로                            | 파라미터                                                             | 용도        |
| --- | ------ | ----------------------------- | ---------------------------------------------------------------- | --------- |
| 1   | GET    | `/mobile/traffic/road`        | `portCode` (선택, `PUS`·`BNP` / 생략 시 전체)                            | 앱 — 인근도로 혼잡도 조회 |
| 2   | GET    | `/mobile/terminal/traffic/all`| `terminalCode` (선택) — **기존 그대로**                                  | 앱 — 터미널 혼잡도 조회 (도로 등급 반영됨) |
| 3   | GET    | `/admin/traffic/road`         | `portCode`·`activeYn` (선택)                                        | 관제 — 도로 마스터 조회 |
| 4   | POST   | `/admin/traffic/road`         | body `PortNearbyRoad`                                             | 관제 — 도로 마스터 등록 |
| 5   | PUT    | `/admin/traffic/road`         | body `PortNearbyRoad`                                             | 관제 — 도로 마스터 수정 |
| 6   | DELETE | `/admin/traffic/road`         | `roadId` (필수)                                                     | 관제 — 도로 마스터 삭제 |

> 3~6 은 앱 소관이 아니다. 맨 뒤 「참고 — 관제용 CRUD」 참조.

## 공통 응답 봉투 (전 API 동일)

```jsonc
{
  "result": "success",     -- 처리 결과 ("success" / "failure")
  "resultMessage": "",     -- 실패 시 메시지
  "data": ...              -- 실제 데이터
}
```

아래는 각 API 의 `data` 부분만 기술한다.

## 코드값

**혼잡도 등급 `congestionLevel`** — 한글 문자열 4종이 그대로 내려간다.

| 값    | 산출 기준 (대표속도)      |
| ---- | ----------------- |
| `원활` | 25 km/h 이상        |
| `서행` | 15 km/h 이상 25 미만  |
| `지체` | 10 km/h 이상 15 미만  |
| `정체` | 10 km/h 미만        |

**항만 코드 `portCode`**

| 값     | 항만 |
| ----- | -- |
| `PUS` | 북항 |
| `BNP` | 신항 |

---

## 1. `GET /mobile/traffic/road`

인근 도로 혼잡도 조회. 활성(`ACTIVE_YN='Y'`) 도로를 `priority` 오름차순으로 내려준다.

```jsonc
"data": [
  {
    "roadId": "TRF001",              -- 도로 식별자
    "roadName": "북항 진입로",         -- 앱 표시용 도로명
    "portCode": "PUS",               -- 항만 코드 (PUS=북항 / BNP=신항)
    "priority": 1,                   -- 앱 표시 우선순위 (오름차순 정렬됨)
    "congestionLevel": "지체",        -- 혼잡도 등급 (원활 / 서행 / 지체 / 정체)
    "avgSpeed": 14.00,               -- 대표 속도 (km/h). 도로 내 링크 중 최저 속도 (필드명과 달리 평균 아님)
    "fetchedDtm": "2026-08-14T10:35:00"  -- 수집 시각 (ISO 8601, 초 단위)
  }
]
```

동작 참고

- 5분 주기 배치가 수집한 값 중 **도로별 최신 1건**이다. 앱이 호출할 때 외부 API 를 타지 않는다.
- 아직 한 번도 수집되지 않았거나 수집이 실패한 도로는 **행은 나오되 `congestionLevel`·`avgSpeed`·`fetchedDtm` 이 `null`** 이다. (도로 마스터와 LEFT JOIN)
- `portCode` 를 넘기면 해당 항만 도로만, 생략하면 전체가 내려온다.
- 초기 등록 도로는 5건 — `TRF001` 북항 진입로 / `TRF002` 신선대 교차로 / `TRF003` 감만부두 입구 / `TRF004` 터미널 연결도로 (이상 `PUS`) / `TRF005` 신항 진입로 (`BNP`). 관제에서 증감 가능하므로 앱은 **건수를 고정하지 말 것**.

---

## 2. `GET /mobile/terminal/traffic/all` — 기존 API, 응답 변경 있음

경로·파라미터·필드 구성은 **그대로**다. 값이 바뀌는 필드는 **`inOutStatusStr` 하나**다.

```jsonc
"data": [
  {
    "terminalCode": "PNCOC010",   -- 터미널 코드
    "terminal": "부산 신항",        -- 터미널명
    "sendErrorInfo": "정상",       -- 원본 전송 상태 (없으면 null)
    "vesselStatus": "12",         -- 선박 대기 수치
    "vesselStatusStr": "fatal",   -- 선박 상태 등급 (primary / danger / fatal) — 변경 없음
    "inOutStatus": "183",         -- 반출입 대기 수치 — 변경 없음 (원본 그대로)
    "inOutStatusStr": "danger",   -- 🔴 반출입 상태 등급. 인근 도로 등급이 반영된다 (아래 참조)
    "inStatus": "30",             -- 반입 대기 수치 (없으면 null)
    "outStatus": "30",            -- 반출 대기 수치 (없으면 null)
    "error": false,               -- 전송 오류 여부 (sendErrorInfo 에 "정상" 없으면 true)
    "maxComplexity": "3"          -- 요청 terminalCode 와 일치하는 항목에만 채워짐 (그 외 null)
  }
]
```

### `inOutStatusStr` 이 어떻게 바뀌나

터미널이 속한 항만의 **가장 나쁜 도로 등급**을 3단계로 접어, 기존 값과 비교해 **나쁜 쪽을 남긴다**.

| 도로 등급 `congestionLevel` | 접힌 값     |
| ----------------------- | -------- |
| `정체`                    | `fatal`  |
| `지체`                    | `danger` |
| `서행` · `원활`             | `primary`|

심각도 순서는 `fatal`(3) > `danger`(2) > `primary`(1) > 그 외(0) 이다.

- 기존 `inOutStatusStr` 이 도로 등급보다 나쁘거나 같으면 **그대로 둔다**.
- 기존 값이 `primary`/`danger`/`fatal` 이 아닌 다른 문자열(예: 원본이 내려주던 `warning`)이면 심각도 0 으로 취급되므로, 도로 등급이 있는 항만의 터미널은 **`primary`/`danger`/`fatal` 중 하나로 바뀌어 내려온다**. 앱에서 `warning` 을 전제로 분기하고 있다면 확인 필요.
- 기존 값이 비어 있거나 `"error"` 면 손대지 않는다.
- `terminalCode` 가 `HPNTC050` 인 항목은 기존대로 `inOutStatus` 수치로 등급을 먼저 매긴 뒤(≤100 `primary` / ≤200 `danger` / 초과 `fatal`) 도로 등급과 비교한다.
- 도로 혼잡도 조회에 실패하거나 수집 데이터가 없으면 **기존 응답 그대로** 나간다 (도로는 부가 정보라 터미널 혼잡도를 막지 않는다).
- 도로 등급은 **항만 단위**다. 같은 항만의 터미널에는 동일한 도로 등급이 적용된다.
- 터미널 ↔ 항만 매칭은 `general_terminal.TERMINAL_PORT_CODE` 기준 — `PUS` 5개(`BICTC010`·`GCTOC050`·`KCTPC011`·`KJTLC050`·`PECTC050`), `BNP` 8개(`BCTHD010`·`BNCTC050`·`DGTBC050`·`HJNPC010`·`HPNTC050`·`PNCOC010`·`PNDKC050`·`PNITC050`).

---

## 참고 — 관제용 CRUD (앱 소관 아님)

`/admin/traffic/road` 4종. `Authorization` 헤더로 admin API 키 검증(`AdminApiKeyFilter`), 미인증 시 401.

- `GET` — `data` 는 도로 마스터 배열: `roadId` · `roadName` · `externalLinkId`(ITS-GO 측 도로명) · `portCode` · `priority` · `activeYn`
- `POST` / `PUT` — 위 필드를 body 로 받아 upsert. `activeYn` 생략 시 `Y`, `priority` 생략 시 `1`
- `DELETE` — `roadId` 파라미터. 삭제 대상이 없으면 `result: "failure"`
- `POST`/`PUT`/`DELETE` 응답 `data`:

```jsonc
{
  "roadId": "TRF001",                    -- 처리한 도로 식별자
  "action": "CREATED",                   -- CREATED / UPDATED / DELETED
  "processedDtm": "2026-08-14T10:35:00"  -- 처리 시각
}
```

마스터를 바꾸면 **다음 수집 사이클(5분 주기)부터** 앱 조회에 반영된다.

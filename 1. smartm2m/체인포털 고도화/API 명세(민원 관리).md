# 민원관리 API 명세서

## 기본 정보
- **Base URL**: `http://localhost:8080`
- **Content-Type**: `application/json`
- **Swagger UI**: http://localhost:8080/swagger-ui/index.html

## 공통 응답 형식
모든 API는 `ResponseFormat<T>` 형태로 응답합니다.

```json
{
  "success": true,
  "message": "성공 메시지",
  "data": <응답 데이터>
}
```

## 📋 1. 민원 분석 API (`/handles`)

### 1.1 민원 분석 상세 조회
- **URL**: `GET /handles/detail`
- **설명**: 민원 분석 상세 정보를 조회합니다
- **Parameters**:
  - `complaintKey` (String, required): 민원 키

**Response**:
```json
{
  "success": true,
  "data": {
    "complaintKey": "string",
    "pinNo": "string",
    "systemKey": "string", 
    "faultKey": 1,
    "user": "string",
    "context": "string"
  }
}
```

### 1.2 민원 분석 등록
- **URL**: `POST /handles/insert`
- **설명**: 새로운 민원 분석을 등록합니다

**Request Body**:
```json
{
  "complaintKey": "string",
  "pinNo": "string",
  "systemKey": "string",
  "faultKey": 1,
  "user": "string",
  "context": "string"
}
```

### 1.3 민원 분석 수정
- **URL**: `POST /handles/update`
- **설명**: 기존 민원 분석을 수정합니다

**Request Body**:
```json
{
  "complaintKey": "string",
  "pinNo": "string",
  "systemKey": "string",
  "faultKey": 1,
  "user": "string",
  "context": "string"
}
```

### 1.4 민원 분석 삭제
- **URL**: `POST /handles/delete`
- **설명**: 기존 민원 분석을 삭제합니다

**Request Body**:
```json
{
  "complaintKey": "string"
}
```

## ⚠️ 2. 주요 장애 사항 관리 API (`/faults`)

### 2.1 장애사항 목록 조회
- **URL**: `GET /faults/list`
- **설명**: 주요 장애사항 목록을 조회합니다

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "value": 1,
      "label": "네트워크 장애"
    }
  ]
}
```

### 2.2 장애사항 등록
- **URL**: `POST /faults/insert`
- **설명**: 새로운 장애사항을 등록합니다

**Request Body**:
```json
{
  "context": "장애 내용",
  "user": "등록자"
}
```

### 2.3 장애사항 수정
- **URL**: `POST /faults/update`
- **설명**: 기존 장애사항을 수정합니다

**Request Body**:
```json
{
  "key": 1,
  "context": "수정된 장애 내용",
  "user": "수정자"
}
```

### 2.4 장애사항 삭제
- **URL**: `POST /faults/delete`
- **설명**: 기존 장애사항을 삭제합니다 (논리삭제)

**Request Body**:
```json
{
  "key": 1,
  "user": "삭제자"
}
```

## 🔍 3. 시스템 조회 API (`/systems`)

### 3.1 시스템 위치 목록 조회
- **URL**: `GET /systems/locationList`
- **설명**: 터미널 내/외부 시스템 위치 목록을 조회합니다

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "value": "I",
      "label": "내부"
    },
    {
      "value": "E", 
      "label": "외부"
    }
  ]
}
```

### 3.2 시스템 상세 목록 조회
- **URL**: `GET /systems/detailList`
- **설명**: 터미널 내/외부 상세 시스템 목록을 조회합니다
- **Parameters**:
  - `systemLoc` (String, required): 시스템 위치 (I: 내부, E: 외부)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "value": "SYS001",
      "label": "게이트 시스템"
    }
  ]
}
```

## 📊 4. 민원 분석 기반 통계 관리 API (`/report`)

### 4.1 통계 조회
- **URL**: `POST /report/getReport`
- **설명**: 민원 분석 기반으로 테이블 및 통계 데이터를 조회합니다

**Request Body**:
```json
{
  "fromDate": "2024-01-01",
  "toDate": "2024-12-31"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "total": {
      "장애": 10,
      "일반 문의": 5
    },
    "table": {
      "total": [
        {
          "systemLoc": "전체 시스템",
          "cnt": 15
        }
      ],
      "detail": [
        {
          "systemLoc": "내부시스템 장애",
          "systemDtl": "게이트 시스템",
          "fault": "네트워크 장애",
          "faultCnt": 3
        }
      ]
    }
  }
}
```

## 📌 5. PIN No 조회 API (`/pinNo`)

### 5.1 Service Key 목록 조회
- **URL**: `GET /pinNo/list`
- **설명**: 민원 ID 기반으로 Service Key 목록을 조회합니다
- **Parameters**:
  - `complaintKey` (String, required): 민원 키

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "pinNo": "PIN001",
      "serviceKey": "SERVICE_KEY_001"
    }
  ]
}
```

---

## 공통 에러 응답

```json
{
  "success": false,
  "message": "에러 메시지",
  "data": null
}
```

### 주요 에러 코드
- **400 Bad Request**: 잘못된 요청 파라미터
- **404 Not Found**: 요청한 리소스를 찾을 수 없음
- **500 Internal Server Error**: 서버 내부 오류
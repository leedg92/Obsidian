# ChainPortal 관제 시스템 민원 처리 API 명세서

## 개요
- **Base URL**: `/api`
- **응답 형식**: JSON
- **인코딩**: UTF-8

## 공통 응답 형식

모든 API는 다음과 같은 공통 응답 형식을 사용합니다:

```json
{
  "result": "success | failure",
  "resultMessage": "응답 메시지",
  "data": "실제 데이터 (성공 시에만 포함)"
}
```

---

## 1. 장애사항 관리 API (`/faults`)

### 1.1 주요 장애사항 목록 조회
- **URL**: `GET /faults/list`
- **설명**: 등록된 주요 장애사항 목록을 조회합니다.

**응답**
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": [
    {
      "value": 1,
      "label": "네트워크 연결 장애"
    },
    {
      "value": 2,
      "label": "시스템 응답 지연"
    }
  ]
}
```

### 1.2 주요 장애사항 등록
- **URL**: `POST /faults/insert`
- **설명**: 새로운 주요 장애사항을 등록합니다.

**요청 본문**
```json
{
  "context": "장애사항 내용",
  "user": "등록자명"
}
```

**요청 필드**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| context | String | Y | 주요 장애사항 내용 |
| user | String | Y | 등록자 |

**응답**
```json
{
  "result": "success",
  "resultMessage": "장애사항이 등록되었습니다.",
  "data": null
}
```

### 1.3 주요 장애사항 수정
- **URL**: `POST /faults/update`
- **설명**: 기존 주요 장애사항을 수정합니다.

**요청 본문**
```json
{
  "key": 1,
  "context": "수정된 장애사항 내용",
  "user": "수정자명"
}
```

**요청 필드**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| key | Integer | Y | 주요 장애사항 고유 번호 |
| context | String | Y | 수정된 장애사항 내용 |
| user | String | Y | 수정자 |

**응답**
```json
{
  "result": "success",
  "resultMessage": "장애사항이 수정되었습니다.",
  "data": null
}
```

### 1.4 주요 장애사항 삭제
- **URL**: `POST /faults/delete`
- **설명**: 기존 주요 장애사항을 삭제합니다.

**요청 본문**
```json
{
  "key": 1,
  "user": "삭제자명"
}
```

**요청 필드**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| key | Integer | Y | 주요 장애사항 고유 번호 |
| user | String | Y | 삭제자 |

**응답**
```json
{
  "result": "success",
  "resultMessage": "장애사항이 삭제되었습니다.",
  "data": null
}
```

---

## 2. PIN 번호 관리 API (`/pinNo`)

### 2.1 민원 ID 기반 Service Key 목록 조회
- **URL**: `GET /pinNo/list`
- **설명**: 민원 ID를 기반으로 관련된 Service Key 목록을 조회합니다.

**요청 파라미터**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| complaintId | String | Y | 민원 ID |

**요청 예시**
```
GET /pinNo/list?complaintId=001
```

**응답**
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": [
    "SERVICE_KEY_001",
    "SERVICE_KEY_002",
    "SERVICE_KEY_003"
  ]
}
```

**오류 응답**
```json
{
  "result": "failure",
  "resultMessage": "민원 정보를 찾을 수 없습니다.",
  "data": null
}
```

---

## 3. 시스템 관리 API (`/systems`)

### 3.1 터미널 내/외부 시스템 목록 조회
- **URL**: `GET /systems/locationList`
- **설명**: 터미널 내부 및 외부 시스템 위치 목록을 조회합니다.

**응답**
```json
{
  "result": "success",
  "resultMessage": "시스템 위치 목록 조회 성공",
  "data": [
    {
      "value": "INTERNAL",
      "label": "터미널 내부"
    },
    {
      "value": "EXTERNAL",
      "label": "터미널 외부"
    }
  ]
}
```

### 3.2 터미널 내/외부 상세 시스템 목록 조회
- **URL**: `GET /systems/detailList`
- **설명**: 특정 위치(내부/외부)의 상세 시스템 목록을 조회합니다.

**요청 파라미터**

| 파라미터      | 타입     | 필수  | 설명           |
| --------- | ------ | --- | ------------ |
| systemLoc | String | Y   | 시스템 위치 (I/E) |

**요청 예시**
```
GET /systems/detailList?systemLoc=I
```

**응답**
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": [
    {
      "value": "SYSTEMKEY",
      "label": "게이트 관리 시스템"
    },
    {
      "value": "SYS_002",
      "label": "컨테이너 추적 시스템"
    }
  ]
}
```

---

## 4. 처리 조치 관리 API (`/handles`)

### 4.1 처리 조치 상세 조회
- **URL**: `GET /handles/detail`
- **설명**: 특정 민원의 처리 조치 상세 정보를 조회합니다.

**요청 파라미터**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| complaintId | String | Y | 민원 ID |

**요청 예시**
```
GET /handles/detail?complaintKey=001
```

**응답**
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": {
    "key": "001",
    "pinNo": "PIN123456",
    "systemKey": "SYSTEMKEY",
    "faultKey": 1,
    "user": "관리자",
    "context": "네트워크 연결 문제로 인한 게이트 시스템 장애 처리 완료"
  }
}
```

**응답 필드**

| 필드 | 타입 | 설명 |
|------|------|------|
| key | String | 민원 ID |
| pinNo | String | PIN 번호 |
| systemKey | String | 시스템 고유 ID |
| faultKey | Integer | 주요 장애사항 고유 번호 |
| user | String | 처리자 |
| context | String | 처리 내용 |

### 4.2 처리 조치 등록
- **URL**: `POST /handles/insert`
- **설명**: 새로운 처리 조치를 등록합니다.

**요청 본문**
```json
{
  "key": "001",
  "pinNo": "PIN123456",
  "systemKey": "SYSTEMKEY",
  "faultKey": 1,
  "user": "관리자",
  "context": "처리 내용"
}
```

**요청 필드**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| key | String | Y | 민원 ID |
| pinNo | String | Y | PIN 번호 |
| systemKey | String | Y | 시스템 ID |
| faultKey | Integer | Y | 장애사항 ID |
| user | String | Y | 처리자 |
| context | String | Y | 처리 내용 |

**응답**
```json
{
  "result": "success",
  "resultMessage": "처리 조치가 등록되었습니다.",
  "data": null
}
```

### 4.3 처리 조치 수정
- **URL**: `POST /handles/update`
- **설명**: 기존 처리 조치를 수정합니다.

**요청 본문**
```json
{
  "key": "001",
  "pinNo": "PIN123456",
  "systemKey": "SYSTEMKEY",
  "faultKey": 1,
  "user": "관리자",
  "context": "수정된 처리 내용"
}
```

**요청 필드는 등록과 동일합니다.**

**응답**
```json
{
  "result": "success",
  "resultMessage": "처리 조치가 수정되었습니다.",
  "data": null
}
```

### 4.4 PIN 번호 목록 조회
- **URL**: `GET /handles/pin/list`
- **설명**: 등록된 PIN 번호 목록을 조회합니다.

**응답**
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": [
    "PIN123456",
    "PIN789012",
    "PIN345678"
  ]
}
```

---

## 오류 코드

모든 API에서 공통으로 발생할 수 있는 오류:

### HTTP 상태 코드
- **200 OK**: 정상 처리 (성공/실패 여부는 `result` 필드로 구분)
- **400 Bad Request**: 잘못된 요청 파라미터
- **500 Internal Server Error**: 서버 내부 오류

### 응답 결과 코드
- **success**: 정상 처리
- **failure**: 처리 실패

### 주요 오류 메시지
- "장애사항 목록 조회 실패"
- "장애사항 등록 실패"
- "장애사항 수정 실패"
- "장애사항 삭제 실패"
- "민원 정보를 찾을 수 없습니다."
- "Service Key 목록 조회 실패"
- "시스템 위치 목록 조회 실패"
- "시스템 상세 목록 조회 실패"
- "처리 조치 정보 조회 실패"
- "처리 조치 등록 실패"
- "처리 조치 수정 실패"
- "PIN 번호 목록 조회 실패"
- "검색 조건 부족"

---

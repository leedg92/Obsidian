# ChainPortal Control System - Complaint Handling API 명세서

## 개요
ChainPortal 민원 처리 시스템의 REST API 명세서입니다. 이 시스템은 민원 처리, 장애사항 관리, 시스템 정보 조회 등의 기능을 제공합니다.

## 공통 응답 형식
모든 API는 공통 응답 형식을 사용합니다.

```json
{
  "result": "success" | "failure",
  "resultMessage": "메시지 내용",
  "data": <응답 데이터>
}
```

## 1. 장애사항 관리 API (/faults)

### 1.1 장애사항 목록 조회
- **URL**: `GET /faults/list`
- **설명**: 주요 장애사항 목록을 조회합니다.
- **Request**: 없음
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": [
    {
      "value": 1,
      "label": "장애사항 내용"
    }
  ]
}
```

### 1.2 장애사항 등록
- **URL**: `POST /faults/insert`
- **설명**: 새로운 장애사항을 등록합니다.
- **Request Body**:
```json
{
  "context": "장애사항 내용",
  "user": "등록자"
}
```
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "장애사항이 등록되었습니다.",
  "data": null
}
```

### 1.3 장애사항 수정
- **URL**: `POST /faults/update`
- **설명**: 기존 장애사항을 수정합니다.
- **Request Body**:
```json
{
  "key": 1,
  "context": "수정된 장애사항 내용",
  "user": "수정자"
}
```
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "장애사항이 수정되었습니다.",
  "data": null
}
```

### 1.4 장애사항 삭제
- **URL**: `POST /faults/delete`
- **설명**: 장애사항을 삭제합니다.
- **Request Body**:
```json
{
  "key": 1,
  "user": "삭제자"
}
```
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "장애사항이 삭제되었습니다.",
  "data": null
}
```

## 2. 처리 조치 관리 API (/handles)

### 2.1 처리 조치 상세 조회
- **URL**: `GET /handles/detail`
- **설명**: 특정 민원의 처리 조치 상세 정보를 조회합니다.
- **Parameters**:
  - `complaintKey` (String): 민원 ID
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": {
    "complaintKey": "민원 ID",
    "pinNo": "PIN 번호",
    "systemKey": "시스템 고유 ID",
    "faultKey": 1,
    "user": "수정자",
    "context": "수정 내용"
  }
}
```

### 2.2 처리 조치 등록
- **URL**: `POST /handles/insert`
- **설명**: 새로운 처리 조치를 등록합니다.
- **Request Body**:
```json
{
  "complaintKey": "민원 ID",
  "pinNo": "PIN 번호",
  "systemKey": "시스템 ID",
  "faultKey": 1,
  "user": "등록자",
  "context": "처리 내용"
}
```
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "처리 조치가 등록되었습니다.",
  "data": null
}
```

### 2.3 처리 조치 수정
- **URL**: `POST /handles/update`
- **설명**: 기존 처리 조치를 수정합니다.
- **Request Body**:
```json
{
  "complaintKey": "민원 ID",
  "pinNo": "PIN 번호",
  "systemKey": "시스템 ID",
  "faultKey": 1,
  "user": "수정자",
  "context": "수정된 처리 내용"
}
```
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "처리 조치가 수정되었습니다.",
  "data": null
}
```

### 2.4 처리 조치 삭제
- **URL**: `POST /handles/delete`
- **설명**: 처리 조치를 삭제합니다.
- **Request Body**:
```json
{
  "complaintKey": "민원 ID"
}
```
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "처리 조치가 삭제되었습니다.",
  "data": null
}
```

## 3. PIN 번호 관리 API (/pinNo)

### 3.1 Service Key 목록 조회
- **URL**: `GET /pinNo/list`
- **설명**: 민원 ID를 기반으로 Service Key 목록을 조회합니다.
- **Parameters**:
  - `complaintId` (String): 민원 ID
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": [
    {
      "value": "PIN 번호"
    }
  ]
}
```

## 4. 시스템 정보 API (/systems)

### 4.1 시스템 위치 목록 조회
- **URL**: `GET /systems/locationList`
- **설명**: 터미널 내/외부 시스템 위치 목록을 조회합니다.
- **Request**: 없음
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "시스템 위치 목록 조회 성공",
  "data": [
    {
      "value": "시스템 위치 고유 번호",
      "label": "시스템 위치 이름"
    }
  ]
}
```

### 4.2 시스템 상세 목록 조회
- **URL**: `GET /systems/detailList`
- **설명**: 특정 시스템 위치의 상세 시스템 목록을 조회합니다.
- **Parameters**:
  - `systemLoc` (String): 시스템 위치
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": [
    {
      "value": "상세 시스템 고유 번호",
      "label": "상세 시스템 이름"
    }
  ]
}
```

## 5. 샘플/테스트 API (/)

### 5.1 Hello World
- **URL**: `GET /hello`
- **설명**: 시스템 상태 확인용 헬로우 메시지를 반환합니다.
- **Request**: 없음
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": "Hello CPC Complaint Handling System!"
}
```

### 5.2 Echo
- **URL**: `POST /echo`
- **설명**: 요청한 데이터를 그대로 반환하는 테스트 API입니다.
- **Request Body**: 임의의 JSON 객체
- **Response**:
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": {
    "received": {요청한 데이터},
    "timestamp": 1234567890
  }
}
```

### 5.3 데이터베이스 연결 테스트
- **URL**: `GET /db-test`
- **설명**: 데이터베이스 연결 상태를 테스트합니다.
- **Request**: 없음
- **Response** (성공 시):
```json
{
  "result": "success",
  "resultMessage": "정상 처리되었습니다.",
  "data": {
    "connected": true,
    "database": "데이터베이스명",
    "url": "jdbc:mysql://...",
    "user": "사용자명"
  }
}
```
- **Response** (실패 시):
```json
{
  "result": "failure",
  "resultMessage": "데이터베이스 연결 실패",
  "data": {
    "connected": false,
    "error": "에러 메시지"
  }
}
```

## 에러 처리
- 모든 API에서 예외 발생 시 `result: "failure"` 상태로 응답
- HTTP 상태 코드는 대부분 200 OK를 사용하며, 응답 본문의 `result` 필드로 성공/실패 구분
- 에러 메시지는 `resultMessage` 필드에 한국어로 제공

## 데이터 타입
- `key`, `faultKey`: Integer (정수형)
- `value`, `label`, `complaintKey`, `pinNo`, `systemKey`, `user`, `context`: String (문자열)
- 모든 날짜/시간: Long (timestamp, 밀리초 단위)

## 참고사항
- Base URL: 프로젝트 배포 환경에 따라 설정
- Content-Type: `application/json`
- 모든 POST 요청은 JSON 형식의 Request Body 필요
- Elasticsearch를 통한 Service Key 검색 기능 포함
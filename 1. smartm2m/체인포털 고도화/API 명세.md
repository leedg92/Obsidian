# ChainPortal HealthCheck Backend API 명세서

  

## 기본 정보

- **Base URL**: `http://{Host:port}/api` (개발환경)

- **Content-Type**: `application/json`

- **API Version**: 1.0.0

  

## 서버 상태 확인

  

### 1. 서버 헬스체크

- **URL**: `GET /health`

- **기능**: 서버 상태 확인

- **Parameters**: 없음

- **Response**:

```json

{

  "status": "ok",

  "timestamp": "2024-01-01T00:00:00.000Z",

  "uptime": 3600,

  "version": "1.0.0"

}

```

  

## 헬스체크 API 그룹

  

### 1. 헬스체크 조회

- **URL**: `POST /api/healthcheck`

- **기능**: 지정된 터미널/서버의 헬스체크 상태 조회

- **Parameters**:

  - **Body**:

    ```json

    {

      "targetName": "string" // 필수

    }

    ```

  - **targetName 가능한 값**:

    - 터미널: `PNIT`, `PNC`, `HJNC`, `HPNT`, `BNCT`, `BCT`, `BPTS`, `BPTG`, `DGT`, `HKTG`

    - API 서버: `ALLCONE-API`, `BCTRANS-API`

- **Response**:

```json

{

  "targetName": "string",

  "result": "SUCCESS" | "FAIL",

  "resultMessage": "string",

  "data": {}

}

```

  

### 2. 데드락 상태 조회

- **URL**: `POST /api/deadlocks`

- **기능**: 지정된 터미널/서버의 데드락 상태 조회

- **Parameters**:

  - **Body**:

    ```json

    {

      "targetName": "string" // 필수

    }

    ```

  - **targetName 가능한 값**:

    - 터미널: `PNIT`, `PNC`, `HJNC`, `HPNT`, `BNCT`, `BCT`, `BPTS`, `BPTG`, `DGT`, `HKTG`

    - API 서버: `ALLCONE-API`, `BCTRANS-API`

  - **주의사항**: `HPNT`, `BNCT`, `BPT`, `BPTG`, `HKTG` 터미널은 데드락 상태 조회가 현재 불가능

- **Response**:

```json

{

  "targetName": "string",

  "result": "SUCCESS" | "FAIL",

  "resultMessage": "string",

  "data": {}

}

```

  

### 3. 메모리 상태 조회

- **URL**: `POST /api/memory`

- **기능**: 지정된 터미널/서버의 메모리 상태 조회

- **Parameters**:

  - **Body**:

    ```json

    {

      "targetName": "string" // 필수

    }

    ```

  - **targetName 가능한 값**:

    - 터미널: `PNIT`, `PNC`, `HJNC`, `HPNT`, `BNCT`, `BCT`, `BPTS`, `BPTG`, `DGT`, `HKTG`

    - API 서버: `ALLCONE-API`, `BCTRANS-API`

- **Response**:

```json

{

  "targetName": "string",

  "result": "SUCCESS" | "FAIL",

  "resultMessage": "string",

  "data": {}

}

```

  

### 4. 스레드 상태 조회

- **URL**: `POST /api/threads`

- **기능**: 지정된 터미널/서버의 스레드 상태 조회

- **Parameters**:

  - **Body**:

    ```json

    {

      "targetName": "string" // 필수

    }

    ```

  - **targetName 가능한 값**:

    - 터미널: `PNIT`, `PNC`, `HJNC`, `HPNT`, `BNCT`, `BCT`, `BPTS`, `BPTG`, `DGT`, `HKTG`

    - API 서버: `ALLCONE-API`, `BCTRANS-API`

- **Response**:

```json

{

  "targetName": "string",

  "result": "SUCCESS" | "FAIL",

  "resultMessage": "string",

  "data": {}

}

```

  

## 스케줄러 관리 API 그룹

  

### 1. 작업 목록 조회

- **URL**: `GET /api/scheduler/tasks`

- **기능**: 등록된 스케줄러 작업 목록 조회

- **Parameters**: 없음

- **Response**:

```json

{

  "tasks": [

    {

      "name": "string",

      "pattern": "string",

      "scheduled": boolean,

      "running": boolean,

      "description": "string"

    }

  ],

  "total": number

}

```

  

### 2. 작업 패턴 수정

- **URL**: `PUT /api/scheduler/tasks/:name/pattern`

- **기능**: 스케줄러 작업의 cron 패턴 수정

- **Parameters**:

  - **Path**: `name` (string) - 작업명

  - **Body**:

    ```json

    {

      "pattern": "string" // 필수, cron 패턴 (예: "0 0 * * *")

    }

    ```

- **Response**:

```json

{

  "success": boolean,

  "message": "string",

  "task": {

    "name": "string",

    "pattern": "string",

    "scheduled": boolean,

    "running": boolean,

    "description": "string"

  }

}

```

  

### 3. 작업 상태 변경

- **URL**: `PUT /api/scheduler/tasks/:name/status`

- **기능**: 스케줄러 작업 상태 변경 (시작/중지)

- **Parameters**:

  - **Path**: `name` (string) - 작업명

  - **Body**:

    ```json

    {

      "action": "start" | "stop" // 필수

    }

    ```

- **Response**:

```json

{

  "success": boolean,

  "message": "string",

  "task": {

    "name": "string",

    "pattern": "string",

    "scheduled": boolean,

    "running": boolean,

    "description": "string"

  }

}

```

  

### 4. 데이터 아카이브 실행

- **URL**: `POST /api/scheduler/tasks/:name/archive`

- **기능**: 데이터 아카이브 (파일 저장만, DB 삭제 안함)

- **Parameters**:

  - **Path**: `name` (string) - 작업명 (현재 `monthly-archive`만 지원)

  - **Body**:

    ```json

    {

      "startDate": "string", // 필수, 형식: YYYY-MM-DD

      "endDate": "string"    // 필수, 형식: YYYY-MM-DD

    }

    ```

- **Response**:

```json

{

  "success": boolean,

  "message": "string",

  "executionId": "string",

  "period": "string",

  "result": {

    "totalFiles": number,

    "totalRecords": number,

    "totalTerminals": number,

    "executionTime": number

  }

}

```

  

### 5. 헬스체크 실행

- **URL**: `POST /api/scheduler/tasks/:name/healthCheck`

- **기능**: 헬스체크 실행 및 DB 저장

- **Parameters**:

  - **Path**: `name` (string) - 작업명 (현재 `healthcheck-batch`만 지원)

  - **Body**: 없음

- **Response**:

```json

{

  "success": boolean,

  "message": "string",

  "executionId": "string",

  "result": {

    "totalEndpoints": number,

    "totalChecks": number,

    "executionTime": number

  }

}

```

  

## 에러 응답 형식

  

### 공통 에러 응답

```json

{

  "statusCode": number,

  "error": "string",

  "message": "string"

}

```

  

### 주요 에러 코드

- **400**: Bad Request - 잘못된 요청 (유효성 검증 실패)

- **404**: Not Found - 경로 또는 리소스를 찾을 수 없음

- **500**: Internal Server Error - 서버 내부 에러

  

### 유효성 검증 실패 시

```json

{

  "statusCode": 400,

  "error": "Bad Request",

  "message": "Validation failed",

  "details": [

    {

      "field": "string",

      "message": "string"

    }

  ]

}

```

  

## 개발 환경 설정

  

### Swagger UI 접속

- **URL**: `http://localhost:3000/docs`

- **조건**: `NODE_ENV=development`이고 `ENABLE_SWAGGER=true`일 때만 활성화

  

### 환경 변수

- `NODE_ENV`: 환경 설정 (development/production)

- `PORT`: 서버 포트 (기본값: 3000)

- `HOST`: 서버 호스트 (기본값: 0.0.0.0)

- `API_PREFIX`: API 경로 prefix (기본값: /api)

- `ENABLE_SCHEDULER`: 스케줄러 활성화 여부 (기본값: true)

- `ENABLE_SWAGGER`: Swagger UI 활성화 여부 (기본값: true)

  

## 주의사항

  

1. **Rate Limiting**: 분당 100회 요청 제한

2. **Body Limit**: 최대 10MB

3. **타임아웃**: 연결 타임아웃 10초, Keep-Alive 타임아웃 30초

4. **로그 레벨**: `LOG_LEVEL` 환경변수로 설정 가능 (기본값: info)

5. **CORS**: 모든 도메인 허용 설정됨

6. **보안**: Helmet 미들웨어 적용, CSP 비활성화

  

## 연락처

- 개발팀: [개발팀 연락처]

- 문의사항: [문의사항 연락처]

  

---

*문서 최종 업데이트: 2024년 1월*
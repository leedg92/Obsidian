# E-slip Recovery API 명세서

**Base URL:** `/api/recovery`
**Content-Type:** `application/json`

---

## 1. 복구 요청

E-slip 복구를 외부 복구시스템에 요청하고, 요청 이력을 DB에 저장한다.

| 항목 | 내용 |
|------|------|
| **Method** | `POST` |
| **URL** | `/api/recovery` |

### Request Body

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| startDateTime | String | Y | 복구 시작 일시 (yyyyMMddHHmmss) |
| endDateTime | String | Y | 복구 종료 일시 (yyyyMMddHHmmss) |
| terminals | String[] | Y | 복구 대상 터미널 코드 목록 |
| recoveryBy | String | Y | 복구 요청자 |
| recoveryIp | String | Y | 복구 요청 IP |

```json
{
    "startDateTime": "20260212000000",
    "endDateTime": "20260212130000",
    "terminals": ["HJNPC010", "PNCOC010"],
    "recoveryBy": "tester",
    "recoveryIp": "192.168.1.100"
}
```

### Response Body

| 필드 | 타입 | 설명 |
|------|------|------|
| result | String | 처리 결과 코드 |
| resultMessage | String | 처리 결과 메시지 |
| data.totalCount | int | 복구 대상 전체 건수 |
| data.taskId | String | 복구 작업 ID (UUID) |

```json
{
    "result": "success",
    "resultMessage": "정상 처리되었습니다.",
    "data": {
        "totalCount": 2122,
        "taskId": "84bb2a97-6e14-4c41-8302-a56c6877e7dc"
    }
}
```

---

## 2. 재처리 요청

실패 건에 대해 선택된 터미널을 재복구 요청한다. 부모 taskId의 기간 정보를 그대로 사용한다.

| 항목 | 내용 |
|------|------|
| **Method** | `POST` |
| **URL** | `/api/recovery/retry` |

### Request Body

| 필드         | 타입       | 필수  | 설명                          |
| ---------- | -------- | --- | --------------------------- |
| taskId     | String   | Y   | 복구 작업 ID (최초 복구 요청의 taskId) |
| terminals  | String[] | Y   | 재처리 대상 터미널 코드 목록            |
| recoveryBy | String   | Y   | 재처리 요청자                     |
| recoveryIp | String   | Y   | 재처리 요청 IP                   |

```json
{
    "taskId": "84bb2a97-6e14-4c41-8302-a56c6877e7dc",
    "terminals": ["PNCOC010"],
    "recoveryBy": "tester",
    "recoveryIp": "192.168.1.100"
}
```

### Response Body

복구 요청과 동일한 구조 (새로운 taskId 발급)

```json
{
    "result": "success",
    "resultMessage": "정상 처리되었습니다.",
    "data": {
        "totalCount": 500,
        "taskId": "6922f8d4-f078-431d-a7e4-dba40100e802"
    }
}
```

---

## 3. 진행 상태 조회

부모 taskId 기준으로 복구 진행 상태를 조회한다.
부모 + 자식 task의 복구 결과를 순차적으로 병합하여, 동일 pinNo는 최신 재처리 결과로 덮어쓴다.
`terminalCode` 파라미터로 전체 또는 특정 터미널의 데이터를 필터링한다.

| 항목         | 내용                                                                   |
| ---------- | -------------------------------------------------------------------- |
| **Method** | `GET`                                                                |
| **URL**    | `/api/recovery/progress?taskId={taskId}&terminalCode={terminalCode}` |

### Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| taskId | String | Y | 부모 taskId |
| terminalCode | String | Y | 터미널 코드 (`ALL`: 전체, 특정 코드: 해당 터미널만) |

### Response Body

| 필드 | 타입 | 설명 |
|------|------|------|
| tasks | Object[] | 부모 + 자식 task 이력 목록 (부모 먼저, 자식은 recovery_at ASC) |
| tasks[].taskId | String | 복구 작업 ID |
| tasks[].parentTaskId | String | 부모 taskId (부모 task인 경우 null) |
| tasks[].startDateTime | String | 복구 시작 일시 |
| tasks[].endDateTime | String | 복구 종료 일시 |
| tasks[].totalCount | int | 복구 대상 건수 |
| tasks[].recoveryBy | String | 요청자 |
| tasks[].recoveryIp | String | 요청 IP |
| tasks[].recoveryAt | String | 요청 시각 |
| tasks[].terminalCodes | String | 대상 터미널 코드 (쉼표 구분) |
| statistics | Object | 통계 (terminalCode 범위에 따른 집계) |
| statistics.totalCount | int | 전체 건수 |
| statistics.successCount | long | 성공 건수 (recoveryStatus = "Y") |
| statistics.failCount | long | 실패 건수 (recoveryStatus = "N") |
| statistics.pendingCount | long | 대기 건수 (totalCount - successCount - failCount) |
| historyList | Object[] | 복구 운송오더 목록 (terminalCode 범위에 따른 필터링) |
| historyList[].pinNo | String | PIN 번호 |
| historyList[].channelCode | String | 채널 코드 |
| historyList[].recoveryStatus | String | 복구 상태 (Y: 성공, N: 실패) |
| historyList[].errorMessage | String | 실패 시 오류 메시지 |
| historyList[].taskId | String | 해당 결과의 복구 작업 ID |
| historyList[].terminalCode | String | 터미널 코드 |
| historyList[].recoveredAt | String | 복구 처리 일시 |
| historyList[].createdAt | String | 생성 일시 |

### 응답 예시 (terminalCode=ALL)

```json
{
    "result": "success",
    "resultMessage": "정상 처리되었습니다.",
    "data": {
        "tasks": [
            {
                "taskId": "84bb2a97-...",
                "parentTaskId": null,
                "startDateTime": "20260212000000",
                "endDateTime": "20260212130000",
                "totalCount": 2122,
                "recoveryBy": "tester",
                "recoveryIp": "192.168.1.100",
                "recoveryAt": "2026-02-12T16:32:38.000+00:00",
                "terminalCodes": "HJNPC010,PNCOC010"
            },
            {
                "taskId": "6922f8d4-...",
                "parentTaskId": "84bb2a97-...",
                "startDateTime": "20260212000000",
                "endDateTime": "20260212130000",
                "totalCount": 500,
                "recoveryBy": "tester",
                "recoveryIp": "192.168.1.100",
                "recoveryAt": "2026-02-12T16:33:01.000+00:00",
                "terminalCodes": "PNCOC010"
            }
        ],
        "statistics": {
            "totalCount": 2122,
            "successCount": 2100,
            "failCount": 5,
            "pendingCount": 17
        },
        "historyList": [
            {
                "pinNo": "SEGU4651144_부산98사4051_2_260212_1",
                "channelCode": "hjnpc010-shipper-hdloc050",
                "recoveryStatus": "Y",
                "errorMessage": null,
                "taskId": "84bb2a97-...",
                "terminalCode": "HJNPC010",
                "recoveredAt": "2026-02-12 16:34:59",
                "createdAt": "2026-02-12 16:34:59"
            }
        ]
    }
}
```

### 응답 예시 (terminalCode=HJNPC010)

```json
{
    "result": "success",
    "resultMessage": "정상 처리되었습니다.",
    "data": {
        "tasks": [
            {
                "taskId": "84bb2a97-...",
                "parentTaskId": null,
                "terminalCodes": "HJNPC010,PNCOC010",
                "..."
            }
        ],
        "statistics": {
            "totalCount": 1500,
            "successCount": 1490,
            "failCount": 3,
            "pendingCount": 7
        },
        "historyList": [
            {
                "pinNo": "SEGU4651144_부산98사4051_2_260212_1",
                "channelCode": "hjnpc010-shipper-hdloc050",
                "recoveryStatus": "Y",
                "errorMessage": null,
                "taskId": "84bb2a97-...",
                "terminalCode": "HJNPC010",
                "recoveredAt": "2026-02-12 16:34:59",
                "createdAt": "2026-02-12 16:34:59"
            }
        ]
    }
}
```

---

## 4. 복구 이력 목록

전체 복구 이력 목록을 조회한다. 부모 task만 대상으로 하며, 재처리 횟수를 포함한다.

| 항목         | 내용                   |
| ---------- | -------------------- |
| **Method** | `GET`                |
| **URL**    | `/api/recovery/list` |

### Response Body

| 필드 | 타입 | 설명 |
|------|------|------|
| [].taskId | String | 복구 작업 ID |
| [].startDateTime | String | 복구 시작 일시 |
| [].endDateTime | String | 복구 종료 일시 |
| [].totalCount | int | 복구 대상 건수 |
| [].recoveryBy | String | 요청자 |
| [].recoveryIp | String | 요청 IP |
| [].recoveryAt | String | 요청 시각 |
| [].retryCount | int | 재처리 횟수 |
| [].terminalCodes | String | 대상 터미널 코드 (쉼표 구분) |

```json
{
    "result": "success",
    "resultMessage": "정상 처리되었습니다.",
    "data": [
        {
            "taskId": "84bb2a97-...",
            "startDateTime": "20260212000000",
            "endDateTime": "20260212130000",
            "totalCount": 2122,
            "recoveryBy": "tester",
            "recoveryIp": "192.168.1.100",
            "recoveryAt": "2026-02-12T16:32:38.000+00:00",
            "retryCount": 1,
            "terminalCodes": "HJNPC010,PNCOC010"
        }
    ]
}
```

## 공통 응답 형식

모든 API는 `ResponseFormat`으로 래핑되어 반환된다.

```json
{
    "result": "success",
    "resultMessage": "정상 처리되었습니다.",
    "data": { ... }
}
```

### 에러 응답

```json
{
    "result": "fail",
    "resultMessage": "존재하지 않는 taskId입니다: xxx-xxx",
    "data": null
}
```

# BlockChain 데이터 복구 API 명세서

## 개요
모종의 이유로 bctrans에 alarm 데이터를 전송하지 못한 경우, 복구용 API를 통해 데이터를 재처리할 수 있습니다.

| 진행방향                  | 인터페이스          | URL                                               | 비고                          |
| --------------------- | -------------- | ------------------------------------------------- | --------------------------- |
| BlockChain -> bctrans | VBS 운송건 복구(단일) | {bctransUrl}/bctrans-api/vbs/invoke/recovery      | 기존 alarm호출방식과 동일(엔드포인트만 상이) |
| BlockChain -> bctrans | VBS 운송건 복구(벌크) | {bctransUrl}/bctrans-api/vbs/invoke/recovery/bulk | 단일 데이터셋의 리스트형태              |
| BlockChain -> bctrans | TSS 운송건 복구(단일) | {bctransUrl}/bctrans-api/itt/invoke/recovery      | 기존 alarm호출방식과 동일(엔드포인트만 상이) |
| BlockChain -> bctrans | TSS 운송건 복구(벌크) | {bctransUrl}/bctrans-api/itt/invoke/recovery/bulk | 단일 데이터셋의 리스트형태              |

---

## 1. VBS 복구 API

### 1.1 단일 데이터 복구
**기본 정보**
- **URL**: `POST /vbs/invoke/recovery`
- **Content-Type**: `application/json`
- **설명**: 단일 VBS 운송건을 복구 처리합니다.

**Request Body**
```json
{
  "method": "CopinoVerificationResult",
  "resultMessage": {
    "message": {
      "dispatchInfoId": "12345",
      "terminalCode": "PIER_01",
      "truckNo": "12가3456",
      "copinoCheckStatus": "SUCCESS"
    }
  }
}
```

**Response**
```json
{
    "result": "success",
    "resultMessage": "",
    "data": null
}
```

### 1.2 벌크 데이터 복구
**기본 정보**
- **URL**: `POST /vbs/invoke/recovery/bulk`
- **Content-Type**: `application/json`
- **설명**: 여러 VBS 운송건을 한 번에 복구 처리합니다.

**Request Body**
```json
[
  {
    "method": "CopinoVerificationResult",
    "resultMessage": {
      "message": {
        "dispatchInfoId": "12345",
        "terminalCode": "PIER_01",
        "truckNo": "12가3456"
      }
    }
  },
  {
    "method": "ReeferPlugInoutResult",
    "resultMessage": {
      "message": {
        "dispatchInfoId": "12346",
        "terminalCode": "PIER_01",
        "plugStatus": "IN"
      }
    }
  }
]
```

**Response**
```json
{
    "result": "success",
    "resultMessage": "",
    "data": null
}
```

---

## 2. TSS 복구 API

### 2.1 단일 데이터 복구
**기본 정보**
- **URL**: `POST /itt/invoke/recovery`
- **Content-Type**: `application/json`
- **설명**: 단일 TSS 운송건을 복구 처리합니다.

**Request Body**
```json
{
  "method": "GateOut",
  "resultMessage": {
    "message": {
      "dispatchInfoId": "67890",
      "terminalCode": "TERM_02",
      "truckNo": "34나5678",
      "latestStatus": "100"
    }
  }
}
```

**Response**
```json
{
    "result": "success",
    "resultMessage": "",
    "data": null
}
```

### 2.2 벌크 데이터 복구
**기본 정보**
- **URL**: `POST /itt/invoke/recovery/bulk`
- **Content-Type**: `application/json`
- **설명**: 여러 TSS 운송건을 한 번에 복구 처리합니다.

**Request Body**
```json
[
  {
    "method": "StartGroupOrder",
    "resultMessage": {
      "message": {
        "groupId": "GROUP_001",
        "terminalCode": "TERM_02"
      }
    }
  },
  {
    "method": "GateOut",
    "resultMessage": {
      "message": {
        "dispatchInfoId": "67890",
        "terminalCode": "TERM_02",
        "latestStatus": "100"
      }
    }
  },
  {
    "method": "JobDone",
    "resultMessage": {
      "message": {
        "dispatchInfoId": "67891",
        "terminalCode": "TERM_02",
        "latestStatus": "110"
      }
    }
  }
]
```

**Response**
```json
{
    "result": "success",
    "resultMessage": "",
    "data": null
}
```

---

## 3. 참고

### 3.1 데이터 호환성
- **복구 API는 기존 alarm API와 동일한 데이터 구조를 사용합니다.**
- 기존에 `/vbs/invoke/alarm` 또는 `/itt/invoke/alarm`으로 보내던 데이터를 그대로 사용 가능합니다.

### 3.2 FCM 처리
- **복구 API는 FCM 알림을 발송하지 않습니다.**
- 데이터베이스에 해당 운송 건에 대한 복구가 필요할 시 사용하는 함수로써 DB 삽입/수정/삭제만을 행합니다.

### 3.3 에러 처리
- 벌크 처리 시 개별 데이터 실패가 전체 처리를 중단하지 않습니다.(필요시 처리 중단, 중단점 return 방식으로 변경가능합니다.)

**잘못된 요청 예시**
```json
// 단일 엔드포인트에 배열 데이터를 보낸 경우
POST /vbs/invoke/recovery
[{...}, {...}]  // X

// 응답
{
    "result": "failure",
    "resultMessage": "Array data sent to single object endpoint. Use /recovery/bulk for array data",
    "data": null
}
```

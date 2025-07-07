# ChainPortal HealthCheck Backend API 명세서

## 1. 데드락 상태 조회 API

**api 기능명**: 데드락 상태 조회  
**api 앤드포인트**: `POST /api/v1/deadlocks`  
**parameters**:
```json
{
  "targetName": "string"
}
```
**response**:
- **200 성공**
```json
{
  "targetName": "BCT",
  "result": "SUCCESS",
  "resultMessage": "데드락 상태 조회 성공",
  "data": {
    "deadlockCount": 0,
    "deadlockInfo": []
  }
}
```
- **422 실패**
```json
{
  "targetName": "BCT",
  "result": "FAIL",
  "resultMessage": "데드락 상태 조회 실패: 연결 오류",
  "data": null
}
```

## 2. 헬스체크 상태 조회 API

**api 기능명**: 헬스체크 상태 조회  
**api 앤드포인트**: `POST /api/v1/healthcheck`  
**parameters**:
```json
{
  "targetName": "string"
}
```
**response**:
- **200 성공**
```json
{
  "targetName": "BCT",
  "result": "SUCCESS",
  "resultMessage": "헬스체크 조회 성공",
  "data": {
    "status": "UP",
    "timestamp": "2024-01-01T00:00:00Z",
    "responseTime": 150
  }
}
```
- **422 실패**
```json
{
  "targetName": "BCT",
  "result": "FAIL",
  "resultMessage": "헬스체크 조회 실패: 타임아웃 발생",
  "data": null
}
```

## 3. 메모리 상태 조회 API

**api 기능명**: 메모리 상태 조회  
**api 앤드포인트**: `POST /api/v1/memory`  
**parameters**:
```json
{
  "targetName": "string"
}
```
**response**:
- **200 성공**
```json
{
  "targetName": "BCT",
  "result": "SUCCESS",
  "resultMessage": "메모리 상태 조회 성공",
  "data": {
    "totalMemory": 8192,
    "usedMemory": 4096,
    "freeMemory": 4096,
    "memoryUsage": 50.0
  }
}
```
- **422 실패**
```json
{
  "targetName": "BCT",
  "result": "FAIL",
  "resultMessage": "메모리 상태 조회 실패: 서버 응답 없음",
  "data": null
}
```

## 4. 스레드 상태 조회 API

**api 기능명**: 스레드 상태 조회  
**api 앤드포인트**: `POST /api/v1/threads`  
**parameters**:
```json
{
  "targetName": "string"
}
```
**response**:
- **200 성공**
```json
{
  "targetName": "BCT",
  "result": "SUCCESS",
  "resultMessage": "스레드 상태 조회 성공",
  "data": {
    "totalThreads": 25,
    "activeThreads": 15,
    "blockedThreads": 2,
    "waitingThreads": 8
  }
}
```
- **422 실패**
```json
{
  "targetName": "BCT",
  "result": "FAIL",
  "resultMessage": "스레드 상태 조회 실패: 인증 오류",
  "data": null
}
```

## 터미널 종류

**사용 가능한 targetName 값**:
- **BCT**: 부산체인 터미널
- **BNCT**: 부산항 신컨테이너 터미널
- **BPTG**: 부산포트터미널(감만)
- **BPTS**: 부산포트터미널(신선대)
- **DGT**: 대구내륙터미널
- **HJNC**: 현대제철 신항컨테이너터미널
- **HKTG**: 한국허치슨터미널(감만)
- **HPNT**: 한국허치슨터미널(신항)
- **PNC**: 부산신항 컨테이너터미널
- **PNIT**: 부산신항국제터미널
- **BCTRANS_API**: BCTRANS API 서버
- **ALLCONE_API**: ALLCONE API 서버 
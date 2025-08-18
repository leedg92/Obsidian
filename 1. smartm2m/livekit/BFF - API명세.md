# Mirroring API 명세서

## 1. 미러링 시작

### API 정보

- **API명**: `http://133.186.222.171:19090/mirroring/startMirroring`
- **Method**: `POST`
- **용도**: 트럭번호와 상담사 아이디를 받아서 JWT 토큰을 생성하고, 운전기사에게 FCM 알림을 전송한 후 상담사에게 토큰을 리턴

### Request Body

```json
{
  "truckNo": "string",      // 트럭번호 (필수)
  "counselorId": "string"   // 상담사 아이디 (필수)
}
```

### Response

```json
{
  "success": true,
  "data": "eyJhbGciOiJIUzI1NiJ9...",  // JWT 토큰 (상담사용)
  "message": null
}
```

### Error Response

```json
{
  "success": false,
  "data": null,
  "message": "트럭번호와 상담사 아이디를 입력해주세요."
}
```

---

## 2. 룸 목록 조회

### API 정보

- **API명**: `http://133.186.222.171:19090/mirroring/getRoomList`
- **Method**: `GET`
- **용도**: 현재 생성된 미러링 룸 목록을 조회

### Request

- Body 없음

### Response

```json
{
  "success": true,
  "data": [
    "truck001_counselor001_mir",
    "truck002_counselor002_mir"
  ],
  "message": null
}
```

---

## 3. 미러링 종료

### API 정보

- **API명**: `http://133.186.222.171:19090/mirroring/endMirroring`
- **Method**: `POST`
- **용도**: 미러링 세션을 종료하고, 상담사가 종료한 경우 운전기사에게 FCM 알림을 전송

### Request Body

```json
{
  "truckNo": "string",      // 트럭번호 (필수)
  "counselorId": "string",  // 상담사 아이디 (필수)
  "counselor": boolean      // 상담사 여부 (true: 상담사가 종료, false: 운전기사가 종료)
}
```

### Response

```json
{
  "success": true,
  "data": null,
  "message": null
}
```

### Error Response

```json
{
  "success": false,
  "data": null,
  "message": "트럭번호와 상담사 아이디를 입력해주세요."
}
```

---

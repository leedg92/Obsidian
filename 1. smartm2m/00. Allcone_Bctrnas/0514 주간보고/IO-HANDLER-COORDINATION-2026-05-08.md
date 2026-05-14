# 외부 IO 페이즈 — 신 allcone 팀 협의 항목 (2026-05-08)

> **bctrans 측 작업 범위**: handler 모듈에 chainportal/FCM 등 외부 IO 어댑터 신설 + core 호출을 handler 위임으로 전환 완료.
> **allcone 측 작업 범위**: 본 협의서의 §1, §2, §3 항목. 양측 동시 배포 시 정상 동작 보장을 위해 협의 필요.

bctrans 브랜치: `feature/msa/bctrans/phase-1`
allcone 참조 브랜치: `origin/feature/gayeon/BCTRA-25-backend` (`24fd738` 기준)

---

## §1. chainportal handler 호출 명세 (allcone 의 NotificationTargetResolver 변경 요청)

### 배경
- bctrans handler 모듈에 `/handler/chainportal/users/by-truck` 신규 endpoint 추가.
- 기능: truckNo 리스트 → 각 truckNo 별 userId 리스트 매핑 조회.
- 현재 allcone 의 `NotificationTargetResolver` 는 truckNo 만으로 driver 변환 (userId 미해석).
- allcone 폴링 → truckNo 추출 → handler chainportal 호출 → userId 리스트 → 자체 device_token 조회 → handler FCM 호출, 흐름으로 변경 요청.

### 호출 명세

**URL**: `POST {bctrans-handler-url}/handler/chainportal/users/by-truck`

**Request body**:
```json
{
  "truckNos": ["1234가1234", "5678나5678"]
}
```

**Response body** (success):
```json
{
  "status": "success",
  "data": {
    "items": [
      { "truckNo": "1234가1234", "userIds": ["user-001", "user-002"] },
      { "truckNo": "5678나5678", "userIds": [] }
    ]
  }
}
```

**Response body** (failure):
```json
{
  "status": "failure",
  "error": { "code": "...", "message": "..." }
}
```

### 동작 보장
- **truckNo 입력 순서 = items 순서 보존**. allcone 측이 인덱스 기반 매핑 가능.
- **매칭 없는 truckNo 는 userIds 빈 리스트로 포함**됨 (404 아님).
- 한 truck 에 복수 userId 매칭 가능 (`user_regist_truck` 다대다).
- 타임아웃: 5s. 실패 시 allcone 측에서 알림 처리 skip + 로그.

### 임시 단계 안내
- bctrans handler 가 chainportal API 미개발 상태에서 임시로 chainportal DB 직접 접속.
- chainportal 측 API 개발 완료 시 handler 측 `chainportal.client=http` property 스왑만으로 동일 wire format 유지하며 전환.
- allcone 측 코드는 영향 없음.

---

## §2. EventCode enum 3개 추가 + Translator 매핑

### 배경
- bctrans 측 outbox INSERT 코드는 Phase 2-A 에서 작성됨 (commit `44537d5b`).
- allcone 측 EventCode enum 에 다음 3개가 누락되어 있어 outbox 폴링 시 처리 불가.

### 추가 요청 EventCode
| Enum 값 | 발생 시점 | 비고 |
|---|---|---|
| `VBS.GATE_IN_WITHOUT_COPINO` | VBS 게이트인 시 코피노 미보유 케이스 | bctrans outbox INSERT 위치: VBS gate-in 처리 |
| `ITT.GROUP_ORDER_EXPIRED` | ITT 그룹 오더 만료 (24h 경과 자동 cancel) | bctrans outbox INSERT 위치: 그룹 오더 만료 스케줄러 |
| `ITT.GROUP_ORDER_UPDATE` | ITT 그룹 오더 업데이트 | bctrans outbox INSERT 위치: 그룹 오더 변경 처리 |

### Translator 메서드 추가
- `IttNotificationTranslator` / `VbsNotificationTranslator` 에 위 EventCode 별 메서드 추가.
- 메시지 포맷은 기존 `ITT.CHANGE_TRUCK_NO`, `VBS.RESERVATION_RESULT` 등과 동일 톤.
- 알림 대상 결정은 §1 의 chainportal 어댑터 호출 후 userId 리스트 기반.

---

## §3. FCM 발송 위임 전환 (allcone 의 FcmPushSender 변경 요청)

### 배경
- 신 allcone 의 `FcmPushSender` 가 현재 Firebase Admin SDK 직접 호출.
- 외부 IO 일원화를 위해 bctrans handler 의 `/handler/fcm/send` 호출로 전환 요청.
- bctrans 측은 이미 `FCMNotificationService` 가 동일 endpoint 호출로 전환 완료.

### 호출 명세

**URL**: `POST {bctrans-handler-url}/handler/fcm/send`

**Request body**:
```json
{
  "to": "fcm-token-or-/topics/foo",
  "registrationIds": ["t1", "t2"],
  "notification": { "title": "...", "body": "..." },
  "clickAction": "VERIFY_RESULT",
  "data": {
    "click_action": "VERIFY_RESULT",
    "alertType": "...",
    "info": "{...stringify...}"
  }
}
```

**Response body** (success):
```json
{
  "status": "success",
  "data": { "sent": true }
}
```

### 동작
- `registrationIds` 비어있으면 단건 발송 (token 또는 /topics/{name}).
- `registrationIds` 있으면 multicast (500개 chunk + 일시 실패 토큰 단건 retry).
- handler 측 `RetryableFirebaseMessaging` 이 backoff 재시도 (1s, 3s, 9s).
- 응답 `sent: false` 는 영구 실패 (UNREGISTERED, INVALID_ARGUMENT 등).
- 타임아웃: 10s. allcone 측은 결과 로그만, 실패 시 token 정리 등 후속 처리는 별도 협의.

### 마이그레이션 윈도우
- bctrans 측 handler 는 2026-05-08 부로 routes 활성화.
- 신 allcone 측 컷오버 시점은 자유 (양측 호환). 컷오버 전까지 신 allcone 의 직접 Firebase 호출 그대로 유지 가능.

---

## §4. 마감 일정 / 호환 윈도우

| 항목 | 시점 |
|---|---|
| bctrans 측 handler routes 활성화 | 2026-05-08 commit 완료 (단계 1~17) |
| bctrans 측 빌드 검증 + 테스트베드 배포 | 외부 IO + 내부 분리 페이즈 모두 끝난 후 일괄 (사용자 결정 2026-05-08) |
| 신 allcone 측 §1 chainportal 어댑터 호출 추가 | allcone 팀 일정 |
| 신 allcone 측 §2 EventCode 3개 + translator | allcone 팀 일정 |
| 신 allcone 측 §3 FCM 위임 전환 | allcone 팀 일정 (자유 컷오버) |
| 양측 통합 테스트 윈도우 | 양측 개별 작업 완료 후 협의 |

---

## §5. 추가 협의 사항

### 핸들러 컴포넌트 공식 이름
- 가칭 "handler" (현 모듈명). 추후 정식 명칭 결정 시 양측 동시 변경 필요.

### handler URL 환경별 endpoint
- bctrans 운영: 환경변수 `HANDLER_URL` 또는 `application-{env}.properties` 의 `handler.url` 로 주입.
- allcone 측에서 호출 시 동일한 URL 정책 사용. 양측 운영 측 협의 필요.

### 인증 정책 (handler 보호)
- 현재: 도커 내부망 신뢰. 애플리케이션 인증 없음.
- 향후 (Phase 외부): 내부 토큰 / IP 화이트리스트 등 검토.

### chainportal API 정식 출시 후 컷오버
- bctrans handler 는 `chainportal.client=http` 로 스왑만 하면 됨.
- allcone 측 변경 없음 (handler endpoint 동일).
- 단, chainportal API 측 응답 wire format 이 §1 과 동일해야 함 (협의 필요).

---

## 부록: bctrans 측 commit 이력 (단계 1~17)

| 단계 | 영역 | commit | 요지 |
|---|---|---|---|
| 1-2 | handler 인프라 | `709d1508` | pom 의존성 + envelope/예외/RestTemplate |
| 3 | KTNET | `c5a34c8b` | KTNet 어댑터 (WebClient + 10s timeout) |
| 4 | TMS | `2a14fac4` | TMS vendor 라우터 |
| 5 | BChain | `6b01273c` | ITT/VBS 채널 분기 |
| 6 | Terminal | `6f02cfdf` | apiKey 헤더 + 동기 RestTemplate |
| 7 | chainportal DB | `30d102d6` | ChainportalUserClient + JDBC 임시 구현 |
| 8 | FCM | `34084544` | Firebase SDK + 단건/멀티캐스트 + Retryable |
| 9 | AAS | `8b58cce7` | validate/callback raw body forward |
| 10 | core HandlerClient | `5611318e` | envelope DTO + handlerRestTemplate Bean |
| 11 | core BChain 전환 | `147341d8` | BChainService/VbsBChainService 위임 |
| 12 | core Terminal 전환 | `4481ab8a` | TerminalRequestClient*Service 위임 |
| 13 | core TMS 전환 | `d8732954` | TssGroupOrderPushService/PushTruckerService 위임 |
| 14 | core KTNET 전환 | `d6320ee7` | MovementAsyncService 위임 |
| 15 | core FCM 전환 | `f7729443` | FCMNotificationService 위임 |
| 16 | core AAS 전환 | `4ad51890` | AASAdapter raw JSON forward |
| 17 | core BlockChainAdapter 흡수 | `c33197b6` + `5e2a2be3` | BChain raw endpoint + BlockChainAdapter 위임 |

---

문서 종료.

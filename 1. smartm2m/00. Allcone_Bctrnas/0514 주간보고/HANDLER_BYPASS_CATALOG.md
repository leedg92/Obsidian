# core → handler 외부 I/O 바이패스 카탈로그

> 생성: 2026-04-30 (Phase 1 §4)
> 갱신: 2026-05-08 (외부 IO 페이즈 완료)
> 갱신: 2026-05-12 (회원 보강 페이즈 완료 - chainportal 회원 endpoint 31 미러링 추가)
>
> Phase 1: handler placeholder Controller 만 작성 — ✅ 완료
> 외부 IO 페이즈 (2026-05-08): handler 어댑터 8종 실제 구현 + core 호출 8종 전환 + 협의서 송부 — ✅ 완료
> 단계 18 결정 (2026-05-08): plan 의 "outbox 폐기" 가 misidentification (실제 outbox 대체 = a-fcm-1/a-fcm-2, 이미 완료). SendNotificationToTruckerAdapter 는 TSS callback 별개 영역 → handler 위임으로 처리 — ✅ 완료
> 회원 보강 페이즈 (2026-05-12): feature/memberTableChange 회원 4 패키지(auth/sign/user/alarm_config) handler 미러링 — ✅ 완료. 신 allcone 측이 회원 Feign client 를 만들면 그대로 base url 만 handler 로 변경하면 바이패스 전환 가능.

## 카테고리별 합계 (2026-05-12 기준)

| 카테고리 | 호출 지점 | 메인 호출 수 | handler endpoint | 단계 |
|---|---|---|---|---|
| 블록체인 (BChain) | 10 | 25+ | `POST /handler/bchain/exchange` | ✅ 5, 11 |
| 블록체인 raw (TSS Open API) | 1 | 3 | `POST /handler/bchain/raw` | ✅ 17 |
| 터미널 API | 2 | 7+ | `POST /handler/terminal/exchange` | ✅ 6, 12 |
| FCM | 5 | 20+ | `POST /handler/fcm/send` | ✅ 8, 15 |
| 운송사 TMS | 5 | 5+ | `POST /handler/tms/{vendor}/push` | ✅ 4, 13 |
| KTNet | 1 | 1 | `POST /handler/ktnet/movement` | ✅ 3, 14 |
| AAS 인증 | 2 | 2 | `POST /handler/aas/tokens/{validate\|callback}` | ✅ 9, 16 |
| TSS Open API 운송사 callback | 4 | 4+ | `POST /handler/trucker/callback` | ✅ 18 |
| 회원 보강 (chainportal mirror) | — | — | 32 endpoint (auth 5 + sign 6 + user 18 + alarm_config 2 + by-truck 1, `/mobile/...`) | ✅ 회원 보강 페이즈 + 통합 |
| **합계** | **30** | **67+** | **9 카테고리** | — |

> 2026-05-12: 기존 chainportal (신규) 카테고리의 `/handler/chainportal/users/by-truck` endpoint 는 회원 영역으로 통합 이동 (`POST /mobile/user/truck/by-truck`, envelope `ApiResponse`). 통합 commit `2316d23f`. 자세한 spec 은 `IO-HANDLER-COORDINATION-2026-05-12-회원.md` §5-1 참조.

## 호출 지점 상세 (이관 완료)

### 블록체인 (BChain) — 단계 5, 11
- `BChainService.exchange()` 가 `BchainHandlerClient.exchange("ITT", ...)` 위임
- `VbsBChainService.exchange()` 가 `BchainHandlerClient.exchange("VBS", ...)` 위임
- 시그니처 무변경. 호출자 (AllconeVbsTruckTransOrderService 등) 수정 불필요.

| 파일:라인 | 호출 | 외부 엔드포인트 |
|---|---|---|
| `AllconeVbsTruckTransOrderService:88` | `vbsBChainService.exchange()` | `/vbs/bpa/ConfirmAppointment` |
| `AllconeVbsTruckTransOrderService:110` | `vbsBChainService.exchange()` | `/vbs/bpa/CancelAppointment` |
| `AllconeVbsTruckTransOrderService:140` | `vbsBChainService.exchange()` | `/vbs/bpa/UpdateAppointment` |
| `AllconeVbsTruckTransOrderService:232` | `vbsBChainService.exchange()` | `/vbs/bpa/CheckAppointmentCompliance` |
| `BctransVbsTruckTransOrderService:130` | `vbsBChainService.exchange()` | `/vbs/bpa/GetCopinoWithReservation` |
| `CpsService:38` | `vbsBChainService.exchange()` | `/vbs/terminal/OnCPSAutomationReady` |
| `IttTruckTransStatusUpdateService:79` | `bChainService.exchange()` | `/driver/UpdateTransStatus` |
| `BctransIttTruckTransOrderService:141/145` | `bChainService.exchange()` | `/terminal/GetCopino` |
| `TssGroupOrderService:240/248/344/502` | `bChainService.exchange()` | `/terminal/UpdateConInfoWithDispatchGroup` |

### 블록체인 raw (TSS Open API) — 단계 17
- `BlockChainAdapter` 의 3 메서드가 `BchainHandlerClient.rawExchange()` 위임
- raw endpoint 사유: 강타입 DTO 송신 + BChainParam wrapping 없음 + 응답 검증 없음 (옛 동작 보존)

| 파일:라인 | 호출 | 외부 엔드포인트 |
|---|---|---|
| `BlockChainAdapter.reportSingleOrder` | `bchainHandlerClient.rawExchange()` | `/trans/CreateCopino` |
| `BlockChainAdapter.getTransHistory` | `bchainHandlerClient.rawExchange()` | `/trans/GetTransHistory` |
| `BlockChainAdapter.getVbsTransHistory` | `bchainHandlerClient.rawExchange()` | `/vbs/bpa/GetTransHistory` |

### 터미널 API (외부 항만 시스템) — 단계 6, 12
- `TerminalRequestClientService` 의 5 메서드 + `IttTerminalRequestService` 의 3 메서드가 `TerminalHandlerClient.exchange()` 위임
- bctrans loop-back endpoint (`requestGateInReqeustBctrans` 등) 는 자기 자신 호출이라 WebClientService 유지

| 파일:라인 | 호출 | 비고 |
|---|---|---|
| `TerminalRequestClientService.requestGateIn/...` (5 메서드) | `terminalHandlerClient.exchange()` | DB 의 TerminalApiInfoVo 조회 후 위임 |
| `IttTerminalRequestService.requestGateIn/...` (3 메서드) | `terminalHandlerClient.exchange()` | 동일 |

### FCM (Firebase Cloud Messaging) — 단계 8, 15
- `FCMNotificationService.sendPushData(FcmMessage)` 가 `FcmHandlerClient.send()` 위임
- 시그니처 무변경. dryRun 옵션은 호환만 유지하고 무시.

| 파일:라인 | 호출 | 비고 |
|---|---|---|
| `UserSignService:57` | `fcmNotificationService.sendPushData()` | 회원 가입 알림 |
| `UserTruckService:170` | `fcmNotificationService.sendPushData()` | 차량 등록 알림 |
| `VbsInvokeAlarmService` (8+ 호출) | `fcmNotificationService.sendPushData()` | VBS invoke 알림 |
| `IttInvokeAlarmService` (8+ 호출) | `fcmNotificationService.sendPushData()` | ITT invoke 알림 |
| `NoticeInvokeAlarmService:78/89` | `fcmNotificationService.sendPushData()` | 공지 멀티캐스트 |

> 신 allcone 의 FcmPushSender 도 협의서 §3 통해 동일 endpoint 호출로 전환 요청. 양측 컷오버 시점 자유.

### 운송사 TMS — 단계 4, 13
- `PushTruckerService.send()` + `TssGroupOrderPushService` 의 4 메서드가 `TmsHandlerClient.push()` 위임
- truckerId → vendor (hanjin/lottegl/chunil) 매핑은 TmsHandlerClient 내부

| 파일:라인 | 호출 | 외부 URL |
|---|---|---|
| `PushTruckerService.send` | `tmsHandlerClient.push(truckerId, ...)` | hanjin/lottegl/chunil hardcode (truckerId 기반) |
| `TssGroupOrderPushService.sendGroupOrderStatusChangedAlarm` | `tmsHandlerClient.push()` | DB 의 TruckerApiInfo.interfaceUrl |
| `TssGroupOrderPushService.sendGroupVerifyResultListAlarm` | `tmsHandlerClient.push()` | 동일 |
| `TssGroupOrderPushService.sendGroupOrderVerifyResultAlarm` | `tmsHandlerClient.push()` | 동일 |

### KTNet — 단계 3, 14
- `MovementAsyncService.sendMovementEventToKtnetAsync` 가 `KtnetHandlerClient.sendMovement()` 위임
- VendorService DB 조회는 core 유지 (vendorApiInfo.interfaceUrl + interfaceId)
- @Async 비동기 + fire-and-forget 동작 보존

| 파일:라인 | 호출 | 비고 |
|---|---|---|
| `MovementAsyncService.sendMovementEventToKtnetAsync` | `ktnetHandlerClient.sendMovement(url, interfaceId, payload)` | KTNet movement 이벤트 |

### AAS 인증 (외부 진입점 인증, TSS Open API 측) — 단계 9, 16
- `AASAdapter.verifyAccessToken / getCallbackUrl` 가 `AasHandlerClient.validateToken / getCallback` 위임
- 외부 진입점 URL 변경 없음 (core 8080 유지). AAS 외부 호출만 handler 위임.
- handler 가 raw JSON forward + status/body 분기 (4xx body 도 DTO 파싱 필요)

| 파일:라인 | 호출 | 외부 엔드포인트 |
|---|---|---|
| `AASAdapter.verifyAccessToken` | `aasHandlerClient.validateToken()` | `/tokens/validate` |
| `AASAdapter.getCallbackUrl` | `aasHandlerClient.getCallback()` | `/tokens/callback` |

### chainportal (신규) — 단계 7
- 회원 정보 조회 (truckNo → userId 리스트). chainportal API 미개발 상태에서 임시로 chainportal DB 직접 접속 (`JdbcChainportalUserClient`)
- chainportal 측 API 완성 시 `chainportal.client=http` property 스왑만으로 `HttpChainportalUserClient` 로 전환 가능 (인터페이스 분리)
- 호출 주체: 신 allcone (협의서 §1)

| 호출 | endpoint | 비고 |
|---|---|---|
| (신 allcone NotificationTargetResolver) | `POST /handler/chainportal/users/by-truck` | truckNo 리스트 → userId 리스트 매핑 |

### TSS Open API 운송사 callback — 단계 18
- `SendNotificationToTruckerAdapter` 의 4 메서드 (sendTerminalEvent / sendGroupOrderStatusChangeEvent / sendGroupOrderVerifyResultEvent / sendGroupOrderVerifyResultListEvent) 가 `TruckerHandlerClient.sendCallback()` 위임
- 단일 endpoint `/handler/trucker/callback` 으로 통합 (operation 필드로 4 종 구분)
- raw JSON forward + status/body 그대로 전달 (caller 가 도메인 Response DTO 로 역직렬화)
- 호출처: NotificationApplicationServiceImpl 의 production 2 메서드 + Test 6 메서드 + GroupOrderVerifyResultNotificationEventListener — 모두 시그니처 무변경

| 메서드 | handler operation 필드 | 외부 callback URL |
|---|---|---|
| `sendTerminalEvent` | `sendTerminalEvent` | AAS 의 getCallbackUrl 결과 |
| `sendGroupOrderStatusChangeEvent` | `sendGroupOrderStatusChangeEvent` | 동일 |
| `sendGroupOrderVerifyResultEvent` | `sendGroupOrderVerifyResultEvent` | 동일 |
| `sendGroupOrderVerifyResultListEvent` | `sendGroupOrderVerifyResultListEvent` | 동일 |

## 보류 / 별건 처리

### 신 allcone 역방향 호출 (이미 폐기됨, 메모리 참조)
- `BctransVbsTruckTransOrderService:567`: `${allcone.url}/vbs/invoke/alarm` → outbox 도입으로 폐기 (Phase 2-A)
- `BctransIttTruckTransOrderService:623`: 동일 (Phase 2-A)

### 공지 외부 API
- `NoticeService:71`: `restTemplate.exchange()` 공지 알림 외부 (NoticeInvokeAlarmController serverName 분기 누락 별건과 함께 정리)

## handler 어댑터 위치 (실제 구현 완료, 2026-05-08)

```
handler/src/main/java/kr/co/chainportal/handler/
├─ common/          공통 envelope (HandlerResponse/HandlerError/HandlerException) + RestTemplateConfig + WebClientConfig + GlobalExceptionHandler
├─ fcm/             FcmController + FcmService + RetryableFirebaseMessaging + FirebaseConfig + FcmSendRequest/FcmNotification + FCMException
├─ bchain/          BchainController (/exchange + /raw) + BchainExchangeService + ChannelType/BChainParam/VbsBChainParam (이식)
├─ terminal/        TerminalApiController + TerminalApiService + TerminalExchangeRequest
├─ tms/             TmsController + TmsPushService + TmsPushRequest
├─ ktnet/           KtnetController + KtnetMovementService + KtnetMovementRequest
├─ aas/             AasController + AasService + AasForwardResponse
├─ trucker/         TruckerController + TruckerCallbackService + 2 DTO (callback raw forward)
└─ chainportal/     ChainportalController + ChainportalUserClient + JdbcChainportalUserClient + ChainportalUserMapper + 3 DTO
```

## core handler sub-client 위치 (2026-05-08)

```
core/src/main/java/kr/co/chainportal/allconebctrans/common/handler/
├─ AbstractHandlerClient.java   공통 RestTemplate 호출 + envelope 풀기 + HandlerCallException 매핑
├─ BchainHandlerClient.java     exchange + rawExchange
├─ TerminalHandlerClient.java   exchange
├─ TmsHandlerClient.java        push (truckerId → vendor 매핑 내장)
├─ KtnetHandlerClient.java      sendMovement
├─ FcmHandlerClient.java        send
├─ AasHandlerClient.java        validateToken / getCallback
├─ TruckerHandlerClient.java    sendCallback (operation 4종)
├─ dto/HandlerResponse.java     core 측 envelope DTO
├─ dto/HandlerError.java
├─ dto/AasForwardResponse.java
├─ dto/TruckerCallbackResponse.java
└─ exception/HandlerCallException.java
```

## commit 이력 (외부 IO 페이즈, 2026-05-08)

| 단계 | commit | 메시지 |
|---|---|---|
| 1-2 | `709d1508` | feat(handler): pom 의존성 + IO 응답 envelope/예외/RestTemplate 공통 인프라 |
| 3 | `c5a34c8b` | feat(handler): KTNet movement 어댑터 |
| 4 | `2a14fac4` | feat(handler): TMS 어댑터 |
| 5 | `6b01273c` | feat(handler): BChain 어댑터 |
| 6 | `6f02cfdf` | feat(handler): Terminal 어댑터 |
| 7 | `30d102d6` | feat(handler): chainportal 어댑터 신규 |
| 8 | `34084544` | feat(handler): FCM 어댑터 |
| 9 | `8b58cce7` | feat(handler): AAS 인증 어댑터 |
| 10 | `5611318e` | feat(core): HandlerClient 공통 인프라 |
| 11 | `147341d8` | refactor(core): BChainService/VbsBChainService → handler 위임 |
| 12 | `4481ab8a` | refactor(core): TerminalRequestClient*Service → handler 위임 |
| 13 | `d8732954` | refactor(core): TssGroupOrderPushService/PushTruckerService → handler 위임 |
| 14 | `d6320ee7` | refactor(core): MovementAsyncService → handler 위임 |
| 15 | `f7729443` | refactor(core): FCMNotificationService → handler 위임 |
| 16 | `4ad51890` | refactor(core): AASAdapter → handler 위임 |
| 17 | `c33197b6` + `5e2a2be3` | refactor(core): BlockChainAdapter → handler 위임 (raw endpoint) |
| 18 | `44d3263a` + `691d8f1f` | refactor(core): SendNotificationToTruckerAdapter → handler 위임 (TSS callback) |
| 19 | `980f2507` | docs: 신 allcone 팀 협의서 |
| 20 | `104aa5cd` | docs: HANDLER_BYPASS_CATALOG 갱신 |

## 회원 보강 endpoint (chainportal handler 미러링, 2026-05-12)

방향이 외부 IO 페이즈와 정반대 (`core → handler` 가 아니라 `신 allcone → handler`).
신 allcone 측이 회원 Feign client 를 만들면 base url 만 handler 로 변경해 바이패스 전환 가능. 본 페이즈 시점엔 미러링만 완료 (allcone Feign client 미구현).

옵션 C 단순화 (사용자 결정 2026-05-12): alarm_config 의 common.terminal 의존성은 이식 안 함. 신 allcone 이 사용자별 알람/터미널 매핑을 자체 관리하고 FCM 발송 시 완성된 데이터를 전달하는 구조라 handler 가 터미널 목록을 알 필요 없음. 자동 초기화 메서드 미이식, getByUserId 가 DB 조회 결과 그대로 반환.

### auth — DeviceAuth + NiceAuth (5 endpoint)

| method | URL | 비고 |
|---|---|---|
| POST | `/mobile/auth/req` | 디바이스 SMS 인증 요청 |
| POST | `/mobile/auth/res` | 디바이스 SMS 인증 응답 |
| GET | `/mobile/auth/nice/auth-url` | NICE 본인인증 url 발급 |
| GET | `/mobile/auth/nice/result` | NICE 본인인증 결과 콜백 |
| GET | `/mobile/auth/nice/close` | NICE 본인인증 close |

handler 경로: `handler/.../chainportal/auth/` + `mappers/chainportal/auth/`

### sign — SignIn/SignUp + DeviceToken (6 endpoint)

| method | URL | 비고 |
|---|---|---|
| POST | `/mobile/signIn/v2` | 로그인 |
| POST | `/mobile/checkusable/v2` | 사용 가능 ID 확인 |
| POST | `/mobile/unused` | 탈퇴 처리 |
| POST | `/mobile/signOut/v2` | 로그아웃 |
| POST | `/mobile/signup` | 회원가입 |
| POST | `/mobile/signup/exists` | 아이디 중복 확인 |

handler 경로: `handler/.../chainportal/sign/` + `mappers/chainportal/sign/`

차이점: SignIn 의 FCM device token 등록 후 push 발송은 allcone 측 책임으로 분리.

### user — UserInfo + UserTruck (18 endpoint)

UserInfoController 7:
| method | URL | 비고 |
|---|---|---|
| POST | `/mobile/user/matchpwd` | 비밀번호 일치 확인 |
| POST | `/mobile/user/modpwd` | 비밀번호 변경 |
| POST | `/mobile/user/findId` | NICE 기반 아이디 찾기 |
| POST | `/mobile/user/resetPassword` | NICE 기반 비밀번호 재설정 |
| POST | `/mobile/user/check/recommender` | 추천인 검증 |
| POST | `/mobile/user/niceAuthUpdate` | 기존 회원 NICE 본인인증 결과 반영 |
| POST | `/mobile/user/updateTermsAgree` | 약관 동의 수정 |

UserTruckController 11:
| method | URL | 비고 |
|---|---|---|
| GET | `/mobile/user/truck` | 내 차량 목록 |
| GET | `/mobile/user/truck/duplicate` | 차량 중복 확인 |
| POST | `/mobile/user/truck` (multipart) | 차량 등록 (등록증 선택 업로드) |
| POST | `/mobile/user/truck/certificate` (multipart) | 차량등록증 업로드 |
| GET | `/mobile/user/truck/certificate` | 차량등록증 이미지 다운로드 |
| GET | `/mobile/user/truck/rep/v2` | 대표차량 등록 가능 여부 확인 |
| POST | `/mobile/user/truck/rep/v2` | 대표차량 등록 |
| POST | `/mobile/user/truck/delete` | 차량 삭제 |
| GET | `/mobile/user/truck/rep/canceluser` | 대표차량 해제 사용자 조회 |
| GET | `/mobile/user/truck/rep/check` | 차량 활동 흔적 기록 |
| POST | `/mobile/user/truck/updateTruckCode` | 트럭 코드 갱신 |

handler 경로: `handler/.../chainportal/user/` + `mappers/chainportal/user/`

차이점: UserTruckService.updateRepTruckV2 의 FCM push (대표차량 해제 알림) 는 allcone 책임으로 분리. handler 는 DB 갱신만 수행.

### alarm_config (2 endpoint)

| method | URL | 비고 |
|---|---|---|
| GET | `/mobile/alarmConfig/getByUserId` | 사용자 알람 설정 조회 (옵션 C - 자동 초기화 X) |
| POST | `/mobile/alarmConfig/setAlarmConfig` | 사용자 알람 설정 갱신 |

handler 경로: `handler/.../chainportal/alarm_config/` + `mappers/chainportal/alarm_config/`

### by-truck (server-to-server batch, 1 endpoint)

| method | URL | 비고 |
|---|---|---|
| POST | `/mobile/user/truck/by-truck` | truckNo 다건 -> userId 매핑. 신 allcone NotificationTargetResolver 가 FCM 발송 전 호출. deviceToken 헤더 없음. |

handler 경로: `handler/.../chainportal/user/web/UserTruckController.findUserIdsByTruckNos` (외부 IO 페이즈의 `/handler/chainportal/users/by-truck` 을 회원 영역 통합 이동, commit `2316d23f`).

### 회원 보강 페이즈 commit 이력 (2026-05-12)

| # | commit | 메시지 |
|---|---|---|
| 1 | `d383225f` | feat(handler): 회원 보강 infra - NICE config + apiRestTemplate Bean |
| 2 | `bc85322c` | feat(handler): 회원 보강 공통 인프라 - egov+Oracle datasource+crypt(Text/CI)+SMS+ApiResponse |
| 3 | `f121ea71` | feat(handler): 회원 보강 - auth (DeviceAuth + NiceAuth) 5 endpoint 미러링 |
| 4 | `664482ad` | feat(handler): 회원 보강 - sign (SignIn/SignUp + DeviceToken) 6 endpoint 미러링 |
| 5 | `411145ad` | feat(handler): 회원 보강 - user (UserInfo + UserTruck) 18 endpoint 미러링 |
| 6 | `7d229ec5` | feat(handler): 회원 보강 - alarm_config 2 endpoint 미러링 |
| 7 | `282ca8a7` | docs: 회원 보강 페이즈 종료 박제 |
| 8 | `2316d23f` | refactor(handler): chainportal users/by-truck 을 UserTruckController 로 통합 (envelope ApiResponse 통일) |
| 9 | (본 commit) | docs: 회원 보강 협의서 + by-truck 통합 반영 |

## 다음 페이즈 작업

1. **내부 분리 페이즈** — invoke 4 + sign/user/alarm_config/ver 4 패키지 통째 폐기 (옵션 A), 단방향 위반 4→0, 6 commit. 메모리 참조 (`project_internal_separation_plan.md`).
2. **빌드 검증 + 테스트베드 배포 + 호출 1회** — 외부 IO + 회원 보강 + 내부 분리 모두 끝난 후 마지막 일괄 검증.

## handler 측 dead code (점진 정리 대상)

- `core/.../common/config/FCMConfig.java` — Firebase Bean. handler 로 이관 후 core 에서 사용 안 함.
- `core/.../common/push/service/RetryableFirebaseMessaging.java` — 동일.
- `core/.../common/support/bchain/BChainParam.java`, `VbsBChainParam.java`, `ChannelType.java` — handler 측 동일 클래스 보유. core 에서 사용 안 함.
- `core/.../common/util/WebClientService.java` — Terminal loop-back 등 일부에서 여전히 사용. 내부 분리 페이즈에서 정리 검토.

위 dead code 제거는 이번 외부 IO 페이즈 범위 외. 내부 분리 페이즈 또는 별도 cleanup commit 에서 처리.

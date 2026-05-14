# 회원 보강 — 신 allcone 팀 협의 항목 (2026-05-12)

> **bctrans 측 작업 범위**: handler 모듈에 chainportal 회원 32 endpoint 미러링 신설 (auth 5 + sign 6 + user 18 + alarm_config 2 + by-truck 1).
> **allcone 측 작업 범위**: 본 협의서의 §1, §2, §3, §4 항목. handler 가 chainportal API 의 임시 대역. 양측 동시 배포 시 정상 동작 보장을 위해 협의 필요.

bctrans 브랜치: `feature/msa/bctrans/phase-1`
allcone 참조 브랜치: `origin/feature/gayeon/BCTRA-25-backend` (`95995b2` 기준)

---

## 배경 (반드시 읽어주세요)

- chainportal API 미완 상태에서 신 allcone 의 회원 호출이 차단되지 않도록 **bctrans handler 가 chainportal API 의 임시 대역** 역할.
- handler 가 chainportal DB 직접 접속해 chainportal API 의 응답 spec 을 그대로 행세 (= 기존 allcone API spec 그대로 미러링).
- 추후 chainportal API 완성 시 **handler 내부 구현만 chainportal API 호출 forwarding 으로 교체**. endpoint URL / DTO / 응답 envelope 는 영구 유지 (외부 IO 페이즈의 BChain/Terminal/TMS/KTNet/FCM 어댑터와 동일 패턴).
- 신 allcone 측 chainportal Feign client 는 본 협의서의 endpoint URL/DTO spec 에 맞춰 신설 또는 follow up 필요.

---

## §1. URL / 응답 envelope 공통 spec

### Base URL
- 호출 대상: `${bctrans-handler-url}/...`
- handler 가 chainportal API 의 임시 대역이므로 신 allcone 측 Feign client `${allcone.chainportal.base-url}` 의 base url 을 일시적으로 bctrans-handler-url 로 설정 가능. chainportal API 완성 시 다시 chainportal 측으로 변경.

### 응답 envelope (전체 endpoint 공통)
```json
{
  "result": "success" | "failure",
  "resultMessage": "<메시지>",
  "data": <endpoint 별 상이>
}
```
- 신 allcone 측 `ChainportalApiResponse<T>` 구조와 wire-compatible (`result/resultMessage/data` 동일).

### 요청 헤더
- 일부 endpoint 에서 `deviceToken` 헤더 필수 (회원 영역). server-to-server batch 호출 (by-truck) 은 헤더 없음.
- 신 allcone Feign client 에서 deviceToken 을 모바일 요청에서 추출해 passthrough 하도록 `RequestInterceptor` 추가 필요.

---

## §2. Endpoint 명세표 (32 endpoint)

> **세부 DTO 구조는 bctrans 측 코드를 source of truth 로 사용**. 모든 endpoint 의 요청/응답 DTO 는 `feature/memberTableChange` 의 기존 allcone API spec 과 100% 일치. 신 allcone client 에서 DTO 작성 시 본 spec 기반.

### auth (DeviceAuth + NiceAuth, 5 endpoint)

| method | URL | 헤더 | 요청 body | 응답 data | 비고 |
|---|---|---|---|---|---|
| POST | `/mobile/auth/req` | — | `DeviceAuth {userHp, userName}` | null | dev/local 환경 SMS 스킵 |
| POST | `/mobile/auth/res` | — | `DeviceAuth {authType, userHp, authNo, userId, userName}` | **authType 분기** ↓ | |
| GET | `/mobile/auth/nice/auth-url` | — | query param: `purpose`, `callbackUrl` 등 | `{authUrl: "..."}` | NICE 본인인증 url 발급 |
| GET | `/mobile/auth/nice/result` | — | query param: NICE return params | NICE 본인인증 결과 콜백 | |
| GET | `/mobile/auth/nice/close` | — | — | — | NICE 팝업 닫기 처리 |

**auth/res 응답 분기**:
- `SIGN_UP` 성공: `{userName, userHp, driverName, driverHp}` (userId 없음)
- `SIGN_UP` 중복: `failure`, "이미 등록된 전화번호입니다."
- `CHANGE_HP` 성공: `null` (data 없이 ok)
- `CHANGE_HP` 미가입: `failure`, "등록된 사용자를 찾을 수 없습니다."
- 그 외 (`FIND_ID`/`SEARCH_ID` 등): `{userId, userName, userHp, driverId, driverName, driverHp, joinDate, isDriver}`

### sign (SignIn/SignUp + DeviceToken, 6 endpoint)

| method | URL | 헤더 | 요청 body | 응답 data |
|---|---|---|---|---|
| POST | `/mobile/signIn/v2` | deviceToken | `{userId, password}` (driverId fallback 지원) | `UserSignInInfo` (아래 §3) |
| POST | `/mobile/checkusable/v2` | deviceToken | `{userId}` | `{usable: boolean}` |
| POST | `/mobile/unused` | deviceToken | `{userId, password}` | null |
| POST | `/mobile/signOut/v2` | deviceToken | `{userId}` | null |
| POST | `/mobile/signup` | deviceToken | `UserInfo` (신규 가입 정보) | null |
| POST | `/mobile/signup/exists` | deviceToken | `UserInfo {userId}` | null (failure 시 "이미 등록된 아이디") |

### user (UserInfo + UserTruck, 18 endpoint)

UserInfoController 7:
| method | URL | 헤더 | 요청 body | 응답 data |
|---|---|---|---|---|
| POST | `/mobile/user/matchpwd` | deviceToken | `{userId, password}` | null |
| POST | `/mobile/user/modpwd` | deviceToken | `{userId, password}` | null |
| POST | `/mobile/user/findId` | — | `{certId}` | `{userId, userName, joinDate}` |
| POST | `/mobile/user/resetPassword` | — | `{certId, userId, password}` | null |
| POST | `/mobile/user/check/recommender` | — | `{recommendTruckNo, recommendName}` | `{userId}` |
| POST | `/mobile/user/niceAuthUpdate` | deviceToken | `{certId, userId}` | null |
| POST | `/mobile/user/updateTermsAgree` | deviceToken | `UserTermsEntity` | null |

UserTruckController 11 + by-truck 1 = 12:
| method | URL | 헤더 | 요청 | 응답 data |
|---|---|---|---|---|
| GET | `/mobile/user/truck` | deviceToken | query: `userId` (or `driverId`) | `List<UserTruck>` |
| GET | `/mobile/user/truck/duplicate` | deviceToken | query: `userId, truckNo, imageSelected` | null |
| POST | `/mobile/user/truck` | deviceToken | multipart: userId, truckNo, file, truckCode | `<fileLoc>` |
| POST | `/mobile/user/truck/certificate` | deviceToken | multipart: userId, truckNo, file | `<fileLoc>` |
| GET | `/mobile/user/truck/certificate` | — | query: `userId, truckNo` | (image binary) |
| GET | `/mobile/user/truck/rep/v2` | deviceToken | query: `truckNo` | null |
| POST | `/mobile/user/truck/rep/v2` | deviceToken | `UserTruck` | null |
| POST | `/mobile/user/truck/delete` | deviceToken | query: `userId, truckNo` | null |
| GET | `/mobile/user/truck/rep/canceluser` | deviceToken | query: `userId` | null |
| GET | `/mobile/user/truck/rep/check` | deviceToken | query: `userId` | null |
| POST | `/mobile/user/truck/updateTruckCode` | — | `UpdateUserTruckCodeDTO` | null |
| **POST** | **`/mobile/user/truck/by-truck`** | **—** | **`{truckNos: ["..."]}`** | **`List<TruckUserMapping {truckNo, userIds: [...]}>`** |

### alarm_config (2 endpoint)

| method | URL | 헤더 | 요청 | 응답 data |
|---|---|---|---|---|
| GET | `/mobile/alarmConfig/getByUserId` | deviceToken | query: `userId` | `List<AlarmConfigJson>` (옵션 C - 자동 초기화 X, DB 조회 결과 그대로) |
| POST | `/mobile/alarmConfig/setAlarmConfig` | deviceToken | `AlarmConfig` | "성공"/"실패" string |

**옵션 C 단순화 (2026-05-12 결정)**: bctrans handler 는 `common.terminal` 의존 미이식. 신 allcone 이 사용자별 알람/터미널 매핑을 자체 관리하고 FCM 발송 시 완성된 데이터+토큰만 handler 에 전달하는 구조라서 handler 가 터미널 목록을 알 필요 없음. getByUserId 응답이 빈 리스트일 수 있음 (사용자가 setAlarmConfig 로 명시 등록 전까지).

---

## §3. 신 allcone 측 이미 만들어진 client (auth 3) follow up 항목

`core/src/main/java/com/smartm2m/allcone/core/client/chainportal/auth/ChainportalMobileAuthClient.java` (origin `95995b2`) 의 3 endpoint 는 이미 작성. 다만 아래 항목 보강 필요:

### 3-1. URL 변경 (필수)
- 현재 신 allcone client URL: `/api/v1/allcone/signIn/v2`, `/api/v1/allcone/auth/req`, `/api/v1/allcone/auth/res`
- bctrans handler URL: `/mobile/signIn/v2`, `/mobile/auth/req`, `/mobile/auth/res`
- 신 allcone client `@PostMapping` path 를 위 bctrans handler URL 로 변경 필요.

### 3-2. `deviceToken` 헤더 (signIn 필수)
- 현재 `ChainportalMobileAuthClient.signIn` interface 에 헤더 명시 없음.
- 모바일 요청에서 받은 deviceToken 을 passthrough 하도록 `RequestInterceptor` 추가 또는 `@RequestHeader("deviceToken")` 명시.

### 3-3. `ChainportalSignInResponse` DTO 누락 필드 추가
현재 신 allcone DTO 12 필드 → bctrans handler `UserSignInInfo` 14 필드. 누락 2개:
- `String userBirthDateEncoding`
- `boolean niceAuthenticated`

또한 handler 응답이 `driverId/driverName/driverHp` (getter) 도 직렬화 포함. 모바일 코드에서 사용하는 필드면 DTO 추가, 사용 안 하면 무시.

### 3-4. `ChainportalAuthenticateResponse` DTO 확장
현재 4 필드 (userId, userName, userHp, joinDate) → handler 응답이 authType 별 분기 (위 §2). DTO 를 모든 분기를 표현할 수 있도록 확장:
- 추가 필드: `driverId, driverName, driverHp, isDriver` (nullable)
- `SIGN_UP` 분기: userId 없이 userName/userHp/driverName/driverHp 만
- `CHANGE_HP` 분기: data 없음 (`null`)

---

## §4. 기술적 합의 사항

### 4-1. Jackson ObjectMapper 설정
- 신 allcone 측 ObjectMapper 가 `FAIL_ON_UNKNOWN_PROPERTIES=false` 설정 (Spring 기본값) 확인 필요.
- handler 응답이 신 allcone DTO 보다 더 많은 필드를 보낼 수 있음 (회원 보강 페이즈가 기존 allcone API spec 그대로 미러링). 신 allcone 측 DTO 가 모든 필드를 받지 않더라도 무시되어야 함.

### 4-2. `LocalDateTime` 직렬화 형식
- bctrans handler 의 `UserSignInInfo.userBirthDate` 는 `LocalDateTime` 타입.
- Spring Boot 기본 직렬화 (ISO 8601): `"2026-03-26T12:15:00"`.
- 신 allcone 측 DTO 가 같은 직렬화 형식으로 deserialize 가능한지 확인.

### 4-3. Multipart 파일 업로드
- `/mobile/user/truck` 과 `/mobile/user/truck/certificate` 는 `multipart/form-data` 요청 (차량등록증 이미지 업로드).
- 신 allcone Feign client 가 multipart 전달을 지원하도록 `feign-form` 라이브러리 또는 별도 client 구현 필요.

### 4-4. Image binary 응답 (`GET /mobile/user/truck/certificate`)
- 응답이 envelope 없이 image binary 직접 반환 (Content-Type: image/*).
- 신 allcone client 가 byte[] 또는 InputStream 으로 받도록 구현 필요.

---

## §5. 폐기 / 변경된 endpoint

### 5-1. `/handler/chainportal/users/by-truck` → `/mobile/user/truck/by-truck` 이동
- 외부 IO 페이즈 commit `30d102d6` 의 `POST /handler/chainportal/users/by-truck` 폐기.
- 회원 영역으로 통합 이동: `POST /mobile/user/truck/by-truck` (envelope `ApiResponse`, deviceToken 헤더 없음).
- 신 allcone 측에 아직 호출 client 없음. 본 spec 으로 신설.
- 외부 IO 페이즈 협의서 (`IO-HANDLER-COORDINATION-2026-05-08.md`) §1 의 chainportal handler 호출 명세는 본 §5-1 로 대체.

---

## §6. 다음 단계 (양측 작업)

### bctrans 측
- ✅ 회원 보강 페이즈 7 commit 완료 (`d383225f` ~ `282ca8a7`)
- ✅ by-truck 통합 commit 완료 (`2316d23f`)
- (대기) handler 빌드 검증 + 테스트베드 배포 (내부 분리 페이즈 종료 후 일괄)

### allcone 측 (요청)
- §3 follow up (이미 만들어진 auth 3 client 보강)
- §2 의 미구현 28 endpoint 의 신규 chainportal Feign client 신설 (sign 6 + user 18 + alarm_config 2 + by-truck 1 + auth/nice 3)
- §4 의 기술적 합의 사항 확인
- §5-1 의 by-truck URL 변경 반영 (NotificationTargetResolver 가 호출 시점)

---

## §7. 5/13 추가 검증 — 마스터 데이터 + DTO 정합 follow up

> 2026-05-13 정합성 재검증 결과 (`.review-context/msa-phase-1-validation-2026-05-13/`) 박제. 본 절은 마스터 데이터(§7-1, §7-2) + DTO 포맷(§7-3, §7-4) + 추가 미구현(§7-5) follow up.

### 7-1. `GET /api/v1/allcone/general/terminal-area` 신규 endpoint

**bctrans 측 완료**:
- Controller / Service / Repository / Mapper / VO 신설 (`AllconeGeneralController.getGeneralTerminalArea`).
- SQL: `bctransdbx.terminal_area WHERE DATA_STATUS = 'DATA_ACTIVATED'`.
- 응답 envelope: `ApiResponse<List<TerminalAreaVo>>`.

**응답 schema** (allcone docs §10 갱신 완료):
| 필드 | 타입 |
|---|---|
| terminalCode | String |
| areaType | String |
| lat | Double |
| lon | Double |

**신 allcone 측**: `BctransReferenceDataClient.getGeneralTerminalArea()` + `BctransGeneralTerminalAreaResponse` 이미 존재 (`95995b2` HEAD). 즉시 호출 가능. 별도 작업 없음.

---

### 7-2. `GET /api/v1/allcone/general/terminal` 응답 17 필드 확장

**문제**: 신 allcone commit `14980e4` (5/8) 에서 `BctransGeneralTerminalResponse` 11 필드 추가 (6 → 17). bctrans 응답은 6 필드만 반환 → 신 allcone `GeneralTerminalCache.toGeneralTerminal()` 가 11 필드를 null 로 deserialize. 도메인 코드 `require()` 검증 fail → IllegalStateException.

**bctrans 측 완료**:
- `GeneralTerminalMapper.xml` 의 `getTerminalNameList` SELECT 확장. `bctrans_terminal_config` LEFT JOIN 추가.
- `TerminalNameVo` 17 필드 확장 (`@NoArgsConstructor + @Setter`).
- 모든 컬럼은 bctrans 측 다른 mapper (`TerminalInfoMapper.xml`, `TerminalAppConfigMapper.xml`) 에서 이미 동일 패턴으로 사용 중 → DDL 추가 없이 안전.

**응답 schema** (allcone docs §10 갱신 완료, 17 필드):
| 필드 | 타입 | 출처 |
|---|---|---|
| terminalCode | String | gt.TERMINAL_CODE |
| terminalKoreanNameAbbr | String | gt.TERMINAL_KOREAN_NAME_ABBR |
| terminalKoreanNameFull | String | gt.TERMINAL_KOREAN_NAME_FULL |
| terminalEnglishNameAbbr | String | gt.TERMINAL_ENGLISH_NAME_ABBR |
| terminalEnglishNameFull | String | gt.TERMINAL_ENGLISH_NAME_FULL |
| terminalKoreanAndEnglishNameAbbr | String | gt.TML_KOR_ENG_ABBR |
| terminalCyCode | String | gt.tml_cy_cd |
| useIttYn | String('Y'/'N') | btc.TSS_SINGLE_ACTIVATION 기반 |
| useVbsYn | String('Y'/'N') | btc.VBS_ACTIVATION 기반 |
| useGroupOrderYn | String('Y'/'N') | btc.TSS_GROUP_ACTIVATION 기반 |
| useVbsAppYn | String('Y'/'N') | btc.VBS_ACTIVATION 기반 |
| useTssAppYn | String('Y'/'N') | btc.TSS_SINGLE OR btc.TSS_GROUP 기반 |
| portCode | String | gt.TERMINAL_PORT_CODE |
| linkedStatus | String | gt.LINKED_STATUS |
| terminalContactUrl | String | gt.TERMINAL_CONTACT_URL |
| latitude | Double | gt.LATITUDE |
| longitude | Double | gt.LONGITUDE |

**신 allcone 측**: 별도 작업 없음. 테스트베드에서 17 필드 모두 채워지는지 1회 호출 검증만.

---

### 7-3. `inOutType` enum 허용 값 명세 (H1 해소)

**대상 endpoint** (3개):
- `POST /api/v1/allcone/container/handle/change-direction` (`BctransContainerHandleChangeDirectionRequest.inOutType`)
- `POST /api/v1/allcone/container/handle/swap` (`BctransContainerHandleSwapRequest.inOutType`)
- `POST /api/v1/allcone/terminal/req/change-con-door-direction` (`BctransChangeConDoorDirectionRequest.inOutType`)

**bctrans 측 동작**: `inOutType` String 을 bctrans `InOutTypeDeserializer` (custom Jackson deserializer) 가 enum 으로 변환. 허용되지 않은 값 송신 시 deserialization fail → 400.

**allcone 측 요청**:
- 위 3 endpoint 에서 실제 송신하는 `inOutType` String 값 목록 회신 (e.g. `"IN"`, `"OUT"`, `"IN_TERMINAL"`, `"OUT_TERMINAL"` 등).
- 또는 신 allcone 의 enum 정의 공유.
- bctrans 측 deserializer 의 허용 값과 일치하는지 확인 + 불일치 시 deserializer 측 보강 또는 신 allcone 측 송신 값 변경 결정.

---

### 7-4. 시간 필드 포맷 명세 (C2 + H2 통보)

**bctrans 측 포맷 (그대로 유지, 변경 없음)**:

| endpoint | 필드 | bctrans parser 포맷 |
|---|---|---|
| `POST /vbs/appointment/confirm` | `reservationTime` | `yyyy-MM-dd HH:mm:ss` (DateTimeFormatter) |
| `POST /vbs/appointment/update-single` | `reservationTime` | `yyyy-MM-dd HH:mm:ss` |
| `POST /container/handle/change-direction` | `reqDT` | Jackson default ISO-8601 (e.g. `2026-05-13T10:30:00`) |
| `POST /container/handle/swap` | `reqDT` | Jackson default ISO-8601 |
| `POST /terminal/req/change-con-door-direction` | `reqDT` | java.util.Date / Jackson ISO-8601 |
| `POST /terminal/req/auto-unload/ready-done` | `requestTime` | Jackson default ISO-8601 |

**allcone 측 요청**:
- 위 endpoint 별 신 allcone 송신 String 포맷 확인.
- bctrans 측 포맷과 일치하는지 confirm.
- 불일치 시 신 allcone 측 String 직렬화 포맷 조정 (bctrans 측 포맷 변경 없음).

---

### 7-5. `ChainportalPopupClient` (`GET /api/v1/allcone/popup/list`) follow up

**현재 상태**:
- 신 allcone client 존재 (commit `1ce3b9d`, 5/12). DTO: `ChainportalPopupResponse`.
- bctrans handler 측 미러링 안 됨 (회원 보강 페이즈 32 endpoint 범위 밖).
- chainportal 진짜 API 도착 대기.

**결정 필요 항목** (allcone 측 회신):
- 모바일 호출 빈도 (예: 앱 진입 시 1회 / 매분 polling 등).
- 영향도 (popup 표시 안 되어도 핵심 흐름 무관 / 필수 흐름).
- 임시 대역 필요 여부:
  - 필요: bctrans handler 측 `/handler/chainportal/popup/list` 또는 `/mobile/popup/list` 신규 endpoint 미러링 협의.
  - 불필요: chainportal 진짜 API 도착까지 client 호출 실패 그대로 (앱 측 fallback 확인).

---

### 7-6. 다음 단계

**bctrans 측 (완료)**:
- terminal-area endpoint 신설 ✅
- general/terminal 17 필드 SQL 확장 ✅
- allcone docs §10 갱신 ✅

**allcone 측 (요청, 추가)**:
- §7-3 inOutType 송신 값 목록 회신
- §7-4 시간 필드 포맷 confirm (불일치 시 송신 측 조정)
- §7-5 popup-list 호출 빈도 + 영향도 회신

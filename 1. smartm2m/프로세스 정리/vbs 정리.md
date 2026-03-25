# VBS 프로세스 흐름도 - PPT 구성안

> **용도**: 이 문서는 PPT 생성용 AI에게 전달할 원본 자료입니다.
> **범위**: bctrans 분기 기준, 프로세스 흐름도 위주
> **참고**: 기존 PPT `올컨e 기능별 분석(VBS Part)_v0.2.pptx`의 2번째 슬라이드처럼 분기 포함 플로우차트 형태로 구성

---

## PPT 구성 (총 15장)

| 슬라이드 | 제목 | 유형 |
|----------|------|------|
| 1 | 표지 | 표지 |
| 2 | 목차 | 목차 |
| 3 | 전체 프로세스 흐름도 | 전체 흐름도 |
| 4 | saveTruckTransOrder (1/2) - 코피노 수신 및 검증 | 이벤트 흐름도 |
| 5 | saveTruckTransOrder (2/2) - 기존 데이터 업데이트 분기 | 이벤트 흐름도 |
| 6 | updateTruckTransStatusInTerminal - 터미널 이벤트 처리 | 이벤트 흐름도 |
| 7 | updateTruckTransStatusOnRoad - 운송 상태 추적 | 이벤트 흐름도 |
| 8 | requestDigitalGatein - 디지털 게이트인 | 이벤트 흐름도 |
| 9 | requestBlockIn / cancelStart - 블록인 및 취소 | 이벤트 흐름도 |
| 10 | removeDuplicateOrder - VBS/TSS 중복 제거 | 이벤트 흐름도 |
| 11 | InternalGateService - 내부게이트 데이터 생성 | 이벤트 흐름도 |
| 12 | UserRequestIssueEslipService - E-Slip 발급 판정 | 이벤트 흐름도 |
| 13 | VbsInvokeAlarmService (1/2) - 알림 라우팅 및 코피노 알림 | 이벤트 흐름도 |
| 14 | VbsInvokeAlarmService (2/2) - 터미널 이벤트 및 예약 알림 | 이벤트 흐름도 |
| 15 | 상태 전이 다이어그램 요약 | 요약 |

---

## 슬라이드 1: 표지

- **제목**: VBS 프로세스 흐름 분석 (Bctrans)
- **부제**: Vehicle Booking System - 부산항 컨테이너 운송 예약 시스템
- **대상**: api-bctrans / bctrans 인스턴스 기준
- **날짜**: 2026-03-25

---

## 슬라이드 2: 목차

> 슬라이드 번호와 제목을 목록으로 나열

---

## 슬라이드 3: 전체 프로세스 흐름도

> **형태**: 참고 PPT 2번째 슬라이드처럼 다이아몬드(분기) + 사각형(처리) + 화살표(흐름)의 플로우차트
> **범위**: VBS 전체 라이프사이클을 하나의 흐름도로 표현

```
[시작] 블록체인에서 코피노 수신
  │
  ▼
┌─────────────────────────┐
│ saveTruckTransOrder()    │ ← 코피노 검증 및 운송 오더 생성/업데이트
└────────────┬────────────┘
             │
             ▼
      ◇ 유효한 코피노?
     / \
  false  true
   │      │
   ▼      ▼
 [종료]  ◇ 기존 운송 오더 존재?
        / \
     true  false
      │      │
      ▼      ▼
 [업데이트  [새 운송 오더 생성]
  분기]        │
      │        │
      ▼        ▼
  ◇ 기존 트럭번호와 동일?    [알림 발송 (FCM)]
    / \                         │
 true  false                    ▼
  │      │                   [종료]
  ▼      ▼
◇ 기존 pinNo와 동일?   [기존 예약 취소]
  / \                      │
true  false                ▼
 │      │              [알림: "운송작업 갱신으로 예약 취소"]
 ▼      ▼
[업데이트] [기존 예약 취소]
 │
 ▼
[알림 발송 (FCM)] ──→ [예약 확정 대기]
                          │
                          ▼
                 ┌─────────────────────┐
                 │ 기사 앱에서 예약 확정  │
                 └────────────┬────────┘
                              │
                              ▼
                 ┌─────────────────────┐
                 │ confirmAppointment() │ ← Blockchain 기록
                 └────────────┬────────┘
                              │
                              ▼
                    [운송 시작 (TRANSPORT_START)]
                              │
                              ▼
                 ┌─────────────────────────────┐
                 │ updateTruckTransStatusOnRoad()│
                 └────────────┬────────────────┘
                              │
                              ▼
              IN_AREA_B → IN_AREA_C → IN_ZONE
                                        │
                                        ▼
                              ◇ CheckAppointmentCompliance
                               / \
                         Y(준수)  N(미준수)
                           │        │
                           ▼        ▼
                     APPT_CONPL  APPT_NOT_CONPL
                           │        │
                           ▼        ▼
                 ┌─────────────────────┐
                 │ requestDigitalGatein()│ ← GPS 좌표 + 터미널 API
                 └────────────┬────────┘
                              │
                              ▼
                 ┌─────────────────────┐
                 │ requestBlockIn()     │ ← 터미널 블록인
                 └────────────┬────────┘
                              │
                              ▼
                 ┌──────────────────────────────────┐
                 │ updateTruckTransStatusInTerminal() │ ← 터미널 이벤트 (GateIn)
                 └────────────┬─────────────────────┘
                              │
                              ▼
                      [E-Slip 발급/조회]
                              │
                              ▼
                      [운송 완료 (GATE_OUT)]
```

**범례**:
- 사각형: 처리 단계
- 다이아몬드(◇): 분기 조건
- 분기가 없는 선: 함수 종료를 의미

---

## 슬라이드 4: saveTruckTransOrder (1/2) - 코피노 수신 및 검증

> **소스**: `BctransVbsTruckTransOrderService.saveTruckTransOrder()`
> **형태**: 플로우차트 (분기 포함)

```
[시작] param 수신 (pinNo, docKey, inOut, copinoErrType, info)
  │
  ▼
◇ copinoErrType → ContainerTransportErrorStatus 변환 가능?
  │ false → [로그 에러] (종료하지 않고 계속 진행)
  │ true
  ▼
┌──────────────────────────────────────────────────────────┐
│ DB 조회: getAllconeTransportOrderDataForSaveCopino()       │
│  - terminalCode, documentKey, inOutType으로 기존 데이터 조회 │
│ → existedCopinoData (null이면 신규)                        │
└──────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────┐
│ Blockchain 호출: blockChainRequestGetCopino(param)        │
│  - 최대 3회 재시도 (2초 간격)                               │
│ → result (코피노 데이터 + 예약 데이터)                       │
└──────────────────────────────────────────────────────────┘
  │
  ▼
◇ result == null OR result.message가 Map이 아닌 경우?
  │ true → [로그: "blockChain GetCopino result data null"] → return false (FCM 미발송)
  │ false
  ▼
┌──────────────────────────────────────────────────────────┐
│ result에서 데이터 추출:                                    │
│  - copino = message.copino                               │
│  - appointment = message.appointment                     │
│  - info = appointment.info                               │
│  - newCopinoDocStatus = CopinoDocStatus 변환              │
│  - truckNo = copino.truckNo                              │
└──────────────────────────────────────────────────────────┘
  │
  ▼
◇ isNeedSaveCopino(existedCopinoData, copino)?
  │ false → return false (FCM 미발송)
  │ true
  ▼
◇ existedCopinoData != null? (기존 데이터 존재 여부)
  / \
true  false → [슬라이드 5의 BRANCH 4: 신규 생성]으로 이동
  │
  ▼
[슬라이드 5: 기존 데이터 업데이트 분기로 이동]
```

**주요 포인트**:
- Blockchain GetCopino는 최대 3회 재시도 (2초 간격)
- 실패 시 null 반환 → FCM 미발송으로 종료
- isNeedSaveCopino는 현재 항상 true (향후 확장 포인트)

---

## 슬라이드 5: saveTruckTransOrder (2/2) - 기존 데이터 업데이트 분기

> **소스**: `BctransVbsTruckTransOrderService.saveTruckTransOrder()` 후반부
> **형태**: 플로우차트 (분기 포함) - 슬라이드 4에서 이어짐

```
[슬라이드 4에서 이어짐]
  │
  ▼
◇ existedCopinoData != null? (기존 데이터 존재?)
  / \
true  false
  │      │
  │      ▼
  │   ◇ newCopinoDocStatus != COPINO_DELETED?
  │     / \
  │   true  false → return false
  │     │
  │     ▼
  │   ┌──────────────────────────────────┐
  │   │ [BRANCH 4: 신규 생성]             │
  │   │ ① checkGeneralContainerByCopino() │
  │   │ ② checkGeneralTruckerByCopino()   │
  │   │ ③ createContainerTransportData()  │
  │   │ ④ 팝업 매칭 및 저장               │
  │   └──────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────────────────────┐
│ 기존 상태 3가지 체크:                                    │
│  - isExistedTransportDataGateOut = (transStatus == GATE_OUT)  │
│  - isExistedTransportCancelInOut = (transStatus == CANCEL_INOUT) │
│  - isExistedOrderGateIn = (gateInTime != null)                   │
│  + 코피노 에러 체크:                                              │
│  - isCopinoLogicError = (copinoErrType에서 "LE" 포함)             │
│  - isExistedOrderError = (copinoErrorStatus == ERROR)             │
└────────────────────────────────────────────────────────┘
  │
  ▼
◇ isExistedTransportDataGateOut OR isExistedTransportCancelInOut?
  │ true → [BRANCH 3A: GATE_OUT/CANCEL 상태 업데이트]
  │         ① 기존 ContainerTransport 조회
  │         ② updateContainerTransport() (기존 데이터 위에 업데이트)
  │         ③ isNeedFcmSend = 변경사항 비교 결과
  │         ④ 팝업 매칭 및 저장
  │
  │ false
  ▼
◇ isExistedOrderGateIn AND isCopinoLogicError AND NOT isExistedOrderError?
  │ true → return false (GateIn + 로직에러 + 정상상태 = FCM 미발송, 무시)
  │
  │ false
  ▼
◇ newCopinoDocStatus == DELETED AND canRemoveCopino == false?
  │ true → return false (6초 이내 삭제 시도 → 거부)
  │
  │ false
  ▼
┌─────────────────────────────────────────────┐
│ [BRANCH 3B: 일반 업데이트]                    │
│ ① checkGeneralContainerByCopino()            │
│ ② checkGeneralTruckerByCopino()              │
│                                              │
│ ◇ feType==EMPTY AND inOut==OUT               │
│   AND terminalCode=="DGTBC050"?              │
│   true → updateDgtEmptyOutContainerTransport │
│           isNeedFcmSend = false              │
│   false → updateContainerTransport           │
│           isNeedFcmSend = 변경사항 비교       │
│                                              │
│ ③ 팝업 매칭 및 저장                           │
└─────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────┐
│ [BRANCH 3C: 중복 예약 취소 체크]              │
│                                              │
│ ◇ existedCopinoData.truckNumber != truckNo?  │
│   true → (다른 트럭 = 처리 불필요)             │
│   false ▼                                    │
│ containerNumber = pinNo.split("_")[0]        │
│ 조회: getForCheckExpired(터미널, 컨번, 타입)   │
│                                              │
│ ◇ expiredData.pinNo != 현재 pinNo            │
│   AND expiredData.appointmentComplience      │
│       == APPT_CONPL?                         │
│   true → cancelAppointment(expiredPinNo)     │
│           채팅메시지: "운송작업 갱신으로        │
│           인해 예약이 취소되었습니다."          │
│   false → (취소 불필요)                       │
└─────────────────────────────────────────────┘
  │
  ▼
return isNeedFcmSend → [VbsInvokeAlarmService에서 알림 처리]
```

**특이 케이스**:
- **DGTBC050 터미널**: Empty OUT인 경우 별도 업데이트 로직, FCM 미발송
- **6초 규칙**: Copino 최초 등록 후 6초 이내 삭제 불가
- **중복 예약 취소**: 같은 트럭이 같은 컨테이너에 새 코피노를 받으면, 기존 예약이 준수 상태(APPT_CONPL)인 경우 자동 취소

---

## 슬라이드 6: updateTruckTransStatusInTerminal - 터미널 이벤트 처리

> **소스**: `BctransVbsTruckTransOrderService.updateTruckTransStatusInTerminal()`
> **형태**: 플로우차트 (분기 포함)

```
[시작] 터미널에서 이벤트 수신 (method, latestStatus, latestStatusTime, terminalCode, docKey, pinNo, inOut)
  │
  ▼
┌──────────────────────────────────────────┐
│ latestStatusTime 파싱                     │
│ - 14자리 미만 → "00" 추가                 │
│ - DateTimeFormatter("yyyyMMddHHmmss")     │
│ - 파싱 실패 → null로 처리 (계속 진행)      │
└──────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────┐
│ DB 조회: getAllconeTransportOrderDataForTerminalEvent()  │
│ → existedTransOrder                       │
└──────────────────────────────────────────┘
  │
  ▼
◇ existedTransOrder == null?
  │ true → [로그 에러] → return (종료)
  │ false
  ▼
◇ isNeedIgnoreUpdateContainerTransportStatus? (무시해야 할 상태 전이?)
  │
  │ ◇ 기존=CHANGE_CON_LOC AND 이벤트=GATE_IN?
  │   true → return (무시: 위치변경 후 중복 게이트인)
  │
  │ ◇ 기존=CANCEL_INOUT AND 이벤트=GATE_OUT?
  │   true → ◇ 터미널이 ["PECTC050","BCTOC050","BICTC010"] 중 하나?
  │           true → return (무시: 정책 적용 터미널)
  │           false → (계속 진행)
  │
  │ false (무시하지 않음)
  ▼
◇ terminalEventTransStatus ∈ [CHANGE_CON_LOC, EMPTY_CON_SWAP, CANCEL_INOUT]?
  │ true → ◇ terminalEventTransStatus == EMPTY_CON_SWAP?
  │         true → param에 unloadConLoc, oldConNo, previousTransTargetLocCode,
  │                 previousTargetLocDetail 추가
  │ false
  ▼
◇ method == "GateIn"?
  │ false → [일반 상태 업데이트로 건너뛰기]
  │ true
  ▼
┌──────────────────────────────────────────────────────────┐
│ [GateIn 특별 처리: VBS 예약 준수 검사]                     │
│                                                          │
│ ◇ vbsStatus ∈ [TRANSPORT_START, IN_AREA_B, IN_AREA_C]    │
│   AND appointmentStatus == APPT_CONFIRM                   │
│   AND appointmentComplience == APPT_NOT_CONPL?            │
│                                                          │
│   true → Blockchain: /CheckAppointmentCompliance          │
│           - zoneArrivalTime = latestStatusTime            │
│           - remainDistance = "0"                          │
│           → alarmList 수신                                │
│           → Loop: updateVbsDataByGatein() (DB 업데이트)    │
│                                                          │
│   false → (준수 검사 건너뛰기)                              │
└──────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────┐
│ [공통] 컨테이너 운송 상태 업데이트                          │
│ updateContainerTransportDataByTerminalEvent()              │
└──────────────────────────────────────────────────────────┘
  │
  ▼
◇ terminalEventTransStatus.isCompleted() AND inOut == "2" (OUT)?
  │ true → updateTssToGateOutBySystem() (TSS 게이트아웃 처리)
  │         ◇ transShipment == "14" (환적)?
  │           true → cancelTssGroupOrderContainer() (그룹 오더 컨테이너 취소)
  │ false
  ▼
┌──────────────────────────────────────────┐
│ 팝업 상태 업데이트                        │
│ eslipPopupDomainService 처리              │
└──────────────────────────────────────────┘
  │
  ▼
[종료] → [VbsInvokeAlarmService에서 알림 처리]
```

**특이 케이스**:
- **CHANGE_CON_LOC → GATE_IN**: 위치 변경 후 중복 게이트인 이벤트는 무시
- **CANCEL_INOUT → GATE_OUT**: 특정 3개 터미널(PECTC050, BCTOC050, BICTC010)에서만 무시
- **GateIn + 미준수 상태**: 터미널에서 직접 게이트인 시 예약 준수 재검사
- **환적(14) OUT 완료**: TSS 그룹 오더 컨테이너도 함께 취소

---

## 슬라이드 7: updateTruckTransStatusOnRoad - 운송 상태 추적

> **소스**: `AllconeVbsTruckTransOrderService.updateTruckTransStatusOnRoad()`
> **트리거**: Controller에서 serverName == "bctrans"일 때 직접 호출
> **형태**: 플로우차트 (분기 포함)

```
[시작] params 수신 (List<Map>: pinNo, transStatus, remainDistance, remainTime, arrivalEstimatedTime)
  │
  ▼
┌──────────────────────────────────────────┐
│ Loop: params 순회 (각 상태 업데이트 건)    │
└──────────────────────────────────────────┘
  │ (각 param에 대해)
  ▼
┌──────────────────────────────────────────┐
│ DB 조회: getAllconeTransportOrderDataByPinNo(pinNo)  │
│ → truckTransOrder                         │
└──────────────────────────────────────────┘
  │
  ▼
◇ arrivalEstimatedTime 존재?
  │ true → arrivalEstimatedTime 파싱 (yyyy-MM-dd HH:mm:ss)
  │ false → null
  ▼
◇ transStatus == "IN_ZONE"?
  / \
true  false
  │      │
  │      ▼
  │    ┌──────────────────────────────────────────┐
  │    │ [일반 상태: TRANSPORT_START, IN_AREA_B 등]  │
  │    │ Blockchain: /UpdateTransStatus             │
  │    │  - transStatus, remainDistance, remainTime  │
  │    │  - estimatedArrivalTime                    │
  │    │ DB: updateTruckTransStatusOnRoad()          │
  │    │ DB: 상태 이력 저장                           │
  │    └──────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────┐
│ [IN_ZONE 처리]                                        │
│ ◇ zoneArrivalTime이 null? (최초 존 진입인지 확인)      │
│   true → zoneArrivalTime = 현재시각                   │
│                                                      │
│ inZoneParams 리스트에 추가 (나중에 일괄 처리)           │
└──────────────────────────────────────────────────────┘
  │
  ▼ (Loop 종료 후)
  │
◇ inZoneParams가 비어있지 않음?
  │ false → return result
  │ true
  ▼
┌──────────────────────────────────────────────────────┐
│ [IN_ZONE 일괄 처리]                                   │
│ Loop: inZoneParams 순회                               │
│                                                      │
│ Blockchain: /CheckAppointmentCompliance               │
│  - transportCode, pinNo, zoneArrivalTime              │
│ → 응답: alarmList                                     │
│                                                      │
│ Loop: alarmList 순회                                  │
│  - appointmentKeepYn 추출                             │
│  - DB: VBS 데이터 업데이트                              │
│                                                      │
│ ◇ appointmentKeepYn == "Y"?                           │
│   true → appointmentComplience = APPT_CONPL           │
│          canCompliedReservation = true                 │
│   false → appointmentComplience = APPT_NOT_CONPL      │
│           canCompliedReservation = false               │
│                                                      │
│ DB: updateTruckTransOrderLatestStatusInZone()          │
│ @Async: VbsInvokeAlarmService → 준수 알림 발송         │
└──────────────────────────────────────────────────────┘
  │
  ▼
return result (orderId, canCompliedReservation 포함)
```

**특이 케이스**:
- **IN_ZONE은 일괄 처리**: Loop 중 IN_ZONE 건들은 모아두었다가 Loop 종료 후 일괄 처리
- **최초 존 진입 체크**: zoneArrivalTime이 null인 경우에만 시각 기록 (중복 진입 방지)
- **Blockchain 예외**: CheckAppointmentCompliance 실패 시 catch 후 계속 진행

---

## 슬라이드 8: requestDigitalGatein - 디지털 게이트인

> **소스**: `BctransVbsTruckTransOrderService.requestDigitalGatein()` (bctrans 분기)
> **형태**: 플로우차트

```
[시작] BctransDigitalGateinRequest 수신
  │     (pinNo, truckNo, terminalCode, requestSeq, gateInTime,
  │      latitude, longitude, headingDirection)
  │
  ▼
┌──────────────────────────────────────────┐
│ DB 조회: getTerminalApiInfoByInterfaceId │
│  - interfaceId = "IF-VBS-SLIP-041"       │
│  - terminalCode                          │
│ → apiInfo (터미널 API 엔드포인트 정보)     │
└──────────────────────────────────────────┘
  │
  ▼
◇ apiInfo == null?
  │ true → throw RuntimeException("API 정보 없음")
  │ false
  ▼
┌──────────────────────────────────────────┐
│ HTTP POST: 터미널 API 호출               │
│  - url = apiInfo.getUrl()                │
│  - body = BctransDigitalGateinRequest    │
│ → ApiResponse                            │
└──────────────────────────────────────────┘
  │
  ▼
◇ 예외 발생?
  │ true → [로그 에러] → re-throw
  │ false
  ▼
return ApiResponse (터미널 응답 그대로 전달)
```

**참고 - Allcone → Bctrans 호출 전 처리** (allcone 분기에서 bctrans로 전달하기 전):
- AllconeDigitalGateinRequest → BctransDigitalGateinRequest 변환
- GPS 좌표(latitude, longitude) 암호화 (TextCryptoService)
- requestSeq = UUID 생성
- gateInTime = 현재 시각
- DB 저장: UserDigitalGateInRequestEntity (암호화된 좌표 포함)
- 이후 bctrans API 호출

---

## 슬라이드 9: requestBlockIn / cancelStart

> **소스**: `VbsTruckTransOrderController` + `AllconeVbsTruckTransOrderService`
> **형태**: 2개 이벤트를 한 슬라이드에 좌우 배치

### 좌측: requestBlockIn

```
[시작] param 수신 (pinNo, truckNo 등)
  │
  ▼
┌──────────────────────────────────────────┐
│ requestBlockInToBctrans(param)            │
│  - HTTP POST to bctrans:                 │
│    "/mobile/trans/vbs/req/blockin"        │
│  - param 그대로 전달                      │
└──────────────────────────────────────────┘
  │
  ▼
return ApiResponse.ok()
```

> 참고: bctrans 분기에서도 동일하게 requestBlockInToBctrans()를 호출.
> 모든 serverName 분기가 같은 메서드 호출.

### 우측: cancelStart

```
[시작] params 수신 (List<Map>: pinNo 등)
  │
  ▼
◇ serverName == "allcone"?
  │ true → try { cancelStartToBctrans(params) }
  │         catch → [로그 에러] → ApiResponse.ok() (에러 억제)
  │
  │ false (bctrans 또는 기타)
  ▼
┌──────────────────────────────────────────┐
│ cancelStartToBctrans(params)             │
│  - HTTP POST to bctrans:                 │
│    "/mobile/trans/vbs/cancelStart"        │
│  - params 그대로 전달                     │
└──────────────────────────────────────────┘
  │
  ▼
return ApiResponse.ok()
```

**특이 케이스**:
- **cancelStart의 allcone 분기**: 예외 발생 시 에러를 억제하고 성공 응답 반환 (기사 앱에 에러 노출 방지)
- **requestBlockIn**: 모든 분기에서 동일 동작 (단순 전달)

---

## 슬라이드 10: removeDuplicateOrder - VBS/TSS 중복 제거

> **소스**: `VbsTransOrderService.removeDuplicateOrder()`
> **형태**: 플로우차트 (분기 포함)

```
[시작] vbsOrderDataList, tssTransOrderDataList 수신
  │
  ▼
┌────────────────────────────────────────┐
│ 리스트 → Map 변환                       │
│  - vbsMap: Map<containerNo, List<VbsOrderData>>  │
│  - tssMap: Map<containerNo, TssTransOrderData>   │
│  (TSS에 conNo 중복 시 빈 Map 반환)               │
└────────────────────────────────────────┘
  │
  ▼
◇ tssMap이 비어있음?
  │ true → return (중복 없음)
  │ false
  ▼
┌────────────────────────────────────────┐
│ Loop: vbsMap 순회                       │
│  각 containerNo에 대해:                 │
└────────────────────────────────────────┘
  │
  ▼
◇ tssMap에 같은 containerNo 존재?
  │ false → 다음 순회
  │ true
  ▼
┌────────────────────────────────────────────┐
│ VBS에서 매칭 오더 추출:                      │
│  - outOrder = vbsList에서 inOutType==OUT     │
│    AND checkTransShipmentOrder 통과,         │
│    최신(LastUpdatedTime) 1건                 │
│  - inOrder = vbsList에서 inOutType==IN       │
│    AND checkTransShipmentOrder 통과,         │
│    최신 1건                                  │
│                                             │
│ tssOrderTransStatus = tss.transStatus (정수) │
└────────────────────────────────────────────┘
  │
  ▼
◇ tssOrderTransStatus < 10? (사전 운송 단계)
  │ true → continue (둘 다 유지)
  │ false
  ▼
◇ tssOrderTransStatus > 80 AND tss.inCancelTime == null? (반입 단계)
  │ true → outOrder 제거 (OUT은 이미 완료)
  │         inOrder에 대해 → determineRemoveOrder() 호출
  │ false
  ▼
┌────────────────────────────────────────────────────┐
│ [기타 상태: 반출 단계 또는 혼합]                      │
│ outOrder에 대해 → determineRemoveOrder() 호출        │
│  결과가 REMOVE_VBS이면:                              │
│    outOrder 제거 + inOrder도 gateInTime==null이면 제거│
│  결과가 REMOVE_TSS이면:                              │
│    tssMap에서 해당 containerNo 제거                   │
└────────────────────────────────────────────────────┘
  │
  ▼ (Loop 종료 후)
┌────────────────────────────────────────┐
│ Map → List 복원                         │
│ vbsOrderDataList.clear() + addAll      │
│ tssTransOrderDataList.clear() + addAll │
└────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[서브 로직] determineRemoveOrder(vbs, tss, tssOrderTransStatus)

  ◇ vbs.isCancelOrder() OR tss.isCancelOrder()?
    true → NO_ACTION (취소된 오더는 건드리지 않음)

  vbsTransStatus = TransshipmentTransStatus 변환
  tssTransStatus = TransshipmentTransStatus 변환

  ◇ vbsTransStatus.ordinal() < tssTransStatus.ordinal()?
    true → REMOVE_VBS (TSS가 더 진행됨)

  ◇ vbsTransStatus.ordinal() > tssTransStatus.ordinal()?
    true → REMOVE_TSS (VBS가 더 진행됨)

  [동일 ordinal인 경우]
  ◇ vbs.docKey == tss.docKey?
    true → REMOVE_VBS (같은 코피노 = VBS 중복 제거)

  [다른 docKey]
  tssSlipErrorYN = (status>80) ? inSlipError : outSlipError
  ◇ tssSlipErrorYN == "Y" AND vbs.copinoErrorStatus == NORMAL?
    true → REMOVE_TSS (TSS에 에러, VBS가 정상)
    false → REMOVE_VBS (기본값: TSS 유지)
```

**핵심 규칙**:
- **TSS 상태 < 10**: 양쪽 모두 유지 (아직 운송 전)
- **TSS 상태 > 80 + inCancelTime null**: 반입 단계 → OUT 오더는 무조건 제거
- **동일 진행도**: docKey 동일하면 VBS 제거, TSS 에러면 TSS 제거
- **취소 오더**: 절대 건드리지 않음

---

## 슬라이드 11: InternalGateService - 내부게이트 데이터 생성

> **소스**: `InternalGateService.createAllInternalGateData()`
> **형태**: 플로우차트

```
[시작] 파라미터 수신
  │   (vbsSlipList, outTssSlipList, inTssSlipList,
  │    tssGroupOrderDataList, terminalInternalGateConfigMap,
  │    latestTerminal, lastTerminalGateInTime)
  │
  ▼
◇ terminalInternalGateConfigMap이 비어있음?
  │ true → return InternalGateDataPair(빈 결과, 버튼 비활성)
  │ false
  ▼
┌──────────────────────────────────────────────────────┐
│ [시간/터미널 기준 필터링]                               │
│                                                      │
│ validVbsSlipList = vbsSlipList에서:                   │
│  - terminalCode == latestTerminal                    │
│  - gateInTime >= lastGateInTime - 1시간               │
│                                                      │
│ validOutTssSlipList = outTssSlipList에서:              │
│  - outTerminalCode == latestTerminal                 │
│  - NOT (fromGateOutTime!=null AND outCancelTime!=null)│
│  - fromGateInTime >= lastGateInTime - 1시간           │
│                                                      │
│ validInTssSlipList = inTssSlipList에서:                │
│  - inTerminalCode == latestTerminal                  │
│  - NOT (toGateOutTime!=null AND inCancelTime!=null)   │
│  - toGateInTime >= lastGateInTime - 1시간             │
└──────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────┐
│ [3가지 소스별 처리]                       │
│                                          │
│ ① processVbsSlipList()                   │
│    → false 반환 시 → return 빈 결과       │
│                                          │
│ ② collectOutTerminalTssSlipData()        │
│    → false 반환 시 → return 빈 결과       │
│                                          │
│ ③ collectInTerminalTssSlipData()         │
└──────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────┐
│ [20ft 컨테이너 합적 체크]                              │
│                                                      │
│ combinedContainerList = 환적 데이터에서:               │
│  - outOrderConSize == 20 AND inOrderConSize == 20    │
│                                                      │
│ ◇ combinedContainerList.size() >= 2?                 │
│   true → showPositionSelectionPopupYN = true         │
│           ◇ checkAllowedCombined() 실패?             │
│             true → return (빈 결과, 버튼 비활성)       │
│   false → showPositionSelectionPopupYN = false       │
└──────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────┐
│ [버튼 활성화 판정]                                    │
│                                                      │
│ hasInactiveButton = outMap + inMap 중 하나라도         │
│                     isInternalGateButtonActivated=false│
│ isAllJobDone = validVbs + validOutTss + validInTss    │
│                모두 jobDoneDateTime != null            │
│                                                      │
│ ◇ hasInactiveButton OR NOT isAllJobDone?             │
│   true → 모든 버튼 비활성화                            │
│   false → 현재 상태 유지                               │
└──────────────────────────────────────────────────────┘
  │
  ▼
return InternalGateDataPair(showPopupYN, outMap, inMap)

[예외 발생 시] → return 빈 결과 (버튼 비활성)
```

**특이 케이스**:
- **1시간 윈도우**: 마지막 게이트인 시간 기준 1시간 이내 데이터만 유효
- **20ft 합적**: 20ft 컨테이너 2개 이상이면 위치 선택 팝업 표시
- **전부 완료 체크**: 하나라도 미완료면 모든 버튼 비활성화 (부분 처리 방지)

---

## 슬라이드 12: UserRequestIssueEslipService - E-Slip 발급 판정

> **소스**: `UserRequestIssueEslipService.checkAndGetCanIssueSLipData()` + `checkSingleTssBackHaulIssueSlip()`
> **형태**: 플로우차트 (분기 포함)

```
[시작] tssTransOrderData, terminalConfig, slipLists, lastGateInTime 수신
  │
  ▼
◇ TransshipmentTransStatus == CANCEL_IN or CANCEL_OUT?
  │ true → return null (취소 오더 = 발급 불가)
  │ false
  ▼
◇ tss.errorYN == "Y" AND terminalConfig.useErrEslipIssueYN?
  / \
true  false → [백홀 로직으로 건너뛰기]
  │
  ▼
┌─────────────────────────────────────────────────┐
│ [에러 E-Slip 발급 판정]                           │
│                                                  │
│ ◇ getInOut(tss) == "OUT"?                        │
│   true → ◇ fromGateInTime != null                │
│             AND fromGateInTime >= lastGateInTime? │
│           true → return CanIssueSlipData("ERR")  │
│                                                  │
│ ◇ getInOut(tss) == "IN"?                         │
│   true → ◇ toGateInTime != null                  │
│             AND toGateInTime >= lastGateInTime?   │
│           true → return CanIssueSlipData("ERR")  │
│                                                  │
│ → return null (에러 슬립 조건 미충족)              │
└─────────────────────────────────────────────────┘

[에러가 아닌 경우 - 백홀 로직]
  │
  ▼
◇ backHaulTssSingleEslipIssueLimitMin == 0?
  │ true → return null (백홀 비활성)
  │ false
  ▼
◇ tss.dataCreatedTime > 1일 전 AND tss.fromGateInTime == null?
  │ false → return null
  │ true
  ▼
  isBringIn = (tss.transStatus > 80)
  terminalCode = isBringIn ? inTerminalCode : outTerminalCode

  ◇ bringInSlip이 존재 AND NOT isBringIn (OUT 단계)?
    │ true ▼
    │ ◇ bringOutSlip도 존재? (IN+OUT 모두 있음)
    │   true → ◇ bringIn 전부 완료 AND bringOut 전부 완료
    │             AND terminalCode == outTerminalCode?
    │           true → return CanIssueSlipData("BACKHAUL",
    │                    시작=마지막완료시각, 만료=+N분)
    │   false → ◇ bringIn만 전부 완료
    │              AND terminalCode == outTerminalCode?
    │            true → return CanIssueSlipData("BACKHAUL")
    │
    │ false ▼
    ◇ bringOutSlip이 존재 AND NOT isBringIn
      AND terminalCode == outTerminalCode?
      true → ◇ slipDataList에 현재 conNo가 이미 포함?
              true → return null (중복)
              false → ◇ bringOut[0].jobDoneDateTime != null?
                      true → return CanIssueSlipData("GENERAL")
                      false → return null
      false → ◇ gateInWithoutCopinoDto != null
                AND gateInTime != null
                AND terminalCode 일치?
              true → return CanIssueSlipData("GENERAL",
                      시작=gateInTime, 만료=+N분)

  → return null
```

**E-Slip 발급 유형**:
- **ERR**: 에러 상태 E-Slip (에러 발생했지만 게이트인 완료된 경우)
- **BACKHAUL**: 백홀 E-Slip (반입/반출 작업 완료 후 제한 시간 내)
- **GENERAL**: 일반 E-Slip (코피노 없이 게이트인한 경우)

**특이 케이스**:
- **백홀 제한시간**: `backHaulTssSingleEslipIssueLimitMin`만큼의 시간 내에만 발급 가능
- **중복 방지**: slipDataList에 이미 동일 conNo가 있으면 발급 거부
- **코피노 없는 게이트인**: gateInWithoutCopinoDto를 통해 수동 게이트인도 지원

---

## 슬라이드 13: VbsInvokeAlarmService (1/2) - 알림 라우팅 및 코피노 알림

> **소스**: `VbsInvokeAlarmService`
> **형태**: 라우팅 흐름도 + 코피노 알림 상세

### 상단: 알림 라우팅 (vbsInvokeAlarm)

```
[시작] VbsInvokeAlarmParam 수신
  │
  ▼
◇ param 유형 판별
  │
  ├─ isReservationResult? ──→ sendRequestAppointmentPushToUserV2()
  │                           ("운송예약요청 정보가 수정되었습니다")
  │
  ├─ isCopinoVerificationResult? ──→ sendCopinoVerificationPushToUser()
  │                                   [아래 상세]
  │
  ├─ isRemoveCopino? ──→ sendRemoveCopinoPushToUser()
  │                       ("운송작업정보가 삭제되었습니다")
  │
  ├─ isReeferPlugInoutResult? ──→ sendReeferPlugInOutResultPushToUser()
  │                                [아래 상세]
  │
  └─ isTerminalEvent? ──→ sendTerminalEventPushToUserV2()
                           [슬라이드 14]
```

### 하단: 코피노 검증 알림 상세 (sendCopinoVerificationPushToUser)

```
[시작] param (terminalCode, docKey, pinNo, copinoErrType)
  │
  ▼
┌────────────────────────────────────────┐
│ DB 조회: getAllconeTransportOrderData() │
│ → allconeTransportOrderData            │
└────────────────────────────────────────┘
  │
  ▼
◇ 조회 결과 비어있음?
  │ true → [로그 에러] → return
  │ false
  ▼
┌────────────────────────────────────────────────────┐
│ FCM 발송 여부 판정:                                  │
│ isOrderError = (copinoErrorStatus == ERROR)         │
│ isOrderGateIn = (gateInTime != null)                │
│ isParamErrorY = (copinoErrType == "LE")             │
│                                                    │
│ ◇ NOT isOrderError AND isOrderGateIn AND isParamErrorY? │
│   true → isNeedFCM = false (복구 시나리오: FCM 억제)     │
│   false → isNeedFCM = true                              │
└────────────────────────────────────────────────────┘
  │
  ▼
◇ isNeedFCM?
  │ false → [로그: "FCM message was not sent."] → return
  │ true
  ▼
┌────────────────────────────────────────────────────┐
│ 알림 구성 (useVbsAppYn == "Y" 확인 후):             │
│                                                    │
│ ◇ docStatus == "1" (삭제)?                          │
│   → 제목: "운송작업 삭제 알림"                        │
│     내용: "운송작업정보가 삭제되었습니다."              │
│     alertType: TRANS_ORDER_EXPIRED                  │
│                                                    │
│ ◇ firstRegistDateTime != transportStatusTime (갱신)?│
│   → 제목: "운송작업 갱신 알림"                        │
│     내용: "운송작업정보가 갱신되었습니다."              │
│     alertType: TRANS_ORDER_UPDATE                   │
│                                                    │
│ ◇ 기타 (신규)                                       │
│   → alertType: TRANS_NOTICE                         │
└────────────────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────────────────┐
│ FCM 발송:                                          │
│ ① 기사 deviceToken → sendPushData()                │
│ ② 관리자 adminTokenData → Loop: sendPushData()     │
│    (각 adminData의 deviceToken으로 발송)             │
└────────────────────────────────────────────────────┘
```

### 리퍼 플러그 알림 (sendReeferPlugInOutResultPushToUser)

```
◇ gateInTime != null? (게이트인 완료 상태?)
  true → 제목: "인수도증 갱신 알림"
          내용: "인수도증이 갱신되었습니다."
          alertType: TRANS_SLIP_UPDATE
  false → 제목: "운송작업 갱신 알림"
           내용: "운송작업정보가 갱신되었습니다."
           alertType: TRANS_ORDER_UPDATE
```

---

## 슬라이드 14: VbsInvokeAlarmService (2/2) - 터미널 이벤트 및 예약 알림

> **소스**: `VbsInvokeAlarmService`

### 터미널 이벤트 알림 (sendTerminalEventPushToUserV2)

```
[시작] param (terminalCode, docKey, pinNo, latestStatus)
  │
  ▼
┌────────────────────────────────────────┐
│ DB 조회: getAllconeTransportOrderData() │
│ → allconeTransportOrderData            │
└────────────────────────────────────────┘
  │
  ▼
◇ 조회 결과 null?
  │ true → [로그 에러] → return
  │ false
  ▼
┌────────────────────────────────────────────────────┐
│ 포트번호 제거 처리:                                  │
│ DB 조회: getTerminalRemovePortNumList()              │
│ → removePortNumYNMap                                │
│                                                    │
│ ◇ removePortNumYNMap.get(terminalCode) == "Y"?     │
│   true → conLoc = conLoc.substring(1)              │
│          (첫 글자 = 포트번호 제거)                    │
│   false → conLoc 그대로 사용                        │
└────────────────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────────────────┐
│ FcmData 구성:                                      │
│  - alertType: SLIP_REFRESH                         │
│  - conLoc (포트번호 제거 적용)                       │
│  - moveLoc = transTargetLocCode.getMoveLoc()       │
│  - etcMessage = transInfoMessage                   │
│  - 제목: "올컨e", 내용: "인수도증 업데이트"           │
└────────────────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────────────────┐
│ FCM 발송:                                          │
│ ① 기사 deviceToken → sendPushData()                │
│ ② 관리자 adminTokenData → Loop: sendPushData()     │
└────────────────────────────────────────────────────┘
```

### 코피노 없는 게이트인 알림 (sendGateInWithoutCopinoAlarm)

```
[시작] GateInWithoutCopinoDto 수신
  │
  ▼
┌────────────────────────────────────────┐
│ FcmData 구성:                          │
│  - alertType: SLIP_REFRESH             │
│  - 제목: "게이트 진입 알림"             │
│  - 내용: "게이트에 진입하셨습니다."     │
└────────────────────────────────────────┘
  │
  ▼
◇ deviceToken이 존재?
  │ true → sendPushData()
  │ false → [로그: "디바이스 토큰을 찾을 수 없습니다"]
```

### 예약 업데이트 알림 (sendPushUpdateDataV2)

```
[시작] allconeTransportOrderData, param 수신
  │
  ▼
◇ terminal.useVbsAppYn == "Y"?
  │ false → return
  │ true
  ▼
┌──────────────────────────────────────────────────────────┐
│ pinNo 파싱:                                              │
│  - pinNo.split("_")                                     │
│  - isOut = (split.length > 2 AND split[2] == "1")       │
│                                                         │
│ conLoc/turnTime 방향 판정:                                │
│  - isOut이면: fromConLoc=conLoc, fromTurnaroundTime=turnTime  │
│  - isOut 아니면: toConLoc=conLoc, toTurnaroundTime=turnTime   │
│                                                         │
│ ◇ transStatus == "GATE_IN"?                              │
│   true → blockEnterAvailableTime = transStatusUpdatedTime + 1분 │
│   false → null                                           │
└──────────────────────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────────────────┐
│ FcmData 구성:                                      │
│  - alertType: TRANS_UPDATE                         │
│  - 모든 상세 필드 포함 (conLoc, turnTime, error,    │
│    chattingMessage, blockEnterAvailableTime,        │
│    copinoErrType, compliedAppointment)              │
└────────────────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────────────────┐
│ FCM 발송:                                          │
│ ① 기사 deviceToken → sendPushData()                │
│ ② 관리자 adminTokenData → Loop: sendPushData()     │
└────────────────────────────────────────────────────┘
```

**특이 케이스**:
- **포트번호 제거**: 특정 터미널은 conLoc 첫 글자(포트번호)를 제거하여 표시
- **방향 판정(isOut)**: pinNo의 3번째 세그먼트가 "1"이면 반출, 아니면 반입
- **blockEnterAvailableTime**: GATE_IN 상태일 때만 +1분 후 시각 계산
- **관리자 발송**: 기사 외에 해당 트럭의 관리자에게도 동일 알림 발송

---

## 슬라이드 15: 상태 전이 다이어그램 요약

### Appointment Status 상태 전이

```
┌──────────────────────┐
│ REQUEST_APPOINTMENT   │ ← 코피노 수신 시 초기 상태
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐      ┌──────────────────────┐
│ APPT_NOT_CONFIRM      │─────→│ APPT_CONFIRM          │
│ (예약 미확정)         │ 확정  │ (예약 확정)           │
└──────────────────────┘      └──────────┬───────────┘
           │                             │
           │ 취소                        │ 취소
           ▼                             ▼
┌──────────────────────────────────────────────────────┐
│                CANCEL_APPOINTMENT                      │
│                (예약 취소)                               │
│ - 기사 수동 취소                                        │
│ - 동일 컨테이너 다른 코피노 수신 시 자동 취소             │
│ - 운송작업 갱신 시 기존 예약 자동 취소                    │
└──────────────────────────────────────────────────────┘
```

### VBS Status (위치 추적) 상태 전이

```
TRANSPORT_START → IN_AREA_B → IN_AREA_C → IN_ZONE
                                            │
                                    ┌───────┴───────┐
                                    ▼               ▼
                              APPT_CONPL      APPT_NOT_CONPL
                              (예약 준수)      (예약 미준수)
```

### Transport Status (터미널 이벤트) 상태 전이

```
                    ┌─ GATE_IN ──→ GATE_OUT (정상 완료)
                    │
터미널 이벤트 ───────┼─ CHANGE_CON_LOC (위치 변경)
                    │   ※ 이후 GATE_IN 이벤트 무시
                    │
                    ├─ EMPTY_CON_SWAP (공컨 교환)
                    │   → unloadConLoc, oldConNo 업데이트
                    │
                    └─ CANCEL_INOUT (반출입 취소)
                        ※ 이후 GATE_OUT 이벤트:
                           PECTC050, BCTOC050, BICTC010 → 무시
                           기타 터미널 → 처리
```

### 무시되는 상태 전이 조합

| 기존 상태 | 수신 이벤트 | 처리 | 비고 |
|----------|-----------|------|------|
| CHANGE_CON_LOC | GATE_IN | **무시** | 위치변경 후 중복 게이트인 |
| CANCEL_INOUT | GATE_OUT | **정책별** | 3개 터미널만 무시, 나머지 처리 |

---

## 부록: 주요 용어/코드 정리

| 용어 | 설명 |
|------|------|
| pinNo | 운송 작업 식별 키 (형식: `컨테이너번호_docKey_방향`) |
| docKey | 코피노 문서 키 |
| transportCode | 운송 레코드 UUID |
| terminalCode | 터미널 식별 코드 (예: DGTBC050, PECTC050) |
| copinoErrType | 코피노 에러 유형 ("LE" = Logic Error) |
| feType | FULL / EMPTY 구분 |
| inOutType | IN(반입) / OUT(반출) |
| transShipment | "14" = 환적 운송 |
| backHaulTssSingleEslipIssueLimitMin | 백홀 E-Slip 발급 제한 시간(분) |
| isOut | pinNo 3번째 세그먼트가 "1"이면 반출 |

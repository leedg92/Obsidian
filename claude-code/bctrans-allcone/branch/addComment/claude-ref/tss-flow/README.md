# TSS 이벤트 프로세스 흐름도

BaaS에서 `POST /itt/invoke/alarm`으로 수신되는 TSS 운송 이벤트별 처리 플로우.

## 공통 진입점

모든 이벤트는 `IttInvokeAlarmController.invokeComplete()`를 통해 진입합니다.
serverName 설정에 따라 bctrans(DB 저장) → allcone(FCM 푸시) 순서로 처리됩니다.

- [공통 진입점 (invoke/alarm)](claude-code/bctrans-allcone/브랜치별%20CLAUDE.md/addComment/claude-ref/tss-flow/invoke-alarm-entry.md)

## 이벤트별 플로우

| 이벤트 | method 값 | 파일 |
|--------|-----------|------|
| COPINO 계열 (배차/생성/차량변경) | `CreateDispatchInfo`, `CreateCopino`, `ChangeTruckNo` | [CreateCopino.md](CreateCopino.md) |
| 터미널 이벤트 | `GateIn`, `BlockIn`, `JobDone`, `GateOut`, `GroupOrderGateIn` 등 | [TerminalEvent.md](claude-code/bctrans-allcone/브랜치별%20CLAUDE.md/addComment/claude-ref/tss-flow/TerminalEvent.md) |
| 취소 | `CancelOut`, `CancelOutGroup` | [CancelOut.md](CancelOut.md) |
| 그룹오더 | 생성 → 시작 → GroupOrderGateIn → 완료 | [GroupOrder.md](GroupOrder.md) |

## 무시 대상 이벤트

아래 이벤트는 bctrans/allcone 양쪽 모두에서 처리하지 않고 무시합니다.

| method | 사유 |
|--------|------|
| `CreateShippingOrderList` | 선적오더 생성 (bctrans 처리 대상 아님) |
| `CreateGroup` | 그룹 생성 (bctrans 처리 대상 아님) |
| `UpdateTransStatus` | 상태 업데이트 (알림 불필요) |
| `UpdateGroupTransStatus` | 그룹 상태 업데이트 (알림 불필요) |

## 관련 소스 파일

| 파일 | 역할 |
|------|------|
| `invoke/web/IttInvokeAlarmController.java` | 진입점, serverName 분기 |
| `invoke/dto/IttInvokeAlarmParam.java` | 이벤트 분류 DTO |
| `bctrans/tss/service/BctransIttTruckTransOrderService.java` | bctrans DB 처리 |
| `invoke/service/IttInvokeAlarmService.java` | allcone FCM 발송 |
| `bctrans/group/service/TssGroupOrderService.java` | 그룹오더 핵심 서비스 |
| `bctrans/group/service/TssGroupOrderProcessService.java` | 그룹오더 상태/배차 처리 |
| `bctrans/group/service/TssGroupOrderAsyncService.java` | 터미널 비동기 통신 |

## IttTransStatus 상태코드 참조

| 코드 | enum | 설명 |
|------|------|------|
| -70 | CANCEL_IN | 반입 취소 |
| -60 | CANCEL_OUT | 반출 취소 |
| 10 | READY | TSS 단건 오더 생성 |
| 20 | START | 운송 출발 |
| 30 | IN_AREA_A | A 구역 통과 |
| 40 | IN_AREA_B | B 구역 통과 |
| 50 | IN_AREA_C | C 구역 통과 |
| 55 | FROM_PRE_GATE_IN | 반출 프리게이트 진입 |
| 60 | FROM_GATE_IN | 반출 터미널 게이트 진입 |
| 65 | FROM_BLOCK_IN | 반출 터미널 블럭 진입 |
| 70 | FROM_LOAD | 반출 터미널 상차 완료 |
| 80 | FROM_GATE_OUT | 반출 터미널 게이트 진출 |
| 85 | TO_PRE_GATE_IN | 반입 프리게이트 진입 |
| 90 | TO_GATE_IN | 반입 터미널 게이트 진입 |
| 95 | TO_BLOCK_IN | 반입 터미널 블럭 진입 |
| 100 | TO_UNLOAD | 반입 터미널 하차 완료 |
| 110 | TO_GATE_OUT | 반입 터미널 게이트 진출 |

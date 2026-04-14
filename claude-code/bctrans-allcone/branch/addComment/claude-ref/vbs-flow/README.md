# VBS 이벤트 프로세스 흐름도

BaaS에서 `POST /vbs/invoke/alarm`으로 수신되는 VBS(EDI망) 이벤트별 처리 플로우.

## 공통 진입점

모든 이벤트는 `VbsInvokeAlarmController.invokeComplete()`를 통해 진입합니다.
serverName 설정에 따라 bctrans(DB 저장) → allcone(FCM 푸시) 순서로 처리됩니다.

- [공통 진입점 (invoke/alarm)](claude-code/bctrans-allcone/branch/addComment/claude-ref/vbs-flow/invoke-alarm-entry.md)

## 이벤트별 플로우

| 이벤트 | method 값 | 파일 |
|--------|-----------|------|
| COPINO 검증결과 | `CopinoVerificationResult`, `CopinoVerificationResultWithReservation` | [CopinoVerificationResult.md](CopinoVerificationResult.md) |
| 예약결과 | `ReservationResult` | [ReservationResult.md](ReservationResult.md) |
| COPINO 삭제 | `RemoveCopino` | [RemoveCopino.md](RemoveCopino.md) |
| 냉컨 Plug In/Out | `ReeferPlugInOutResult` | [ReeferPlugInOutResult.md](ReeferPlugInOutResult.md) |
| 터미널 이벤트 | `GateIn`, `EnterBlock`, `JobDone`, `GateOut`, `CancelInOut`, ... | [TerminalEvent.md](claude-code/bctrans-allcone/branch/addComment/claude-ref/vbs-flow/TerminalEvent.md) |

## 관련 소스 파일

| 파일 | 역할 |
|------|------|
| `invoke/web/VbsInvokeAlarmController.java` | 진입점, serverName 분기 |
| `invoke/dto/VbsInvokeAlarmParam.java` | 이벤트 분류 DTO |
| `bctrans/vbs/service/BctransVbsTruckTransOrderService.java` | bctrans DB 처리 |
| `invoke/service/VbsInvokeAlarmService.java` | allcone FCM 발송 |
| `allcone/vbs/service/AllconeVbsTruckTransOrderService.java` | 예약 확인/취소 |

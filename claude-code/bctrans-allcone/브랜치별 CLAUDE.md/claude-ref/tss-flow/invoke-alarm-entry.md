# TSS Invoke Alarm - 공통 진입점

## 개요

BaaS에서 TSS 운송 이벤트 발생 시 `POST /itt/invoke/alarm`으로 호출.
serverName에 따라 bctrans(DB 처리) → allcone(FCM 푸시) 순서로 분기.

## 진입 분기

```mermaid

flowchart TD
    START(["TSS 이벤트 수신
    POST /itt/invoke/alarm"]) --> SERVER{"서버 구분?"}

    SERVER -->|"allcone"| AC["FCM 푸시 발송"]
    AC --> OK

    SERVER -->|"bctrans"| BC["DB 저장 / 상태 업데이트
    + KTNET 이동실적 전송
    + 운송사(TMS) 콜백 전송"]
    BC --> SEND["allcone으로 알림 전달"]
    SEND --> OK

    OK(["응답 반환"])
```

> VBS와 달리 TSS는 bctrans 처리 후 **항상** allcone으로 알림을 전달합니다 (FCM 발송 여부 게이트 없음).

## 이벤트별 처리 분기

```mermaid

flowchart TD
    EVENT{"이벤트 종류?"}

    EVENT -->|"StartGroupOrder
    RestartGroupOrder"| GRP["트럭-그룹 매핑
    저장 (upsert)"]

    EVENT -->|"CreateShippingOrderList
    CreateGroup
    UpdateTransStatus
    UpdateGroupTransStatus"| SKIP["무시"]

    EVENT -->|"CreateDispatchInfo
    CreateCopino
    ChangeTruckNo"| COPINO["운송오더 저장/갱신
    + BaaS COPINO 조회"]

    EVENT -->|"GateIn, BlockIn
    JobDone, GateOut
    GroupOrderGateIn 등"| TML["운송 상태 업데이트
    + 부가 처리"]

    EVENT -->|"CancelOut
    CancelOutGroup"| CANCEL["취소 처리
    + 그룹오더 연동"]
```

## bctrans 공통 후처리

COPINO 계열, 터미널 이벤트, 취소를 제외한 그룹오더 시작/재시작을 제외하고,
모든 이벤트는 아래 공통 후처리를 거칩니다.

| 순서 | 처리 | 조건 |
|------|------|------|
| 1 | 운송오더 DB 저장/갱신 | 항상 |
| 2 | KTNET 이동실적 전송 | CreateCopino 제외 |
| 3 | 운송사(TMS)에 터미널 이벤트 콜백 | 항상 |
| 4 | 운송이력 저장 | GateOut/JobDone이고 latestStatus ≥ 100 (반입 완료 이후) |

## allcone FCM 발송 분기

```mermaid

flowchart TD
    START(["allcone 이벤트 수신"]) --> CHECK{"알림 설정 활성화?"}
    CHECK -->|No| DONE(["종료"])

    CHECK -->|Yes| TYPE{"이벤트 종류?"}

    TYPE -->|"CreateDispatchInfo
    CreateCopino
    ChangeTruckNo"| ARRIVE["운송작업 도착 알림
    (새 기사 + 관리자)"]
    ARRIVE --> PREV{"이전 기사 존재 &&
    트럭번호 변경?"}
    PREV -->|Yes| CANCEL_PUSH["이전 기사에게
    운송작업 취소 알림"]
    PREV -->|No| DONE

    TYPE -->|"CancelOut
    CancelOutGroup"| CANCEL["작업 취소 알림
    (기사 + 관리자)"]

    TYPE -->|"기타 (터미널 이벤트)"| SLIP["인수도증 갱신 알림
    (기사만)"]

    CANCEL_PUSH --> DONE
    CANCEL --> DONE
    SLIP --> DONE
```

# 05. 터미널 이벤트 (Terminal Event)

## 개요

터미널 내부에서 발생하는 운송 진행 이벤트(게이트인/블록진입/작업완료/게이트아웃 등) 수신 시 호출.
bctrans에서 상태 업데이트 + 부가 처리 → allcone에서 인수도증 업데이트 FCM 푸시 발송.

## 포함되는 이벤트(method)

| method | 설명 | Controller에서 매핑하는 latestStatus |
|--------|------|------|
| GateIn | 터미널 게이트 진입 | (Controller에서 매핑 안함) |
| EnterBlock | 야드 블록 진입 | (Controller에서 매핑 안함) |
| JobDone | 하역/상차 작업 완료 | (Controller에서 매핑 안함) |
| GateOut | 터미널 게이트 반출 | (Controller에서 매핑 안함) |
| CancelInOut | 반출입 취소 | (Controller에서 매핑 안함) |
| EmptyConInspectionResult | 공컨테이너 EIR 검사 | EMPTY_CON_INSPTN_RESULT |
| EmptyConCleaningResult | 공컨테이너 세척 | EMPTY_CON_CLEAN_RESULT |
| EmptyConSwapResult | 공컨테이너 교환(스왑) | EMPTY_CON_SWAP_RESULT |
| ChangeConLoc | 장치장 위치 변경 | CHANGE_CON_LOC |
| OnEmptyConCPSArrival | CPS 도착 감지 | CPS_ARRIVAL |
| OnCPSAutomationStart | CPS 자동 하차 시작 | CPS_AUTO_START |

## 전체 프로세스 플로우

```mermaid

---
config:
  theme: dark
---

flowchart TD
    START(["터미널 이벤트 수신"]) --> PARSE["수신된 latestStatusTime 파싱
    수신된 latestStatus를
    TransportStatus로 변환"]
    PARSE --> QUERY["DB에서 기존 오더 조회"]

    QUERY --> EXIST{"기존 오더 존재?"}
    EXIST -->|No| DONE_ERR(["에러 로그, 종료"])

    EXIST -->|Yes| IGNORE{"무시해야 할
    상태 전환?"}
    IGNORE -->|Yes| DONE_SKIP(["종료"])

    IGNORE -->|No| LOC{"수신된 상태가
    위치 변경 관련?
    CHANGE_CON_LOC ||
    EMPTY_CON_SWAP ||
    CANCEL_INOUT"}
    LOC -->|Yes| LOC_PARAM["위치 상세 정보
    파라미터 세팅"]
    LOC -->|No| GATEIN_CHECK
    LOC_PARAM --> GATEIN_CHECK

    GATEIN_CHECK{"수신 이벤트 GateIn &&
    기존 오더가
    운송시작/B구역/C구역 &&
    예약확인 && 예약미준수?"}
    GATEIN_CHECK -->|Yes| COMPLIANCE["블록체인에 예약준수
    검증 요청 후
    VBS 데이터 업데이트"]
    GATEIN_CHECK -->|No| UPDATE
    COMPLIANCE --> UPDATE

    UPDATE["터미널 이벤트로
    기존 오더 운송 상태 업데이트"]

    UPDATE --> COMPLETED{"수신 상태가 완료
    && 반출(inOut=2)?"}
    COMPLETED -->|Yes| TSS["TSS 운송도 게이트아웃 처리"]
    TSS --> TRANSSHIP{"환적(14)?"}
    TRANSSHIP -->|Yes| CANCEL_TSS["TSS 그룹오더
    컨테이너 취소"]
    TRANSSHIP -->|No| POPUP
    CANCEL_TSS --> POPUP
    COMPLETED -->|No| POPUP

    POPUP["팝업 처리"] --> AC_QUERY["allcone:
    오더 데이터 조회"]

    AC_QUERY --> AC_EXIST{"오더 존재?"}
    AC_EXIST -->|No| DONE(["종료"])
    AC_EXIST -->|Yes| PORT{"터미널별 포트번호
    제거 설정 Y?"}
    PORT -->|Yes| PORT_REMOVE["conLoc 첫 글자
    (포트번호) 제거"]
    PORT -->|No| PUSH
    PORT_REMOVE --> PUSH

    PUSH["인수도증 업데이트
    푸시 발송
    (기사 + 관리자)"]
    PUSH --> DONE(["완료"])
```

## 무시 조건 (isNeedIgnoreUpdateContainerTransportStatus)

| 기존 오더 상태 | 수신 이벤트 | 결과 | 사유 |
|--------------|-----------|------|------|
| CHANGE_CON_LOC | GateIn | 무시 | 위치변경 후 게이트인 이벤트 중복 방지 |
| CANCEL_INOUT | GateOut | 특정 터미널만 무시 (BPTS, BCT, BPTG) | 취소 후 게이트아웃 이벤트 정책 |

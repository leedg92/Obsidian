
### 공통 시작 변수선언

```
        Map<String, Object> param = new HashMap<>(message);
        String now = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        int transStatus = 10;
        boolean isUpdateIgnored = false;
        IttTransStatus ittTransStatus = IttTransStatus.READY;
```

### CreateCopino
```
mermaid
flowchart TD

    A[saveTruckTransOrder 호출<br/>method: CreateCopino] --> B[기본 변수 초기화<br/>transStatus = 10<br/>ittTransStatus = READY]

    B --> C[기존 운송 오더 조회<br/>getByDocKey]

    C --> D[블록체인 Copino 정보 조회<br/>copinoParam.put inOut: FR<br/>bChainService.exchange GetCopino]

    D --> E{copinoResult 존재?}

    E -->|예| F{운영환경 체크<br/>allcone or bctrans?}

    F -->|예| G[Ketnet 검증 요청<br/>verifyService.requestTssOrderKetnetVerify]

    F -->|아니오| H[Profile 로그 출력]

    G --> I[배차일시/상태값 세팅]

    H --> I

    E -->|아니오| I

    I --> J{dispatchDate 존재?}

    J -->|아니오| K[현재시간으로 세팅<br/>dispatchDate = now<br/>latestStatus = 10<br/>transStatus = 10<br/>latestStatusTime = now]

    J -->|예| L[latestStatusTime = dispatchDate]

    K --> M[컨테이너 무게 보정<br/>String → Integer]

    L --> M

    M --> N{기존 오더 존재?}

    N -->|예| O[이전 위치/변경 카운트 세팅<br/>changeOutConLocCount<br/>changeInConLocCount<br/>prevOutConLoc<br/>prevInConLoc]

    N -->|아니오| P[컨테이너 정보 체크<br/>checkGeneralContainerByTssOrderInsertParam]

    O --> Q[에러/에러메시지 보정<br/>error 값 Y/N 변환<br/>errorMessage 200자 제한]

    Q --> R[게이트타입 세팅<br/>빈 문자열로 초기화]

    R --> S[터미널 코드 세팅<br/>outTerminalCode<br/>inTerminalCode]

    S --> T[오더 변환<br/>convertUpdateOrder]

    T --> U{outCancelTime 존재?}

    U -->|예| V[취소 오더 갱신<br/>updateTruckTransOrderAfterCancelOut]

    U -->|아니오| W{inCancelTime 존재?}

    W -->|예| X[취소 오더 갱신<br/>updateTruckTransOrderAfterCancelIn]

    W -->|아니오| Y[일반 오더 갱신<br/>updateTruckTransOrder]

    V --> Z[운송 상태 갱신<br/>updateTransTruckStatus]

    X --> Z

    Y --> Z

    P --> AA[트럭 정보 체크<br/>checkGeneralTruckerByTruckerId]

    AA --> BB[신규 오더 생성<br/>insertTruckTransOrder]

    BB --> Z

    Z --> CC{dispatchGroup 존재?}

    CC -->|아니오| DD[그룹오더 포함 체크<br/>checkContainGroupOrder]

    CC -->|예| EE[그룹오더 상태 저장<br/>saveGroupOrderTransStatus]

    DD --> EE

    EE --> FF[Copino 검증 요청<br/>requestTssCopinoVerify<br/>docKey, truckNo, conNo]

    FF --> GG[프로세스 완료]

    style A fill:#e1f5fe

    style D fill:#fff3e0

    style G fill:#fce4ec

    style FF fill:#e8f5e8

    style GG fill:#f3e5f5
```
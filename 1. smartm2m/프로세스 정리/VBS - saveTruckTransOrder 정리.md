
# saveTruckTransOrder 함수 플로우차트

  

  
```
graph TD
    START[📋 saveTruckTransOrder 시작] --> EXTRACT[🔍 오류 상태 추출<br/>ContainerTransportErrorStatus]
    EXTRACT --> INIT[⚙️ 변수 초기화<br/>isNeedFcmSend = true<br/>pinNo, terminalCode, documentKey]
    INIT --> GET_EXISTED[📊 기존 COPINO 데이터 조회<br/>existedCopinoData]
    GET_EXISTED --> BLOCKCHAIN[🔗 블록체인 COPINO 조회<br/>blockChainRequestGetCopino]
    
    BLOCKCHAIN --> VALID_RESULT{✅ 블록체인 결과<br/>유효성 체크<br/>isAvaliableResult?}
    VALID_RESULT -->|❌ No| FAIL1[❌ 로그 출력<br/>return false]
    
    VALID_RESULT -->|✅ Yes| VALID_COPINO{✅ COPINO 데이터<br/>유효성 체크<br/>isAvaliableCopinoData?}
    VALID_COPINO -->|❌ No| FAIL1
    
    VALID_COPINO -->|✅ Yes| EXTRACT_DATA[📋 데이터 추출<br/>copino, appointment, info]
    EXTRACT_DATA --> NEED_SAVE{💾 COPINO 저장 필요?<br/>isNeedSaveCopino}
    NEED_SAVE -->|❌ No| FAIL2[❌ return false]
    
    NEED_SAVE -->|✅ Yes| EXTRACT_STATUS[📝 상태 및 트럭번호 추출<br/>newCopinoDocStatus<br/>truckNo]
    EXTRACT_STATUS --> EXIST_CHECK{🔍 기존 COPINO<br/>데이터 존재?}
    
    %% 기존 데이터가 있는 경우
    EXIST_CHECK -->|✅ 있음| CHECK_STATUS[📊 기존 상태 체크<br/>isExistedOrderGateIn<br/>isExistedOrderError<br/>isCopinoLogicError]
    CHECK_STATUS --> CALC_TIME[⏰ 삭제 가능 시간 계산<br/>canUpdateRemoveCopinoTime]
    CALC_TIME --> GET_TRANSPORT[🚛 기존 운송 데이터 조회<br/>existedContainerTransport]
    
    GET_TRANSPORT --> GATE_CHECK{🚪 GATE OUT 또는<br/>CANCEL INOUT?}
    GATE_CHECK -->|✅ Yes| UPDATE1[🔄 운송 데이터 업데이트<br/>updateContainerTransport]
    UPDATE1 --> FCM_CHECK1[📱 FCM 전송 필요성 체크<br/>isNeedFcmSend = !equals]
    FCM_CHECK1 --> POPUP1[🔔 팝업 데이터 처리<br/>saveNewAllconeShowPopup]
    
    GATE_CHECK -->|❌ No| LOGIC_CHECK{🔍 Gate In & Logic Error &<br/>기존오류 아님?}
    LOGIC_CHECK -->|✅ Yes| NO_PROCESS[⏸️ 아무 처리 안함]
    
    LOGIC_CHECK -->|❌ No| DELETE_CHECK{🗑️ COPINO 삭제 상태 &<br/>삭제 불가능?}
    DELETE_CHECK -->|✅ Yes| FAIL3[❌ return false]
    
    DELETE_CHECK -->|❌ No| CHECK_GENERAL1[🔍 일반 컨테이너/트럭 정보 체크<br/>checkGeneralContainerAndTrucker]
    CHECK_GENERAL1 --> DGT_CHECK{🏢 DGT신항 EMPTY OUT<br/>특수 조건?}
    
    DGT_CHECK -->|✅ Yes| DGT_UPDATE[🔄 DGT EMPTY OUT 업데이트<br/>updateDgtEmptyOutContainerTransport<br/>isNeedFcmSend = false]
    DGT_CHECK -->|❌ No| NORMAL_UPDATE[🔄 일반 운송 데이터 업데이트<br/>updateContainerTransport<br/>FCM 전송 필요성 체크]
    
    DGT_UPDATE --> POPUP2[🔔 팝업 데이터 처리<br/>saveNewAllconeShowPopup]
    NORMAL_UPDATE --> POPUP2
    
    %% 기존 데이터가 없는 경우 (신규)
    EXIST_CHECK -->|❌ 없음| NEW_DELETE_CHECK{🗑️ COPINO 삭제 상태?<br/>COPINO_DELETED}
    NEW_DELETE_CHECK -->|✅ Yes| NO_PROCESS2[⏸️ 아무 처리 안함]
    NEW_DELETE_CHECK -->|❌ No| CHECK_GENERAL2[🔍 일반 컨테이너/트럭 정보 체크<br/>checkGeneralContainerAndTrucker]
    CHECK_GENERAL2 --> CREATE[✨ 운송 데이터 생성<br/>createContainerTransportData]
    CREATE --> POPUP3[🔔 팝업 데이터 처리<br/>saveNewAllconeShowPopup]
    
    %% 후처리 - 동일 트럭번호 체크
    POPUP1 --> TRUCK_CHECK{🚛 동일 트럭번호<br/>기존 데이터 존재?}
    NO_PROCESS --> TRUCK_CHECK
    POPUP2 --> TRUCK_CHECK
    NO_PROCESS2 --> TRUCK_CHECK
    POPUP3 --> TRUCK_CHECK
    
    TRUCK_CHECK -->|❌ No| SUCCESS[✅ return isNeedFcmSend]
    TRUCK_CHECK -->|✅ Yes| SPLIT_PIN[📝 pinNo 분할<br/>containerNumber, inOutType 추출]
    SPLIT_PIN --> GET_EXPIRED[🔍 만료된 데이터 조회<br/>getAllconeTransportOrderDataForCheckExpired]
    GET_EXPIRED --> EXPIRED_CHECK{🔍 만료된 데이터가<br/>현재와 다르고<br/>예약 완료 상태?}
    
    EXPIRED_CHECK -->|❌ No| SUCCESS
    EXPIRED_CHECK -->|✅ Yes| CREATE_CANCEL[📋 예약 취소 파라미터 생성<br/>cancelParam]
    CREATE_CANCEL --> CANCEL[❌ 예약 취소 실행<br/>cancelAppointment]
    CANCEL --> SUCCESS
    
    %% 예외 처리
    BLOCKCHAIN -.->|💥 Exception| EXCEPTION[❌ 예외 로그 출력<br/>return false]
    FAIL3 --> FAIL_FINAL[❌ return false]
    
    %% 스타일링
    classDef startEnd fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef success fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
    classDef fail fill:#ffebee,stroke:#d32f2f,stroke-width:3px
    
    class START startEnd
    class SUCCESS success
    class FAIL1,FAIL2,FAIL3,FAIL_FINAL,EXCEPTION fail
    class VALID_RESULT,VALID_COPINO,NEED_SAVE,EXIST_CHECK,GATE_CHECK,LOGIC_CHECK,DELETE_CHECK,DGT_CHECK,NEW_DELETE_CHECK,TRUCK_CHECK,EXPIRED_CHECK decision
```
---

  

- 각 분기에서 조건에 따라 함수가 종료되거나, 다음 단계로 넘어갑니다.

- 예외 발생 시에는 에러 로그를 남기고 false를 반환하며 종료됩니다.
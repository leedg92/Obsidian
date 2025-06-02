# saveTruckTransOrder 프로세스 플로우

```mermaid
graph TD
    START[📋 트럭 운송 주문 저장 요청] --> VALIDATE[🔍 블록체인에서 COPINO 정보 조회 및 검증]
    
    VALIDATE --> VALID_CHECK{✅ 유효한 데이터?}
    VALID_CHECK -->|❌ No| FAIL[❌ 처리 실패]
    
    VALID_CHECK -->|✅ Yes| NEED_SAVE{💾 저장이 필요한 데이터?}
    NEED_SAVE -->|❌ No| SKIP[⏸️ 저장 생략]
    
    NEED_SAVE -->|✅ Yes| EXIST_CHECK{🔍 기존 운송 주문 존재?}
    
    %% 기존 주문이 있는 경우
    EXIST_CHECK -->|✅ 있음| STATUS_CHECK{📊 현재 상태는?}
    
    STATUS_CHECK -->|🚪 GATE OUT/CANCEL| UPDATE_FINAL[🔄 최종 상태 업데이트]
    
    STATUS_CHECK -->|🚛 운송 중| CONDITION_CHECK{🔍 업데이트 조건 확인}
    CONDITION_CHECK -->|❌ 조건 불만족| NO_UPDATE[⏸️ 업데이트 하지 않음]
    CONDITION_CHECK -->|✅ 조건 만족| SPECIAL_CHECK{🏢 특수 처리 대상?}
    
    SPECIAL_CHECK -->|✅ DGT신항 EMPTY OUT| SPECIAL_UPDATE[🔄 특수 업데이트]
    SPECIAL_CHECK -->|❌ 일반| NORMAL_UPDATE[🔄 일반 업데이트]
    
    %% 새로운 주문인 경우
    EXIST_CHECK -->|❌ 없음| DELETE_CHECK{🗑️ 삭제된 COPINO?}
    DELETE_CHECK -->|✅ Yes| NO_CREATE[⏸️ 생성하지 않음]
    DELETE_CHECK -->|❌ No| CREATE[✨ 새로운 운송 주문 생성]
    
    %% 후처리
    UPDATE_FINAL --> POST_PROCESS[📱 알림 및 팝업 처리]
    SPECIAL_UPDATE --> POST_PROCESS
    NORMAL_UPDATE --> POST_PROCESS
    CREATE --> POST_PROCESS
    
    POST_PROCESS --> TRUCK_CHECK{🚛 동일 트럭번호로<br/>기존 예약 있음?}
    
    TRUCK_CHECK -->|❌ No| SUCCESS[✅ 처리 완료]
    TRUCK_CHECK -->|✅ Yes| CANCEL_OLD[❌ 기존 예약 취소]
    CANCEL_OLD --> SUCCESS
    
    NO_UPDATE --> SUCCESS
    NO_CREATE --> SUCCESS
    SKIP --> SUCCESS
    
    %% 스타일링
    classDef startEnd fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef success fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
    classDef fail fill:#ffebee,stroke:#d32f2f,stroke-width:3px
    classDef skip fill:#f5f5f5,stroke:#757575,stroke-width:2px
    
    class START startEnd
    class SUCCESS success
    class FAIL fail
    class SKIP,NO_UPDATE,NO_CREATE skip
    class VALID_CHECK,NEED_SAVE,EXIST_CHECK,STATUS_CHECK,CONDITION_CHECK,SPECIAL_CHECK,DELETE_CHECK,TRUCK_CHECK decision
```

## 주요 프로세스 단계

### 1️⃣ 검증 단계

- 블록체인에서 COPINO 정보 조회
- 데이터 유효성 및 저장 필요성 검증

### 2️⃣ 메인 처리 (분기)

**기존 주문이 있는 경우:**

- 현재 상태 확인 (GATE OUT/CANCEL vs 운송 중)
- 업데이트 조건 확인
- 특수 처리 대상 여부 확인 (DGT신항 EMPTY OUT)
- [[컨테이너 운송 업데이트(DGT)]]
- [[컨테이너 운송 업데이트(etc)]]

**신규 주문인 경우:**

- [[삭제된 COPINO가 아니면 새로운 운송 주문 생성]]

### 3️⃣ 후처리

- 알림 및 팝업 처리
- 동일 트럭번호로 기존 예약이 있으면 취소

### 📋 주요 분기점

- **데이터 유효성**: 블록체인 조회 결과 검증
- **저장 필요성**: 중복 데이터인지 확인
- **기존 주문 존재**: 업데이트 vs 신규 생성
- **현재 상태**: 최종 단계 vs 진행 중
- **특수 조건**: DGT신항 EMPTY OUT 처리
- **트럭번호 중복**: 기존 예약 취소 필요성

네, 인터널게이트 사용을 위한 **모든 조건**을 종합해서 정리해드리겠습니다.

## 🚪 인터널게이트 사용 조건 종합

### 1️⃣ **데이터베이스 설정 조건** (필수)
```sql
-- allcone_terminal_trucker_internal_gate_config 테이블에 레코드 존재
선사코드 = MSC
트럭커ID = CITLC051  
OUT터미널 = PNCOC010
IN터미널 = PNITC050
TERMINAL_USE_INTERNAL_GATE = 'TML_CONFIG_ACT'
```

### 2️⃣ **비즈니스 로직 조건** (checkCanUseInternalGateOrder)
```java
✅ terminalInternalGateConfig != null              // DB 설정 존재
✅ transOrderData.getOutTerminalCode().equals(latestTerminal)  // 현재 터미널과 일치
✅ 트럭커ID 일치
✅ 선사코드 일치  
✅ OUT터미널 코드 일치
✅ IN터미널 코드 일치
```

### 3️⃣ **컨테이너 타입별 허용 조건**
| 서비스 타입  | 컨테이너 크기 | 설정 필드                   | 예시 데이터 |
| ------- | ------- | ----------------------- | ------ |
| **VBS** | 20ft    | `edi20FtYN = 1`         | ✅ (1)  |
| **VBS** | 40ft    | `edi40FtYN = 1`         | ✅ (1)  |
| **VBS** | 20ft 결합 | `edi20FtCombinedYN = 1` | ✅ (1)  |
| **TSS** | 20ft    | `tss20FtYN = 1`         | ✅ (1)  |
| **TSS** | 40ft    | `tss40FtYN = 1`         | ✅ (1)  |
| **TSS** | 20ft 결합 | `tss20FtCombinedYN = 1` | ✅ (1)  |

### 4️⃣ **OOG 컨테이너 제외 조건**
```java
❌ 과치수 컨테이너는 인터널게이트 사용 불가
- overLength != "0" && !isEmpty
- overWidth != "0" && !isEmpty  
- overHeight != "0" && !isEmpty
```

### 5️⃣ **작업 완료 조건**
```java
✅ 모든 VBS 슬립의 jobDoneDateTime != null
✅ 모든 OUT TSS 슬립의 loadDateTime != null
✅ 모든 IN TSS 슬립의 unLoadDateTime != null
✅ IN Order가 아직 Gate In 하지 않음 (!isInOrderGateIn)
```

### 6️⃣ **20ft 결합 운송 특별 조건**
```java
if (20ft 컨테이너 >= 2개) {
    ✅ edi20FtCombinedYN = 1 (VBS의 경우)
    ✅ tss20FtCombinedYN = 1 (TSS의 경우)
}
```

## 🎯 **실제 사용 가능한 케이스 (예시 데이터 기준)**

### ✅ **사용 가능**
```
선사: MSC
운송사: CITLC051
터미널: PNCOC010 → PNITC050 (또는 역방향)
컨테이너: [TSS,VBS] 20ft, 40ft, 20ft 결합
조건: 모든 작업 완료 + 과치수 아님
```

### ❌ **사용 불가능**
```
1. EDI 서비스 (VBS) 컨테이너
2. 과치수(OOG) 컨테이너  
3. 작업 미완료 상태
4. 다른 선사/트럭커 조합
5. 설정되지 않은 터미널 조합
```

**결론**: 총 **15개 이상의 조건**이 모두 만족되어야 인터널게이트를 사용할 수 있습니다! 🚛✨
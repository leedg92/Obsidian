
### 공통 시작 변수선언

```
        Map<String, Object> param = new HashMap<>(message);
        String now = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        int transStatus = 10;
        boolean isUpdateIgnored = false;
        IttTransStatus ittTransStatus = IttTransStatus.READY;
```

### GateIn
1. docKey로 기존 운송 오더가 있는지 조회 => tssTruckTransOrder
	- bctransdbx.tb_b_truck_trans_odr
2. 블록체인으로 GetCopino 요청 => copinoResult
3. (코피노 검증 성공 == copinoResult not empty)
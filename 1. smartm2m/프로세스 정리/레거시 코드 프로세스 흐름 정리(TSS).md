
### 공통 시작 변수선언

```
        Map<String, Object> param = new HashMap<>(message);
        String now = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        int transStatus = 10;
        boolean isUpdateIgnored = false;
        IttTransStatus ittTransStatus = IttTransStatus.READY;
```

### GateIn
1. \[tssTruckTransOrder\] <- docKey로 기존 운송 오더가 있는지 조회
	- bctransdbx.tb_b_truck_trans_odr
2. \[copinoResult\] <- 블록체인으로 GetCopino 요청
3. (if copinoResult not empty) Ktnet으로 데이터 전송 + 결과 데이터 저장
	- 데이터 저장 : general_container
4. \[param\] <- 배차일시, 상태값 세팅(배차일시 없으면 현재날짜로)
5. \[param\] <- 컨테이너 무게 Integer로 변경
6. (기존 운송오더 존쟇)
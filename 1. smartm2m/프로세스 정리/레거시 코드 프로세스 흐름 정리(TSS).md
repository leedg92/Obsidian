
### 공통 시작 변수선언

```
        Map<String, Object> param = new HashMap<>(message);
        String now = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        int transStatus = 10;
        boolean isUpdateIgnored = false;
        IttTransStatus ittTransStatus = IttTransStatus.READY;
```

### CreateCopino
1.  <b style="color:yellow;">[tssTruckTransOrder]</b> <- docKey로 기존 운송 오더가 있는지 조회
	- `bctransdbx.tb_b_truck_trans_odr`
2. <b style="color:yellow;">[copinoResult]</b> <- 블록체인으로 GetCopino 요청
3. <u style="color:red;">코피노검증 결과 존재[copinoResult] ? </u>
	- <u style="color:red;">Y</u> :
		- Ktnet으로 데이터 전송 + 결과 데이터 저장
			- 데이터 저장 : `general_container`
4. <b style="color:yellow;">[param]</b> <- 배차일시, 상태값 세팅 (배차일시 없으면 현재날짜로)
5. <b style="color:yellow;">[param]</b> <- 컨테이너 무게 Integer로 변경
6. <b style="color:yellow;">[param]</b> <- error 메세지 파싱(Y or N)
7. <u style="color:red;">기존 운송 오더 존재[tssTuckTransOrder] ? </u>
	- <u style="color:red;">Y</u> : <u style="color:green;">반출/반입 취소시간 존재 ? </u>
		- <u style="color:green;">Y</u> :  취소 오더 갱신
			- `bctransdbx.tb_b_truck_trans_odr`
		- <u style="color:green;">N</u> : 오더 갱신
			- `bctransdbx.tb_b_truck_trans_odr`
	- <u style="color:red;">N</u> :
		1. 컨테이너 정보 체크 + 갱신
			-  데이터 갱신 : `general_container`(param)
		2. 운송사 정보 체크 (운송사 정보 없을 시 삽입)
			- 데이터 삽입 : `general_trucker`(param)
		3. 신규 오더 생성
			- `container_transport_vbs_status`(param)
			- `tb_b_truck_trans_odr`(param)
8. 운송오더 갱신
	- tb_b_trans_trucks(param)
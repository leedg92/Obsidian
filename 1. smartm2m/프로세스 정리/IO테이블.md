
## createNewCopinoData
### 1. containerTransportMapper.saveNewContainerTransport(containerTransport)
- 테이블: bctransdbx.container_transport (컨테이너 운송)
- 설명: 컨테이너 운송 기본 정보 저장

---
### 2. containerTransportVbsMapper.saveNewContainerTransportVbs(containerTransportVbs)
- 테이블: bctransdbx.container_transport_vbs (vbs 운송 예약관련(?))
- 설명: VBS(예약) 관련 정보 저장

---
### 3. containerTransportSummaryMapper.saveContainerTransportSummary(containerTransportSummary)
- 테이블: bctransdbx.container_transport_summary (컨테이너 운송건 요약 정보)
- 설명: 운송 요약 정보 저장 (게이트 인/아웃, 작업 완료 등)

---
### 4. containerTransportDigitalGateMapper.saveContainerTransportDigitalGate(containerTransportDigitalGate)
- 테이블: bctransdbx.container_transport_digital_gate (컨테이너 운송 디지털 게이트(?))
- 설명: 디지털게이트 사용 여부 등 관련 정보 저장

---
### 5. containerRfPowerStatusMapper.saveNewContainerRfPowerStatus(containerRfPowerStatus)
- 테이블: bctransdbx.container_rf_power_status (냉동컨테이너 전원 변경 상태)
- 설명: 냉동 컨테이너 전원 상태(RF Power Status) 관련 정보 저장



# !!! TRANSPORT_CODE가 KEY임
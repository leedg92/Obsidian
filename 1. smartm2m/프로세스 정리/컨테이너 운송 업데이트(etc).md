### 1. containerTransportMapper.updateContainerTransport / updateContainerTransportWithPinNo

- 테이블: bctransdbx.container_transport (컨테이너 운송)
- 설명: 컨테이너 운송 기본 정보 갱신

---

### 2.containerTransportSummaryMapper.updateContainerTransportSummary

- 테이블: bctransdbx.container_transport_summary (컨테이너 운송건 요약 정보)
- 설명: 운송 요약 정보 갱신 (게이트 인/아웃, 작업 완료 등)

---

### 3. containerRfPowerStatusMapper.saveNewContainerRfPowerStatus

- 테이블: bctransdbx.container_rf_power_status (냉동컨테이너 전원 변경 상태)
- 설명: 냉동 컨테이너 전원 상태(RF Power Status) 관련 정보 저장 (insert/update)
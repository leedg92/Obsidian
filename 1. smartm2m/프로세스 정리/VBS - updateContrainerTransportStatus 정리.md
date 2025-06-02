
#### 1. container_transport (컨테이너 운송)

- 테이블: bctransdbx.container_transport
- 설명: 컨테이너 번호, 트럭번호 등 운송 기본 정보 update (터미널 이벤트에 따라 변경)

---

#### 2. container_transport_status (운송 상태 이력)

- 테이블: bctransdbx.container_transport_status
- 설명: 운송 상태 이력 insert (GATE IN, BLOCK IN, JOB DONE, GATE OUT 등 터미널 이벤트별 상태 기록)

---

#### 3. container_transport_status_ex_data (상태 부가정보, 상황에 따라)

- 테이블: bctransdbx.container_transport_status_ex_data
- 설명: 운송 상태 부가정보 insert (상황에 따라, 예: 추가 메시지, 위치 등)

---

#### 4. container_transport_summary (운송 요약)

- 테이블: bctransdbx.container_transport_summary
- 설명: 운송 요약 정보 update (게이트 인/아웃, 작업 완료 등 상태 변화에 따라)
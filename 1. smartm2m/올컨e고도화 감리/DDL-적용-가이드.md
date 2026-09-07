# DDL 적용 가이드 (최초 2026-08-03 · 최종 갱신 2026-08-19)

> 🔴 **2026-08-19 사용자 확인 — 운영망은 현재 배포 스냅샷 기준 전부 적용되어 있다.**
> 아래 「적용 현황」 표의 운영망 칸(❌·❓)은 이 확인 이전에 쓴 것이라 **더 이상 맞지 않는다.**
> 🔴 **2026-09-01 재정정 — 앞으로 운영망에 실행할 것은 3건이다.**
> 약관 2건(`create_allcone_terms_tables.sql` → **`migrate_allcone_terms_agreement_v1.sql`**) ·
> `add_tss_movement_interface_code.sql`(판단 대기).
> - **이관 쿼리는 반드시 실행한다.** 빼면 기존 회원의 v1 동의 이력이 생성되지 않는다.
>   선행 순서는 create → 관제 5종 등록(`/terms/sync`) → 이관. 순서를 어기면 이관 대상이 비어 버린다
> - **터미널 담당자 연락처는 감리용(GR 브랜치)이라 운영망 대상이 아니다.** 종전 "4건"에 잘못 들어가 있었다.
> 항목별 절차·검증 쿼리·롤백은 이 문서가 계속 SoT다.


사용자가 직접 실행하는 DDL의 실행 순서·사전 확인·검증 쿼리를 한 곳에 모은 문서.
파일 원본은 전부 `src/main/resources/db/migration/` 아래에 있다.
운영망 실행용 통합 스크립트는 리포 루트 `배포전-DDL-2026-08-03.sql` (파일명만 08-03, 내용은 이 문서와 함께 갱신된다).

**적용 대상 망**: 개발망(`133.186.222.171:23306`) → 검증 후 운영망.
**원칙**: 실행 전 반드시 사전 확인 쿼리로 현재 상태를 보고, 이미 적용된 건은 건너뛴다.

## 배포 회차 (2026-08-12 확정)

| 회차 | 시점 | 대상 | 필요 DDL |
|---|---|---|---|
| **1차** | **2026-08-13** | 지오펜스 통보·HPNT(CHENH-128) / 주간보고(CHMAN-140) / 회원집계(CHMAN-141·171) / 차상세척(CHENH-95) / 지오펜스 필터·배치(CHENH-109) / 그룹오더(CHENH-82) | 🔴 **별도 파일 `배포DDL-1차-2026-08-13.sql`** |
| **2차** | 08-17 주 | 팝업 우선순위 / 블록 인덱스 / 약관(CHENH-87) | `배포전-DDL-2026-08-03.sql` STEP 1·4·9 |
| 제외 | — | 감리용 3건 — 취소(CHENH-102)·혼잡도(CHENH-88)·연락처(CHENH-125) | **적용하지 않는다** |

🔴 **1차 배포분은 이 문서의 항목별 절차와 별개로 `배포DDL-1차-2026-08-13.sql` 하나로 끝난다.**
그 파일은 자기완결형(원본 참조 없이 그대로 실행 가능)이고, 아래 §2·§3의 차상세척 2건과 지오펜스 관련 DDL이 이미 그 안에 들어가 있다.
1차 적용이 끝나면 아래 표의 해당 항목은 "운영망 적용됨"으로 갱신할 것.

→ 아래 §4(혼잡도)는 감리용이므로 **운영망 적용 대상이 아니다**. 개발망에만 넣는다.

> **개발망 실측 완료 (2026-08-03)** — 아래 각 항목의 "개발망" 표기는 실제 조회 결과다. 운영망은 전부 미확인.

---

## 0. 실행 전 공통 확인

### 0-1. DB 종류·버전

```sql
SELECT VERSION();
```

**개발망 실측: `10.5.9-MariaDB`** → `ADD COLUMN IF NOT EXISTS` / `DROP COLUMN IF EXISTS` 사용 가능. 1번 항목을 재실행 안전한 형태로 쓸 수 있다.
운영망도 MariaDB인지는 실행 전 확인할 것. MySQL이면 `IF NOT EXISTS`가 파싱 에러다.

### 0-2. 접속 계정 권한

```sql
SHOW GRANTS FOR CURRENT_USER();
```

**개발망 실측: `GRANT ALL PRIVILEGES ON *.* TO smartm2m@%`** → 크로스 DB(`chainportaldb`) 쓰기 포함 전부 가능. 개발망에서는 권한 이슈 없음.
**운영망은 반드시 별도 확인** — 운영 계정이 `chainportaldb`에 SELECT만 갖고 있으면 공지팝업 INSERT가 런타임에 터진다.

---

## 1. `alter_popup_manage_add_priority.sql` — 2차 배포분

| 항목 | 값 |
|---|---|
| 대상 | `chainportaldb.tb_a_popup_manage_i` |
| 관련 | 관제 메인 공지팝업 BPABCTRANS-159 / CHMAN-138 |
| 긴급도 | **보통** — 2026-08-12 하향 조정 (아래 참조) |
| 재실행 안전 | MariaDB면 `IF NOT EXISTS`로 안전. MySQL이면 ❌ (`Duplicate column name`) |
| **개발망** | ✅ **적용 완료** (`int(11) NOT NULL DEFAULT 1`, 코멘트까지 일치) |
| **운영망** | ❌ 미적용 (추정, 미확인) |

**2026-08-12 긴급도 정정** — 예전에는 "안 하면 기존 앱 팝업 조회 전체가 장애"인 최우선 항목이었다. `bf7322206`(이미 운영 배포됨)에서 앱 조회 정렬을 `POPUP_PRIORITY` → `POPUP_BGNDE`로 원복해 **컬럼이 없어도 `GET /mobile/popup/list`가 정상 동작한다**.

남은 참조는 `PopupMapper.xml`의 등록/수정 쿼리뿐이므로, **관제 연계 API(`POST /popup/notice`)를 켜는 시점에 필요**하다. 멱등이라 2차 배포 때 같이 넣어둔다.

### 사전 확인

```sql
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
  FROM information_schema.COLUMNS
 WHERE TABLE_SCHEMA = 'chainportaldb'
   AND TABLE_NAME   = 'tb_a_popup_manage_i'
   AND COLUMN_NAME  = 'POPUP_PRIORITY';
```

결과가 **0행이면 미적용** → 아래 실행. 1행이면 이미 적용됨 → 건너뛴다.

### 실행

MariaDB (개발망·운영망이 MariaDB인 경우):

```sql
ALTER TABLE chainportaldb.tb_a_popup_manage_i
    ADD COLUMN IF NOT EXISTS `POPUP_PRIORITY` int(11) NOT NULL DEFAULT 1 COMMENT '팝업우선순위(작을수록 상위)';
```

MySQL이면 `IF NOT EXISTS`를 빼고 실행(사전 확인 쿼리 필수):

```sql
ALTER TABLE chainportaldb.tb_a_popup_manage_i
    ADD COLUMN `POPUP_PRIORITY` int(11) NOT NULL DEFAULT 1 COMMENT '팝업우선순위(작을수록 상위)';
```

기존 행은 전부 `1`로 채워진다.

### 실행 후 검증

```sql
SELECT POPUP_ID, POPUP_PRIORITY, USE_AT, SYS_ID, FST_REGR_ID
  FROM chainportaldb.tb_a_popup_manage_i
 ORDER BY POPUP_PRIORITY, IFNULL(LST_UPD_DTM, FST_REG_DTM) DESC, POPUP_ID DESC
 LIMIT 20;
```

정렬 규칙이 바뀌었으므로(`POPUP_BGNDE` → `POPUP_PRIORITY, 수정일시 desc, POPUP_ID desc`) **기존 포털 등록 팝업의 앱 노출 순서도 함께 바뀐다.** 위 쿼리 결과가 실제로 앱에 보여도 되는 순서인지 확인할 것.

**개발망 실측**: 전 행이 `POPUP_PRIORITY=1`, `FST_REGR_ID='ADMIN'`, `SYS_ID='09'`. 우선순위가 모두 같으므로 실제 순서는 **수정일시 desc → POPUP_ID desc** 로만 갈린다. 관제 등록건(`FST_REGR_ID='CONTROL'`)이 들어오기 전까지는 우선순위가 순서를 흔들지 않는다.

`USE_APP_VER`가 `NULL`인 행이 섞여 있다(예: POPUP_ID 455). 조회 조건이 `USE_APP_VER='2'` 문자열 일치라 이런 행은 애초에 앱에 안 나온다 — 정렬 변경과 무관.

⚠️ **`POPUP_TY` 분포가 기존 기록과 다르다.** 개발망 실측은 `T`=132 / `I`=42 / **`Y`=9** / `NULL`=1. "실데이터 전수 T"로 알고 있던 것과 어긋난다. 조회 로직이 `POPUP_TY='I'`만 이미지로 보고 나머지를 HTML로 처리하므로 `Y`·`NULL`도 HTML로 흘러간다 — 동작은 하되 의도된 값인지 확인이 필요하다.

### 함께 확인해야 할 것 — 크로스 DB 쓰기 권한

관제 공지팝업은 bctrans가 `chainportaldb`에 **INSERT/UPDATE** 한다. 지금까지는 SELECT만 하던 접근이라 권한이 없으면 런타임에 터진다.

```sql
-- application.yml 의 mainDataSource 계정으로 접속해서 실행
SHOW GRANTS FOR CURRENT_USER();
```

`chainportaldb.*` 또는 `chainportaldb.tb_a_popup_manage_i`에 INSERT·UPDATE가 있는지 확인.

**개발망 실측**: `GRANT ALL PRIVILEGES ON *.*` → 이상 없음. **운영망 미확인.**

### 롤백

```sql
ALTER TABLE chainportaldb.tb_a_popup_manage_i DROP COLUMN `POPUP_PRIORITY`;
```

⚠️ 코드가 이미 develop에 있으므로, 롤백하면 팝업 조회가 즉시 깨진다. 코드 되돌림과 세트로만 의미 있다.

---

## 2. `create_allcone_terminal_interface_operating_hour.sql`

| 항목 | 값 |
|---|---|
| 대상 | `bctransdbx.allcone_terminal_interface_operating_hour` (신규) |
| 관련 | 차상세척 운영시간 차단 BPABCTRANS-275 |
| 긴급도 | 275 브랜치 머지 전까지는 여유 |
| 재실행 안전 | ✅ (`CREATE TABLE IF NOT EXISTS` + `ON DUPLICATE KEY UPDATE`) |
| **개발망** | ✅ **적용 완료 (2026-08-03 재실행·검증). 8행 전부 기대값 일치** |
| **운영망** | ❌ 미적용 |

> 08-03 오전 첫 실행은 **테이블이 생성되지 않은 채로 끝나 있었다**(오후 확인 시 `information_schema`에 없음). 재실행으로 정상 적용.

초기 데이터 INSERT 8행(HPNT/PNIT × 평일·토·일·공휴일)이 파일에 포함돼 있다.

⚠️ 한글 컬럼값(`SERVICE_NAME='세척장'`)이 있으므로 실행 시 **`--default-character-set=utf8mb4` 필수**.

### 사전 확인

```sql
SELECT TABLE_NAME FROM information_schema.TABLES
 WHERE TABLE_SCHEMA = 'bctransdbx'
   AND TABLE_NAME   = 'allcone_terminal_interface_operating_hour';
```

### 실행

```bash
mysql -h 133.186.222.171 -P 23306 -u smartm2m -p bctransdbx \
  < src/main/resources/db/migration/create_allcone_terminal_interface_operating_hour.sql
```

### 실행 후 검증

```sql
SELECT TERMINAL_CODE, INTERFACE_CODE_ID, DAY_TYPE, SERVICE_NAME,
       AVAILABLE_YN, OPER_ST_TM, OPER_ED_TM, REQ_DEADLINE_TM
  FROM bctransdbx.allcone_terminal_interface_operating_hour
 ORDER BY TERMINAL_CODE, FIELD(DAY_TYPE,'WEEKDAY','SATURDAY','SUNDAY','HOLIDAY');
```

기대값 8행:

| TERMINAL_CODE | DAY_TYPE | AVAILABLE_YN | OPER_ST_TM | REQ_DEADLINE_TM |
|---|---|---|---|---|
| HPNTC050 | WEEKDAY | Y | 08:30 | 16:55 |
| HPNTC050 | SATURDAY | Y | 08:30 | 14:55 |
| HPNTC050 | SUNDAY | N | NULL | NULL |
| HPNTC050 | HOLIDAY | N | NULL | NULL |
| PNITC050 | WEEKDAY | Y | 09:00 | 17:15 |
| PNITC050 | SATURDAY | Y | 09:00 | 12:05 |
| PNITC050 | SUNDAY | N | NULL | NULL |
| PNITC050 | HOLIDAY | N | NULL | NULL |

### 정합성 확인 — 대상 터미널이 이 둘뿐인지

```sql
SELECT TERMINAL_CODE, INTERFACE_CODE_ID
  FROM bctransdbx.terminal_interface
 WHERE INTERFACE_CODE_ID = 'REQ_CONTAINER_WASH';
```

HPNTC050·PNITC050 외에 다른 터미널이 나오면 그 터미널은 **운영시간 제한 없음(항상 가능)** 으로 동작한다. 이 테이블은 "막을 것만" 등록하는 구조이기 때문. 의도한 것인지 확인.

**개발망 실측**: `HPNTC050`·`PNITC050` 2건뿐 → 초기 데이터 8행이 대상 전체를 덮는다. 누락 없음.

### 롤백

```sql
DROP TABLE bctransdbx.allcone_terminal_interface_operating_hour;
```

---

## 3. `create_allcone_holiday.sql`

| 항목 | 값 |
|---|---|
| 대상 | `bctransdbx.allcone_holiday` (신규) |
| 관련 | 차상세척 운영시간 차단 BPABCTRANS-275 |
| 긴급도 | 2번과 동일. **2번과 세트로 적용** |
| 재실행 안전 | ✅ (`CREATE TABLE IF NOT EXISTS` + `ON DUPLICATE KEY UPDATE`) |
| **개발망** | ✅ **적용 완료 (2026-08-03 검증). 22행, 전부 `DATA_SOURCE=MANUAL`** |
| **운영망** | ❌ 미적용 |

**2026-08-03 변경**: 빈 테이블이 아니라 **2026년 공휴일 22행 INSERT를 파일에 포함**시켰다.
공공데이터포털 특일정보 `getRestDeInfo` 2026년 1~12월 응답 전량(`isHoliday='Y'`)이며, 노동절·지방선거일·제헌절도 사용자 판단으로 그대로 포함했다 — 이 3일은 차상세척이 종일 불가가 된다.
토요일과 겹치는 4일(06-06, 08-15, 09-26, 10-03)은 공휴일 우선 규칙에 따라 SATURDAY 가 아닌 HOLIDAY 설정을 탄다.

한글 컬럼값(`HOLIDAY_NAME`)이 있으므로 실행 시 **`--default-character-set=utf8mb4` 필수**.

### 실행 후 검증 (2026-08-03 실시 완료 — 22행 일치)

```sql
SELECT COUNT(*) FROM bctransdbx.allcone_holiday;   -- 기대 22행
SELECT HOLIDAY_DATE, HOLIDAY_NAME FROM bctransdbx.allcone_holiday ORDER BY HOLIDAY_DATE;
```

⚠️ 2단계 배치가 붙은 뒤로는 **당월 행의 `DATA_SOURCE` 가 `API` 로 바뀐다.** 배치는 당월 `API` 건만 맞추고
`MANUAL` 건은 건드리지 않으므로, 수동 등록분이 배치에 지워지는 일은 없다.

### 사전 확인

```sql
SELECT TABLE_NAME FROM information_schema.TABLES
 WHERE TABLE_SCHEMA = 'bctransdbx' AND TABLE_NAME = 'allcone_holiday';
```

### 실행

```bash
mysql -h 133.186.222.171 -P 23306 -u smartm2m -p bctransdbx \
  < src/main/resources/db/migration/create_allcone_holiday.sql
```

### 수동 등록 (2단계 배치 전까지)

공공데이터포털 배치가 붙기 전에는 아래처럼 직접 넣는다. 임시공휴일도 통상 2주~1개월 전에 확정되므로 이 방식으로 커버된다.

```sql
INSERT INTO bctransdbx.allcone_holiday (HOLIDAY_DATE, HOLIDAY_NAME) VALUES
  ('2026-08-15', '광복절'),
  ('2026-09-24', '추석 연휴'),
  ('2026-09-25', '추석'),
  ('2026-09-26', '추석 연휴'),
  ('2026-10-03', '개천절'),
  ('2026-10-09', '한글날'),
  ('2026-12-25', '기독탄신일');
```

⚠️ 위 날짜는 **미검증 예시**다. 실제 등록 전 공공데이터포털 특일정보 또는 관보로 확인할 것.

### 롤백

```sql
DROP TABLE bctransdbx.allcone_holiday;
```

---

## 4. `create_port_nearby_road.sql` + `create_port_nearby_road_congestion_cache.sql`

🔴 **2026-09-01 확인 — 이 두 파일은 `db/migration/` 에 없다.** 감리용 CHENH-88 이 미머지라
`feat/CHENH-88-nearby-road-congestion` 브랜치와 GR 에만 있다. 아래 `SOURCE` 경로는 그 브랜치를 체크아웃해야 유효하다.

| 항목 | 값 |
|---|---|
| 대상 | `bctransdbx.port_nearby_road`, `bctransdbx.port_nearby_road_congestion_cache` (둘 다 신규) |
| 관련 | 인근도로 혼잡도 CHENH-88 (설계 CHENH-94) |
| 긴급도 | 감리용이라 운영 배포 대상이 아니다 |
| 재실행 안전 | ✅ (`CREATE TABLE IF NOT EXISTS` + `ON DUPLICATE KEY UPDATE`) |
| **개발망** | ✅ **적용 완료 (2026-08-12)** — 마스터 5행, `PORT_CODE` 코드계 대조 완료(PUS 5 / BNP 8) |
| **운영망** | ⛔ **적용하지 않는다** — 감리용 3건에 속해 미머지 유지 |

두 파일은 **마스터 → 캐시 순서로** 실행한다(캐시가 `ROAD_ID`를 참조한다. FK는 걸지 않았으나 데이터 정합상 순서를 지킨다).

### 사전 확인

```sql
SELECT TABLE_NAME FROM information_schema.TABLES
 WHERE TABLE_SCHEMA = 'bctransdbx'
   AND TABLE_NAME IN ('port_nearby_road', 'port_nearby_road_congestion_cache');
-- 0행이면 미적용
```

### 실행

```
SOURCE src/main/resources/db/migration/create_port_nearby_road.sql;
SOURCE src/main/resources/db/migration/create_port_nearby_road_congestion_cache.sql;
```

### 실행 후 검증

```sql
SELECT ROAD_ID, ROAD_NAME, EXTERNAL_LINK_ID, PORT_CODE, PRIORITY, ACTIVE_YN
  FROM bctransdbx.port_nearby_road ORDER BY PRIORITY;
```

기대값 5행:

| ROAD_ID | ROAD_NAME | EXTERNAL_LINK_ID | PORT_CODE |
|---|---|---|---|
| TRF001 | 북항 진입로 | 충장대로 | PUS |
| TRF002 | 신선대 교차로 | 신선로 | PUS |
| TRF003 | 감만부두 입구 | 우암로 | PUS |
| TRF004 | 터미널 연결도로 | 북항로 | PUS |
| TRF005 | 신항 진입로 | 신항로 | BNP |

`PORT_CODE`는 설계서 예시(`BPNO/BPSO`)가 아니라 **`general_terminal.TERMINAL_PORT_CODE`의 실제 값**을 쓴다. 터미널 혼잡도에 도로 등급을 반영할 때 매핑 없이 대응시키기 위함이다(D012).

```sql
-- 코드계가 맞는지 확인 (PUS 5행 / BNP 8행이 나와야 한다)
SELECT TERMINAL_PORT_CODE, COUNT(*) FROM bctransdbx.general_terminal
 WHERE DATA_STATUS='DATA_ACTIVATED' GROUP BY TERMINAL_PORT_CODE;
```

`EXTERNAL_LINK_ID`는 ITS-GO **도로명**이다. 설계서는 이 컬럼에 linkId 를 넣도록 규정했으나 실제 API 에 linkId 조회가 없어 도로명 매칭으로 바꿨다(사유는 `.review-context/decisions.json` D001·D008).

배치가 한 사이클(5분) 돈 뒤 캐시 적재 확인:

```sql
SELECT c.ROAD_ID, r.ROAD_NAME, c.CONGESTION_LEVEL, c.AVG_SPEED, c.FETCHED_DTM
  FROM bctransdbx.port_nearby_road_congestion_cache c
  JOIN bctransdbx.port_nearby_road r ON r.ROAD_ID = c.ROAD_ID
 ORDER BY c.CACHE_ID DESC LIMIT 10;
```

### 함께 필요한 것 — DDL이 아닌 선행 조건

| 항목 | 내용 |
|---|---|
| 환경변수 | `ITS_API_SERVICE_KEY` (미설정이면 배치가 warn 만 남기고 스킵) |
| 방화벽 | `openapi.its.go.kr` **9443/tcp** 아웃바운드. 443이 아니라 별도 신청 대상 |

### 롤백

```sql
DROP TABLE IF EXISTS bctransdbx.port_nearby_road_congestion_cache;
DROP TABLE IF EXISTS bctransdbx.port_nearby_road;
```

---

## 5. 파일 없이 확인만 필요한 건

### 4-1. 🔴 운영망 인덱스 — 블록 대기차량 리스트 (BPABCTRANS-241)

없으면 조회가 **0.067초 → 32초**로 회귀한다. 개발망은 2026-07-30에 직접 추가함.

⚠️ **대상 테이블은 `container_transport`가 아니라 `container_transport_status`다.** (`cts` = **c**ontainer_**t**ransport_**s**tatus. 개발망 행수 144만)

```sql
SELECT TABLE_NAME, INDEX_NAME, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS COLS
  FROM information_schema.STATISTICS
 WHERE TABLE_SCHEMA = 'bctransdbx'
   AND TABLE_NAME   = 'container_transport_status'
 GROUP BY TABLE_NAME, INDEX_NAME;
```

**개발망 실측 — 관련 인덱스 3개 존재 ✅**

| INDEX_NAME | 컬럼 |
|---|---|
| `idx_cts_status_time` | `TRANSPORT_STATUS, TRANSPORT_STATUS_TIME` |
| `idx_cts_transcode_status_time` | `TRANSPORT_CODE, TRANSPORT_STATUS, TRANSPORT_STATUS_TIME` |
| `idx_cts_covering_transcode_status_eir_event_time` | `TRANSPORT_CODE, TRANSPORT_STATUS, EIR_SHOWN, TERMINAL_EVENT_FROM, TRANSPORT_STATUS_TIME` |

핵심은 `idx_cts_status_time`. **운영망에 없으면 아래로 추가**:

```sql
CREATE INDEX idx_cts_status_time
    ON bctransdbx.container_transport_status (TRANSPORT_STATUS, TRANSPORT_STATUS_TIME);
```

⚠️ 144만 행 테이블의 인덱스 생성이므로 **트래픽이 적은 시간대에 실행**할 것.

### 4-2. 운영망 `TRUCK_CODE` 컬럼 — 트럭코드 (BPABCTRANS-261)

```sql
SELECT COLUMN_NAME, COLUMN_TYPE
  FROM information_schema.COLUMNS
 WHERE TABLE_SCHEMA = 'bctransdbx'
   AND TABLE_NAME   = 'tb_b_truck_trans_odr'
   AND COLUMN_NAME  = 'TRUCK_CODE';
```

**개발망 실측: 존재 ✅ / 운영망 미확인.**

### 4-3. `create_allcone_geofence_notify_log.sql`

```sql
SELECT TABLE_NAME FROM information_schema.TABLES
 WHERE TABLE_SCHEMA = 'bctransdbx' AND TABLE_NAME = 'allcone_geofence_notify_log';
```

**개발망 실측: 존재 ✅** (생성 2026-07-16, 0행). **운영망 미확인.**

### 4-4. 🔴 `add_tss_movement_interface_code.sql` — 적용 추정이 틀렸다

"적용된 것으로 추정"으로 분류돼 있었으나 **개발망 실측 결과 미적용**이다. `general_code`·`terminal_interface` 양쪽 모두 0행.

```sql
SELECT CODE, CODE_CATEGORY, CODE_NAME FROM bctransdbx.general_code
 WHERE CODE = 'REQ_MISSING_MOVEMENT';

SELECT INTERFACE_CODE_ID, TERMINAL_CODE, INTERFACE_URL, DATA_STATUS
  FROM bctransdbx.terminal_interface
 WHERE INTERFACE_CODE_ID = 'REQ_MISSING_MOVEMENT';
```

TSS 무브먼트 보정(PNC 터미널 `REQ_MISSING_MOVEMENT` 인터페이스) 기능이 실제로 쓰이고 있다면 이 데이터가 없어 동작하지 않는다. **해당 기능의 배포·사용 여부를 먼저 확인**한 뒤 적용 여부를 판단할 것 — 안 쓰는 기능이면 넣지 않아도 된다.

이 파일은 `INSERT`만 있고 중복 가드가 없어 **재실행 시 PK 중복 에러**가 날 수 있다. 실행 전 위 확인 쿼리 필수.

### 4-5. `tss_group_order_container_pre_update_shp_vrf.sql`

**개발망 실측: 존재 ✅** (생성 2026-06-22, 0행). **운영망 미확인.**

---

## 6. `create_allcone_terms_tables.sql`

| 항목 | 값 |
|---|---|
| 대상 | `bctransdbx` 신설 3개 — `allcone_terms_type` / `allcone_terms_version` / `allcone_terms_agreement` |
| 관련 | 올컨e 약관 관리기능 CHENH-87 → **재설계 CHENH-133** |
| 개발망 | ✅ **적용 완료 (2026-08-12)** + **`CONTENT` 개명 ALTER 적용 (2026-08-21)**. 데이터 0행 |
| 운영망 | ❌ **미적용 — 배포 전 필수** |

기존 테이블을 건드리지 않는 순수 신설이라 적용 자체는 안전하다. 다만 **적용 순서에 제약이 있다.**

### 🔴 2026-08-21 — `CONTENT_HTML` → `CONTENT` 개명 (CHENH-133)

약관 본문 형식이 **HTML 에서 평문으로 확정**되면서 컬럼명을 바꿨다. `create_allcone_terms_tables.sql` 에는 이미 반영돼 있다.

| 환경 | 해야 할 것 |
|---|---|
| **운영망** | **`create_allcone_terms_tables.sql` 만 실행한다.** 테이블 자체가 없으므로 처음부터 `CONTENT` 로 생성된다 — **ALTER 는 실행하지 않는다** |
| 개발망 | 08-12 에 `CONTENT_HTML` 로 만들어 둔 상태라 `alter_allcone_terms_content_column.sql` 이 필요했다. **2026-08-21 적용 완료** |

⚠️ 개명을 빠뜨리고 구 스크립트로 만들면 약관 조회가 전부 `Unknown column 'CONTENT'` 로 실패한다. 조회가 통째로 죽으므로 배포 직후 바로 드러난다.

> **개발망 검증 완료 항목 (2026-08-12)** — 이관 SQL 포함해 아래 5가지를 실측했다.
> ① 현행 판정 5행 정상 ② 부분 개정(SERVICE만 v2 → 그것만 재동의) ③ 시행일 예약(내일 시행 v3는 현행에서 제외)
> ④ 종류 마스터 `SORT_ORDER` 변경 시 재동의 판정 불변 ⑤ 이관 재실행 멱등(1,213행 유지)
> 이관 시 마케팅 임의 승격이 없음도 확인했다(before_y 20 = after_y 20).

### 사전 확인

```sql
SHOW TABLES FROM bctransdbx LIKE 'allcone_terms%';

-- 콜레이션 확인 — allcone_terms_agreement.USER_ID 가 여기에 맞춰져 있어야 한다
SELECT COLLATION_NAME FROM information_schema.COLUMNS
 WHERE TABLE_SCHEMA='chainportaldb' AND TABLE_NAME='tb_member' AND COLUMN_NAME='LGN_ID';
```

**개발망 실측 (2026-08-12): `tb_member.LGN_ID` = `utf8mb4_bin`** (`bctransdbx` 기본은 `utf8mb4_general_ci`).
DDL이 `USER_ID VARCHAR(50) COLLATE utf8mb4_bin` 으로 명시하고 있다. 운영망 콜레이션이 다르면 **DDL을 그쪽에 맞춰 고친 뒤** 적용할 것 — 안 맞추면 동의 이력 조인이 인덱스를 못 탄다.

### 적용 후 순서 — 이게 중요하다

```
1. create_allcone_terms_tables.sql          ← 여기
2. 관제가 약관 초기 5종 등록 → /terms/sync 로 수신   ← TERMS_ID 가 여기서 확정된다
3. migrate_allcone_terms_agreement_v1.sql   ← 반드시 2 다음
```

**2번을 건너뛰고 서버를 배포하면** 현행 목록이 0행이 되어 `GET /mobile/terms` 가 빈 배열을 내려주고, `needsAgreement` 가 항상 false가 되어 **아무도 재동의를 안 하게 된다.** 에러가 안 나서 알아채기 어렵다.

**3번을 2번보다 먼저 실행하면** 이관할 `TERMS_ID` 가 존재하지 않아 0건이 들어가고, 기존 회원 전원이 재동의 대상이 된다.

### 이관 전 실측 (운영망)

이관 효과를 미리 가늠하는 쿼리다. 필수 4종이 전부 `'Y'` 인 회원만 재동의를 면한다.

```sql
SELECT TERM_AGRE_YN, PRVC_AGRE_YN, INDV_LOCTN_INFO_PRCS_AGRE_YN,
       LOCTN_TERM_AGRE_YN, COUNT(*)
  FROM chainportaldb.tb_member WHERE USE_YN='Y' GROUP BY 1,2,3,4;
```

**개발망 실측 (2026-08-12)**: 앱 로그인 가능 회원 257명 중 필수 4종 전부 `'Y'` 는 **34명뿐**. 나머지는 위치 관련 2종이 `'N'` 이라 이관해도 재동의 대상이다(가입채널 NULL인 구 회원 이관분이 대부분). **운영망은 분포가 다를 수 있으므로 이관 전 반드시 확인할 것.**

---

## 7. 운영망에 아직 적용하면 안 되는 것

| 파일 | 사유 |
|---|---|
| `create_port_nearby_road.sql` + `_congestion_cache.sql` | **감리용 CHENH-88.** 코드가 `develop`·`smartm2m/develop` 어디에도 머지되지 않는다. 개발망에만 넣는다(08-12 적용) |
| `create_allcone_maintenance_tables.sql` | 점검페이지 BPABCTRANS-244. 브랜치 미머지. 다만 **운영망·개발망 양쪽에 이미 테이블이 있다**(운영 08-03 확인 / 개발 07-15 생성, schedule 12행 · bypass 1행) → 추가 조치 없음 |

감리용 나머지 2건(취소 CHENH-102 · 연락처 CHENH-125)은 DDL이 없어 이 표에 항목이 없다.

---

## 8. 실행 순서 요약

**개발망 (133.186.222.171)** — 2026-08-12 전수 점검·조치 완료. DDL로 남은 것은 없다.

```
✅ popup priority / 인덱스 3개 (idx_cts_status_time · idx_event_fst_reg_dtm 포함)
✅ maintenance 2종 / geofence_notify_log / shedlock / pre_update_shp_vrf
✅ terminal_interface_operating_hour(8행) + allcone_holiday(22행)
✅ gps_geofence_notify_template(COMMON 1행) + gps_geofence_area_cache.NOTIFY_TEMPLATE_CODE
✅ terminal_interface SEND_GEOFENCE_EVENT 2행 (BNCTC050 · HPNTC050)
✅ port_nearby_road(5행) + port_nearby_road_congestion_cache   ← 2026-08-12 신규 적용
✅ allcone_terms 3테이블 (데이터 0행 — 관제 초기등록 대기, 의도된 상태)

남은 판단거리 1건: add_tss_movement_interface_code.sql (§4-4)
  general_code·terminal_interface 양쪽 0행. 코드에는 TerminalInterfaceType.
  GET_MOVEMENT_EVENT 가 이 코드를 참조하고 TerminalAgentAdapter 가 호출한다.
  → 기능을 실제로 쓸 것인지 확인 후 적용 판단.
```

**운영망** — 회차별로 파일이 다르다.

```
[1차 · 2026-08-13]  → 배포DDL-1차-2026-08-13.sql 하나만 실행하면 된다
  STEP 0 점검 → STEP 1(통보 템플릿·필수) → STEP 2(HPNT 등록)
              → STEP 3(폐기배치 인덱스) → STEP 4·5(운영시간·공휴일) → STEP 6 검증
  + 환경변수 HOLIDAY_API_SERVICE_KEY (2026-08-10 재발급분)
  + 🔴 운영 서버 TZ 가 KST 인지 확인 (차상세척 판정이 JVM 기본 TZ 를 쓴다)
  ※ 순서 원칙: 통보 템플릿 INSERT → 서버 배포. 역순이면 BNCT 통보가 전면 중단된다.

[2차 · 2026-08-17 주]  → 배포전-DDL-2026-08-03.sql
  1. STEP 1 : popup priority 컬럼
  2. STEP 4 : idx_cts_status_time 확인 → 없으면 생성 (없으면 블록 대기차량 조회 32초)
  3. STEP 9 : create_allcone_terms_tables.sql
              → 관제 초기 5종 등록(sync) → migrate_allcone_terms_agreement_v1.sql 순서 엄수
     ※ 확인만: tb_b_truck_trans_odr.TRUCK_CODE / geofence_notify_log / pre_update_shp_vrf

[제외] port_nearby_road 2건 — 감리용(CHENH-88). 운영망에 넣지 않는다.
```

---

## 운영 규칙

새 DDL 파일이 생기면 이 문서에 항목을 추가하고, 적용 완료 시 해당 항목에 적용일·적용 망을 기록한다.

**적용 현황 (개발망 = 2026-08-12 전수 재점검 / 운영망 = 전부 미확인)**

| 파일·대상 | 개발망 | 운영망 | 회차 |
|---|---|---|---|
| `gps_geofence_notify_template` + `area_cache.NOTIFY_TEMPLATE_CODE` | ✅ 적용됨 (08-12, COMMON 1행) | ❌ 미적용 | 🔴 **1차** (1차 파일 STEP 1) |
| `terminal_interface` SEND_GEOFENCE_EVENT HPNTC050 | ✅ 적용됨 (08-12, BNCT와 2행) | ❌ 미적용 | 🔴 **1차** (STEP 2) |
| `create_allcone_user_area_event_retention_index.sql` | ✅ 존재 (`idx_event_fst_reg_dtm`) | ❌ 미적용 | 🔴 **1차** (STEP 3) |
| `create_allcone_terminal_interface_operating_hour.sql` | ✅ 적용됨 (8행) | ❌ 미적용 | 🔴 **1차** (STEP 4) |
| `create_allcone_holiday.sql` | ✅ 적용됨 (22행) | ❌ 미적용 | 🔴 **1차** (STEP 5) |
| `alter_popup_manage_add_priority.sql` | ✅ 적용됨 | ❓ 미확인 | 2차 |
| 인덱스 `idx_cts_status_time` 외 2개 | ✅ 존재 (`container_transport_status`) | ❓ 미확인 | 2차 |
| `create_allcone_terms_tables.sql` | ✅ 적용됨 (08-12) + `CONTENT` 개명 ALTER (08-21) | ❌ 미적용 | 2차 |
| `alter_allcone_terms_content_column.sql` | ✅ 적용됨 (08-21) | ⛔ **불필요** — create 에 이미 반영 | — |
| `migrate_allcone_terms_agreement_v1.sql` | ✅ 실행·검증됨 (08-12, 이후 롤백) | ❌ 미적용 (**관제 초기등록 이후**) | 2차 |
| `create_port_nearby_road.sql` + `_congestion_cache.sql` | ✅ **적용됨 (08-12, 5행)** | ⛔ 넣지 않음 | 제외(감리) |
| `create_allcone_maintenance_tables.sql` | ✅ 적용됨 (07-15) | ✅ 존재 (08-03 확인) | — |
| `create_allcone_geofence_notify_log.sql` | ✅ 적용됨 (07-16, 0행) | ✅ 존재 (08-03 확인) | — |
| `shedlock_table.sql` | ✅ 적용됨 (06-22, 4행) | ❓ 미확인 | — |
| `tss_group_order_container_pre_update_shp_vrf.sql` | ✅ 적용됨 (06-22) | ❓ 미확인 | — |
| `tb_b_truck_trans_odr.TRUCK_CODE` | ✅ 존재 (`varchar(10)`) | ❓ 미확인 | 확인만 |
| `add_tss_movement_interface_code.sql` | ❌ **미적용** (양쪽 0행) | ❓ 미확인 | **판단 대기** |

**환경 실측값 (개발망)**

| 항목 | 값 |
|---|---|
| DB | `10.5.9-MariaDB` → `IF NOT EXISTS` 구문 사용 가능 |
| 계정 권한 | `smartm2m@%` = `GRANT ALL PRIVILEGES ON *.*` |
| `container_transport` | 226만 행 |
| `container_transport_status` | 144만 행 |
| `tb_member.LGN_ID` 콜레이션 | `utf8mb4_bin` (`bctransdbx` 기본은 `utf8mb4_general_ci`) — 2026-08-12 실측 |
| 앱 로그인 가능 회원 | `ROLE_DRIVER` 255명 + `ROLE_TRANSFER` 2명 — 2026-08-12 실측 |

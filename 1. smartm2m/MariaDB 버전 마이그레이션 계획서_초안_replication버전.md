# MariaDB 버전 마이그레이션 계획서 (복제 방식)

## 1. 마이그레이션 계획 (10.5.9 → 11.8 LTS)

### 1.1 마이그레이션 방식

- **방식: 크로스 버전 복제(Replication) 후 전환**
- 기존 CentOS 7 VM의 MariaDB 10.5.9를 Master로, 신규 Rocky Linux VM의 MariaDB 11.8을 Slave로 구성
- 실시간 복제로 데이터를 동기화한 후, 명절 당일 Slave를 Master로 승격하여 전환

```
CentOS 7 VM                    Rocky Linux VM

┌──────────────────┐           ┌──────────────────┐
│ MariaDB 10.5.9   │──복제──→  │ MariaDB 11.8.x   │
│   (Master)       │  binlog   │   (Slave)        │
│                  │           │   (read_only)    │
└──────────────────┘           └──────────────────┘
```

**동작 원리:**

1. 10.5.9가 binlog 생성 (모든 변경사항 기록)
2. 11.8이 binlog를 읽어서 relay log로 저장
3. 11.8이 SQL 재실행하여 동기화
4. 동기화 완료 후 전환 (11.8을 Master로 승격)

**덤프 & 리스토어 대비 장점:**

- 다운타임이 수 시간 → **수 분**으로 단축
- 테이블 분류(A/B/C) 불필요. 전체 데이터가 실시간으로 동기화됨
- 전환 전까지 기존 서비스에 영향 없음

**리스크:**

- 10.5 → 11.8은 메이저 4단계를 건너뛰는 크로스 버전 복제로, binlog 호환성 문제 가능성 있음
- charset 차이(10.5 latin1 vs 11.8 utf8mb4)로 복제 에러 가능성
- **반드시 테스트 환경에서 검증 후 진행**

### 1.2 서버 환경

- Master: 기존 CentOS 7 VM (MariaDB 10.5.9)
- Slave: 신규 Rocky Linux VM (MariaDB 11.8 신규 설치)
- 전환 완료 후 기존 CentOS 7 VM은 폐기 (일정 기간 보존 후)

### 1.3 11.8 주요 설정

```ini
[mysqld]
# binlog format 변경 (STATEMENT → ROW)
# - INSERT...ON DUPLICATE KEY UPDATE 구문의 동시 실행 시 락 경합 완화
binlog_format = ROW

# 11.8 기본 charset이 utf8mb4로 변경되었으므로
# 기존 데이터 호환을 위해 명시적으로 지정
character-set-server = utf8mb3
collation-server = utf8mb3_general_ci
```

### 1.4 작업 일정

- **D-Day: 2026-02-17 (설 명절)**
- 해당 일자에 터미널이 닫혀 전산 작업이 모두 중지되므로 서비스 중단 가능

---

#### Phase 1: 사전 조사 (명절 전까지)

서비스 영향 없이 진행 가능한 작업.

**1) DB 용량 파악**

```sql
SELECT table_schema, table_name,
  ROUND((data_length + index_length)/1024/1024, 1) AS size_mb,
  table_rows
FROM information_schema.tables
WHERE table_schema NOT IN ('mysql','information_schema','performance_schema')
ORDER BY (data_length + index_length) DESC;
```

**2) 테이블 charset/collation 현황**

> ⚠️ **11.8 변경사항:** 기본 charset이 `latin1` → `utf8mb4`로, 기본 collation이 `utf8mb3_general_ci` → `utf8mb4_uca1400_ai_ci`로 변경됨. 기존 테이블 중 charset이 제각각인 경우 복제 시 또는 전환 후 JOIN 시 `Illegal mix of collations` 에러가 발생할 수 있으므로 사전 파악 필요.

```sql
SELECT table_schema, table_name, table_collation
FROM information_schema.tables
WHERE table_schema NOT IN ('mysql','information_schema','performance_schema')
ORDER BY table_schema, table_name;
```

**3) 컬럼 레벨 charset/collation 확인**

> ⚠️ **11.8 변경사항:** 테이블 레벨뿐 아니라 컬럼 단위로도 charset이 다를 수 있음. 기존 컬럼이 `latin1`, `utf8mb3` 등 혼재된 경우 11.8 환경에서 문제가 될 수 있으므로 컬럼 레벨까지 확인 필요.

```sql
SELECT table_schema, table_name, column_name,
  character_set_name, collation_name
FROM information_schema.columns
WHERE character_set_name IS NOT NULL
  AND table_schema NOT IN ('mysql','information_schema','performance_schema')
ORDER BY table_schema, table_name;
```

**4) 스토리지 엔진 확인**

> ⚠️ TokuDB, Spider 등 deprecated 엔진 사용 시 11.8에서 지원되지 않을 수 있음.

```sql
SELECT DISTINCT ENGINE FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema','mysql','performance_schema');
```

**5) 플러그인 확인**

```sql
SHOW PLUGINS;
```

**6) 데이터 무결성 검증**

```bash
mysqlcheck --all-databases --check -u root -p
```

**7) 애플리케이션 호환성 확인**

> ⚠️ **10.6 변경사항:** `OFFSET`이 예약어(Reserved Word)로 지정됨. 소스코드에서 `OFFSET`을 컬럼명이나 별칭으로 사용하고 있으면 11.8에서 SQL 문법 에러가 발생하므로 사전 확인 필요.

```bash
# OFFSET 예약어 사용 여부 (10.6부터 예약어)
grep -rni "OFFSET" --include="*.java" --include="*.xml" src/
```

**8) 현행 my.cnf 설정 백업**

```bash
cp /etc/my.cnf.d/server.cnf ~/backup_server.cnf
```

**9) 현행 binlog 설정 확인**

```sql
SHOW VARIABLES LIKE 'log_bin';
SHOW VARIABLES LIKE 'binlog_format';
SHOW VARIABLES LIKE 'server_id';
```

---

#### Phase 2: 테스트 환경 검증 (명절 전까지)

> ⚠️ **크로스 버전 복제는 반드시 테스트 검증 후 진행.** 테스트에서 복제 에러가 발생하면 덤프 & 리스토어 방식으로 전환.

**1) 테스트 서버에 Rocky Linux + MariaDB 11.8 설치**

```bash
curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup | \
  sudo bash -s -- --mariadb-server-version="mariadb-11.8"
sudo dnf install MariaDB-server MariaDB-client
```

**2) 테스트 복제 구성**

Master (10.5) 설정:

```ini
[mysqld]
server-id = 1
log_bin = mysql-bin
binlog_format = ROW
```

Slave (11.8) 설정:

```ini
[mysqld]
server-id = 2
read_only = ON
binlog_format = ROW
character-set-server = utf8mb3
collation-server = utf8mb3_general_ci
```

**3) 초기 데이터 동기화**

```bash
# Master에서 풀 덤프 (복제 시작점 기록 포함)
mysqldump -u root -p \
  --single-transaction \
  --master-data=1 \
  --routines --triggers --events \
  --all-databases > init_dump.sql

# Slave에 리스토어
mysql -u root -p < init_dump.sql
```

**4) 복제 시작**

```sql
-- Slave에서 실행
CHANGE MASTER TO
  MASTER_HOST = 'master-ip',
  MASTER_USER = 'repl_user',
  MASTER_PASSWORD = 'password',
  MASTER_LOG_FILE = 'mysql-bin.XXXXXX',  -- 덤프에 기록된 값
  MASTER_LOG_POS = XXXXXX;               -- 덤프에 기록된 값

START SLAVE;
```

**5) 검증 항목**

- [ ] 복제 정상 동작 확인 (`SHOW SLAVE STATUS\G` → Slave_IO_Running: Yes, Slave_SQL_Running: Yes)
- [ ] 복제 지연(Seconds_Behind_Master) 확인
- [ ] 복제 에러 없음 확인 (Last_Error 비어있음)
- [ ] Master에 INSERT/UPDATE → Slave에 반영되는지 확인
- [ ] charset 관련 복제 에러 없음 확인
- [ ] 일정 기간(수일) 복제 안정성 확인

**산출물:**

- [ ] 복제 테스트 결과 보고서
- [ ] 이슈 목록 및 해결 방안
- [ ] 확정된 my.cnf (Master / Slave)

---

#### Phase 3-1: 본 환경 복제 구성 (명절 전)

**1) 신규 Rocky Linux VM에 MariaDB 11.8 설치 및 설정**

**2) Master(10.5) binlog 설정 확인/적용**

```ini
[mysqld]
server-id = 1
log_bin = mysql-bin
binlog_format = ROW
```

> ※ binlog_format 변경 시 MariaDB 재시작 필요. 트래픽 적은 시간에 진행.

**3) 복제용 계정 생성 (Master에서)**

```sql
CREATE USER 'repl_user'@'slave-ip' IDENTIFIED BY 'password';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'slave-ip';
FLUSH PRIVILEGES;
```

**4) 초기 데이터 동기화**

```bash
# Master에서 풀 덤프 (서비스 영향 없음)
mysqldump -u root -p \
  --single-transaction \
  --master-data=1 \
  --routines --triggers --events \
  --all-databases > init_dump.sql

# Slave에 리스토어
mysql -u root -p < init_dump.sql
```

**5) 복제 시작 및 모니터링**

```sql
-- Slave에서 실행
CHANGE MASTER TO
  MASTER_HOST = 'master-ip',
  MASTER_USER = 'repl_user',
  MASTER_PASSWORD = 'password',
  MASTER_LOG_FILE = 'mysql-bin.XXXXXX',
  MASTER_LOG_POS = XXXXXX;

START SLAVE;

-- 복제 상태 확인
SHOW SLAVE STATUS\G
```

**6) 명절 전까지 복제 안정성 모니터링**

```sql
-- 주기적으로 확인
SHOW SLAVE STATUS\G

-- 확인 항목:
-- Slave_IO_Running: Yes
-- Slave_SQL_Running: Yes
-- Seconds_Behind_Master: 0 (따라잡은 상태)
-- Last_Error: (비어있어야 함)
```

---

#### Phase 3-2: D-Day (2026-02-17, 명절 당일)

```
□ 1. 데이터 유입 중단 확인 (08:00)

□ 2. 애플리케이션 전체 중지

□ 3. Slave 복제 완전 따라잡기 확인
     SHOW SLAVE STATUS\G
     → Seconds_Behind_Master = 0 확인

□ 4. Slave 복제 중지
     STOP SLAVE;

□ 5. Slave를 Master로 승격
     RESET SLAVE ALL;          -- 복제 설정 제거
     SET GLOBAL read_only = OFF;  -- 쓰기 허용

□ 6. 시스템 테이블 호환성 검증
     mariadb-upgrade -u root -p
     mysqlcheck --all-databases --check -u root -p

□ 7. 데이터 검증
     - 주요 테이블 row count 비교 (Master vs 신규 Master)
     - 핵심 데이터 샘플 확인

□ 8. 애플리케이션 연결 정보를 신규 서버로 변경

□ 9. 애플리케이션 시작 및 동작 확인

□ 10. 완료 확인
```

**롤백 플랜 (문제 발생 시)**

- 신규 서버에 문제가 생기면 기존 CentOS 7 VM의 MariaDB 10.5를 그대로 재가동
- 앱 연결 정보를 기존 서버로 원복

---

#### Phase 4: 사후 모니터링 (명절 이후 1~2주)

- [ ] 에러 로그 일일 확인: /var/lib/mysql/*.err
- [ ] 슬로우 쿼리 모니터링
- [ ] Signal 6 재발 여부 확인
- [ ] 정상 확인 후 기존 CentOS 7 VM 폐기 (일정 기간 보존 후)

---

## 2. Community vs Enterprise 비교

### 2.1 기능 비교

|항목|Community (현재)|Enterprise|
|---|---|---|
|DB 엔진|MariaDB Server|거의 동일 (추가 테스트 빌드)|
|기술 지원|없음 (커뮤니티 포럼만)|24x7 전문 엔지니어 + SLA 보장|
|유지보수 기간|3년|최대 8년|
|버그 수정|분기별 릴리스 대기|우선 처리 + 커스텀 핫픽스|
|복제(Replication)|**무제한 무료**|동일|
|MaxScale (DB 프록시)|2노드까지 무료|제한 없음|
|백업 도구|MariaBackup 기본|Enterprise Backup (락 최소화)|
|감사(Audit)|기본 플러그인|Enterprise Audit (고급)|
|KMS 연동|미지원|HashiCorp Vault 등 연동|
|컨설팅/교육|없음|커스텀 교육, 전략 컨설팅|

> ※ 복제(Replication)는 Community에서 무제한 무료로 사용 가능. 이번 마이그레이션에 Enterprise는 필요하지 않음.

### 2.2 비용

|플랜|서버당 연간 비용|
|---|---|
|Enterprise Standard|$2,500|
|Enterprise Advanced|$5,000|
|Enterprise Cluster|$6,500/노드|

※ 서버 대수에 따라 총 비용 산정 필요

### 2.3 검토 의견

**현재 환경(단일 DB)에서는 Community로 충분함.**

Enterprise 전환이 필요한 시점:

- 이중화(HA) 도입 시 MaxScale 3노드 이상 사용 필요
- 장애 대응 시 SLA 기반 전문 기술지원 필요
- 유지보수 기간 연장 필요 (3년 → 8년)

---

## 3. 향후 검토 사항: 이중화 (HA)

### 3.1 이중화 구성

```
[Spring Boot App] → [MaxScale] → [MariaDB Master] (쓰기)
                      (프록시)  → [MariaDB Slave]  (읽기)
```

> ※ 이번 마이그레이션에서 사용하는 복제는 데이터 이전 목적이며, 전환 후 기존 서버는 폐기함. 이중화(HA)는 상시 운영을 위한 별도 프로젝트임.

### 3.2 이중화 도입 근거

- 이번 Signal 6 장애는 물리적 corruption (페이지 깨짐)
- 물리적 corruption은 Master/Slave 간 전파되지 않음
- 이중화가 있었다면 Master 장애 시 Slave로 자동 전환되어 서비스 중단 없었음

### 3.3 이중화 도입 시 필요 사항

- 서버 최소 3대 (Master + Slave + MaxScale)
- MaxScale 3노드 이상 시 Enterprise 라이선스 필요
- 별도 프로젝트로 계획 수립 필요

---

## 4. 전체 타임라인

|시점|작업|비고|
|---|---|---|
|명절 전까지|Phase 1: 사전 조사|서비스 영향 없음|
|명절 전까지|Phase 2: 테스트 환경에서 복제 검증|별도 테스트 서버|
|명절 전|Phase 3-1: 본 환경 복제 구성 및 동기화|서비스 영향 없음|
|2026-02-17 (명절 당일)|Phase 3-2: Slave를 Master로 전환|서비스 중단 (수 분)|
|명절 이후 1~2주|Phase 4: 사후 모니터링||

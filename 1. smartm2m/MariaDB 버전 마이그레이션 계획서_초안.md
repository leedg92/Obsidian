## 1. 마이그레이션 계획 (10.5.9 → 11.8 LTS)

### 1.1 마이그레이션 방식

- **방식: 덤프 & 리스토어 (신규 설치)**
- in-place 업그레이드 방식은 패치/마이너 버전을 순차적으로 올려야 정상동작함(MariaDB jira) :
    - 기존 .ibd 파일에 corruption 이력이 있어 신뢰할 수 없음
    - 10.5 → 11.8은 메이저 버전 4단계를 건너뛰는 작업
    - 신규 설치 시 인덱스, 페이지 구조가 새로 생성되어 기존 파일 레벨 문제 해소

### 1.2 서버 환경

- **OS 재설치(Rocky Linux)** 후 MariaDB 11.8을 신규 설치하는 방식으로 진행
- 기존 서버에 진행할 경우, 롤백을 위해 OS 재설치 전 데이터 디렉토리 및 설정 파일 별도 백업 필수
- 신규 서버에 진행할 경우, 롤백은 기존 서버를 그대로 재가동하면 되므로 더 안전함

### 1.3 11.8 주요 설정

```ini
[mysqld]
# binlog format 변경 (STATEMENT → ROW)
binlog_format = ROW

# 11.8 기본 charset이 utf8mb4로 변경되었으므로
# 기존 데이터 호환을 위해 명시적으로 지정
character-set-server = utf8mb3
collation-server = utf8mb3_general_ci

# binlog format 변경 (STATEMENT → ROW)
# - 대표님 지시사항: INSERT...ON DUPLICATE KEY UPDATE 구문의 동시 실행 시 락 경합 완화를 위해 ROW 모드로 변경
binlog_format = ROW

```

### 1.4 작업 일정

- **D-Day: 2026-02-17 (설 명절)**
- 해당 일자에 서비스 중단 가능

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

**2) 날짜 컬럼 유무 확인 (델타 덤프 가능 여부 판단)**

```sql
SELECT table_schema, table_name, column_name
FROM information_schema.columns
WHERE column_name IN ('created_at','reg_dt','reg_date','insert_dt','log_dt','log_date')
  AND table_schema NOT IN ('mysql','information_schema','performance_schema')
ORDER BY table_schema, table_name;
```

**3) 최근 변경 여부 확인**

```sql
SELECT table_schema, table_name, update_time
FROM information_schema.tables
WHERE table_schema NOT IN ('mysql','information_schema','performance_schema')
ORDER BY update_time DESC;
```

**4) 테이블 charset/collation 현황**

> **11.8 변경사항:** 기본 charset이 `latin1` → `utf8mb4`로, 기본 collation이 `utf8mb3_general_ci` → `utf8mb4_uca1400_ai_ci`로 변경됨. `character-set-server=utf8mb3`으로 설정하더라도, 기존 테이블 중 charset이 제각각인 경우 리스토어 후 JOIN 시 `Illegal mix of collations` 에러가 발생할 수 있으므로 사전 파악 필요.

```sql
SELECT table_schema, table_name, table_collation
FROM information_schema.tables
WHERE table_schema NOT IN ('mysql','information_schema','performance_schema')
ORDER BY table_schema, table_name;
```

**5) 컬럼 레벨 charset/collation 확인**

> **11.8 변경사항:** 테이블 레벨뿐 아니라 컬럼 단위로도 charset이 다를 수 있음. 기존 컬럼이 `latin1`, `utf8mb3` 등 혼재된 경우 11.8 환경에서 문제가 될 수 있으므로 컬럼 레벨까지 확인 필요.

```sql
SELECT table_schema, table_name, column_name,
  character_set_name, collation_name
FROM information_schema.columns
WHERE character_set_name IS NOT NULL
  AND table_schema NOT IN ('mysql','information_schema','performance_schema')
ORDER BY table_schema, table_name;
```

**6) 데이터 무결성 검증**

```bash
mysqlcheck --all-databases --check -u root -p
```

**7) 애플리케이션 호환성 확인**

> **10.6 변경사항:** `OFFSET`이 예약어(Reserved Word)로 지정됨. 소스코드에서 `OFFSET`을 컬럼명이나 별칭으로 사용하고 있으면 11.8에서 SQL 문법 에러가 발생하므로 사전 확인 필요.

```bash
# OFFSET 예약어 사용 여부 (10.6부터 예약어)
grep -rni "OFFSET" --include="*.java" --include="*.xml" src/
```

**8) 현행 my.cnf 설정 백업**

```bash
cp /etc/my.cnf.d/server.cnf ~/backup_server.cnf
```


---

#### Phase 1.5: 테이블 분류

사전 조사 결과를 바탕으로 테이블을 아래 기준으로 분류.

| 분류                              | 기준                            | 덤프 시점           | 비고                   |
| ------------------------------- | ----------------------------- | --------------- | -------------------- |
| A. 대용량 + 거의 안 변함<br>(ex 로그 테이블) | 로그/이력 테이블, 날짜 컬럼 있음           | 전날 풀 덤프 + 당일 델타 | created_at 등으로 델타 추출 |
| B. 절대 안 변함<br>(ex 코드/메타데이터)     | 코드/메타데이터 테이블, update_time 오래됨 | 전날 풀 덤프로 끝      | 당일 추가 작업 없음          |
| C. 실시간 변경<br>(ex 운송건)           | 업무/사용자 데이터                    | 당일 풀 덤프         | 서비스 중지 후 진행          |

**분류 기준:**

- 용량 크고 + 날짜 컬럼 있고 + 최근 변경 적음 → A
- 변경 전혀 없음 → B
- 날짜 컬럼 없거나, 실시간 변경됨 → C

**목표:** 당일 풀 덤프 대상(C)의 총 용량을 최소화하여 작업 시간 단축

---

#### Phase 2: 테스트 환경 검증 (명절 전까지)

**1) 테스트 서버에 Rocky Linux + MariaDB 11.8 설치**
- VM으로 할지 인스턴스를 추가할지 정해야함

```bash
curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup | \
  sudo bash -s -- --mariadb-server-version="mariadb-11.8"
sudo dnf install MariaDB-server MariaDB-client
```

**2) my.cnf 설정 적용**

- binlog_format = ROW
- character-set-server = utf8mb3
- collation-server = utf8mb3_general_ci
- binlog_format = ROW (대표님 지시사항)
- 기존 innodb 관련 설정 이관

**3) 테스트용 덤프 & 리스토어**

```bash
# 현행에서 덤프 (서비스 영향 없음)
mysqldump -u root -p \
  --single-transaction \
  --routines --triggers --events \
  --all-databases > test_dump.sql

# 테스트 서버에 리스토어
mysql -u root -p < test_dump.sql
mariadb-upgrade -u root -p
mysqlcheck --all-databases --check -u root -p
```

---

#### Phase 3-1: 명절 전날 사전 작업 (2026-02-16)

**0) 타겟 서버에 Rocky Linux + MariaDB 11.8 설치 및 설정 완료**

**1) A 그룹 (대용량 + 거의 안 변함) 풀 덤프**

```bash
mysqldump -u root -p --single-transaction \
  mydb table_a1 table_a2 table_a3 ... > pre_dump_a.sql
```

**2) B 그룹 (절대 안 변함) 풀 덤프**

```bash
mysqldump -u root -p --single-transaction \
  mydb table_b1 table_b2 table_b3 ... > pre_dump_b.sql
```

**3) 마이그레이션 타겟 서버에 A + B 리스토어**

```bash
mysql -u root -p < pre_dump_a.sql
mysql -u root -p < pre_dump_b.sql
```

---

#### Phase 3-2: D-Day (2026-02-17, 명절 당일)

```
□ 1. 데이터 유입 중단 확인 (08:00)

□ 2. 애플리케이션 전체 중지

□ 3. A 그룹 델타 덤프 (전날 이후 변경분만)
     mysqldump -u root -p mydb table_a1 \
       --where="created_at > '2026-02-16'" > delta_a.sql

□ 4. C 그룹 풀 덤프
     mysqldump -u root -p --single-transaction \
       mydb table_c1 table_c2 ... > dump_c.sql

□ 5. 덤프 파일 검증
     tail -5 delta_a.sql   # "Dump completed" 확인
     tail -5 dump_c.sql    # "Dump completed" 확인

□ 6. 현행 MariaDB 중지
     systemctl stop mariadb

□ 7. 타겟 서버에 델타 + C 적용
     mysql -u root -p < delta_a.sql
     mysql -u root -p < dump_c.sql

□ 8. 업그레이드 및 검증
     mariadb-upgrade -u root -p
     mysqlcheck --all-databases --check -u root -p

□ 9. 데이터 검증
     - 주요 테이블 row count 비교 (이전 vs 이후)
     - 핵심 데이터 샘플 확인

□ 10. 애플리케이션 연결 정보 변경 (서버가 변경된 경우)

□ 11. 애플리케이션 시작 및 동작 확인

□ 12. 완료 확인
```

**롤백 플랜 (문제 발생 시)**

- 신규 서버인 경우: 기존 서버의 MariaDB 10.5를 그대로 재가동
- 같은 서버인 경우: 백업해둔 데이터 디렉토리 복원 후 MariaDB 10.5 재설치

---

## 4. 전체 타임라인

| 시점                 | 작업                             | 비고        |
| ------------------ | ------------------------------ | --------- |
| 명절 전까지             | Phase 1: 사전 조사                 | 서비스 영향 없음 |
| 명절 전까지             | Phase 1.5: 테이블 분류              |           |
| 명절 전까지             | Phase 2: 테스트 검증                | 별도 테스트 서버 |
| 2026-02-16 (명절 전날) | Phase 3-1: A+B 그룹 사전 덤프 & 리스토어 | 서비스 영향 없음 |
| 2026-02-17 (명절 당일) | Phase 3-2: 델타 + C 그룹 덤프 & 전환   | 서비스 중단    |

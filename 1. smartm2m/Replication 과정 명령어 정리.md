

---

## 1. 사전 확인

### 1.1 binlog 활성화 여부 확인 (Master)

```sql
SHOW VARIABLES LIKE 'log_bin';
```

- `ON`: 활성화됨
- `OFF`: my.cnf에 설정 추가 필요

### 1.2 binlog 설정 (Master - 비활성화 시)

```ini
# /etc/my.cnf 또는 /etc/mysql/mariadb.conf.d/50-server.cnf
[mysqld]
log_bin = mysql-bin
server-id = 1
binlog_format = ROW
```

설정 후 MariaDB 재시작 필요

### 1.3 binlog 삭제 주기 확인

```sql
SHOW VARIABLES LIKE 'expire_logs_days';
-- 또는 (11.x)
SHOW VARIABLES LIKE 'binlog_expire_logs_seconds';
```

- `0`: 자동 삭제 안 함
- 숫자가 있으면 해당 일수 후 삭제

### 1.4 binlog 삭제 주기 변경 (임시)

```sql
SET GLOBAL expire_logs_days = 90;
```

### 1.5 현재 binlog 파일 목록 확인

```sql
SHOW BINARY LOGS;
```

### 1.6 binlog 이벤트 상세 확인

```sql
SHOW BINLOG EVENTS IN 'mysql-bin.000001' LIMIT 20;
```

---

## 2. Master에서 덤프

### 2.1 Docker 환경에서 덤프

```bash
docker exec [컨테이너명] mysqldump \
  --single-transaction \
  --master-data=2 \
  --all-databases \
  --routines \
  --triggers \
  -u root -p'비밀번호' > /home/rocky/master_dump.sql
```

### 2.2 일반 환경에서 덤프

```bash
mysqldump \
  --single-transaction \
  --master-data=2 \
  --all-databases \
  --routines \
  --triggers \
  -u root -p > /home/rocky/master_dump.sql
```

### 2.3 주요 옵션 설명

|옵션|설명|
|---|---|
|`--single-transaction`|InnoDB 테이블 락 없이 일관된 스냅샷 덤프|
|`--master-data=2`|덤프 시점의 binlog position을 주석으로 기록|
|`--all-databases`|모든 데이터베이스 덤프|
|`--routines`|저장 프로시저, 함수 포함|
|`--triggers`|트리거 포함|

### 2.4 --master-data 옵션 차이

|옵션|결과|
|---|---|
|`--master-data=1`|`CHANGE MASTER TO ...` 실행 가능한 형태로 포함|
|`--master-data=2`|`-- CHANGE MASTER TO ...` 주석으로 포함 (권장)|
|옵션 없음|binlog position 기록 안 됨|

**Replication 용도면 반드시 `--master-data=2` 필수**

---

## 3. 덤프 파일에서 binlog position 확인

```bash
head -30 /home/rocky/master_dump.sql | grep "MASTER_LOG"
```

결과 예시:

```sql
-- CHANGE MASTER TO MASTER_LOG_FILE='mysql-bin.000001', MASTER_LOG_POS=328;
```

→ 이 값을 Slave 설정에 사용

---

## 4. Slave에 리스토어

### 4.1 기존 사용자 DB 삭제 (중간에 끊긴 경우)

```sql
-- 시스템 DB(information_schema, mysql, performance_schema, sys)는 제외
DROP DATABASE IF EXISTS bctransdb_v2;
DROP DATABASE IF EXISTS bctransdbx;
DROP DATABASE IF EXISTS chainportaldb;
DROP DATABASE IF EXISTS test_db;
```

### 4.2 리스토어 전 속도 향상 설정 (권장)

**리스토어 전에 반드시 실행 - 2~3배 속도 향상**

```sql
-- 버퍼풀을 4GB로 증가 (가장 효과 큼)
SET GLOBAL innodb_buffer_pool_size = 4294967296;
-- 트랜잭션 로그 flush 빈도 줄이기
SET GLOBAL innodb_flush_log_at_trx_commit = 0;
-- binlog 매번 fsync 안함
SET GLOBAL sync_binlog = 0;
 -- double write 해제
SET GLOBAL innodb_doublewrite = OFF;
```

### 4.3 리스토어 실행

```bash
sudo mariadb -u root -p < /home/rocky/master_dump.sql
```

### 4.4 백그라운드로 리스토어 (세션 끊어도 유지 - 권장)

```bash
nohup sudo mariadb -u root -p'비밀번호' < /home/rocky/master_dump.sql > /home/rocky/restore.log 2>&1 &
```

### 4.5 진행 상황 확인

```bash
tail -f /home/rocky/restore.log
```

또는:

```sql
SHOW PROCESSLIST;
```

### 4.6 리스토어 완료 후 설정 원복 (필수)

```sql
SET GLOBAL innodb_flush_log_at_trx_commit = 1;
SET GLOBAL sync_binlog = 1;
SET GLOBAL foreign_key_checks = 1;
SET GLOBAL unique_checks = 1;
```

### 4.7 예상 소요 시간 (5GB 기준)

|설정|소요 시간|
|---|---|
|기본 설정|30분 ~ 1시간|
|속도 향상 설정 적용|10분 ~ 20분|

---

## 5. Slave 복제 설정

### 5.1 기존 Slave 설정 초기화

```sql
STOP SLAVE;
RESET SLAVE;
```

### 5.2 Slave 등록 (SSL 비활성화 - 크로스 버전 권장)

```sql
CHANGE MASTER TO
  MASTER_HOST = '133.186.222.171',
  MASTER_PORT = 23306,
  MASTER_USER = 'root',
  MASTER_PASSWORD = 'rootpass',
  MASTER_LOG_FILE = 'mysql-bin.000001',
  MASTER_LOG_POS = 48973,
  MASTER_SSL = 0;

START SLAVE;
```

### 5.3 Slave 등록 (SSL 활성화 - 기본값)

```sql
CHANGE MASTER TO
  MASTER_HOST = '133.186.222.171',
  MASTER_PORT = 23306,
  MASTER_USER = 'root',
  MASTER_PASSWORD = 'rootpass',
  MASTER_LOG_FILE = 'mysql-bin.000001',
  MASTER_LOG_POS = 328;

START SLAVE;
```

### 5.4 필드 설명

|필드|설명|예시|
|---|---|---|
|`MASTER_HOST`|Master 서버 IP|`'133.186.222.171'`|
|`MASTER_PORT`|Master 서버 포트 (기본 3306)|`23306`|
|`MASTER_USER`|복제용 계정|`'root'`|
|`MASTER_PASSWORD`|복제용 계정 비밀번호|`'rootpass'`|
|`MASTER_LOG_FILE`|덤프에 기록된 binlog 파일명|`'mysql-bin.000001'`|
|`MASTER_LOG_POS`|덤프에 기록된 binlog position|`328`|
|`MASTER_SSL`|0: SSL 비활성화, 1: SSL 활성화|`0`|

---

## 6. 복제 상태 확인

### 6.1 상태 조회

```sql
SHOW SLAVE STATUS\G
```

### 6.2 정상 상태 예시

```
Slave_IO_Running: Yes
Slave_SQL_Running: Yes
Seconds_Behind_Master: 0
Last_IO_Error: (없음)
Last_SQL_Error: (없음)
```

### 6.3 주요 확인 항목

|항목|정상 값|의미|
|---|---|---|
|`Slave_IO_Running`|Yes|Master에서 binlog 수신 중|
|`Slave_SQL_Running`|Yes|binlog 이벤트 실행 중|
|`Seconds_Behind_Master`|0|Master와 동기화 완료|
|`Last_IO_Error`|없음|IO 스레드 에러 없음|
|`Last_SQL_Error`|없음|SQL 스레드 에러 없음|

---

## 7. 복제 테스트

### 7.1 Master에서 테스트 데이터 생성

```sql
CREATE DATABASE repl_test;
USE repl_test;
CREATE TABLE test1 (id INT PRIMARY KEY, val VARCHAR(10));
INSERT INTO test1 VALUES (1, 'hello');
```

### 7.2 Slave에서 확인

```sql
SHOW DATABASES;
SELECT * FROM repl_test.test1;
```

---

## 8. 흔한 에러와 해결

### 8.1 SSL 에러

```
Last_IO_Error: SSL connection error: SSL is required, but the server does not support it
```

**해결:** `CHANGE MASTER TO`에 `MASTER_SSL = 0` 추가

### 8.2 소켓 연결 에러 (Permission denied)

```
ERROR 2002 (HY000): Can't connect to local server through socket '/var/lib/mysql/mysql.sock' (13)
```

**해결:** `sudo mariadb -u root -p`로 접속

### 8.3 소켓 파일 없음

```
ERROR 2002 (HY000): Can't connect to local server through socket '...' (2)
```

**해결:** 소켓 위치 확인 후 경로 지정

```bash
find / -name "*.sock" 2>/dev/null
sudo mariadb -u root -p -S /var/lib/mysql/mysql.sock
```

### 8.4 Duplicate Key 에러

복제 중 중복 키 에러 발생 시 → 덤프 시점과 binlog position이 맞지 않음

**해결:** 덤프를 다시 뜨고, 해당 덤프의 position으로 `CHANGE MASTER TO` 재설정

---

## 9. 운영 마이그레이션 시나리오

### 9.1 상황: 크래시 전 덤프 + 복구 후 binlog 활용

```
[크래시 전 정상 덤프]
        ↓
[현재 10.5.9에 리스토어] → 복구 후 새 binlog 시작 (position 4)
        ↓
[데이터 복구 작업] → binlog에 기록됨
        ↓
[정상 운영 중] → binlog 계속 기록 중
```

### 9.2 마이그레이션 절차

1. **Slave(11.8)에 동일한 크래시 전 덤프 리스토어**
2. **Master(10.5.9)에서 복구 시점 binlog position 확인**
    
    ```sql
    SHOW BINARY LOGS;SHOW BINLOG EVENTS IN 'mysql-bin.000001' LIMIT 20;
    ```
    
3. **Slave에서 해당 position부터 복제 시작**
    
    ```sql
    CHANGE MASTER TO  MASTER_HOST = 'Master IP',  MASTER_PORT = 포트,  MASTER_USER = '계정',  MASTER_PASSWORD = '비밀번호',  MASTER_LOG_FILE = 'mysql-bin.000001',  MASTER_LOG_POS = 4,  MASTER_SSL = 0;START SLAVE;
    ```
    
4. **동기화 완료 확인 후 순간 전환**

### 9.3 주의사항

- `expire_logs_days` 확인 필수 (0이 아니면 binlog 삭제될 수 있음)
- 크로스 버전 복제 시 charset, binlog 호환성 테스트 필요
- 복제 전 반드시 테스트 환경에서 검증

---

## 10. binlog 관련 참고사항

### 10.1 binlog에 기록되는 것

- INSERT, UPDATE, DELETE (DML)
- CREATE, ALTER, DROP (DDL)
- GRANT, REVOKE

### 10.2 binlog에 기록되지 않는 것

- SELECT
- SHOW
- DESCRIBE

### 10.3 binlog 파일 번호가 증가하는 조건

- MariaDB 재시작
- `FLUSH LOGS` 실행
- `max_binlog_size` 초과 (기본 1GB)

### 10.4 binlog position

- position 0~3: 파일 헤더 (매직 넘버)
- position 4부터: 실제 이벤트 시작
- 첫 이벤트부터 재생하려면 `MASTER_LOG_POS = 4`



### 진행률 확인
```
# GB 단위
sudo cat /proc/1702/fdinfo/0 | grep pos | awk '{printf "%.2f GB\n", $2/1024/1024/1024}'

# 진행률(%)
sudo cat /proc/1702/fdinfo/0 | grep pos | awk '{printf "%.2f%%\n", $2/(191*1024*1024*1024)*100}'
```
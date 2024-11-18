
## 1. 변경사항

### 1.1 Airflow 이식
* 기존: 여러 Python 스크립트를 Airflow에서 실행시키기만 했음
* 변경: Airflow DAG로 이식하여 스케줄링 및 모니터링 가능하도록 개선
### 1.2 설정 관리 DB화
* 기존: config.ini에 하드코딩된 설정값을 불러와서 사용
* 변경: DB 테이블을 통한 설정 관리(예시)

```sql
-- 공통된 API호출시 페이로드에 관한 관리용 테이블 생성(이건 파이썬 코드내에 선언해도 무방할것같음)
CREATE TABLE config_ecos_common (
    config_id VARCHAR(50) PRIMARY KEY,
    config_value VARCHAR(200) NOT NULL,
    description VARCHAR(200),
    update_dtm DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 수집될 데이터에 대한 config.ini의 복잡한 하드코딩 설정을 DB화
CREATE TABLE config_ecos_codes (
    code_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    period CHAR(1) NOT NULL,
    table_code VARCHAR(20) NOT NULL,
    item_code_list TEXT NOT NULL,
    use_yn CHAR(1) DEFAULT 'Y',
    description VARCHAR(200),
    created_dtm DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_dtm DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category_period (category, period)
);
```

- 변경 예시
```python
# 변경 전(config.ini)
[ECOS-INTEREST_RATE_MONTH]
CATEGORY = INTEREST_RATE
API_URL = https://ecos.bok.or.kr/api/StatisticSearch
API_KEY = 8KD0RJO6MEUW4E540QG8
COLLECT_AT_ONCE_CNT = 1000
OUTPUT_FORMAT = json
LANG = kr
PERIOD = M
CODE_LIST = [
    {'TABLE_CODE' : '722Y001', 'ITEM_CODE_LIST': ['0101000']},
    {'TABLE_CODE' : '721Y001', 'ITEM_CODE_LIST': ['1010000']},
    {'TABLE_CODE' : '721Y001', 'ITEM_CODE_LIST': ['1030000']},
    {'TABLE_CODE' : '721Y001', 'ITEM_CODE_LIST': ['5030000']},
    {'TABLE_CODE' : '721Y001', 'ITEM_CODE_LIST': ['5020000']},
    {'TABLE_CODE' : '721Y001', 'ITEM_CODE_LIST': ['5040000']}]

[ECOS-STOCK_MONTH]
CATEGORY = STOCK
API_URL = https://ecos.bok.or.kr/api/StatisticSearch
API_KEY = 8KD0RJO6MEUW4E540QG8
COLLECT_AT_ONCE_CNT = 1000
OUTPUT_FORMAT = json
LANG = kr
PERIOD = M
CODE_LIST = [
    {'TABLE_CODE' : '901Y014', 'ITEM_CODE_LIST' : ['1050000']},
    {'TABLE_CODE' : '901Y014', 'ITEM_CODE_LIST' : ['1060000']},
    {'TABLE_CODE' : '901Y014', 'ITEM_CODE_LIST' : ['1070000']},
    #... 등등 굉장히 길었음

# 변경 후
def get_ecos_codes(category, period):
    """DB에서 설정 조회"""
    conn = maria_kmi_dw_db_connection()
    codes_df = pd.read_sql("""
        SELECT table_code, item_code_list
        FROM config_ecos_codes
        WHERE category = %s 
        AND period = %s
        AND use_yn = 'Y'
    """, conn, params=[category, period])
    return codes_df
```

### 1.3 데이터 적재 프로세스 개선
* 기존: 매번 전체 데이터 MERGE(항목 시작 전 비교 불가)
* 변경: 최신 데이터 비교 후 필요한 경우만 적재

```python
def check_latest_data(new_df, table_name):
    """최신 데이터 비교 후 업데이트 필요 여부 반환"""
```



## 터미널 코드 -> 터미널명 딕셔너리 생성 쿼리
```
-- 소스 테이블
CREATE TABLE IF NOT EXISTS logs.terminal_code_map
(
    terminal_code    String,
    terminal_name_kr String,
    terminal_name_en String
)
ENGINE = MergeTree()
ORDER BY terminal_code;

-- 터미널 데이터 삽입
INSERT INTO logs.terminal_code_map VALUES
('BCTHD010', 'BCT 신항',    'BCT'),
('BCTOC050', '허치슨 부산',   'HKT'),
('BICTC010', 'BPT 감만',    'BPTG'),
('BNCTC050', 'BNCT 신항',   'BNCT'),
('DGTBC050', 'DGT 신항',    'DGT'),
('GCTOC050', '허치슨 신감만',  'HKTG'),
('HJNPC010', '한진 신항',    'HJNC'),
('HPNTC050', '현대 신항',    'HPNT'),
('PECTC050', 'BPT 신선대',   'BPTS'),
('PNCOC010', '부산 신항',    'PNC'),
('PNITC050', '국제 신항',    'PNIT');

-- 사전 생성
CREATE DICTIONARY IF NOT EXISTS logs.terminal_dict
(
    terminal_code    String,
    terminal_name_kr String,
    terminal_name_en String
)
PRIMARY KEY terminal_code
SOURCE(CLICKHOUSE(
    DB 'logs'
    TABLE 'terminal_code_map'
))
LAYOUT(FLAT())
LIFETIME(3600);

-- UDF 생성
CREATE FUNCTION IF NOT EXISTS terminal_to_en AS
    (code) -> dictGetOrDefault('logs.terminal_dict', 'terminal_name_en', code, code);```


## 목록 조회
```
SELECT
    service_key,
    latest_timestamp                                                     AS timestamp,
    if(terminal != '', terminal, concat(in_terminal, '-', out_terminal))  AS terminal,
    if(truck_no != '', truck_no, splitByChar('_', service_key)[2])        AS truck_no,
    con_no,
    service_type,
    in_out,
    func_name
FROM (
    SELECT
        max(timestamp)                                                    AS latest_timestamp,
        service_key,
        argMaxIf(lower(service_type), timestamp, service_type != '')       AS service_type,
        argMaxIf(con_no,       timestamp, con_no != '')                    AS con_no,
        argMaxIf(in_out,       timestamp, in_out != '')                    AS in_out,
        argMaxIf(func_name,    timestamp, func_name != '')                 AS func_name,
        argMaxIf(terminal,     timestamp, terminal != '')                  AS terminal,
        argMaxIf(truck_no,     timestamp, truck_no != '')                  AS truck_no,
        argMaxIf(in_terminal,  timestamp, in_terminal != '')               AS in_terminal,
        argMaxIf(out_terminal, timestamp, out_terminal != '')              AS out_terminal
    FROM (
        SELECT *
        FROM logs.blockchain_logs_prod
        WHERE ((type = 'req' AND func_name != 'GetTransHistory')
               OR (type = 'res' AND func_name = 'GetTransHistory'))
        AND module = 'bc'                
    ) a
    GROUP BY service_key
    LIMIT 1000
) 
```
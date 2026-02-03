
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
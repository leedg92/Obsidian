
TB_COPARN(컨테이너 사전통지) 테이블과 TB_RF_ONOFF(리퍼 전원상태) 테이블을 LEFT JOIN하여,
아직 사용되지 않은(USED_DATE IS NULL) 반입/반출 모드(IO_MODE가 'I' 또는 'O')의 컨테이너 정보 중
마지막 처리 순번 이후의 새로운 데이터(TRANS_ODR_NO > 기준값)이면서 아직 차량예약 인터페이스에 전송되지 않은(IF_VEHICLE_BOOKING에 존재하지 않는) 건들을 대상으로, 중복을 제거하고(GROUP BY + HAVING COUNT(*)=1) 문서키 순으로 정렬하여 최대 300건까지 조회



```sql
-- =====================================================
-- COPINO 사전통지 조회 쿼리
-- 목적: 터미널 도착 전 컨테이너 사전통지 정보 조회
-- =====================================================

SELECT * FROM (
    -- 외부 SELECT: 중복 제거 및 최종 결과 정렬
    SELECT 
        -- 기본 문서 정보
        docKey,                    -- 문서 키 (SIC_NO 또는 TRANS_ODR_NO)
        docStatus,                 -- 문서 상태 (고정값 '9')
        senderId,                  -- 송신자 ID (실제 운송사 또는 기본 운송사)
        terminalId,                -- 터미널 ID (고정값 'HJNPC010')
        
        -- 차량 정보
        truckCode,                 -- 차량 코드 (TRUCK_ID)
        truckNo,                   -- 차량 번호
        
        -- 출발지/목적지 정보
        fromPlaceCode,             -- 출발지 코드 (반입시: FROM_DEPOT, 반출시: 'HJNPC010')
        fromPlaceName,             -- 출발지 명칭
        toPlaceCode,               -- 목적지 코드 (반입시: 'HJNPC010', 반출시: TO_DEPOT)
        toPlaceName,               -- 목적지 명칭
        toCy,                      -- 목적 야드 (TO_BONDAREA_NO)
        
        -- 시간 정보
        inOutReserveTime,          -- 반입/반출 예약시간
        outExpirationDate,         -- 반출 만료일 (빈값)
        inExpirationDate,          -- 반입 만료일 (빈값)
        
        -- 운송사 정보
        truckerId,                 -- 운송사 ID
        bondedTruckerCode,         -- 보세운송사 코드
        
        -- 컨테이너 정보
        conNo,                     -- 컨테이너 번호
        conType,                   -- 컨테이너 타입 (SZTP)
        transshipType,             -- 환적 타입 ('Z'클래스면 '14', 아니면 빈값)
        feType,                    -- FE 타입 ('F'면 '5', 아니면 '4')
        inOut,                     -- 반입/반출 구분 ('O'=1:반출, 'I'=2:반입)
        expImpType,                -- 수출/수입 타입 (빈값)
        
        -- 특수 화물 정보
        temp,                      -- 설정 온도
        tempUnit,                  -- 온도 단위 (온도가 있으면 'CEL')
        imdgCode,                  -- IMDG 코드 (위험물)
        unnoCode,                  -- UN 번호
        
        -- 선적 정보
        blNo,                      -- B/L 번호
        bookingNo,                 -- 부킹 번호
        conWeight,                 -- 컨테이너 중량
        conSealNo,                 -- 컨테이너 실 번호
        shippingVoyageNo,          -- 선사 항차 번호
        terminalShipCode,          -- 터미널 선박 코드
        arrivalYear,               -- 도착 년도
        terminalShipVoyageNo,      -- 터미널 선박 항차 번호
        shippingCode,              -- 선사 코드
        pod,                       -- 양하항
        pol,                       -- 적하항
        
        -- 초과 치수 정보
        overLength,                -- 초과 길이 (전면 + 후면)
        overWidth,                 -- 초과 폭 (우현 + 좌현)
        overHeight,                -- 초과 높이
        
        -- 시스템 정보
        tms,                       -- TMS (VAN_CODE)
        tsYn,                      -- 환적 여부 ('Z'클래스면 'Y')
        sendResult,                -- 전송 결과 (고정값 'S')
        xRayInspYN,                -- X-RAY 검사 여부 (빈값)
        expiredTime,               -- 만료 시간
        reeferPowerStatus,         -- 리퍼 전원 상태 ('IN'/'OUT')
        inOutPossible,             -- 반입/반출 가능 여부 ('Y'/'N')
        copinoCheckStatus,         -- COPINO 체크 상태
        copinoErrType,             -- COPINO 오류 타입 ('NM'/'LE')
        receiveTime,               -- 수신 시간
        
        -- 표시용 정보
        conTypeDisplayName,        -- 컨테이너 타입 표시명 (TANK/FLATRACK/RF/DRY)
        commodityType,             -- 화물 타입 (RF/DG/OOG/DRY 등)
        controlNo,                 -- 제어 번호
        staffCd,                   -- 담당자 코드
        
        -- 조건절에 사용되는 원본 데이터 (디버깅용)
        SZTP2 as orgSztp2,         -- 원본 SZTP2
        CARGO_TYPE as orgCargoType, -- 원본 CARGO_TYPE
        CLASS as orgClass,          -- 원본 CLASS
        USED_DATE as orgUsedDate,   -- 원본 USED_DATE
        TRANS_ODR_NO as orgTransOdrNo, -- 원본 TRANS_ODR_NO
        
        COUNT(*) as record_count   -- 레코드 개수 (중복 체크용)
    FROM (
        -- 내부 SELECT: 실제 데이터 조회 및 변환
        SELECT 
            -- 문서 키: SIC_NO가 있으면 SIC_NO, 없으면 TRANS_ODR_NO 사용
            NVL(C.SIC_NO, TRANS_ODR_NO) AS docKey,
            '9' AS docStatus,  -- 생성(9)
            
            -- 송신자: 실제 운송사가 있으면 사용, 없으면 기본 운송사 사용
            NVL(ACTUAL_TRUCKER, TRUCKER) AS senderId,
            'HJNPC010' AS terminalId,  -- 고정값
            
            -- 차량 정보
            TRUCK_ID AS truckCode,
            TRUCK_NO AS truckNo,
            
            -- 출발지/목적지: IO_MODE에 따라 분기
            DECODE(IO_MODE, 'I', FROM_DEPOT, 'HJNPC010') AS fromPlaceCode,
            DECODE(IO_MODE, 'I', '', 'HJNC') AS fromPlaceName,
            DECODE(IO_MODE, 'I', 'HJNPC010', TO_DEPOT) AS toPlaceCode,
            DECODE(IO_MODE, 'I', 'HJNC', '') AS toPlaceName,
            TO_BONDAREA_NO AS toCy,
            
            -- 시간 정보
            TO_CHAR(EIO_DATE, 'YYYYMMDDHHMM') AS inOutReserveTime,
            '' AS outExpirationDate,   -- 빈값
            '' AS inExpirationDate,    -- 빈값
            
            -- 운송사 정보
            TRUCKER AS truckerId,
            CUSTOM_TRUCKER AS bondedTruckerCode,
            
            -- 컨테이너 기본 정보
            TRIM(C.CNTR_NO) AS conNo,  -- 공백 제거
            SZTP AS conType,
            
            -- 환적 및 FE 타입
            CASE WHEN CLASS='Z' THEN '14' ELSE '' END AS transshipType,
            CASE WHEN FE='F' THEN '5' ELSE '4' END AS feType,
            
            -- 반입/반출 구분
            CASE WHEN IO_MODE='O' THEN '1' WHEN IO_MODE='I' THEN '2' ELSE '' END AS inOut,
            '' AS expImpType,  -- 빈값
            
            -- 온도 정보
            SET_TEMP AS temp,
            CASE WHEN SET_TEMP IS NOT NULL THEN 'CEL' ELSE '' END AS tempUnit,
            
            -- 위험물 정보
            IMDG AS imdgCode,
            UNNO AS unnoCode,
            
            -- 선적 서류 정보
            BL_NO AS blNo,
            BOOKING_NO AS bookingNo,
            WGT AS conWeight,
            SEAL_NO1 AS conSealNo,
            
            -- 선박 정보
            USER_VOY AS shippingVoyageNo,
            C.VSL_CD AS terminalShipCode,
            C.CALL_YEAR AS arrivalYear,
            C.CALL_SEQ AS terminalShipVoyageNo,
            PTNR_CODE AS shippingCode,
            POD AS pod,
            POL AS pol,
            
            -- 초과 치수 계산
            C.OV_FORE + C.OV_AFT AS overLength,    -- 전면 + 후면
            C.OV_STBD + C.OV_PORT AS overWidth,    -- 우현 + 좌현
            C.OV_HEIGHT AS overHeight,
            
            -- 기타 시스템 정보
            C.VAN_CODE AS tms,
            CASE WHEN CLASS='Z' THEN 'Y' ELSE '' END AS tsYn,
            'S' AS sendResult,  -- 고정값
            '' AS xRayInspYN,   -- 빈값
            
            -- 만료시간: EXPIRE_DATE가 있으면 사용, 없으면 현재시간+3일
            NVL(TO_CHAR(C.EXPIRE_DATE, 'YYYYMMDDHH24MI'),
                TO_CHAR(SYSDATE + 3, 'YYYYMMDDHH24MI')) AS expiredTime,
            
            -- 리퍼 전원 상태 판단
            (CASE
                WHEN R.PLUGOUT_TIME IS NULL AND R.PLUGIN_TIME IS NOT NULL THEN 'IN'
                WHEN R.PLUGOUT_TIME IS NOT NULL THEN 'OUT'
            END) AS reeferPowerStatus,
            
            -- 반입/반출 가능 여부 및 상태
            CASE WHEN REMARK IS NULL THEN 'Y' ELSE 'N' END inOutPossible,
            REMARK AS copinoCheckStatus,
            CASE WHEN REMARK IS NULL THEN 'NM' ELSE 'LE' END copinoErrType,
            
            TO_CHAR(EDI_IO_DATE, 'YYYYMMDDHH24MISS') AS receiveTime,
            
            -- 컨테이너 타입 표시명 변환 (SZTP2의 3번째 문자 기준)
            CASE    
                WHEN SUBSTR(C.SZTP2,3,1) = 'T' THEN 'TANK'      -- 탱크
                WHEN SUBSTR(C.SZTP2,3,1) = 'P' THEN 'FLATRACK'  -- 플랫랙
                WHEN SUBSTR(C.SZTP2,3,1) = 'R' THEN 'RF'        -- 리퍼
                WHEN SUBSTR(C.SZTP2,3,1) = 'G' THEN 'DRY'       -- 드라이
                ELSE 'DRY'
            END AS conTypeDisplayName,
            
            -- 화물 타입 변환
            CASE 
                WHEN C.CARGO_TYPE IN ('DR', 'RF') THEN 'RF'      -- 리퍼
                WHEN C.CARGO_TYPE = 'DG' THEN 'DG'               -- 위험물
                WHEN C.CARGO_TYPE = 'AK' THEN 'OOG'              -- 초과치수
                WHEN C.CARGO_TYPE IN ('BN', 'GP', 'DO', 'ED', 'MT') THEN 'DRY'  -- 일반
                ELSE C.CARGO_TYPE
            END AS commodityType,
            
            C.CONTROL_NO AS controlNo,
            C.STAFF_CD AS staffCd,
            
            -- 조건절에 사용되는 원본 데이터도 함께 SELECT
            C.SZTP2,
            C.CARGO_TYPE,
            C.CLASS,
            C.USED_DATE,
            C.TRANS_ODR_NO
        FROM 
            -- 메인 테이블: 컨테이너 사전통지 정보
            TB_COPARN C,
            
            -- 서브쿼리: 리퍼 컨테이너 전원 상태 (최신 정보만)
            (SELECT SEQ, VSL_CD, CALL_SEQ, CALL_YEAR, CNTR_NO, PLUGIN_TIME, PLUGOUT_TIME
             FROM (
                 SELECT
                     ROW_NUMBER() OVER (PARTITION BY VSL_CD, CALL_SEQ, CALL_YEAR, CNTR_NO 
                                       ORDER BY ODR_SEQ DESC) SEQ,
                     VSL_CD, CALL_SEQ, CALL_YEAR, CNTR_NO, PLUGIN_TIME, PLUGOUT_TIME
                 FROM TB_RF_ONOFF
             )
             WHERE SEQ = 1  -- 컨테이너별 최신 전원 상태만
            ) R
        WHERE 1=1
          -- LEFT JOIN 조건: 리퍼 전원 상태와 연결
          AND C.VSL_CD = R.VSL_CD (+)
          AND C.CALL_YEAR = R.CALL_YEAR (+)
          AND C.CALL_SEQ = R.CALL_SEQ (+)
          AND C.CNTR_NO = R.CNTR_NO (+)
          
          -- 핵심 필터 조건들
          AND C.IO_MODE IN ('I','O')     -- 반입(I) 또는 반출(O) 모드만
          AND C.USED_DATE IS NULL        -- 아직 사용되지 않은 데이터 (터미널 도착 전)
          
          -- 마지막 처리된 순번 이후의 새로운 데이터만
          AND C.TRANS_ODR_NO > (SELECT COPINO_IO_IDX 
                                FROM HJNC_PROD_IF.IF_VEHICLE_SCHEDULE_LOG 
                                WHERE SCH_ID = 'COPINO_SCH')
          
          -- 이미 인터페이스 테이블에 적재된 건은 제외
          AND NOT EXISTS (
              SELECT 1 FROM HJNC_PROD_IF.IF_VEHICLE_BOOKING I 
              WHERE I.DOC_KEY = C.SIC_NO
          )
          
          -- 테스트 차량 제외
          AND C.TRUCK_NO != '그룹00가0000'
    )
    -- GROUP BY: 중복 제거를 위한 그룹핑
    GROUP BY 
        docKey,docStatus,senderId,terminalId,truckCode,truckNo,fromPlaceCode,fromPlaceName,
        toPlaceCode,toPlaceName,toCy,inOutReserveTime,outExpirationDate,inExpirationDate,
        truckerId,bondedTruckerCode,conNo,conType,transshipType,feType,inOut,expImpType,
        temp,tempUnit,imdgCode,unnoCode,blNo,bookingNo,conWeight,conSealNo,shippingVoyageNo,
        terminalShipCode,arrivalYear,terminalShipVoyageNo,shippingCode,pod,pol,overLength,
        overWidth,overHeight,tms,tsYn,sendResult,xRayInspYN,expiredTime,reeferPowerStatus,
        inOutPossible,copinoCheckStatus,copinoErrType,receiveTime,conTypeDisplayName,
        commodityType,controlNo,staffCd,SZTP2,CARGO_TYPE,CLASS,USED_DATE,TRANS_ODR_NO
    
    -- 중복 데이터 제거: 같은 조건의 레코드가 1개인 것만
    HAVING COUNT(*) = 1
    
    -- 결과 정렬
    ORDER BY docKey
)
-- 최대 300건까지만 조회 (배치 처리 제한)
WHERE ROWNUM <= 300
```
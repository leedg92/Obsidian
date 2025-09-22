
TB_COPARN(컨테이너 사전통지) 테이블과 TB_RF_ONOFF(리퍼 전원상태) 테이블을 LEFT JOIN하여,
아직 사용되지 않은(USED_DATE IS NULL) 반입/반출 모드(IO_MODE가 'I' 또는 'O')의 컨테이너 정보 중
마지막 처리 순번 이후의 새로운 데이터(TRANS_ODR_NO > 기준값)이면서 아직 차량예약 인터페이스에 전송되지 않은(IF_VEHICLE_BOOKING에 존재하지 않는) 건들을 대상으로, 중복을 제거하고(GROUP BY + HAVING COUNT(*)=1) 문서키 순으로 정렬하여 최대 300건까지 조회



```sql
SELECT * FROM (

SELECT

NVL(C.SIC_NO, TRANS_ODR_NO) AS docKey, -- SIC 번호 또는 운송주문번호를 문서키로 사용

'9' AS docStatus, -- 문서상태 (9: 생성, 1: 삭제)

NVL(ACTUAL_TRUCKER, TRUCKER) AS senderId, -- 실제운송사코드 우선, 없으면 운송사코드 사용

'HJNPC010' AS terminalId, -- 터미널ID (한진 고정값)

TRUCK_ID AS truckCode, -- 트럭ID

TRUCK_NO AS truckNo, -- 트럭번호

DECODE(IO_MODE, 'I', FROM_DEPOT, 'HJNPC010') AS fromPlaceCode, -- 출발지코드

DECODE(IO_MODE, 'I', '', 'HJNC') AS fromPlaceName, -- 출발지명

DECODE(IO_MODE, 'I', 'HJNPC010', TO_DEPOT) AS toPlaceCode, -- 도착지코드

DECODE(IO_MODE, 'I', 'HJNC', '') AS toPlaceName, -- 도착지명

TO_BONDAREA_NO AS toCy, -- 목적지 보세구역번호

TO_CHAR(EIO_DATE, 'YYYYMMDDHHMM') AS inOutReserveTime, -- 반입반출예약시간

'' AS outExpirationDate, -- 반출만료일자

'' AS inExpirationDate, -- 반입만료일자

TRUCKER AS truckerId, -- 운송사코드

CUSTOM_TRUCKER AS bondedTruckerCode, -- 세관보세운송 운송사코드

TRIM(C.CNTR_NO) AS conNo, -- 컨테이너번호 (공백제거)

SZTP AS conType, -- 컨테이너 크기타입(1)

CASE WHEN CLASS='Z' THEN '14' ELSE '' END AS transshipType, -- 환적타입

CASE WHEN FE='F' THEN '5' ELSE '4' END AS feType, -- 컨테이너구분 (F:적컨=5, E:공컨=4)

CASE WHEN IO_MODE='O' THEN '1' WHEN IO_MODE='I' THEN '2' ELSE '' END AS inOut, -- 반입반출구분 (O:반출=1, I:반입=2)

'' AS expImpType, -- 수출입구분(''로 고정)

SET_TEMP AS temp, -- 설정온도

CASE WHEN SET_TEMP IS NOT NULL THEN 'CEL' ELSE '' END AS tempUnit, -- 온도단위 (설정온도 있을시 섭씨)

IMDG AS imdgCode, -- IMDG 위험물코드

UNNO AS unnoCode, -- UN 위험물번호

BL_NO AS blNo, -- B/L NO

BOOKING_NO AS bookingNo, -- 부킹번호

WGT AS conWeight, -- 컨테이너 중량

SEAL_NO1 AS conSealNo, -- 컨테이너 씰넘버(봉인번호)

USER_VOY AS shippingVoyageNo, -- 선박번호(항차)

C.VSL_CD AS terminalShipCode, -- 선박코드

C.CALL_YEAR AS arrivalYear, -- 입항년도

C.CALL_SEQ AS terminalShipVoyageNo, -- 입항순번

PTNR_CODE AS shippingCode, -- 파트너코드

POD AS pod, -- 양하항

POL AS pol, -- 적하항

C.OV_FORE + C.OV_AFT AS overLength, -- 전후 돌출길이 합계

C.OV_STBD + C.OV_PORT AS overWidth, -- 좌우 돌출폭 합계

C.OV_HEIGHT AS overHeight, -- 돌출높이

C.VAN_CODE AS tms, -- 밴코드(TMS코드 - 'TSS','KL','KT' 등)

CASE WHEN CLASS='Z' THEN 'Y' ELSE '' END AS tsYn, -- TSS여부

'S' AS sendResult, -- 전송결과

'' AS xRayInspYN, -- X-Ray 검사여부

NVL(TO_CHAR(C.EXPIRE_DATE, 'YYYYMMDDHH24MI'),TO_CHAR(SYSDATE + 3, 'YYYYMMDDHH24MI')) AS expiredTime, -- 만료시간 (없으면 현재+3일)

(

CASE

WHEN R.PLUGOUT_TIME IS NULL AND R.PLUGIN_TIME IS NOT NULL THEN 'IN'

WHEN R.PLUGOUT_TIME IS NOT NULL THEN 'OUT'

END

) AS reeferPowerStatus, -- 냉컨 전원상태(플러그인만 있고 플러그아웃 없으면 플러그인상태, 플러그아웃 시간이 있으면 플러그아웃상태)

CASE WHEN REMARK IS NULL THEN 'Y' ELSE 'N' END inOutPossible, -- 반입반출가능여부 (비고없으면 가능)

REMARK AS copinoCheckStatus, -- COPINO 체크상태 (비고사항)

CASE WHEN REMARK IS NULL THEN 'NM' ELSE 'LE' END copinoErrType, -- COPINO 오류타입 (NM:정상, LE:오류)

TO_CHAR(EDI_IO_DATE, 'YYYYMMDDHH24MISS') AS receiveTime, -- EDI 수신?일시

CASE

WHEN SUBSTR(C.SZTP2,3,1) = 'T' THEN 'TANK' -- 탱크컨테이너

WHEN SUBSTR(C.SZTP2,3,1) = 'P' THEN 'FLATRACK' -- 플랫랙컨테이너

WHEN SUBSTR(C.SZTP2,3,1) = 'R' THEN 'RF' -- 냉동컨테이너

WHEN SUBSTR(C.SZTP2,3,1) = 'G' THEN 'DRY' -- 드라이컨테이너

ELSE 'DRY'

END AS conTypeDisplayName, -- 컨테이너타입 표시명

CASE

/*

AK : OOG

BB : Break Bulk

BN : Bundle

DG : Dangerous

DO : DG_OOG

DR : Reefer_DG

ED : Empty_DG

FR : Fragile

GP : General

MT : Empty

RF : Reefer

*/

WHEN C.CARGO_TYPE IN ('DR', 'RF') THEN 'RF' -- 냉컨

WHEN C.CARGO_TYPE = 'DG' THEN 'DG' -- 위험물

WHEN C.CARGO_TYPE = 'AK' THEN 'OOG' -- 특수화물

WHEN C.CARGO_TYPE IN ('BN', 'GP', 'DO', 'ED', 'MT') THEN 'DRY' -- 일반화물

ELSE C.CARGO_TYPE

END AS commodityType, -- 컨테이너 내용물 코드

C.CONTROL_NO AS controlNo, -- 관리번호

C.STAFF_CD AS staffCd, -- 담당자코드

/* 조건절에 사용되는 원본 데이터도 함께 SELECT */

C.SZTP2, -- 컨테이너 크기타입(2)

C.CARGO_TYPE, -- 컨테이너 타입

C.CLASS, -- 클래스??????

C.USED_DATE, -- 사용일자??

C.TRANS_ODR_NO -- 운송주문번호

FROM

TB_COPARN C, -- 컨테이너 선적정보 메인테이블

(

SELECT SEQ, VSL_CD, CALL_SEQ, CALL_YEAR, CNTR_NO, PLUGIN_TIME, PLUGOUT_TIME

FROM

(

SELECT

ROW_NUMBER() OVER (PARTITION BY VSL_CD, CALL_SEQ, CALL_YEAR, CNTR_NO ORDER BY ODR_SEQ DESC) SEQ,

VSL_CD, CALL_SEQ, CALL_YEAR, CNTR_NO, PLUGIN_TIME, PLUGOUT_TIME -- 선박코드, 입항순번, 입항년도, 컨테이너번호, 플러그인시간, 플러그아웃시간

FROM TB_RF_ONOFF -- 냉컨 전원 ON/OFF 관리테이블

)

WHERE 1=1

AND SEQ = 1

)R -- 컨테이너별 가장 최근 냉동 전원상태

WHERE 1=1

AND C.VSL_CD = R.VSL_CD (+) -- 선박코드 Left Outer Join

AND C.CALL_YEAR = R.CALL_YEAR (+) -- 입항년도 Left Outer Join

AND C.CALL_SEQ = R.CALL_SEQ (+) -- 입항순번 Left Outer Join

AND C.CNTR_NO = R.CNTR_NO (+) -- 컨테이너번호 Left Outer Join

AND C.IO_MODE IN ('I','O') -- 반입(I) 또는 반출(O)만 조회

AND C.USED_DATE IS NULL -- 사용일자가 NULL인 것만 (아직 안들어온 건..?)

AND C.TRANS_ODR_NO > (SELECT COPINO_IO_IDX FROM HJNC_PROD_IF.IF_VEHICLE_SCHEDULE_LOG WHERE SCH_ID = 'COPINO_SCH') -- 인터페이스 테이블에 마지막 처리된 운송주문번호 이후 건만

AND NOT EXISTS ( -- 인터페이스 테이블에 이미 적재된 건은 제외

SELECT 1 FROM HJNC_PROD_IF.IF_VEHICLE_BOOKING I WHERE I.DOC_KEY = C.SIC_NO

)

AND C.TRUCK_NO != '그룹00가0000' -- 테스트용 트럭번호 제외

)

GROUP BY docKey,docStatus,senderId,terminalId,truckCode,truckNo,fromPlaceCode,fromPlaceName,toPlaceCode,toPlaceName,toCy,inOutReserveTime,

outExpirationDate,inExpirationDate,truckerId,bondedTruckerCode,conNo,conType,transshipType,feType,inOut,expImpType,temp,tempUnit,imdgCode,

unnoCode,blNo,bookingNo,conWeight,conSealNo,shippingVoyageNo,terminalShipCode,arrivalYear,terminalShipVoyageNo,shippingCode,pod,pol,

overLength,overWidth,overHeight,tms,tsYn,sendResult,xRayInspYN,expiredTime,reeferPowerStatus,inOutPossible,copinoCheckStatus,copinoErrType,

receiveTime,conTypeDisplayName,commodityType,controlNo,staffCd,

SZTP2,CARGO_TYPE,CLASS,USED_DATE,TRANS_ODR_NO

HAVING COUNT(*)=1 -- 중복 제거

ORDER BY docKey

)

WHERE ROWNUM <= 300
```
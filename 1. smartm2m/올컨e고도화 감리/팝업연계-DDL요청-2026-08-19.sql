-- ============================================================================
-- 관제 메인 공지팝업 연계 (CHMAN-173) — 체인포털 적용 요청 DDL
-- 대상 테이블: chainportaldb.tb_a_popup_manage_i
-- 작성일: 2026-08-19
--
-- 배경
--   관제시스템이 bctrans API 로 앱 메인 공지팝업을 등록·수정·삭제한다.
--   저장처가 bctransdbx 가 아니라 체인포털 DB 라 컬럼 추가를 요청드린다.
--
-- 운영에 요청드리는 것은 STEP 1 (POPUP_PRIORITY 컬럼) 하나다.
-- STEP 2 는 개발망 전용이며 2026-08-19 에 이미 적용했다(운영은 원래 정상).
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 실행 전 확인
-- ----------------------------------------------------------------------------
SHOW COLUMNS FROM chainportaldb.tb_a_popup_manage_i;


-- ----------------------------------------------------------------------------
-- STEP 1. 팝업 노출 우선순위 컬럼  ※ 운영 적용 요청
-- ----------------------------------------------------------------------------
-- 관제가 지정한 노출 순서를 담는다. 값이 작을수록 상위에 노출된다.
-- 기존 행은 DEFAULT 1 로 채워진다.
--
-- 앱 팝업 조회 정렬이 이 컬럼을 1차 기준으로 쓰도록 바뀐다.
--   변경 전: order by POPUP_BGNDE
--   변경 후: order by POPUP_PRIORITY asc, POPUP_BGNDE
--
-- 기존 포털 등록 팝업은 전부 POPUP_PRIORITY=1 이 되어 1차 기준에서 동률이 되고,
-- 2차 기준이 POPUP_BGNDE 이므로 **기존 팝업들끼리의 노출 순서는 지금과 동일하게 유지된다.**
-- 관제가 우선순위를 지정한 팝업만 그 위로 올라온다.

ALTER TABLE chainportaldb.tb_a_popup_manage_i
    ADD COLUMN `POPUP_PRIORITY` int(11) NOT NULL DEFAULT 1 COMMENT '팝업우선순위(작을수록 상위)';


-- ----------------------------------------------------------------------------
-- STEP 2. POPUP_ID 를 PK + AUTO_INCREMENT 로  ※ 개발망 전용 — 운영은 이미 적용되어 있음
-- ----------------------------------------------------------------------------
-- 개발망에는 PK 도 인덱스도 없어 INSERT 시 POPUP_ID 에 NULL 이 들어가고 있었다.
-- 등록 응답으로 팝업ID 를 관제에 돌려줘야 이후 수정·삭제가 가능하므로 운영 스키마에 맞췄다.
-- (2026-08-19 적용 완료. 운영에서는 실행하지 않는다)
--
-- 선행: POPUP_ID 가 NULL 인 행이 있으면 PK 를 걸 수 없다.
--   SELECT COUNT(*) FROM chainportaldb.tb_a_popup_manage_i WHERE POPUP_ID IS NULL;
--
-- ALTER TABLE chainportaldb.tb_a_popup_manage_i
--     MODIFY COLUMN `POPUP_ID` int(11) NOT NULL COMMENT '팝업ID',
--     ADD PRIMARY KEY (`POPUP_ID`);
--
-- ALTER TABLE chainportaldb.tb_a_popup_manage_i
--     MODIFY COLUMN `POPUP_ID` int(11) NOT NULL AUTO_INCREMENT COMMENT '팝업ID';


-- ----------------------------------------------------------------------------
-- 적용 후 검증
-- ----------------------------------------------------------------------------
SHOW COLUMNS FROM chainportaldb.tb_a_popup_manage_i;

-- 기존 행이 전부 우선순위 1 로 채워졌는지
SELECT POPUP_PRIORITY, COUNT(*) FROM chainportaldb.tb_a_popup_manage_i GROUP BY POPUP_PRIORITY;


-- ----------------------------------------------------------------------------
-- 롤백
-- ----------------------------------------------------------------------------
-- ALTER TABLE chainportaldb.tb_a_popup_manage_i DROP COLUMN `POPUP_PRIORITY`;
--   ※ 되돌리면 앱 조회 정렬도 함께 원복해야 한다(order by POPUP_BGNDE).

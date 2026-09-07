-- 약관 채번 주체 이전 (CHENH-133 / 2026-08-28)
-- 관제가 약관 DB 를 두지 않기로 하면서 TERMS_ID 채번이 bctrans 로 넘어왔다.
-- 이미 allcone_terms_* 3종이 적용된 환경에만 실행한다. 신규 환경은 create_allcone_terms_tables.sql 하나면 된다.
--
-- 적용 대상: 개발망(적용 필요) / 운영망(약관 기능 미배포 — 배포 시점에 create 스크립트로 한 번에)


-- ── STEP 1. 현재 상태 확인 ─────────────────────────────────────────
-- AUTO_INCREMENT 시작값이 기존 최대 TERMS_ID 보다 커야 한다.
SELECT IFNULL(MAX(TERMS_ID), 0) AS max_terms_id
  FROM bctransdbx.allcone_terms_version;


-- ── STEP 2. TERMS_ID 를 AUTO_INCREMENT 로 ──────────────────────────
-- PK 라 별도 인덱스 추가 없이 MODIFY 만으로 된다.
ALTER TABLE bctransdbx.allcone_terms_version
    MODIFY COLUMN TERMS_ID BIGINT UNSIGNED NOT NULL AUTO_INCREMENT
    COMMENT 'PK. bctrans 가 채번한다 (관제는 약관 DB 를 두지 않는다)';

-- STEP 1 결과가 0 이 아니면 그 값 + 1 로 맞춘다. 0 이면 이 문장은 건너뛴다.
-- ALTER TABLE bctransdbx.allcone_terms_version AUTO_INCREMENT = <max_terms_id + 1>;


-- ── STEP 3. VERSION 컬럼 주석 갱신 ─────────────────────────────────
ALTER TABLE bctransdbx.allcone_terms_version
    MODIFY COLUMN VERSION INT NOT NULL
    COMMENT '종류 내 개정 버전. bctrans 가 MAX(VERSION)+1 로 채번한다';


-- ── STEP 4. CTRL_STATUS 제거 ───────────────────────────────────────
-- 관제 상태값 대조용이었다. 원본이 bctrans 한 곳이 되어 대조할 대상이 없어졌다.
ALTER TABLE bctransdbx.allcone_terms_version
    DROP COLUMN CTRL_STATUS;


-- ── STEP 5. 검증 ───────────────────────────────────────────────────
SHOW CREATE TABLE bctransdbx.allcone_terms_version;

-- AUTO_INCREMENT 가 기존 최대값보다 큰지 확인
SELECT AUTO_INCREMENT
  FROM information_schema.TABLES
 WHERE TABLE_SCHEMA = 'bctransdbx'
   AND TABLE_NAME   = 'allcone_terms_version';

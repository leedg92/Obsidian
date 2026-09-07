-- 지오펜스 통보 블록 진입 템플릿 (CHENH-149 / 2026-08-31)
-- 블록 진입(BLOCK_IN) 영역 전용 전송 body. 기본 템플릿(COMMON)은 그대로 두고 새로 추가한다.
-- 명세: 올컨e-터미널연계-인터페이스명세-2026-08-31.xlsx 「지오펜싱 진출입 이벤트 전송」
--
-- 적용 대상: 개발망(적용 필요) / 운영망(터미널 연계 확정 후)


-- ── STEP 1. 현재 템플릿 확인 ───────────────────────────────────────
SELECT TEMPLATE_CODE, TEMPLATE_NAME, DEFAULT_YN, DATA_STATUS
  FROM bctransdbx.gps_geofence_notify_template;


-- ── STEP 2. 블록 진입 템플릿 추가 ──────────────────────────────────
-- COMMON 대비 차이: areaBlockCode·conLoc 추가 / orderList → eslipList / bkNo·etcOrderList 제거
INSERT INTO bctransdbx.gps_geofence_notify_template
    (TEMPLATE_CODE, TEMPLATE_NAME, BODY_TEMPLATE, DEFAULT_YN, DATA_STATUS)
VALUES ('BLOCK_IN', '블록 진입 통보(IF-GEO-ALLCONE-001)', '{
  "truckNumber":   "${event.truckNumber}",
  "areaId":        "${event.areaId}",
  "areaTp":        "${event.areaTp}",
  "areaBlockCode": "${event.terminalExternalCode}",
  "eventTp":       "${event.eventTp}",
  "eventDt":       "${event.eventDt}",
  "eslipList": {
    "@each": "orders",
    "@as": {
      "terminalCode":  "${terminalCode}",
      "transportCode": "${transportCode}",
      "transportTp":   "${transportTp}",
      "conNo":         "${conNo}",
      "inOut":         "${inOut}",
      "conLoc":        "${conLoc}"
    }
  }
}', 'N', 'DATA_ACTIVATED');


-- ── STEP 3. 블록 영역에 템플릿 지정 ────────────────────────────────
-- 관제 sync 가 NOTIFY_TEMPLATE_CODE 를 채우기 전까지의 임시 조치.
UPDATE bctransdbx.gps_geofence_area_cache
   SET NOTIFY_TEMPLATE_CODE = 'BLOCK_IN'
 WHERE AREA_TP = 'BLOCK_IN'
   AND NOTIFY_TEMPLATE_CODE IS NULL;


-- ── STEP 4. 결과 확인 ──────────────────────────────────────────────
SELECT AREA_ID, TERMINAL_CODE, AREA_TP, AREA_NAME, TERMINAL_EXTERNAL_CODE, NOTIFY_TEMPLATE_CODE
  FROM bctransdbx.gps_geofence_area_cache
 WHERE AREA_TP = 'BLOCK_IN';

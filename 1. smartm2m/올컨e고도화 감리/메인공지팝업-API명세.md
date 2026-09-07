# 메인 공지팝업 연계 API

> 베이스 `https://bcapi.chainportal.co.kr/bctrans-api` (관제 호출 대상)
> CHMAN-173

관제시스템이 올컨e 앱 메인 공지팝업을 등록·수정·삭제한다. 단일 엔드포인트에서 `action`으로 구분한다.

## 엔드포인트

| 메서드 | 경로 | 인증 |
| --- | --- | --- |
| POST | `/popup/notice` | 없음 (내부망 전제) |

---

## 연계 흐름

**등록 응답으로 내려주는 `popupId`를 관제가 반드시 보관해야 한다.** 이후 수정·삭제는 그 값으로 대상을 지목한다.

```
1. 관제 → POST /popup/notice  {"action":"CREATE", ...}
2. 서버 → 200  {"data":{"popupId": 499}}
3. 관제   popupId=499 를 자기 이력에 저장
4. 이후   {"action":"UPDATE","data":{"popupId":499, ...}}
          {"action":"DELETE","data":{"popupId":499}}
```

⚠️ **2번 응답을 받지 못하면 그 팝업은 이후 수정·삭제할 수 없다.** 팝업은 이미 등록된 상태이므로, 타임아웃 등으로 응답을 놓친 경우 재등록하지 말고 담당자에게 문의해 주기 바란다(중복 등록이 된다).

---

## 요청

### 공통 구조

```jsonc
{
  "action": "CREATE",     // CREATE / UPDATE / DELETE (대소문자 무관)
  "data": { ... }
}
```

### CREATE

```jsonc
{
  "action": "CREATE",
  "data": {
    "title": "시스템 점검 안내",              // 필수. 팝업 제목
    "contentHtml": "<p>본문</p>",            // 필수. HTML 본문
    "contentFormat": "HTML",                 // 선택. 수신만 하고 저장하지 않는다
    "priority": 1,                           // 선택. 노출 우선순위, 작을수록 위. 미전달 시 1
    "beginDt": "2026-09-01 00:00:00",        // 필수. 표출 시작 일시
    "endDt": "2026-09-30 23:59:59",          // 필수. 표출 종료 일시
    "useAt": "Y"                             // 선택. 사용 여부. "N" 이 아니면 전부 "Y" 로 처리
  }
}
```

### UPDATE

```jsonc
{
  "action": "UPDATE",
  "data": {
    "popupId": 499,                          // 필수. CREATE 응답으로 받은 값
    "title": "시스템 점검 안내 (연장)",
    "contentHtml": "<p>수정된 본문</p>",
    "priority": 1,
    "beginDt": "2026-09-01 00:00:00",
    "endDt": "2026-10-15 23:59:59",
    "useAt": "Y"
  }
}
```

전체 필드를 다시 보낸다. 일부만 보내는 부분 수정은 지원하지 않는다.

### DELETE

```jsonc
{
  "action": "DELETE",
  "data": { "popupId": 499 }                 // popupId 만 있으면 된다
}
```

논리 삭제(`useAt='N'`)로 처리되어 앱 조회에서 즉시 제외된다. 데이터 자체는 남는다.

### 일시 형식

`beginDt` · `endDt` 는 아래 두 형식을 모두 받는다. 기준 시간대는 KST다.

```
2026-09-01 00:00:00          (공백 구분)
2026-09-01T00:00:00          (ISO)
2026-09-01T00:00:00+09:00    (오프셋 포함)
```

---

## 응답

HTTP 상태 코드는 성공·실패 모두 200이므로 `result` 로 판정한다.

### 성공

```jsonc
{
  "result": "success",
  "resultMessage": "공지팝업이 처리되었습니다.",
  "data": { "popupId": 499 }        // CREATE 는 채번값, UPDATE·DELETE 는 요청한 값
}
```

### 실패

```jsonc
{
  "result": "failure",
  "resultMessage": "title 은 필수 입력값 입니다.",
  "data": null
}
```

`resultMessage` 로 내려오는 값:

| 값 | 발생 조건 |
| --- | --- |
| `action 은 필수 입력값 입니다.` | `action` 누락·빈 값 |
| `data 는 필수 입력값 입니다.` | `data` 누락 |
| `지원하지 않는 action 입니다. (CREATE / UPDATE / DELETE)` | 그 외 action 값 |
| `title 은 필수 입력값 입니다.` | 제목 누락·빈 값 |
| `contentHtml 은 필수 입력값 입니다.` | 본문 누락·빈 값 |
| `beginDt / endDt 는 필수 입력값 입니다.` | 표출 기간 누락 |
| `endDt 가 beginDt 보다 빠릅니다.` | 기간 역전 |
| `popupId 는 필수 입력값 입니다.` | UPDATE·DELETE 에 popupId 누락 |
| `수정 대상 공지팝업을 찾을 수 없습니다.` | 없는 popupId, 또는 **관제가 등록하지 않은 팝업** |
| `삭제 대상 공지팝업을 찾을 수 없습니다.` | 〃 |
| `공지팝업 처리 중 오류가 발생했습니다.` | 그 외 서버 오류 |

> 관제가 등록한 팝업만 수정·삭제할 수 있다. 체인포털 관리자가 등록한 팝업 ID를 보내면 "대상을 찾을 수 없습니다"로 거절된다.

---

## 노출 규칙

### 노출 조건

아래를 모두 만족하는 팝업만 앱에 내려간다.

```
표출 시작일시 <= 현재 <= 표출 종료일시
사용 여부 = Y
```

`beginDt` 에 미래 일시를 주면 그때까지 노출되지 않는다. **예약 등록이 가능하다.**

### 노출 순서

```
1순위  priority 오름차순 (작을수록 위)
2순위  표출 시작일시 오름차순 (먼저 시작한 것이 위)
```

`priority` 를 지정하지 않으면 1이 들어간다. 체인포털 관리자가 등록한 기존 팝업도 전부 1이므로, **우선순위를 2 이상으로 준 팝업은 기존 팝업보다 아래에 표시된다.** 위로 올리려면 1을 주고 표출 시작일시로 순서를 조정하거나, 0 이하를 주면 된다.

> ⚠️ 우선순위와 표출 시작일시가 **모두 같으면 순서가 보장되지 않는다.** 순서가 중요한 팝업은 우선순위를 서로 다르게 지정해 주기 바란다.

---

## 이미지형 팝업 미지원

현재 HTML 본문형만 지원한다. 이미지 팝업(`POPUP_TY='I'`)은 연계 대상이 아니다.

---

## 앱 조회 API (참고 — 관제는 호출하지 않는다)

앱은 아래 API 로 노출 대상 팝업을 배열로 받는다.

```
GET https://bcapi.chainportal.co.kr/allcone-api/mobile/popup/list
```

```jsonc
{
  "result": "success",
  "resultMessage": "",
  "data": [
    {
      "popupId": 499,
      "title": "시스템 점검 안내",
      "contentType": "html",              // 'html' 고정 (이미지형이면 'url')
      "content": "<p>본문</p>",
      "link": "",                         // 이미지형 전용, HTML형은 빈 문자열
      "priority": 1                       // 노출 우선순위 (작을수록 위)
    }
  ]
}
```

배열 순서가 곧 노출 순서다. 다만 앱이 순서에 의존하지 않아도 되도록 `priority` 를 함께 내려준다.

---

## 호출 예시

```bash
# 등록
curl -X POST 'https://bcapi.chainportal.co.kr/bctrans-api/popup/notice' \
  -H 'Content-Type: application/json' \
  -d '{
        "action": "CREATE",
        "data": {
          "title": "시스템 점검 안내",
          "contentHtml": "<p>9월 1일 02시~04시 점검이 진행됩니다.</p>",
          "priority": 1,
          "beginDt": "2026-09-01 00:00:00",
          "endDt": "2026-09-30 23:59:59",
          "useAt": "Y"
        }
      }'

# 삭제
curl -X POST 'https://bcapi.chainportal.co.kr/bctrans-api/popup/notice' \
  -H 'Content-Type: application/json' \
  -d '{"action":"DELETE","data":{"popupId":499}}'
```

---

## 적용 전 확인 사항

- 🔴 **운영 DB 에 `POPUP_PRIORITY` 컬럼 추가가 선행되어야 한다.** 미적용 상태에서 등록을 호출하면 실패한다 (`팝업연계-DDL요청-2026-08-19.sql`)
- 개발망(테스트베드)에는 적용 완료. `133.186.222.171:18080` 으로 연동 시험이 가능하다

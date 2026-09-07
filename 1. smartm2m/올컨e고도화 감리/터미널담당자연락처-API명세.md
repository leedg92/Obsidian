# 터미널 담당자 연락처 조회 API

> 베이스 `https://bcapi.chainportal.co.kr/allcone-api` (앱 호출 대상)
> CHENH-125 · 브랜치 `feat/CHENH-125-terminal-contact`

터미널 대표 전화번호와 담당자 목록을 함께 내려준다. 관제가 등록한 값을 그대로 조회하는 읽기 전용 API다.

## 엔드포인트

| 메서드 | 경로 | 파라미터 |
| --- | --- | --- |
| GET | `/mobile/terminal/contact` | 헤더 `deviceToken` (필수) · query `terminalCode` (필수) |

> ⚠️ 기존 `/mobile/terminal/contract/list`(터미널 홈페이지 링크 목록)와 **다른 API**다. `contract`가 아니라 `contact`다.

---

## 요청

### 헤더

```jsonc
{
  "deviceToken": "<디바이스 토큰>"      -- 필수. 없거나 서버에 등록되지 않은 값이면 HTTP 401
}
```

### 쿼리 파라미터

```
terminalCode=HPNTC050                  -- 필수. 8자리 터미널 코드. 누락 시 HTTP 400
```

---

## 응답

### 성공

```jsonc
{
  "result": "success",
  "resultMessage": "",
  "data": {
    "terminalCode": "HPNTC050",              -- 요청한 코드 그대로
    "contactTel": "051-000-0000",            -- 터미널 대표 전화번호. 미등록이면 null
    "managers": [                            -- 담당자 목록. 미등록이면 빈 배열 []
      {
        "managerName": "김철수",              -- 담당자 이름. null 가능
        "managerEmail": "chulsoo.kim@medu.com" -- 담당자 이메일. null 가능
      },
      {
        "managerName": "이영희",
        "managerEmail": "younghee.lee@medu.com"
      }
    ]
  }
}
```

**`managers` 배열 순서가 곧 화면 표시 순서다.** 앱에서 다시 정렬하지 않는다.

### 데이터가 없을 때

등록된 연락처가 없어도 실패가 아니다. HTTP 200 · `result: "success"`로 내려온다.

```jsonc
{
  "result": "success",
  "resultMessage": "",
  "data": {
    "terminalCode": "HPNTC050",
    "contactTel": null,                      -- 전화번호 미등록
    "managers": []                           -- 담당자 미등록
  }
}
```

**존재하지 않는 터미널 코드를 보내도 같은 형태로 200이 내려온다.** 오류로 구분되지 않으므로, 앱은 `contactTel`이 null이고 `managers`가 비었으면 "연락처 미제공"으로 표시하면 된다.

### 실패

| HTTP | 응답 | 발생 조건 |
| --- | --- | --- |
| 401 | `{"code":"UNAUTHENTICATED","message":"인증되지 않은 사용자입니다. forbidden access","subMessages":[]}` | `deviceToken` 헤더가 없거나, 서버에 등록되지 않은 토큰 |
| 400 | `{"timestamp":"...","status":400,"error":"Bad Request","path":"/allcone-api/mobile/terminal/contact"}` | `terminalCode` 파라미터 누락 |

> 401·400은 `result`/`resultMessage` 형식이 아니라 위 형태로 내려온다. 파싱 시 주의.

---

## 앱 구현 시 유의

| 항목 | 내용 |
| --- | --- |
| 조회 시점 | **연락처 화면·팝업을 열 때마다 호출한다.** 터미널 설정(`/mobile/terminal/config/all`)처럼 앱 시작 시 일괄 캐싱하지 않는다. 관제 변경이 즉시 반영되게 하려는 것이다 |
| 이름·이메일 | 각각 null일 수 있다. 둘 다 빈 항목은 서버가 저장 단계에서 걸러내므로 내려오지 않는다 |
| 전화 걸기 | `contactTel`은 하이픈 포함 문자열로 저장된다(`051-000-0000`). `tel:` 스킴으로 그대로 넘기면 된다 |
| 담당자 수 | 상한 없음. 관제가 등록한 만큼 내려간다 |

---

## 호출 예시

```bash
curl 'https://bcapi.chainportal.co.kr/allcone-api/mobile/terminal/contact?terminalCode=HPNTC050' \
  -H 'deviceToken: <디바이스토큰>'
```

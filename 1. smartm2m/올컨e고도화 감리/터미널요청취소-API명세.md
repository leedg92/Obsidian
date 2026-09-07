# 터미널 요청 3유형 취소 API

> 베이스 `https://bcapi.chainportal.co.kr/allcone-api` (앱 호출 대상)
> CHENH-102 · 브랜치 `feature/CHENH-102-cancelTerminalRequest`

## 엔드포인트 목록

앱이 호출하는 것은 **allcone** 경로다. 기존 요청 API 경로 뒤에 `/cancel`을 붙인 형태다.

| #   | 메서드  | 경로                                                                | 파라미터                                   |
| --- | ---- | ----------------------------------------------------------------- | -------------------------------------- |
| 1   | POST | `/mobile/terminalConHandler/reqeust/terminal/container/swap/cancel`            | 헤더 `deviceToken` (필수) · body (아래 공통 요청) |
| 2   | POST | `/mobile/terminalConHandler/reqeust/terminal/container/changeDirection/cancel` | 헤더 `deviceToken` (필수) · body (아래 공통 요청) |
| 3   | POST | `/mobile/terminalConHandler/reqeust/terminal/container/wash/cancel`            | 헤더 `deviceToken` (필수) · body (아래 공통 요청) |

> 경로 중간의 `reqeust`는 오타지만 기존 요청 API 경로가 그렇게 되어 있어 그대로 맞췄다. 여기서만 바로잡으면 요청과 취소의 경로가 달라진다.

### (참고) 내부 중계 경로 — 앱은 호출하지 않는다

allcone이 위 요청을 받아 bctrans로 다시 중계한다. 베이스 `https://bcapi.chainportal.co.kr/bctrans-api`.

| #   | 메서드  | 경로                                                | 대응 |
| --- | ---- | ------------------------------------------------- | -- |
| 1   | POST | `/mobile/terminal/req/container/handle/swap/cancel`            | 위 1번 |
| 2   | POST | `/mobile/terminal/req/container/handle/changeDirection/cancel` | 위 2번 |
| 3   | POST | `/mobile/terminal/req/container/handle/wash/cancel`            | 위 3번 |

> 요청 body·응답 형식은 allcone 경로와 동일하다. allcone은 body를 그대로 전달하고, bctrans 응답의 `data`만 꺼내 다시 감싼다.

---

## 공통 요청

### 헤더

```jsonc
{
  "deviceToken": "<디바이스 토큰>",   -- 필수. 헤더 자체가 없으면 HTTP 400, 빈 값이면 result="failure" / resultMessage="디바이스 토큰은 필수 입력값 입니다."
  "Content-Type": "application/json"
}
```

### 본문 — 3유형 동일

기존 요청 API 본문에서 `reasonCode`만 뺀 형태다. 취소는 대상을 지목하는 것뿐이라 사유를 받지 않는다.

```jsonc
{
  "terminalCode": "HPNT",                -- 터미널 코드. 응답에 그대로 되돌아온다
  "inOutType": "OUT",                    -- 반출입 구분. "OUT"/"IN" (레거시 "1"=반출·"2"=반입, 소문자 "out"/"in"도 허용. 그 외 값은 오류가 아니라 NULL로 파싱됨)
  "documentKey": "20260810000123",       -- 대상 운송건 식별자. 응답에 그대로 되돌아온다
  "reqDT": "2026-08-10T14:30:00"         -- 요청 일시. ISO-8601 yyyy-MM-dd'T'HH:mm:ss. 서버가 파싱만 하고 사용하지 않음
}
```

> 서버 검증은 `deviceToken` 하나뿐이다. 취소 엔드포인트에는 `@Valid`가 없어 나머지 4개 필드는 누락·오타여도 거절되지 않고 그대로 접수된다(`terminalCode`·`documentKey`는 null인 채 응답에 실린다).
> 차상세척 **요청**에 걸린 터미널 운영시간 거절은 **취소에는 걸려 있지 않다.** 운영시간이 지난 뒤에도 취소된다.

---

## 공통 응답

3유형 모두 동일하다. HTTP 상태 코드는 접수·거절 모두 200이므로 `result`로 판정한다.

### 성공

```jsonc
{
  "result": "success",                   -- 처리 결과. "success" / "failure"
  "resultMessage": "",                   -- 실패 시 메시지 (성공 시 빈 문자열)
  "data": {
    "requestType": "wash",               -- 취소 유형. "swap" / "changeDirection" / "wash"
    "documentKey": "20260810000123",     -- 요청에 실어 보낸 값 그대로
    "terminalCode": "HPNT",              -- 요청에 실어 보낸 값 그대로
    "canceled": true,                    -- 서버가 취소 요청을 접수함 (항상 true)
    "terminalNotified": false            -- 터미널 송신 여부. 현 단계에서는 항상 false (터미널 취소 인터페이스 미개발)
  }
}
```

### 실패

```jsonc
{
  "result": "failure",                                    -- 처리 결과
  "resultMessage": "디바이스 토큰은 필수 입력값 입니다.",       -- 거절 사유. 중계 실패 시에는 예외 메시지가 그대로 실린다
  "data": null                                            -- 실패 시 항상 null
}
```

`resultMessage`로 내려오는 값:

| 값                                | 발생 지점                          |
| -------------------------------- | ------------------------------ |
| `디바이스 토큰은 필수 입력값 입니다.` | `deviceToken` 헤더가 빈 값 |
| `요청 처리 중 오류가 발생했습니다.` | allcone 컨트롤러에서 예외 발생 |
| (예외 메시지 원문)                  | allcone → bctrans 중계 실패 |

---

## 현 단계 동작 제약

| 항목 | 현 동작 |
| --- | --- |
| 터미널 송신 | **하지 않는다.** 수신 후 200만 반환하며 `terminalNotified: false`가 그 표시다 |
| 운송 상태(`transStatus`) 변경 | **하지 않는다.** 요청 시 기록된 `REQ_CON_SWAP` / `REQ_CON_CHAN_DIRECT` / `REQ_CON_WASH`가 그대로 남는다 → 앱이 서버 상태로 버튼을 그린다면 취소 후에도 화면이 되돌아오지 않는다 |
| 운영시간 제약 | 없다. 요청과 달리 취소는 운영시간 밖에도 접수된다 |
| 서버 로그 표식 | `[CHENH-102][STUB] 취소 요청을 수신했으나 터미널로 송신하지 않았다. ...` |

---

## 호출 예시

```bash
curl -X POST 'https://bcapi.chainportal.co.kr/allcone-api/mobile/terminalConHandler/reqeust/terminal/container/wash/cancel' \
  -H 'Content-Type: application/json' \
  -H 'deviceToken: <디바이스토큰>' \
  -d '{
        "terminalCode": "HPNT",
        "inOutType": "OUT",
        "documentKey": "20260810000123",
        "reqDT": "2026-08-10T14:30:00"
      }'
```

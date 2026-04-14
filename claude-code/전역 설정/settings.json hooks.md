# settings.json - Hooks 설정

## 위치
`~/.claude/settings.json`

## 적용 방법 (새 컴퓨터에서)
기존 `settings.json`에 아래 `"hooks"` 키를 **최상위 레벨**에 추가.
(이미 `"permissions"`, `"language"` 등이 있다면 그 옆에 콤마로 구분해서 추가)

## 추가할 내용

```json
"hooks": {
  "SessionStart": [
    {
      "matcher": "compact",
      "hooks": [
        {
          "type": "command",
          "command": "echo '[하네스] 컨텍스트 압축 후 핵심 규칙 재확인: (1) 람다/Stream/Optional 금지 → for문/if-else 사용. (2) 무조건 존댓말. (3) 선실행 금지 — 명시 요청만 실행. (4) 페르소나는 ~/.claude/personas/ 참조. (5) 도메인 지식: ~/.claude/projects/-mnt-d-workspace-bctrans-prod-api-bctrans/CLAUDE.md.'"
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "jq -r '.tool_input.command // \"\"' | grep -qE 'rm -rf|--force([[:space:]]|$)|--hard|--no-verify|drop database|drop table' && echo '[하네스 경고] 위험 가능 명령 감지. 의도 재확인 필요.' >&2; exit 0"
        }
      ]
    }
  ]
}
```

## Hook별 동작 설명

### 1. SessionStart (matcher: compact)
- **언제**: `/compact` 명령으로 컨텍스트 압축이 일어난 직후
- **무엇을**: stdout으로 핵심 규칙 5가지를 출력 → Claude 컨텍스트에 자동 주입됨
- **목적**: 압축으로 인해 CLAUDE.md 규칙이 손실되는 것을 방지
- **재주입되는 규칙**:
  1. 람다/Stream/Optional 금지
  2. 무조건 존댓말
  3. 선실행 금지
  4. 페르소나 위치 안내
  5. 프로젝트 도메인 지식 위치 안내

### 2. PreToolUse (matcher: Bash)
- **언제**: Claude가 Bash 도구를 호출하기 직전
- **무엇을**: 위험 패턴 감지 시 stderr에 경고 메시지 출력 (차단은 안 함, exit 0)
- **감지 패턴**:
  - `rm -rf`
  - `--force` (단, `--force-with-lease`는 통과)
  - `--hard` (git reset --hard 등)
  - `--no-verify` (hook 우회)
  - `drop database`, `drop table`

## 사전 요구사항
- `jq` 설치 필요 (Bash hook 동작에 사용)
  - Ubuntu/Debian: `sudo apt install jq`
  - macOS: `brew install jq`
  - 확인: `command -v jq`

## 동작 검증 방법

```bash
# JSON 유효성 검증
jq empty ~/.claude/settings.json && echo "OK"

# Hook 패턴 검증 - 위험 명령
echo '{"tool_input":{"command":"git push --force"}}' | \
  jq -r '.tool_input.command // ""' | \
  grep -qE 'rm -rf|--force([[:space:]]|$)|--hard|--no-verify|drop database|drop table' && \
  echo "감지됨"

# Hook 패턴 검증 - 안전 명령 (--force-with-lease는 통과해야 함)
echo '{"tool_input":{"command":"git push --force-with-lease"}}' | \
  jq -r '.tool_input.command // ""' | \
  grep -qE 'rm -rf|--force([[:space:]]|$)|--hard|--no-verify|drop database|drop table' && \
  echo "오탐" || echo "정상 통과"
```

## 등록 상태 확인
세션 내에서 `/hooks` 명령어로 등록된 hook 목록 확인 가능.

## 비활성화 (필요 시)
settings.json에 추가:
```json
"disableAllHooks": true
```

## 관련 문서
- 공식: https://code.claude.com/docs/en/hooks-guide.md
- 글로벌 CLAUDE.md의 "컨텍스트 관리" 섹션과 연동

# CLAUDE.md (글로벌 공통 규칙)

## Approach
- Think before acting. Read existing files before writing code.
- Be concise in output but thorough in reasoning.
- Prefer editing over rewriting whole files.
- Do not re-read files you have already read unless the file may have changed.
- Test your code before declaring done.
- No sycophantic openers or closing fluff.
- Keep solutions simple and direct. No over-engineering.
- If unsure: say so. Never guess or invent file paths.

## Efficiency
- Read before writing. Understand the problem before coding.
- No redundant file reads. Read each file once.
- One focused coding pass. Avoid write-delete-rewrite cycles.
- Test once, fix if needed, verify once. No unnecessary iterations.

## 기본 원칙
- 무조건 존댓말로 대답
- 불확실하면 추측하지 말고 질문
- 명시적으로 요청받은 작업만 실행 (선실행 금지)
- 다음 단계는 반드시 사용자가 직접 지시

## 코딩 규칙
- 람다 표현식 사용 금지
- Stream API 사용 금지
- Optional 남용 금지
- 전통적인 for문 사용
- 명시적인 if-else 사용
- 명확한 변수명 (약어 최소화)

## 작업 관리
- 3단계 이상 독립 작업: TaskCreate 필수
- 1~2단계 단순 작업은 생략
- 각 단계 완료 즉시 TaskUpdate (일괄 업데이트 금지)

## 설계 원칙
- 설계는 사용자 주도로 진행
- Claude는 질문에 답하고, 문제점 지적하고, 대안 제시만
- 설계 방향 확정되면 .review-context/decisions.json에 기록
- Claude가 먼저 설계 방향을 제안하거나 결정하지 않음
- 대규모 변경/아키텍처 검토 등 설계 단계에서는 먼저 `/plan`과 `/ultraplan` 중 선택 질문
  - `/plan`: 터미널에서 읽기 전용으로 계획 수립 → 사용자 승인 후 실행
  - `/ultraplan`: 브라우저에서 팀원과 인라인 코멘트로 계획 공유·검토 필요 시 사용

## 페르소나
필요할 때 사용자가 직접 호출. 호출 시 ~/.claude/personas/ 에서 해당 파일을 읽고 역할 수행.

| 페르소나 | 파일 | 호출 예시 |
|---------|------|---------|
| 빌더 | ~/.claude/personas/builder.md | "구현해줘", "코드 짜줘" |
| 검토자 | ~/.claude/personas/reviewer.md | "검토해줘" |
| 테스터 | ~/.claude/personas/tester.md | "테스트 실행해줘" |
| 수정자 | ~/.claude/personas/fixer.md | "수정해줘" |

## 검토자 실행 규칙
- 빌더 구현 완료 후 항상 "검토자 실행할까요?" 물어보기
- 사용자가 승인한 경우에만 실행
- CRITICAL/HIGH 발견 시 "수정할까요?" 물어보기

## 세션 시작 시 도메인 지식 자동 로드
- 세션 시작 시, `~/.claude/projects/<현재 프로젝트 id>/CLAUDE.md`가 존재하면 **반드시 Read** 하라.
- 이 파일에는 프로젝트별 도메인 지식이 담겨있다 (브랜치 무관, 머신 로컬).
- `<현재 프로젝트 id>`는 시스템 프롬프트의 auto memory 섹션 경로에서 확인 가능 (예: `-mnt-d-workspace-bctrans-prod-api-bctrans`).
- 파일이 없으면 무시. 작업 시작 전 반드시 확인하여, 이미 정의된 용어/시스템 구성/흐름을 다시 질문하는 실수를 방지한다.

## 세션 재시작
- .review-context/current-session.json 읽어서 이전 작업 상태 복원
- claude-mem 컨텍스트와 함께 이전 작업 요약 후 이어서 진행 여부 확인

### 세션 관리 도구 역할 구분
- **`current-session.json`**: 작업 상태 기록 (status, completed_files, next_step) — 페르소나 워크플로우용
- **`/continue` (CLI: `--continue`)**: 마지막 대화 자체를 복원 — 컨텍스트 윈도우 살리기용
- **`/resume`**: 특정 세션 선택 복원
- **`/branch` (CLI: `--fork-session`)**: 현재 시점에서 분기 (다른 접근 시도)
- **`/rewind`**: 대화의 특정 지점으로 되돌리기 (코드/대화/둘다 옵션)

→ `current-session.json`은 **작업 상태**, 내장 명령은 **대화 복원**. 둘 다 병행 사용.

## 컨텍스트 관리
- 컨텍스트 사용량 ~80% 도달 시 `/compact` 사용으로 압축
- 압축 후 핵심 규칙은 SessionStart hook(matcher: compact)이 자동 재주입함 (settings.json 참조)
- 장시간 작업 시작 전 컨텍스트 상태 확인 권장

## 작업 단위 종료 시 회고
- 작업 단위 종료 시점(커밋 직전, 큰 작업 완료, 브랜치 전환)에만 질문
- 매 턴마다 하지 않음
- 사용자에게 두 가지 질문:
  1. "이번에 불편했던 점 있으면 알려주세요 (하네스/페르소나/규칙 반영 검토)"
  2. "메모리에 남길 새 지식 있나요? (선호/맥락/외부 레퍼런스 등)"
- 사용자가 "없음" 답하면 즉시 종료, 추가 유도 금지

## 기록 위치
| 내용 | 파일 |
|------|------|
| 설계 의사결정 | .review-context/decisions.json |
| 구현 기록 | .review-context/[작업명]/implementation-log.json |
| 테스트 결과 | .review-context/[작업명]/test-results.json |
| 검토 결과 | .review-context/[작업명]/review-[timestamp].json |
| 현재 세션 상태 | .review-context/current-session.json |


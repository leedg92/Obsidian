## 브랜치 목적
- 브랜치: `branch/comment/WIP`
- 목적: 레거시 코드 분석 및 주석 작업용 브랜치
- 주의: NICE 본인인증/회원 테이블 마이그레이션 브랜치(`feature/memberTableChange`)와 혼동 금지

## 도메인 지식 참조 순서
도메인 용어/시스템 구성/프로세스 흐름이 필요한 작업은 아래 순서로 정보를 획득한다:
1. **`~/.claude/projects/-mnt-d-workspace-bctrans-prod-api-bctrans/CLAUDE.md`** (메모리 디렉토리, 자동 로드 안 됨 → 반드시 Read)
   - 시스템 구성, 망 구분(VBS/TSS), 핵심 용어, 프로세스 흐름 한줄 요약
2. **`docs/claude-ref/` 하위 문서** — 1)로 모자라면 참조
   - `docs/claude-ref/infra-overview.md` — 인프라 구성 + mermaid 다이어그램
   - `docs/claude-ref/tss-flow/` — TSS(블록체인 망) 이벤트별 상세 흐름
   - `docs/claude-ref/vbs-flow/` — VBS(EDI 망) 이벤트별 상세 흐름
3. 그래도 모르면 사용자에게 질문 (추측 금지)

## Approach
- Think before acting. Read existing files before writing code.
- Be concise in output but thorough in reasoning.
- Prefer editing over rewriting whole files.
- Do not re-read files you have already read unless the file may have changed.
- Test your code before declaring done.
- No sycophantic openers or closing fluff.
- Keep solutions simple and direct. No over-engineering.
- If unsure: say so. Never guess or invent file paths.
- User instructions always override this file.

## Efficiency
- Read before writing. Understand the problem before coding.
- No redundant file reads. Read each file once.
- One focused coding pass. Avoid write-delete-rewrite cycles.
- Test once, fix if needed, verify once. No unnecessary iterations.
- Budget: 50 tool calls maximum. Work efficiently.

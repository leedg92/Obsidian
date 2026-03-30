# Harness 세팅 가이드

## 전체 구조

```
~/.claude/                         ← 글로벌 (세팅 완료)
├── CLAUDE.md                      ← 공통 규칙 전체
└── personas/
    ├── builder.md
    ├── reviewer.md
    ├── tester.md
    └── fixer.md

~/projects/bctrans-api-v2/         ← 각 프로젝트
└── .review-context/
    ├── current-session.json
    ├── decisions.json
    └── [작업명]/
        ├── implementation-log.json
        ├── test-results.json
        └── review-xxx.json
```

---

## 새 프로젝트 시작할 때

```bash
# 프로젝트 루트에서
mkdir -p .review-context
```

프로젝트 정보(스택, DB 등)는 첫 프롬프트에 직접 설명하면 됩니다.

---

## 사용 패턴 요약

```
간단한 질문        → 그냥 바로 질문
설계 같이 하기     → "OOO 개발할 건데 설계 같이 하자"
구현               → "구현해줘"
검토               → 빌더 완료 후 Claude가 먼저 물어봄
세션 재시작        → "어제 작업 이어서 해줘"
```

---

## 워크플로우

```
설계 (티키타카)
    ↓ decisions.json 기록
빌더 구현
    ↓ "검토자 실행할까요?"
검토자 (승인 시)
    ↓ CRITICAL/HIGH 없으면 완료
    ↓ 있으면 "수정할까요?"
수정자
    ↓ "테스터부터 다시 실행할까요?"
테스터 → 검토자 반복
```
# claude/ — 가이드 모음

이 폴더에는 Claude가 작업 단계·상황에 따라 참조하는 가이드 파일들이 있다.

## 파일 구조

```
claude/
├── core.md                  Cross-cutting 보조 규칙 (세션 시작 시 1회)
├── ideate.md                모호한 희망 → 발산→수렴 → PROJECT.md (intake 앞단)
├── intake.md                새 프로젝트 인테이크 (PROJECT.md 미완성 시)
├── plan.md                  계획 단계
├── implement.md             구현 단계
├── verify.md                검증 단계
├── token-efficiency.md      큰 파일·데이터 처리 시
├── llm-performance.md       추론 품질이 중요할 때
├── model-routing.md         모델 선택·전환
└── profiles/                프로젝트 유형별 규칙
    ├── dev.md               코드 개발
    ├── research.md          자료조사·논문·분석 보고서
    ├── docs.md              문서 업데이트·번역·정리
    ├── data.md              데이터 수집·스크래핑·ETL
    └── paper.md             완료된 aimux 런(AIMemory/)을 입력으로 논문 작성
```

> `/ideate` 스킬 본체는 Claude Code 표준 위치인 **`.claude/skills/ideate/`** 에 있다(SKILL·flow·gate + methods).
> `ideate.md`(이 폴더)는 그 흐름 계약이고, 실제 실행 파일은 `.claude/skills/`에 둬서 폴더를 통째로 복사해도 슬래시 커맨드가 그대로 동작한다.

## 로딩 시점

자세한 로딩 시점은 **`../CLAUDE.md §1·§2`** 참조.

핵심 원칙:
- 한꺼번에 다 읽지 않는다. 필요 시점에 1개씩.
- 한 단계가 끝나면 다음 단계 가이드로 교체.
- 같은 세션에서 이미 본 파일은 다시 읽지 않는다.

## 추가 가이드를 만들 때

새 도메인·반복 작업이 생기면:
- 프로젝트 유형이 4개 profile로 못 묶이면 `profiles/`에 새 프로파일 추가.
- 단계별 cross-cutting 보조가 필요하면 이 폴더 루트에 파일 추가.
- 두 경우 모두 `../CLAUDE.md §2`의 표에 한 줄 추가.

파일명은 kebab-case, 영어로.

# make_Harness

Claude Code용 **프로젝트 부트스트랩 하네스** + **AIMemory tmux 멀티에이전트 오케스트레이션(aimux)**.

> **이 README는 스캐폴드(make_Harness) 자체 설명입니다.**
> 이 폴더를 복사해 새 프로젝트를 시작하면, intake(`claude/intake.md`) 또는 `/ideate` 마지막 단계가
> 이 파일을 **그 프로젝트용 README로 교체**합니다(템플릿: `templates/project/README.md`).
> 스캐폴드 구조·동작 레퍼런스는 복사본에도 그대로 남는 `DESIGN.md`를 보세요.

- 사용자 응답 언어: 한국어. 가이드 본문은 토큰·추론 효율을 위해 영어.
- **설계·아키텍처·근거·전체 레퍼런스**: `DESIGN.md`.
- 스캐폴드 개발 이력: `HARNESS-CHANGELOG.md`(T 시리즈).

---

## 1. 두 개의 축

### (A) 프로젝트 가이드 하네스
세션마다 Claude가 읽는 진입점과 단계별 가이드 모음.

- `CLAUDE.md` — 항상 적용되는 규칙 + 단계 가이드 인덱스.
- `PROJECT.md` — 프로젝트 정보(요청 메모 → 인테이크로 채움).
- `claude/` — `core.md`, `intake/plan/implement/verify`, `profiles/{dev,research,docs,data}.md` 등 단계·유형별 가이드.

### (B) AIMemory/aimux — tmux 멀티에이전트 오케스트레이션
여러 AI 에이전트(claude·gemini·opencode·qwen 등)를 tmux 패널로 띄우고, **매니저 1명이 사람과 대화하며 작업을 분해·위임**, 워커들이 수행해 결과를 돌려주는 체계.

- `AIMemory/PROTOCOL.md` — AICP(파일 기반 핸드오프 + append-only `work.log`) 규약. 진실의 원천.
- `AIMemory/tmux-handoff.md` — 큐 기반 전달/회수 메커니즘 + 오케스트레이션 전략.
- `AIMemory/agents.md` — 에이전트 역량·실패모드·노하우 원장(매니저가 읽고 갱신).
- `AIMemory/bin/aimux` — 디스패처 엔진(큐·전달·상태).
- `AIMemory/bin/aimux-up` — 세션 런처(매니저·워커 객관식 선택 + 역할 브리프 생성).
- `AIMemory/agents.roster` — 매니저·워커 후보 풀(편집 가능한 단일 출처).
- `AIMemory/briefs/{manager,worker}.md` — 역할 브리프 템플릿(기동 시 세션별로 렌더).
- `AGENTS.md`(opencode·codex) / `GEMINI.md` / `QWEN.md` — 각 CLI가 시작 시 자동로드하는 **역할 중립** 브리프. 단독 실행 시 독립 에이전트로 동작하고, aimux 세션이면 pane에 붙는 ROLE 메시지가 이 파일을 덮어씀.

---

## 2. aimux 핵심 설계

- **큐 + 단일 디스패처**: 에이전트는 서로의 패널에 직접 paste하지 않고 `aimux enqueue`로 큐에 적재. 단일 디스패처만 전달 → 초인종 겹침 차단.
- **idle 게이트 + 연속 idle 해제**: 타깃 패널이 idle이고 in-flight 잠금이 없을 때만 전달. 해제는 연속 idle streak 충족 시(`idle-stable`)만 → 바쁜 패널 덮어쓰기 방지.
- **세션 격리**: 세션명 timestamp + 세션별 상태 디렉터리(`AIMemory/.aimux/<session>`) + `AIMUX_SESSION` 범위 pane 해석 → 동시 세션이 서로 간섭하지 않음.
- **자동 통지**: 워커 요청이 응답 없이 해제되면(idle/timeout) 디스패처가 매니저에게 `notice` 자동 전송 — "idle ≠ 완료".
- **라이브 피드**: dispatch 패널에 `＋ QUEUE → ▶ DELIVER → ✔ DONE` + `┄ p i d ┄` 보드 실시간 표시.
- **상태기반 운영**: `aimux agents`(idle/busy·처리중)와 `agents.md`로 역량·가용성 기반 배정, 부실 결과 시 진단→적응→재시도→다른 idle 에이전트로 재위임.
- **견고성**: 디스패처 PID lock + HUP 트랩(패널 종료 시 동반 종료) + `dispatch --force`(stale lock 회수).
- **계측·논문화**: `aimux report`가 신뢰 가능한 `run-summary.json`(라운드·재배분·에이전트별 성공/실패·소요시간) 산출 → `paper` 프로파일(`claude/profiles/paper.md`)이 완료된 `AIMemory/`를 입력으로 LaTeX 논문화(`templates/paper/`). 상세: `DESIGN.md` §11.

---

## 3. 빠른 시작

```bash
# 1) 후보 풀을 확인/수정 (AIMemory/agents.roster — [manager]/[worker] 섹션)
# 2) 세션 기동 → 매니저 1명 객관식 선택 + 워커 다중 선택, 디스패처 패널 자동
AIMemory/bin/aimux-up

# 상태 보기
AIMemory/bin/aimux status      # 큐·디스패처
AIMemory/bin/aimux agents      # 에이전트 idle/busy·처리중
AIMemory/bin/aimux report --write          # 버전 run-summary 스냅샷(논문용 계측)
AIMemory/bin/aimux checkpoint --label m1   # 마일스톤 신호 → 디스패처가 버전 스냅샷 자동 저장
AIMemory/bin/aimux panes       # 패널 레지스트리

# 완결·종료 (현재 세션만)
AIMemory/bin/aimux down --yes
```

### 레이아웃(예: 워커 3명)
```
┌──────────┬──────────┐
│ manager  │ worker1  │
│          ├──────────┤
├──────────┤ worker2  │   우측 = 선택한 워커 균등 스택
│ dispatch ├──────────┤
│ (~10%)   │ worker3  │
└──────────┴──────────┘
```
매니저 pane은 어떤 CLI를 골라도 항상 `manager`로 명명. 선택된 역할에 맞는
세션 브리프가 `AIMemory/briefs/` 템플릿에서 생성되어 각 pane이 1차로 읽음
(커밋된 CLAUDE.md/AGENTS.md 등은 무수정).

### 주요 환경변수(선택)
- `AWM_ROSTER` — 후보 풀 파일(기본 `AIMemory/agents.roster`).
- `AWM_MANAGER` / `AWM_WORKERS` — 매니저·워커 사전선택(프롬프트 생략; label/index, 워커는 `all` 가능).
- `AWM_CONFIG` — 전체 명시 로스터 파일(첫 줄=매니저; 풀·선택 건너뜀).
- `AWM_AUTO_APPROVE=1` — 권한/trust 프롬프트 없이 기동: claude=`--dangerously-skip-permissions`, codex=`--dangerously-bypass-approvals-and-sandbox`.
- `AWM_DISPATCH_HEIGHT` — 디스패처 패널 높이 %(기본 10).
- `AIMUX_VLOG=0` — 디스패처 라이브 피드 끄기.

---

## 4. 디렉터리

```
make_Harness/
├── CLAUDE.md  PROJECT.md  README.md           세션 진입점 / 프로젝트 정보·README(복사 시 채움)
├── CHECKLIST.md                               프로젝트 단계 체크리스트(plan이 채움; 복사 시 빈 템플릿)
├── HARNESS-CHANGELOG.md                        스캐폴드 자체 개발 이력(T 시리즈)
├── DESIGN.md                                   스캐폴드 아키텍처·레퍼런스
├── AGENTS.md  GEMINI.md  QWEN.md              역할 중립 CLI 자동로드 브리프(독립/aimux 양립)
├── templates/                                  산출물 스캐폴딩
│   ├── project/README.md                       프로젝트 README 템플릿(intake가 렌더)
│   ├── ideate/                                 ideate 산출 템플릿(초안·루브릭·게이트)
│   ├── codex/config.toml                       codex CLI 권장 설정 레퍼런스(모델·승인·trust)
│   └── paper/                                   논문 LaTeX 스캐폴딩(paper 프로파일용)
├── claude/                                     가이드(core/ideate/intake/단계; profiles 포함)
├── .claude/skills/ideate/                      /ideate 스킬 본체(슬래시 커맨드)
└── AIMemory/
    ├── PROTOCOL.md  tmux-handoff.md  agents.md
    ├── agents.roster                          매니저·워커 후보 풀(편집 가능)
    ├── briefs/{manager,worker}.md             역할 브리프 템플릿
    ├── work.log  handoff_example.md
    └── bin/{aimux, aimux-up}
```

런타임 산출물(`AIMemory/.aimux/`, `AIMemory/tmp/`)은 `.gitignore` 대상.

---

## 5. 의존성
tmux 3.0a+, bash, coreutils, flock(util-linux). jq·외부 라이브러리 불필요.
에이전트 CLI(claude/gemini/opencode/qwen)는 사용 시 각각 설치·인증 필요.

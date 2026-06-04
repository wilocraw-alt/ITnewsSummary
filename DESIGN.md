# aimux 설계 문서

AIMemory tmux 멀티에이전트 오케스트레이션(`aimux`)의 아키텍처·동작·설계 근거·레퍼런스.
개요는 `README.md`, 에이전트용 규약(영문)은 `AIMemory/tmux-handoff.md`·`AIMemory/PROTOCOL.md`,
역량 원장은 `AIMemory/agents.md`, 스캐폴드 개발 이력은 `HARNESS-CHANGELOG.md`(T 시리즈).

---

## 1. 목표

여러 AI 에이전트(claude·gemini·opencode·qwen 등)를 tmux 패널로 띄우고, **매니저 1명이
사람과 대화하며 작업을 분해·위임**하고 워커들이 수행해 결과를 돌려주는 협업 체계.
설계 원칙은 "한 사람만 사람과 대화, 나머지는 워커", "전달은 단일 채널로 직렬화",
"idle을 완료로 착각하지 않기", "동시 세션 간섭 없음".

---

## 2. 아키텍처

구성요소:
- **매니저 패널** — 사람과 대화하고 프로젝트를 소유. 작업을 분해·배정·통합·판정. 실질 작업(구현·통합·검증)은 전부 위임하고 **직접 일하지 않음** — 직접 수행은 해당 유닛이 위임에서 2회+ 실패 AND 사용자 승인일 때만(T29).
- **워커 패널** — 핸드오프를 받아 *정해진 범위만* 수행하고 결과를 큐로 반환(gemini·opencode·qwen 등).
- **디스패처 패널** — 단일 데몬(`aimux dispatch`). 큐를 읽어 idle 패널에만 전달, 상태 추적, 라이브 피드 출력.
- **큐/상태**(`AIMemory/.aimux/<session>/{queue,inflight,done,failed}`) — 요청·응답을 파일로 적재.
- **AICP**(`AIMemory/PROTOCOL.md`) — 진실의 원천. 핸드오프 파일 + append-only `work.log`.

데이터 흐름(요청 1건):
```
매니저: handoff_*.md 작성 + work.log(HANDOFF) → aimux enqueue
   → queue/  ──(디스패처)── 타깃 idle? & 잠금 없음? → paste+Enter → inflight/
   → 워커 수행 → 응답 handoff + aimux enqueue --type response
   → queue/ ──(디스패처)── 매니저 idle? → paste → 매니저 판정 → done/
```

---

## 3. 동작 생명주기 (디스패처)

매 사이클(`dispatch_once`):
1. 큐의 신규 항목을 피드에 `＋ QUEUE`로 표시.
2. in-flight 항목 진행/해제 판정(`process_inflight`).
3. 대기(pending) 항목을 우선순위+FIFO로 전달 시도(`deliver_pending`).
4. 카운트 변동 시 `┄ p=N i=M d=K ┄` 보드 출력.

전달 가드(겹침 차단):
- **in-flight 잠금**: 한 패널에 동시 1건만. 그 패널에 처리 중 항목이 있으면 보류.
- **idle 게이트**: 타깃 화면 tail이 안정(idle)일 때만 paste. 작업 중이면 보류.

해제 사유(`release_reason`):
- `response-seen` — 타깃이 응답(reply-to)을 enqueue함 → 정상 완료.
- `idle-stable` — 전달 후 work.log에 활동이 보였고 연속 idle 충족 → 완료.
- `unacked` — 재촉 후에도 무활동 → 미수신으로 판단(escalate).
- `timeout` — 하드 타임아웃.
- `pane-gone` — 패널 소멸.

---

## 4. 핵심 메커니즘과 근거(why)

각 장치는 실제 에이전트 운영에서 드러난 문제를 막기 위해 도입됨.

- **큐 + 단일 디스패처** — 에이전트가 서로 직접 paste하면 다수 동시 사용 시 초인종이 겹침.
  적재만 하게 하고 단일 디스패처가 전달 → 겹침 원천 차단.
- **idle 게이트 + 연속 idle 해제(streak)** — 초기엔 단일 idle 체크로 해제(`idle-no-change`)해서,
  생각 중인 LLM의 일시적 화면 안정을 idle로 오판 → 바쁜 패널에 덮어쓰기·유실 발생.
  이제 `AIMUX_RELEASE_IDLE_CYCLES`회 **연속** idle일 때만 해제(busy면 streak 리셋). (T1·T17)
- **사용자 입력 대기 vs 완료 후 idle 구별** — 권한/예-아니오/선택 프롬프트로 **사용자 입력을 기다리는**
  패널(화면은 안정=idle처럼 보임)은 `AIMUX_WAIT_PATTERN`으로 감지해 **보류**(해제·재촉 안 함,
  재배분 안 함, 새 전달 안 함) → 매니저에 오보·건너뛰기 방지. "완료 후 무응답 idle"(통지/재촉 대상)과
  구분. 하드 타임아웃은 백스톱으로 유지. (T24)
- **대기 프롬프트의 위험도 라우팅** — 보류된 프롬프트를 `AIMUX_WAIT_RISK_PATTERN`(파괴적/비가역/외부노출/
  자격증명 마커)으로 한 번 더 분류해 에피소드당 1회 라우팅. 위험도는 프롬프트 **배후 동작**으로 판정 —
  "always allow / don't ask again" 같은 UI 옵션은 거의 모든 권한 프롬프트에 떠 있어 그 자체로 고위험이
  아님(T29). **저위험**(단순 권한 요청 포함)이면 매니저에게 "사람 역할
  수행" notice(워커 pane id + 프롬프트 발췌 포함)를 보내 매니저가 해당 패널에 `tmux send-keys`로 직접
  답하게 함(프롬프트 응답은 핸드오프가 아니므로 허용되는 유일한 직접 paste) → 사소한 확인으로 워커가
  멈추지 않음. **고위험**이면 매니저가 답하지 않고 **실제 사람에게만** 표면화. 매니저가 저위험 notice를
  읽고 위험하다고 판단하면 답 대신 사용자에게 에스컬레이션. (T25, T29)
- **세션 격리** — pane 이름 해석이 서버 전역이라 동일 이름 패널이 여러 세션에 있으면 오배달,
  단일 lock도 충돌. 해결: 세션명 timestamp + 세션별 상태 디렉터리 + `AIMUX_SESSION`으로 pane 해석을
  해당 세션으로 한정. **주의**: 기존 tmux 서버가 떠 있으면 `export`가 패널에 안 닿으므로,
  런처가 실행줄에 `env AIMUX_STATE=… AIMUX_SESSION=… TMPDIR=…`를 직접 프리픽스. (T11)
- **자동 통지(notice)** — 워커가 응답 없이 idle/timeout으로 해제되면 "idle=완료"가 아님을
  매니저가 모름. 디스패처가 원 source(매니저)에 `notice`를 자동 enqueue: "워커 X 무응답 — 산출물
  확인 후 accept/재배분". (T14)
- **무활동 재촉(re-nudge)** — 멀티라인 paste가 idle 패널 입력창에 *미제출*로 남아, 전달된 응답을
  매니저가 못 집는 경우. 전달 후 work.log의 에이전트 이벤트(aimux 제외) 증가가 없으면 = 미처리로 보고,
  **단일줄 nudge**(개행 없어 Enter로 제출 → 입력창의 원본까지 함께 제출)를 1회 재전달. 그래도 없으면
  `unacked`. (T17)
- **견고성** — 디스패처 PID를 lock에 기록 + HUP 트랩(패널/서버 종료 시 동반 종료, orphan 방지)
  + `dispatch --force`(stale lock 회수). (T1·gap2)
- **`/tmp` → `AIMemory/tmp`** — 프로젝트 밖(/tmp) 쓰기는 권한 프롬프트 유발. 스크래치를 프로젝트
  내부로. (T8)
- **라이브 피드** — dispatch 패널에 `＋ QUEUE → ▶ DELIVER → ✔ DONE`(+ `↻ NUDGE`) + 보드 실시간 표시.
  `AIMUX_VLOG=0`로 끔. (T13)
- **`aimux down`** — 작업 완결 시 현재 세션만 finalize+종료. (T16)

---

## 5. 오케스트레이션 정책 (매니저 행동)

**Phase 0 — 발산→수렴 계획(비단순 작업, 구현 전):**
- (0a) 사용자 요구사항(범위·제약·수용기준)을 확인·명확화.
- (0b) 확인된 요구사항을 파일로 적고, **매니저와 각 워커가 각자 독립적으로 자기 계획안을 병렬 작성**.
  워커에는 `PROPOSE` 핸드오프("너 자신의 접근을 자유롭게 제안하라, 구현 금지"), 매니저도 동시에 자기 안 작성.
  각 제안을 REVIEW_RESPONSE로 회수.
- (0c) 모든 제안(워커들 + 매니저)의 **아이디어별 장단점을 분석**해 좋은 부분을 결합한 **최선의 최종안** 도출
  (어떤 안에서 왔는지·트레이드오프 명시). 한 초안을 추인하는 게 아니라 독립적 발산 후 수렴이 목적. 이후 루프 진행.

매니저는 `AIMemory/agents.md`와 `aimux agents`(상태 보드)를 보고 운영하는 폐루프:
1. **분해** — 최종안을 가능한 독립적인 단위로(테스트/검증 단위 포함).
2. **배정** — idle이고 역량 맞는 에이전트에 병렬 배정. 라우팅 제약:
   - **데이터 민감도 우선**: 개인/민감/기밀 데이터는 **qwen(완전 로컬) 전담**, 클라우드 에이전트
     (claude/opencode/gemini)에는 절대 전달 금지.
   - **qwen은 약함**: 자료조사·simple shell script·소규모 기계적 작업만. 주요/복잡 작업은
     **opencode·gemini**.
3. **모니터** — "idle≠완료". 무응답은 자동통지로 받음. 실제 산출물을 확인.
4. **실패 대응** — 버리지 말고 **진단 → 적응(범위 축소·"지금 적용"·"실제 실행") → 1회 재시도 →
   다른 idle 가용 에이전트로 재배분**. 원인·해법을 `agents.md` Learnings에 기록.
5. **검증도 위임** — 통합/테스트/검증은 *작업*이지 judgment가 아님. "테스트/하네스를 작성하고 **실행**해
   증거 보고"를 idle 워커에 VERIFY 단위로 위임. 매니저는 분해/증거기반 accept·재배분/최종 조립만.

이 정책은 워커 초기 브리프(`AGENTS.md`/`GEMINI.md`/`QWEN.md`)와 런처의 매니저 온보딩, `tmux-handoff.md`
Roles·Orchestration strategy에 함께 명시됨.

---

## 6. 명령 레퍼런스

### `AIMemory/bin/aimux`
- `panes` — 패널 레지스트리(id·name·kind·init·위치).
- `agents` — 상태 보드(name·kind·idle/busy/waiting·처리중). 상태기반 배정/재배분용. `waiting`=권한 프롬프트 대기(보류 중, 재배분·실패 아님)이라 `idle`과 구분(T29).
- `name <name> [--kind <k>] [--pane <id>]` — 현재/지정 패널 이름·종류 지정 + 보더 고정.
- `enqueue --to <name> --handoff <path> [--roles R[+R]] [--from <pane>] [--type request|response] [--reply-to <id>] [--priority N]` — 큐 적재.
- `dispatch [--interval S] [--once] [--force]` — 디스패처 루프(단일 인스턴스, flock).
- `status` — 큐·디스패처 상태(+ 세션 패널).
- `send-test --to <name>` — 하이파이브 스모크테스트.
- `cancel <req-id>` — 대기/처리중 요청 취소.
- `down [--yes] [--purge]` — 현재 세션 finalize+종료(다른 세션/서버 무영향; `--yes` 없으면 프리뷰).

### `AIMemory/bin/aimux-up` (런처)
- 매니저(좌상)+디스패처(좌하) 좌측 컬럼, 워커 우측 균등 스택으로 세션 기동.
- 후보 풀(로스터): `AIMemory/agents.roster`(기본; `AWM_ROSTER`로 교체)에 `[manager]`/`[worker]` 두 섹션, 각 줄 `label | command`. 모델 태그·후보를 자유롭게 추가/변경. `AWM_CONFIG` 파일을 주면 풀·선택을 모두 건너뛰고 전체 로스터를 대체(첫 줄=매니저).
- **역할 선택(기동 시)**: ① `[manager]` 풀에서 매니저 1명 객관식 → ② `[worker]` 풀에서 워커 다중 선택(번호/이름, `all`). `AWM_MANAGER`/`AWM_WORKERS`로 프롬프트 생략 가능. 매니저 pane은 어떤 CLI를 골라도 항상 `manager`로 명명(워커가 `--to manager` 반환). 첫 워커=split h(우측 컬럼 개시), 나머지=v.
- **세션 브리프 생성**: 선택된 역할에 맞춰 매니저 브리프 1개 + 워커별 브리프를 `AIMemory/briefs/{manager,worker}.md` 템플릿에서 세션 state 디렉터리로 렌더링하고, 각 pane이 자기 브리프를 1차로 읽게 함(`@awm_init_file`). 커밋된 `CLAUDE.md`/`AGENTS.md`/`GEMINI.md`/`QWEN.md`는 **수정하지 않음** — 생성 브리프 + 온보딩 메시지가 역할의 권위 → 어떤 CLI든 매니저/워커로 기동 가능(T30).
- **독립 실행 ↔ 멀티 실행 양립**: 커밋된 자동로드 브리프(`AGENTS.md`/`GEMINI.md`/`QWEN.md`)는 **역할 중립** — 단독 실행 시 독립 에이전트로 동작(PROJECT.md/CLAUDE.md 따라 프로젝트 규칙 적용), aimux로 기동되면 pane에 붙는 `ROLE:` 메시지 + 세션 브리프가 이를 덮어써 매니저/워커가 됨. 같은 폴더에서 CLI를 단독으로 띄워도 워커로 멈추지 않음(T31).

---

## 7. 설정 (환경변수)

aimux:
- `AIMUX_SESSION` — pane 라우팅을 이 세션으로 한정(런처가 자동 설정).
- `AIMUX_STATE` — 큐/lock 상태 디렉터리(기본 `AIMemory/.aimux`; 런처는 세션별).
- `AIMUX_WORKLOG` — work.log 경로(기본 `AIMemory/work.log`).
- `AIMUX_TMP` — 스크래치(기본 `AIMemory/tmp`).
- `AIMUX_DISPATCH_INTERVAL`(2s) / `AIMUX_IDLE_SAMPLE_SECS`(1.2s) / `AIMUX_CAPTURE_LINES`(40) — 폴링·idle 감지.
- `AIMUX_MIN_INFLIGHT_SECS`(4s) — 해제 전 유예.
- `AIMUX_RELEASE_IDLE_CYCLES`(3) — 해제에 필요한 연속 idle 횟수.
- `AIMUX_INFLIGHT_TIMEOUT`(900s) — 하드 타임아웃.
- `AIMUX_VLOG`(1) — 라이브 피드(0=끔).
- `AIMUX_WAIT_PATTERN` — 사용자 입력 대기 프롬프트 감지 ERE(대소문자 무시). CLI별로 튜닝(관찰한 마커를 agents.md에 기록).
- `AIMUX_WAIT_RISK_PATTERN` — 대기 프롬프트 중 **고위험**(배후 동작이 파괴적/비가역/외부노출/자격증명) 판별 ERE(대소문자 무시). 매칭=사람에게만 에스컬레이션, 미매칭=매니저가 대신 응답. 빈 값=전부 저위험 취급. UI 옵션("always allow / don't ask again")은 고위험 마커가 아님 — 동작으로 판정(T29).

aimux-up:
- `AWM_ROSTER` — 후보 풀 파일(기본 `AIMemory/agents.roster`).
- `AWM_MANAGER` — 매니저 사전선택(label 또는 1-기반 index). 매니저 프롬프트 생략.
- `AWM_WORKERS` — 워커 사전선택(label/index 콤마·공백 목록 또는 `all`). 워커 프롬프트 생략. (이전의 "워커 개수" 의미를 대체.)
- `AWM_CONFIG` — 전체 명시 로스터 파일(첫 줄=매니저). 풀·선택 프롬프트를 모두 건너뜀.
- `AWM_SESSION` — 고정 세션명(기본 `aimux-<names>-yymmdd-HHMMSS`).
- `AWM_AUTO_APPROVE=1` — 권한/trust 프롬프트 없이 기동: claude=`--dangerously-skip-permissions`, codex=`--dangerously-bypass-approvals-and-sandbox`(매우 위험 — 외부 샌드박스 환경 전용).
- `AWM_DISPATCH_HEIGHT`(10) — 디스패처 패널 높이 %.
- `AWM_CLI_WARMUP`(6s) — CLI 부팅 대기.

---

## 8. 레이아웃·패널 레지스트리

```
┌──────────┬──────────┐
│ manager  │  gemini  │
│          ├──────────┤
├──────────┤ opencode │   우측 = 워커 균등 스택
│ dispatch ├──────────┤
│ (~10%)   │  qwen    │
└──────────┴──────────┘
```
라우팅은 tmux pane 옵션 `@awm_pane_name`(고정 라우팅 이름)·`@awm_agent_kind`·`@awm_init_file`로.
CLI가 타이틀을 덮어써도 보더에 고정 이름이 유지됨.

---

## 9. 에이전트 특성 (요약 — 상세는 agents.md)

- **claude-code** — 강함·신뢰. 편집 자율 적용. 매니저·워커 어느 역할로도 기동 가능(로스터 선택).
- **opencode** — 가장 신뢰. 멀티파일 구현·재배분 1순위.
- **codex** — 브리프는 `AGENTS.md` 공유(opencode와 동일). 설정은 `~/.codex/config.toml`(권장값 `templates/codex/config.toml`), 프로젝트 trust 필요. 자율 실행은 `AWM_AUTO_APPROVE=1` 또는 `approval_policy="never"`+trust.
- **gemini-cli** — 유능하나 취약: 편집승인 모드 꺼지면 *plan만*(Shift+Tab 필요), tool-call 다발 시
  오류 → 단일파일·단일스텝.
- **qwen(gemma4:e4b)** — 약한 **로컬** 모델. 도구호출을 서술만 하는 경향("실제 실행" 지시 필요).
  민감데이터 전담 + 단순작업 한정. 주요작업 금지.

---

## 10. 파일 맵 + 이력

```
make_Harness/
├── README.md(하네스 개요)  DESIGN.md(본 문서)  HARNESS-CHANGELOG.md(스캐폴드 개발 이력)
├── CHECKLIST.md  PROJECT.md                   복사한 프로젝트가 채우는 템플릿
├── AGENTS.md  GEMINI.md  QWEN.md            역할 중립 CLI 자동로드 브리프(독립/aimux 양립)
├── templates/codex/config.toml             codex CLI 권장 설정 레퍼런스
├── claude/                                  가이드(core/profiles/단계)
└── AIMemory/
    ├── PROTOCOL.md(AICP)  tmux-handoff.md(전송·전략)  agents.md(역량 원장)
    ├── agents.roster(매니저·워커 후보 풀)  briefs/{manager,worker}.md(역할 브리프 템플릿)
    ├── work.log  handoff_example.md
    └── bin/{aimux, aimux-up}
```
스캐폴드 개발 이력·근거는 `HARNESS-CHANGELOG.md`(복사 프로젝트의 단계 체크리스트는 `CHECKLIST.md`). 런타임(`AIMemory/.aimux/`, `AIMemory/tmp/`)은 `.gitignore`.

---

## 11. 런 계측 + 논문화

목적: 완료된 멀티에이전트 런을 **별도 프로젝트에서, 이 하네스로** 논문화. 두 부분으로 분리:

**(가벼운) 실행 하네스 계측** — `aimux report`가 디스패처의 자기 기록(`.aimux/done`·`failed`의
`*.req`, 기계 생성=신뢰)에서 인용 가능한 run-summary를 산출:
- `aimux report` 사람용 요약 / `--json` JSON / `--write`로 **버전 스냅샷** 저장.
- **버전 관리**: 스냅샷은 `AIMemory/run-summary/vNNN-<ts>[-label].json`으로 시점별 보존,
  `AIMemory/run-summary.json`은 항상 **최신** 미러(기본 읽기 대상). 시점 간 비교 분석 가능.
- **매니저 신호 체크포인트**: 매니저가 대규모 요구 해결/마일스톤에서 `aimux checkpoint --label <m>` →
  디스패처가 신호를 받아 자동으로 버전 스냅샷 작성(디스패처와 협업; 디스패처 없으면 즉시 작성).
- `aimux down --yes`는 종료 전 최종 스냅샷(`final`)을 남김.
- 스키마 `aimux-run-summary/1`:
  - `totals{requests,responses,notices,highfives,redispatches}`
  - `release_reasons{response-seen,idle-stable,unacked,timeout,pane-gone}`
  - `durations_seconds{session_span,turnaround_min/avg/max}`
  - `per_agent{<name>{requests,completed,failed}}` (completed=응답 반환, failed=무응답/unacked/timeout)
  - `handoffs[]{type,to,handoff,delivered,released,release_reason}`
  - `redispatches`=토픽당 첫 배정 이후 추가 요청(재시도+재배분), `notices`=무응답 사건(재배분 트리거 프록시).
- 정량 주장은 run-summary.json(기계), 서사는 `work.log`(LLM 작성)에서.

**(별도 프로젝트) 논문 작성 스킬** — `paper` 프로파일(`claude/profiles/paper.md`):
완료 프로젝트의 `AIMemory/`(run-summary.json + work.log + handoff_*)를 입력으로 새 세션에서 실행 →
`templates/paper/`를 채워 논문화. 산출물 **PDF + Word(.docx)**, **시각자료**(실험 구조도 SVG +
표/pgfplots 차트; PDF·Word 모두 임베드), **버전 관리**(피드백 반영 전 `make snapshot` → `versions/vNNN`,
통째로 갈아엎지 않고 증분 수정). 모든 결과는 아티팩트 필드와 1:1 추적. PROJECT.md `profile: paper`로 진입.
빌드 도구: latexmk+xelatex, pandoc, rsvg-convert, ghostscript.

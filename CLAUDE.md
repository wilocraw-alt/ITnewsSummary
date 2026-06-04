# CLAUDE.md

## 요약 (사용자용)

- 이 파일은 모델이 세션마다 항상 읽는 진입점. 본문은 토큰·추론 효율을 위해 영어로 작성됨.
- 사용자 응답은 **한국어**, 가로 표 금지, 세로 `key: value` 형식.
- 세션 시작 시 로딩 순서: `PROJECT.md` → (필요 시 `intake.md`) → `core.md` + `profiles/{profile}.md`.
- 표준 작업 흐름: 계획(`plan.md`) → 구현(`implement.md`) → 검증(`verify.md`).
- 푸시·파괴적 명령은 **사용자가 명시 요청할 때만** 실행.

---

This file lists Claude's **always-on rules** and a guided index of stage files to load on demand.
- Project-specific info lives in `PROJECT.md`.
- Cross-cutting helper rules live in `claude/core.md`.
- Project-type rules live in `claude/profiles/{profile}.md`.
- Stage guides live in `claude/`.

**Load files only when needed** to conserve context.

---

## 0. Always-on rules

- **User-facing language: Korean.** For technical terms (table names, function names, library names) include a brief Korean gloss.
  - Example: `dataset_meta`(데이터셋 메타정보 테이블)
- **Output format: vertical `key: value` blocks.** **Do not use horizontal markdown tables** (`| col | col |`) in user-facing output. (Tables inside guide files like this one are fine — they're not user output.)
- **Reasoning language: English internally, Korean for the final user response.** (Performance optimization — English-dominant training distribution.)
- **No hardcoding.** Dates, paths, URLs, parameters must come from input files or CLI arguments — never embedded as literals.
- **Secrets stay in `.env`.** Read from `.env`, maintain `.env.example` alongside. Never inline credentials.
- **No guessing.** If you don't know, verify or ask the user (1–3 condensed questions).
- **Destructive commands** (`git push`, `reset --hard`, `clean -f`, file deletion, etc.): execute **only when the user explicitly requests them**.
- **Long-running batch / subagent work**: before starting, also write a standalone status-check script (`status.sh` or `check_status.py`) the user can run from a terminal outside Claude's session.

---

## 1. Files to load at session start

In this order:

1. **`PROJECT.md`** — project name, purpose, profile, tech stack, domain notes.
   - If any required field (`이름`·`목적`·`입력`·`출력`) is empty → **시작 시점에 사용자에게 진입 경로를 물어본다**:
     - 요청이 **모호한 희망**(구체적 스펙 아님)이면 → `claude/ideate.md`(`/ideate` 스킬)로 발산→수렴 구체화 후, 산출된 PROJECT.md로 intake 진입.
     - 이미 **구체적 스펙**이거나 사용자가 직접 진행을 택하면 → 바로 **`claude/intake.md` 실행**.
   - If `profile` is empty → intake §3.3 recommends and confirms one.
2. **`claude/core.md`** — cross-cutting helper rules (memory, diagrams, general outputs, batch scripts).
3. **`claude/profiles/{profile}.md`** — exactly one file, chosen by PROJECT.md's `profile` value.

After intake completes, transition to the normal workflow (§3).

---

## 2. Stage-specific references (load only when needed)

| Situation | File | When to load |
| --- | --- | --- |
| Cross-cutting rules | `claude/core.md` | Once at session start (§1) |
| Profile-specific rules | `claude/profiles/{profile}.md` | Once at session start (§1) |
| Vague wish / new idea (no concrete spec) | `claude/ideate.md` | Before intake — when PROJECT.md fields are empty and the request is only a fuzzy wish (ask the user at the start which path to take) |
| New project intake | `claude/intake.md` | When PROJECT.md is incomplete |
| Planning | `claude/plan.md` | Just before a non-trivial task |
| Implementation | `claude/implement.md` | During code changes |
| Verification | `claude/verify.md` | After changes, before reporting done |
| Large files / data | `claude/token-efficiency.md` | Before reading or editing big files |
| Reasoning-heavy work | `claude/llm-performance.md` | Design, debugging, deep analysis |
| Model selection / switching | `claude/model-routing.md` | Once at session start + on trial-and-error |

> Loading discipline: read one file just before entering its stage, then swap to the next. Don't read them all up front.

---

## 3. Workflow skeleton

```
Load PROJECT.md → check profile
   ↓
If incomplete (name / purpose / input / output / profile missing)
   → ask at start: 모호한 희망 vs 구체적 스펙?
       ├ 모호한 희망 → claude/ideate.md (/ideate): S0→S4 발산→수렴 → 채워진 PROJECT.md → intake
       └ 구체적 스펙 / 직접 진행 → claude/intake.md (request memo → profile recommendation → fill fields)
   ↓
Load claude/core.md + claude/profiles/{profile}.md
   ↓
[PLAN]    claude/plan.md
          → step checklist + verification criteria
          → save CHECKLIST.md → get user agreement
   ↓
[BUILD]   claude/implement.md (+ token-efficiency.md, profile output rules as needed)
          After each step:
            1) Update CHECKLIST.md (tick the box, append history line)
            2) Print progress (N / total, next step) to user
            3) Decide on context compaction (/compact conditions)
   ↓
[VERIFY]  claude/verify.md (against CHECKLIST.md criteria)
          → mark CHECKLIST.md fully complete
   ↓
On failure or stalling → claude/model-routing.md (rollback, replan with Opus)
   ↓
Update docs / memory → commit & push (with user approval)
```

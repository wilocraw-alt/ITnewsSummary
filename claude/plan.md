# plan.md — Planning stage guide

## 요약 (사용자용)

- 비자명한 작업 시작 직전에 읽음. 한두 줄 변경이나 단순 조회는 제외.
- 3~7단계로 분해, 각 단계마다 입력·출력·검증 기준·롤백 지점.
- CHECKLIST.md로 저장 → 사용자 합의 → 그 다음 구현.
- "일단 X 해보고 안 되면 Y" 같은 가설 없는 계획은 다시 분석.

---

**When to read**: just before starting a non-trivial task. Skip for one- or two-line changes, typo fixes, single renames, and pure lookups.

---

## 1. Procedure

### 1.1 Requirements

- Extract goal, constraints, and scope from `README.md`, `REQUIREMENTS.md`, and the user's messages.
- If anything is ambiguous or missing, don't guess — **ask the user (1–3 compressed questions via `AskUserQuestion`)**.
- State the purpose ("why are we doing this?") in **one sentence**. If you can't, planning isn't ready yet.

### 1.2 Survey existing code

- Skim relevant files briefly. **Don't read entire files** (`token-efficiency.md`).
- If you don't know where something lives, narrow with `grep -n` / `rg -n`.
- For broad exploration, delegate to `Agent` (subagent_type=`Explore`). Ask for "200-word summary + file path list".

### 1.3 Decompose and write the checklist (think in English)

- Break the work into **3–7 steps**. For each, state:
  - **Input** — preconditions, data it receives.
  - **Output** — artifacts, what the next step inherits.
  - **Verification criteria** — what proves this step is done (used by `verify.md`).
- Separate hypotheses from facts. Use "if X holds then Y" form.
- Identify each step's **rollback point**.
- Express the decomposition as a checklist (see §2 template).

### 1.4 Save CHECKLIST.md

- Save the checklist as **`CHECKLIST.md`** at the project root, using the §2 template.
- If the file already exists, ask the user before overwriting.
- After saving, show the checklist to the user and get agreement.

### 1.5 Externalize and agree

- Present the plan via `ExitPlanMode` or a short Korean report.
- **No code changes before user agreement** (unless the user explicitly delegated that authority).
- Once agreed, follow the plan exactly. No drift or scope creep.

---

## 2. CHECKLIST.md template

Save in this form after the plan is finalized. Replace bracketed placeholders.

```markdown
# CHECKLIST.md

생성일  : [YYYY-MM-DD]
목표    : [한 문장]
진행    : 0/[N] 완료

---

## 수행 단계

- [ ] 1. [단계명]
  - 검증 기준: [이 조건이 충족되면 완료]
  - 롤백 지점: [되돌릴 위치/방법]
- [ ] 2. [단계명]
  - 검증 기준: ...
  - 롤백 지점: ...

(repeat)

---

## 진행 이력

(append on each step: YYYY-MM-DD HH:MM — N단계 완료: [단계명])
```

---

## 3. Hallmarks of a good plan

- 3–7 steps. Smaller decomposition becomes noise.
- Every step has a verification criterion (one line). If missing → bad plan.
- "If stuck, roll back to here" is explicit.
- Outputs are concrete (filenames, paths, column names, function signatures).

## 4. Red flags — re-analyze

- "Try X, if it fails try Y" — no hypothesis. Start from analysis.
- 1 step or 10+ steps.
- No verification criteria.
- Vague phrases like "handle various cases".

---

## 5. Fast path

Skip planning if:
- The change is one or two lines, a typo, a single rename.
- The user specified one concrete action ("change X to Y in this file").
- It's a lookup-only task ("where is this function used?").

If a "fast path" task **reveals 3+ steps mid-execution**, stop and return to planning — write CHECKLIST.md and get user agreement.

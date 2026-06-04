# ideate.md — Pre-project ideation flow

## 요약 (사용자용)

- 모호한 **희망사항**을 받아 발산→수렴으로 구체화해, PLAN→DEV→EVAL에 바로 들어갈 `PROJECT.md`를 산출하는 사전 단계.
- `paper`(프로젝트 사후 논문화)의 대칭 — 이건 프로젝트 **사전** 문제 구체화.
- 5단계 흐름: S0 포착 → S1 방법론 선택(발산→수렴) → S2 아이디어 발산 → S3 수렴·가치판정 → S4 PROJECT.md.
- 각 단계 끝에 **사용자 게이트**(G0~G3) — 단일 확인/선택으로 진행. 모호하면 깊게, 명확하면 Fast-track으로 축약.
- 실제 멀티에이전트(aimux)로 워커에게 PROPOSE/VERIFY 위임. aimux 없으면 매니저 단독 fallback.

---

**When to read**: when the user arrives with a vague wish (not a concrete spec) and a `PROJECT.md` does not yet exist or its required fields are empty. This is the stage *before* `intake.md`. If the wish is already a concrete, well-scoped request, skip straight to `intake.md`.

This guide is the **flow contract**. Operational detail lives in:
- `.claude/skills/ideate/SKILL.md` — entry point, invocation, aimux vs solo branch.
- `.claude/skills/ideate/methods/` — methodology library (one file per method).
- `.claude/skills/ideate/gate.md` — gate question templates and pass/fail criteria.
- `templates/ideate/` — PROJECT.md draft template, valuation rubric, gate checklist.

---

## 0. Principle — two-level diverge→converge

Ideation here applies **diverge→converge twice**:
1. **Methodology selection** (S1) — diverge candidate methods, converge on 2–3 that fit the wish.
2. **Idea development** (S2→S3) — diverge ideas with the chosen methods, converge on the project-worthy one.

This mirrors the harness's Phase 0 (`DESIGN.md §5`): everyone proposes independently, then the manager synthesizes — no anchoring on a first draft.

**Anti-theater rule**: cap methods at 2–3, and bind each chosen method to **one concrete unknown** it must resolve (see `methods/`). A method with no unknown to answer is dropped.

---

## 1. Ambiguity triage (sets the path)

At intake, classify the wish so the flow adapts:

| Level | Signal | Path |
|---|---|---|
| **Vague** | "뭔가 ~했으면", no clear problem/user/outcome | Full flow; S1 favors root/purpose methods (5 Whys, First Principles). |
| **Fuzzy** | Problem named, solution/scope open | Full flow; S1 favors reframing/option methods (HMW, SCAMPER, Crazy 8s). |
| **Clear** | Problem + rough solution + outcome already stated | **Fast-track**: skip S2 divergence; confirm framing, run a light valuation, go to S4. |

Record the level; it justifies the methodology choice in S1 and is written to the PROJECT.md domain note.

---

## 2. The five stages

### S0 — Capture & frame
- **Input**: a free-text idea memo file (if the user points to one) **and/or** conversation. If neither is clear, elicit with a few questions.
- **Do**: restate the wish in 2–3 sentences ("~하시려는 거죠?"). Run ambiguity triage (§1).
- **Gate G0 (의도 확인)**: user confirms the framing. On "no" → re-frame. Manager-only; no workers yet.

### S1 — Methodology selection (meta diverge→converge)
- **Diverge**: propose candidate methods fit to the wish's nature + ambiguity level. With aimux, send `PROPOSE` to 1–2 workers ("이 희망에 맞는 방법론 2~3개와 이유"); the manager also drafts its own. Solo mode: the manager lists candidates itself.
- **Converge**: manager synthesizes → pick **2–3** methods, each bound to a concrete unknown.
- **Gate G1 (방법 승인)**: show the chosen methods + the unknown each will answer. Clear wishes may auto-pass. On "no" → re-pick.

### S2 — Idea divergence
- **Do**: apply the chosen methods. With aimux, fan out `PROPOSE` units in parallel (one method/angle per worker) → collect framed options. Solo mode: the manager works each method in turn.
- **Routing**: main/creative work → opencode/gemini. **Sensitive/personal wishes → qwen only** (local; never to cloud agents). Simple research → qwen.
- **Output**: a deduped spread of candidate ideas/options (manager removes noise/duplicates before showing the user).

### S3 — Convergence & valuation
- **Do**: score candidates with the valuation rubric (`templates/ideate/`): 실현성 · 임팩트 · 적합(희망과의 정합) · 노력. Delegate this as `VERIFY` units ("이 아이디어의 강점·위험·필요 리소스를 평가, 증거 보고") — verification is work, not judgment. A pre-mortem (`methods/`) stress-tests the front-runner.
- **Converge**: manager synthesizes evidence → a recommended project-worthy idea + rationale.
- **Gate G2 (컨셉 확정)**: user picks/refines. On "no" → re-converge from another candidate or loop back to S2.

### S4 — Concretize to PROJECT.md
- **Do**: fill the harness `PROJECT.md` template (`templates/ideate/`): 이름 · 목적 · profile · 입력 · 출력 · 주요 제약 · 기술 스택 · 경로. Recommend the **downstream profile** (dev/research/docs/data/paper). Preserve the original wish as the request memo.
- **Also render the project README**: fill `templates/project/README.md` from the same PROJECT.md fields and **overwrite the scaffold's root `README.md`** so the copied folder reads as *this* project (the scaffold reference stays in `DESIGN.md`). Same step as `intake.md §3.6`.
- **Gate G3 (설계도 승인)**: user approves the PROJECT.md.
- **Exit**: hand the approved PROJECT.md to `intake.md` (which, finding required fields filled, confirms lightly and proceeds to `plan.md`).

---

## 3. Termination & loop control

- **Converged**: G3 approved → exit to intake/plan.
- **Round cap**: if S1–S3 loop more than **3 rounds** without converging, surface a "good-enough" choice to the user (top candidate as-is, or park the wish) instead of looping forever.
- **Abandon**: if valuation shows no project-worthy idea, say so plainly and stop — do not manufacture a project.

---

## 4. Roles (manager / worker)

- **Manager (claude)**: owns the dialogue, all gates, decomposition, convergence/synthesis, the final PROJECT.md, and accept/re-route decisions.
- **Workers**: `PROPOSE` (candidate methods in S1, candidate ideas in S2), `VERIFY` (valuation/pre-mortem in S3, PROJECT.md completeness in S4). Route by capability and data sensitivity (`AIMemory/agents.md`).
- **No aimux session?** The manager performs worker roles itself in a single session — same stages and gates, sequential instead of parallel. The `SKILL.md` branch decides which mode is active.

---

## 5. Relationship to intake.md

`ideate.md` handles the **vague-wish → idea → PROJECT.md** funnel. `intake.md` handles the **memo → structured PROJECT.md fields** fill. ideate sits in front: its output is a filled PROJECT.md that intake then validates. For an already-concrete request, skip ideate and use intake directly.

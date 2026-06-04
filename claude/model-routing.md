# model-routing.md — Model selection and switching

## 요약 (사용자용)

- 주력은 Sonnet. 단순·정형 반복은 Haiku 가능. Opus는 막혔을 때 재계획용.
- 같은 오류 2~3회 반복 / 추측 패치 누적 / 사용자 같은 지적 반복 → 멈춤.
- 멈춘 뒤: 롤백 → 사용자 보고 → Opus 전환 → 재계획 → Sonnet 복귀해 재구현.
- 막혔다고 느낄 때 먼저 `/compact`·관련 없는 파일 읽기 중단·가정 재진술 → 그래도 안 풀리면 전환.

---

**When to read**:
- Once at session start (for the default operating rules).
- Whenever trial-and-error is mounting (run the switchover procedure).

---

## 1. Defaults

- **Lead model is Sonnet.** Normal implementation, edits, and debugging.
- **Simple, formulaic, repetitive work** (file renaming, format conversion, short replies) can run on **Haiku**.
- **Don't use Opus by default.** Reserve it for replanning when stuck.

---

## 2. Sonnet → Opus triggers

If **any** of these signals appears, stop and go to §3.

- The same kind of error / failure recurs **2–3 times**.
- Fixes don't change the symptom, or new errors keep appearing in the same region.
- "I don't know why it's broken, but let me try X anyway" — **guess-patches piling up**.
- The user repeats the same complaint ("still doesn't work").
- The work unit has **10+ tool calls** with no progress.

---

## 3. Switchover procedure (in this order)

### 3.1 Roll back
- Undo the changes made in the stuck region.
  - With git: `git stash` or `git restore <files>`.
  - Without git: restore from backup or via Edit history.
- **Destructive commands** (`reset --hard`, `clean -f`, force-delete): **never without explicit user approval**.

### 3.2 Report status
Two short lines in Korean:
```
trial-and-error 누적이 감지되어 롤백했습니다.
Opus로 전환해 원인 분석·재계획을 진행하려고 합니다.
```

### 3.3 Switch model
- The user runs `/model opus` (or equivalent).
- If immediate switching isn't possible, **at least externalize the plan** with the current model and present it to the user.

### 3.4 Root-cause analysis + replan (Opus or `Plan` agent)
- Via the `Plan` agent or `ExitPlanMode`:
  - List the top 3 likely root causes.
  - Write a step-by-step, verifiable plan.
  - State the success criterion for each step.
- Get user agreement.

### 3.5 Re-implement
- After the plan is confirmed, **return to Sonnet** to implement.
- Verify after each step (`verify.md`).
- If complexity stays high, staying on Opus is acceptable.

---

## 4. Prevention

- Keep change units **small** and verify after each (`implement.md §1`).
- When the same error appears a **second time**, pause **before the third attempt** and write down hypotheses.
- When you feel stuck, first:
  1. Compact context (`/compact`).
  2. Stop reading unrelated files.
  3. Restate assumptions and verify them.
  Only switch the model if that doesn't unstick things.

---

## 5. Post-switch hygiene

- After re-implementation, if this trial-and-error episode is worth turning into a **regression-prevention rule**, write one line into feedback memory or project docs.
- Don't record one-off mistakes — that's noise.

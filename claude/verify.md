# verify.md — Verification stage guide

## 요약 (사용자용)

- 코드 변경 후 결과 확인. 타입체크·린트 통과만으로 끝내지 않고 실제 실행해서 결과를 본다.
- 빈 입력·`None`·큰 입력·비ASCII 같은 경계 테스트.
- 검증 기준은 CHECKLIST.md의 해당 단계에서 가져온다.
- 같은 오류 2~3회 반복 시 즉시 멈추고 `model-routing.md` 절차로.

---

**When to read**: after a code change, to confirm what actually happened.
Type-check / lint passes are **not** enough — **actually run it** and observe the output.

---

## 1. Basic checks

### 1.1 Run it
- Execute with sample input and inspect output by eye.
- For CLIs, verify `--help` against the argument set.
- For large datasets, **start with a small sample (N = 10–100)**, then scale.

### 1.2 Input edges
- Does it work on empty input, `None`, and large input?
- Encoding-safe on non-ASCII data (Korean, emoji)?
- Edge dates / times (end of month, year boundaries, time zones)?

### 1.3 Match the criteria
- Verify against **the verification criteria of the current CHECKLIST.md step**.
- If CHECKLIST.md doesn't exist (fast path), list the user's requirements and check them off explicitly.
- If something is missing, **report it openly** instead of hiding it. Then continue.

### 1.4 Side effects
- Did file / DB / external calls happen only where intended?
- Are temporary files cleaned up?
- Did any token / API key leak into logs?

---

## 2. Reporting to the user

Use vertical `key: value`:

```
변경 파일      : src/loader.py, src/cli.py
샘플 입력      : data/input/sample.xlsx (1,243행)
실행 시간      : 2.4초
출력 위치      : data/output/result.jsonl
검증 결과      : 요구사항 3/3 충족
회귀 점검      : 기존 케이스 2개 재실행 통과
남은 작업      : 없음
```

- If anything failed, **state it openly**: "X is unresolved; suspected cause is Y."
- Don't show only the cooked result — include a **raw sample** (5–10 rows).

---

## 3. Regression checks

- If the change could affect other features, run them too — briefly.
- Re-run 1–2 previously-passing cases to detect regressions.
- On suspicion, **bisect**: revert the changes one by one to identify the cause.

---

## 4. Handling failure

### 4.1 First failure
- Quote the error message verbatim, write down 1–3 hypotheses, and fix the most likely one first.
- After the fix, restart from §1.

### 4.2 Same error repeats (2–3 times)
- **Stop immediately.** No more guess-patches.
- Go to `claude/model-routing.md`'s switchover procedure:
  1. Roll back (`git stash` / `git restore` / manual restore).
  2. Report status to the user.
  3. Switch to Opus and replan.
  4. Once the plan is agreed, return to Sonnet and re-implement.

---

## 5. Docs / memory updates

After verification passes:
- **Complete CHECKLIST.md**: run `implement.md §6` (tick the box, bump counter, append history). If every step is done, mark `진행` as `전체/전체 완료`.
- Recheck that the README's usage / examples are still accurate.
- Record any non-obvious decisions or trade-offs briefly (commit message or `docs/`).
- If the user corrected a rule, save it to feedback memory.

---

## 6. Commit and push

- Commit only after verification passes **and** the user approves.
- Push only when the user explicitly requests it.
- Commit messages explain **the why**. (Co-Authored-By line: follow the tool guide.)

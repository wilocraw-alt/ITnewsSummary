# implement.md — Implementation stage guide

## 요약 (사용자용)

- 계획 확정 후 코드 변경 진입 직전 로딩.
- 한 번에 한 의미 단위(CHECKLIST.md의 한 단계). 컴파일·임포트 가능 상태에서 검증으로 넘김.
- 부분 변경은 `Edit`·`sed`. 통째 `Write`로 덮어쓰지 않음.
- 각 단계 완료 후: CHECKLIST.md 갱신 → 진행 화면 표시 → 컨텍스트 최적화 판단.
- 장시간 작업은 `status.sh` / `check_status.py` 함께 작성.

---

**When to read**: after planning is confirmed, just before starting code changes.

Domain-specific implementation rules (scraping, data collection, etc.) live in the relevant profile (`profiles/data.md` etc.).

---

## 1. Change unit

- **One meaningful unit at a time** — a single CHECKLIST.md step = a single change unit.
- Cut big changes into smaller units. After each, switch to `verify.md`, confirm, then move on.
- Issues discovered mid-unit go to a **separate task** — don't tack them onto the current unit.

---

## 2. Tool selection

| Task | Tool |
| --- | --- |
| Partial edit of existing file | `Edit` |
| Simple find / replace / delete | `sed -i 's/old/new/g' file` |
| Multi-file batch substitution | `find ... -exec sed -i ... {} +` |
| Variable rename across one file | `Edit` with `replace_all=true` |
| New file creation | `Write` |

- **Never overwrite an existing file with `Write`.** Partial edits win on tokens and safety.
- After editing, don't `Read` the same file again — the edit tool raises on failure.

---

## 3. Coding principles

### 3.1 Hard rules
- **No hardcoding.** Dates, paths, URLs, parameters must come from arguments, input files, or `.env`.
- **Secrets in `.env`.** Maintain `.env.example`. Check `.gitignore`.
- **Stick to scope.** No refactoring, no abstractions, no "while we're at it" changes.

### 3.2 Style
- Names express meaning. Don't abuse abbreviations.
- Comments only when the **why** is non-obvious. The **what** is shown by the identifier.
- New functions, tables, columns, variables get a **one-line Korean gloss** (docstring or inline comment).
  - Example: `def chunked(items, size):  # 청크 단위로 자르기`
  - Example: column `valid_until` → `유효기간 만료 시각`

### 3.3 Output and logging
- User-facing output: vertical `key: value`.
- Logs: JSONL or one line per event in plain text. Preserve raw → processed traceability — don't keep only the cooked result.

---

## 4. Dependencies

- When adding a package, update `requirements.txt` / `environment.yml` / `package.json` **immediately**.
- Use verified stable versions. Don't bump to latest just because.
- Prefer stdlib and familiar tools (`pandas`, `requests`, ...) first.

---

## 5. Environment reproducibility

- New files and env vars must be reflected in README and `.env.example`.
- Automate via `run.sh` or a single entrypoint.

---

## 6. Step-completion routine (perform after every step)

Immediately after `verify.md` passes, do these three, **in this order**:

### 6.1 Update CHECKLIST.md (with `Edit`)
1. Change the completed step's `[ ]` to `[x]`.
2. Bump the `진행` counter (`N/총` format).
3. Append one line to "진행 이력":
   ```
   YYYY-MM-DD HH:MM — N단계 완료: [단계명]
   ```

### 6.2 Print progress to the user
Use vertical `key: value`:
```
진행    : N/전체 단계 완료
방금    : N단계 — [방금 완료한 단계명]
다음    : N+1단계 — [다음 단계명]
남은    : [남은 단계 번호와 이름 목록]
```
If everything is done:
```
진행    : 전체/전체 완료
다음    : 검증 단계로 이동
```

### 6.3 Context-optimization decision
Run `/compact` if **any** of the following holds.
After compaction, re-read CHECKLIST.md to relocate yourself before moving on.

- The step just read a file with **500+ lines**.
- This step accumulated **15+ tool calls**.
- The next step's **domain is sharply different** from the current one
  (e.g., data collection → report writing; scraping → DB design).

Otherwise keep context and proceed.

---

## 7. When to hand off to verification

- The change unit compiles / imports cleanly, **or**
- A small sample runs end-to-end.

→ Load `verify.md` and confirm results.
→ After verification passes, run §6 (the step-completion routine).

---

## 8. Long-running batch / subagent work

When launching such work, also write a status-check script **before** starting.
The user must be able to monitor progress from a terminal even when Claude's session is closed or the work runs in the background.

### 8.1 Script criteria

- **Filename**: `status.sh` (shell) or `check_status.py` (Python) — pick to fit the project.
- **Location**: project root, or alongside `run.sh`.
- **Standalone execution**: works without virtualenv activation, or handles that itself (shebang, etc.).
- Output: vertical `key: value`.

### 8.2 What the script displays

```
상태     : 실행 중 / 완료 / 오류
진행     : 처리완료 / 전체  (예: 1,234 / 10,000)
성공     : N건
실패     : N건  (생략 가능 if 0)
경과     : HH:MM:SS
ETA      : HH:MM:SS  (when computable)
마지막   : 가장 최근 처리 항목 또는 로그 한 줄
로그     : logs/YYYY-MM-DD.jsonl  (경로)
```

### 8.3 Log format (what the status script reads)

The batch body writes JSONL in this shape:

```jsonc
// One line per processed unit
{"ts": "2026-05-21T14:00:00", "status": "ok",     "item": "...", "n": 1234, "total": 10000}
{"ts": "2026-05-21T14:00:01", "status": "error",  "item": "...", "error": "timeout"}
// Start / end markers
{"ts": "...", "event": "start", "total": 10000}
{"ts": "...", "event": "done",  "success": 9998, "fail": 2}
```

- `n` / `total` lets the script compute ETA.
- If using SQLite, equivalent aggregate queries via a `status` column also work.

### 8.4 Pre-launch checklist

- [ ] Log path decided (`logs/` or `data/output/`).
- [ ] Status script written and tested standalone (`bash status.sh` / `python check_status.py`).
- [ ] Batch body actually emits `event: start` / `event: done` markers.

---

## 9. When stuck

- If the same error repeats **2+ times**, jump immediately to `model-routing.md`'s switchover procedure.
- **No piling on guess-patches.**

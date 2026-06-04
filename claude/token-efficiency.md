# token-efficiency.md — Token-efficient operation

## 요약 (사용자용)

- 큰 파일·로그·데이터 처리 시 필요한 부분만 읽고 쓰기.
- 부분 변경은 `Edit`만. `Read → Write` 패턴 금지.
- 검색·탐색은 `grep` / `rg` / `jq`로 좁히거나 `Agent`(Explore) 위임.
- 결과는 파일로 떨어뜨리고 경로만 공유.

---

**When to read**: before touching large files, logs, or datasets — anywhere the context window could fill up.

Read and write **only what's needed**. Full context degrades reasoning and inflates cost.

---

## 1. Reading — "read whole file" is the last resort

- Check size first: `wc -l file`, `ls -lh file`.
- Use `Read`'s `offset` / `limit` to grab just the relevant slice.
- If you don't know where to look, narrow with search:
  ```bash
  grep -n "needle" file.py           # line numbers only
  rg -n "pattern" -C 3 src/          # ±3 lines of context
  grep -l "pattern" -r .             # filenames only
  grep -c "pattern" file             # match counts only
  ```
- JSON / JSONL: pull just the fields you need with `jq`:
  ```bash
  jq -r '.message.content' file.jsonl | head -50
  jq 'keys' file.json                # schema first
  jq -c '.[0:3]' file.json           # first 3 samples
  ```
- CSV / Excel: `head` or `pandas.read_excel(nrows=10)` for the schema first.

---

## 2. Editing — no `Read → Write` cycles

- Partial edits go through `Edit` only (sends diff, not whole file).
- Simple substitutions / renames: `sed -i` doesn't even need to read the file:
  ```bash
  sed -i 's/old_name/new_name/g' file.py
  sed -i '/^TODO/d' file.md                          # delete lines starting with TODO
  find . -name '*.py' -exec sed -i 's/A/B/g' {} +    # multi-file batch
  ```
- `Edit`'s `replace_all=true` is great for variable renames.
- Never overwrite an existing file with `Write`.
- Don't re-read a file you just edited.

---

## 3. Search and exploration — protect main context

- Broad, multi-step exploration: delegate to `Agent` (subagent_type=`Explore`). Only the summary comes back.
- When delegating, **bound the output**:
  - _"Summarize in under 200 words"_
  - _"File paths only"_
  - _"Up to 5 function definitions"_
- Single, definite lookups: use `grep` / `rg` directly without delegation.
- `find` starts from `.` or a specific path — **never scan from `/`**.

---

## 4. Large data and logs

- **Drop results to a file, share the path:**
  ```bash
  python script.py > out.jsonl
  wc -l out.jsonl                # row count only
  head -3 out.jsonl              # sample only
  ```
- Log debugging: narrow with `tail -n 100` and `grep ERROR`.
- DB queries: `LIMIT` first to get schema and samples.

---

## 5. Parallelism

- Independent lookups → **multiple tool_use blocks in one message**, executed in parallel.
- Only serialize when one call depends on a previous one.

---

## 6. Context management

- When a session gets long, run `/compact`.
- **Don't re-read information you already absorbed.** No re-reading a file you saw moments ago.
- Speculative pieces: try them and let results verify, instead of asking.
- Memory holds **reusable rules and background**. Don't store one-shot work details.

### Step-completion checkpoint (`implement.md §6.3`)

Right after each implementation step, check the conditions below.
If any match, run `/compact` → re-read CHECKLIST.md → continue.

`/compact` triggers (any one is enough):
- The step just read a file with 500+ lines.
- Tool calls accumulated to 15+ in this step.
- The next step's domain is sharply different from this one.

Skip `/compact` when:
- Tool calls < 10 and next step is in the same domain.

---

## 7. Output

- User responses are **decision- and result-focused**, short. Don't enumerate process.
- Show only changed code blocks. Don't paste whole files back.
- Tables and diagrams only when truly necessary. **No horizontal tables in user output.**

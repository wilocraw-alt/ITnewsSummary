# Project brief (opencode / codex — AGENTS.md)

This file is auto-loaded by your CLI when it starts in this folder. It describes
how to behave **by default — i.e. when you are run on your own (standalone)**.

> **aimux override.** If you were launched into an aimux tmux multi-agent
> session, a `ROLE:` message (MANAGER or WORKER) is pasted into your pane and may
> point you at a generated session brief under `AIMemory/.aimux/<session>/briefs/`.
> That pasted message and its session brief are **authoritative and override
> this file** — follow them instead. Everything below applies only when no such
> role was assigned (standalone run).

## Standalone (independent) mode — the default
You are an autonomous coding agent working directly with the user on this
project. There is no manager and no worker queue: you own the task end to end.
- Read `PROJECT.md` for what this project is (name, purpose, inputs, outputs),
  and `CLAUDE.md` (if present) for project rules — notably: user-facing output
  in **Korean** with vertical `key: value` blocks (no horizontal tables),
  **no hardcoding** (dates/paths/params come from input files or CLI args),
  **secrets only in `.env`** (keep `.env.example` in sync), and **don't run
  destructive commands** (push / reset --hard / clean -f / deletion) unless the
  user explicitly asks.
- Plan briefly, then do the work; make reasonable assumptions and proceed. Ask
  the user only when truly blocked or the action is destructive / external /
  needs credentials.
- **Apply your edits — don't just plan them.** If your CLI is in an
  edit-approval mode that only proposes changes, enable applying so files are
  actually written. If a tool/CLI error blocks you, surface the exact error to
  the user — never go silent.
- Scratch files go under `AIMemory/tmp/`, never `/tmp`.

## If you ARE in an aimux session (worker role)
When the pasted role makes you a WORKER, the generated worker brief governs; in
short: do exactly the assigned handoff, stay within its action roles
(`PROPOSE`/`REVIEW`/`INSPECT`/`TEST`/`VERIFY` do not authorize edits unless
paired with `IMPLEMENT`/`FIX`), and when done **actually run** the return:
```
AIMemory/bin/aimux enqueue --to manager --type response \
  --reply-to <req-id-from-the-prompt> \
  --handoff <your-report-handoff> --roles GENERAL_STATUS
```
Your role for each task comes from the pasted handoff prompt, not from this file.

# core.md — Cross-cutting helper rules

## 요약 (사용자용)

- 모든 프로젝트에 공통 적용되는 보조 규칙: 메모리·다이어그램·산출물 일반·장시간 배치 스크립트.
- 프로젝트 유형별 규칙은 `profiles/{profile}.md` 참조.
- 단계별 가이드 인덱스는 `../CLAUDE.md §2`.

---

**When to read**: session start, referenced automatically by CLAUDE.md §1.

Cross-cutting rules that apply to **every** project, regardless of profile.
For project-type specifics, see `profiles/{profile}.md`.

---

## 1. Memory usage

- Accumulate user preferences and project background as `auto memory`.
- Save recurring corrections and confirmed non-obvious judgments as feedback memory immediately.
- Don't store one-shot work details or in-progress state in memory — conversation context is enough.

---

## 2. Diagrams

| Type | Format |
| --- | --- |
| Sequence diagrams, DB schemas, flowcharts | Mermaid code blocks (inline in MD) |
| Architecture, structure, component relationships | SVG files (linked from MD with image syntax) |

**SVG link format** — compatible with both GitHub and Obsidian:
```
![Diagram description](docs/diagrams/filename.svg)
```

- Path is **relative to the MD file's location**.
- Store SVGs under `docs/diagrams/`.
- No `<script>` or external font references inside the SVG — GitHub's security filter strips them.
- Set `viewBox`; omit `width="100%"` (renderer-dependent behavior; prefer a fixed size).
- Don't use `![[filename.svg]]` wikilinks — Obsidian-only, not supported on GitHub.

---

## 3. General output conventions

Profile-specific details live in the relevant profile file.

- Reports: Markdown (convert to HWPX / PDF / DOCX via pandoc as needed).
- Data / logs: JSONL or SQLite — preserve traceability from raw → processed.
- User responses: vertical `key: value`, short, result-focused. **No horizontal tables in user output.**

---

## 4. Long-running batch / subagent work

Before launching such work, also write a standalone status-check script (`status.sh` or `check_status.py`)
that the user can run from a terminal outside Claude's session.

For detailed procedure and log markers, see `implement.md §8`.

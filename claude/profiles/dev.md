# profile: dev — Software development

## 요약 (사용자용)

- 코드(앱·라이브러리·CLI·자동화) 산출이 중심인 프로젝트.
- 기본 도구: Python 3.11+`pytest`+`.venv`(프로젝트 내부 가상환경), TS+`pnpm`+`vitest`, Go, Rust — PROJECT.md에서 덮어쓰기 가능.
- 한 커밋 = 한 의미 단위. 의존성 추가 시 매니페스트 파일에 즉시 반영.
- 새 함수·테이블·컬럼·변수에 한국어 설명 한 줄 병기.

---

**Project type**: apps, libraries, CLI tools, automation scripts — anywhere code is the primary deliverable.

---

## 1. Deliverables

- Source code (`src/` or language convention).
- Unit / integration tests (`tests/`).
- README and API docs.
- Optional: release artifacts (Docker image, PyPI / npm package).

---

## 2. Default tool stack

Override in PROJECT.md when a project needs something different.

- Languages: Python 3.11, TypeScript, Go, Rust — confirm with the user.
- Package management
  - Python: **프로젝트 내부 `.venv`** — `python -m venv .venv` (또는 `uv venv`). conda 같은 외부/전역 환경은 폴더와 분리돼 "따로 노는" 문제가 있으니 피한다. `.venv/`는 `.gitignore`에 넣고 의존성은 `requirements.txt`로 고정.
  - JS / TS: `pnpm`
  - Rust: `cargo`
- Tests: `pytest`, `vitest` / `jest`, `go test`.
- Lint / format: whatever the project already prescribes.

---

## 3. Workflow notes

Follow the standard `plan.md` → `implement.md` → `verify.md` flow.

Profile-specific rules:
- Move to verification only when the change unit **compiles / imports cleanly**.
- One commit = one meaningful unit, matching a single CHECKLIST.md step.
- When adding a dependency, **immediately** update the manifest (`requirements.txt`, `package.json`, `go.mod`, ...).
- New functions, tables, columns, variables carry a **one-line Korean gloss** as a docstring or comment.
  - Example: `def chunked(items, size):  # 청크 단위로 자르기`
  - Example: column `valid_until` → comment `유효기간 만료 시각`

---

## 4. References

- General implementation rules: `implement.md`
- Verification procedure: `verify.md`
- Large file handling: `token-efficiency.md`

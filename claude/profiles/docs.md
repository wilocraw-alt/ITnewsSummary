# profile: docs — Documentation updates, translation, restructuring

## 요약 (사용자용)

- 기존 문서 갱신, 매뉴얼·가이드 작성, 한·영 번역, 문서 구조 재정비.
- 톤·문체는 프로젝트 시작 시 한 가지로 통일 (존댓말 / 평어 / 학술체 중 택일).
- 번역은 직역 우선, 의역은 주석으로 표시.
- 새 문서 작성 전에 기존 문서 먼저 확인 — 중복·상충 방지.

---

**Project type**: refreshing existing docs, writing manuals and guides, Korean/English translation, restructuring documentation.

---

## 1. Deliverables

- Markdown documents (`docs/`, `README.md`).
- Change history (`CHANGELOG.md`).
- Translated counterparts (e.g., `README.md` + `README.ko.md`).
- Diagram assets (`docs/diagrams/*.svg`) — see `core.md §2`.

---

## 2. Default tool stack

- Markdown formatting: `prettier --prose-wrap=always` or `markdownlint`.
- Link checking: `markdown-link-check`.
- External conversion: pandoc (MD → HWPX / PDF / DOCX).
- Diagrams: `core.md §2`.

---

## 3. Writing and translation rules

- Tone / register consistency: settle on one style at project start (존댓말 / 평어 / 학술체).
- Translation: **literal first**; mark any interpretive rewording in a side comment.
- For technical terms, include a Korean gloss (per CLAUDE.md §0).
- Before drafting anything new, **survey existing documents first** — avoid duplication and contradiction.

---

## 4. Workflow

```
1. Survey                  scan existing structure; flag gaps / duplication
2. Plan changes            what to edit, add, or remove
3. Write / revise          one document or section at a time
4. Verify                  links resolve, example code runs
5. User review
```

Apply `implement.md §1`'s change-unit principle: one meaningful unit at a time.

---

## 5. References

- Token efficiency (large doc partial edits): `token-efficiency.md`

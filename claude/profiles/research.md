# profile: research — Research, literature review, analysis reports

## 요약 (사용자용)

- 문헌 조사·시장/기술 분석·논문 초안·정책 보고서 등 텍스트·근거 중심 프로젝트.
- 모든 주장에 출처. 추정은 "추정" / "가설"로 명시.
- 자료 원본은 `data/sources/`, 인용 목록은 `references.bib` 또는 `references.md`.
- 산출물 완성 후 인용 검증(링크·파일 유효성) 필수.

---

**Project type**: literature reviews, market / technology analyses, paper drafts, policy briefs — text and evidence are central.

---

## 1. Deliverables

- Report / paper body: Markdown (convert to HWPX / DOCX / PDF via pandoc).
- Citation list: `references.bib` (BibTeX) or `references.md`.
- Source materials: `data/sources/` — PDFs, web captures, interview notes, metadata.
- Working notes: `notes/` — exploration process, intermediate reasoning.

---

## 2. Default tool stack

- Literature search: `WebSearch`, `WebFetch`. Academic: Google Scholar, KCI, RISS.
- PDF handling: `pypdf` or `pdfplumber`. Scanned: `pytesseract` (OCR).
- Citation style: APA / Chicago / venue-specified — confirm at project start.
- English → Korean rendering: distinguish literal vs. interpretive translation; quote originals verbatim.

---

## 3. Source-management rules

- **Every claim carries a citation.** No unsourced assertions. Mark guesses explicitly as "추정" or "가설".
- Cite inline as `(Author, Year) [path or URL]`.
- Keep originals under `data/sources/`. Reference by filename + page when quoting.
- Before finalizing, **verify every citation**: links resolve, files are readable.

---

## 4. Workflow

```
1. Define scope and research questions      → note in PROJECT.md request memo
2. Collect sources                          → save under data/sources/
3. Organize / tag / summarize               → one-paragraph summary + keywords per source
4. Draft                                    → section per argument, mark hypotheses
5. Verify citations + user review
6. Final conversion                         → pandoc, etc.
```

Map `plan.md`'s step decomposition onto stages 5–6 above.

---

## 5. References

- Token efficiency (long PDFs): `token-efficiency.md`
- Verification (fact + citation focus): `verify.md`
- Reasoning quality: `llm-performance.md`

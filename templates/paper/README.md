# LaTeX + Word paper scaffold (aimux run case study)

Skeleton for writing a paper **from a completed aimux project's records**.
Procedure: `claude/profiles/paper.md` (the `paper` profile). Builds to **PDF and
Word (.docx)**, with figures, and is **version-managed** so iterations never
clobber earlier drafts.

## Inputs (cite these — do not invent numbers)
- `<completed-project>/AIMemory/run-summary.json` — machine-authored metrics
  (schema `aimux-run-summary/1`); the latest mirror, history under
  `run-summary/vNNN-*.json`. Refresh with `aimux report --write` / `aimux
  checkpoint`.
- `…/AIMemory/work.log` — narrative (use for the story; numbers → run-summary).
- `…/AIMemory/handoff_*.md` — plans/reports. `DESIGN.md` etc. — the method.

## Build
```
make            # pdf + docx
make pdf        # main.pdf  (xelatex; figures auto-built)
make docx       # main.docx (pandoc; inlines refs, embeds figure PNGs)
make figures    # (re)build figures only
make clean
```
Toolchain: latexmk + xelatex (Korean: texlive-lang-korean + fonts-nanum),
pandoc, rsvg-convert (librsvg2-bin), ghostscript `gs`.

## Versioning — iterate without clobbering
Before each revision round (responding to feedback), snapshot the current draft:
```
make snapshot LABEL=<what-this-version-is>     # -> versions/vNNN-<date>-<label>/
```
Then edit **incrementally** — change only what the feedback targets; do NOT
regenerate the whole paper. Earlier versions stay in `versions/` for comparison
or rollback.

## Figures (PDF + Word)
Author figures in `figures/`, include them in LaTeX **without an extension**
(`\includegraphics{figures/<name>}`) — the PDF uses `.pdf`, the Word build uses
`.png` (rewritten by `build_docx.py`). Two sources are supported:
- `figures/<name>.svg` — diagrams (e.g. `experiment-structure.svg`, the overall
  experiment design). Edit the SVG to match the real experiment.
- `figures/<name>.fig.tex` — standalone pgfplots **charts** for numerical
  comparison (e.g. `results-bar.fig.tex`). Pair every chart with a `booktabs`
  table in the text.

## Files
`main.tex`, `sections/*.tex`, `references.bib`, `figures/`, `Makefile`,
`snapshot.sh`, `build_docx.py`, `versions/`.

## Writing rules (see `claude/profiles/paper.md` for detail)
- **Related Work is required**: survey prior research and state similarities &
  differences vs. this work. Cite real external literature only.
- **Never name internal project artifacts** (run-summary.json, per_agent,
  compare_*.md, work.log, handoff_*, aimux…) in the paper text/captions/refs —
  report their data as *measured results*. They are not citable sources.
- **Write for a non-expert**: motivate the problem, describe the example and its
  characteristics, define key terms briefly.
- **Stay on theme**: omit off-topic trial-and-error that doesn't serve the thesis.
- Every quantitative claim traces (author-side) to a real measurement.

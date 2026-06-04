# Build the paper to BOTH PDF and Word (.docx), with figures.
# Toolchain: latexmk + xelatex (texlive-xetex; for Korean: texlive-lang-korean +
# fonts-nanum), pandoc (docx), rsvg-convert (librsvg2-bin; SVG figures),
# ghostscript `gs` (pgfplots/standalone-tex charts -> PNG). English-only papers
# may switch xelatex->pdflatex.
PAPER=main

all: pdf docx

# --- figures: one source -> PDF (for LaTeX) + PNG (for Word). Include them in
# --- LaTeX WITHOUT an extension: \includegraphics{figures/name} (pdflatex uses
# --- .pdf; build_docx.py rewrites to .png so Word embeds the raster). ---------
SVGS  := $(wildcard figures/*.svg)
FIGTEX:= $(wildcard figures/*.fig.tex)
FIGS  := $(SVGS:.svg=.pdf) $(SVGS:.svg=.png) $(FIGTEX:.fig.tex=.pdf) $(FIGTEX:.fig.tex=.png)

figures: $(FIGS)

# Diagrams authored as SVG (easy to hand-edit; e.g. the experiment structure).
figures/%.pdf: figures/%.svg
	rsvg-convert -f pdf -o $@ $<
figures/%.png: figures/%.svg
	rsvg-convert -f png -d 150 -p 150 -o $@ $<

# Data charts authored as standalone LaTeX (pgfplots): figures/<name>.fig.tex.
figures/%.pdf: figures/%.fig.tex
	cd figures && pdflatex -interaction=nonstopmode $*.fig.tex >/dev/null 2>&1 && mv $*.fig.pdf $*.pdf
figures/%.png: figures/%.pdf
	gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r150 -dUseCropBox -sOutputFile=$@ $<

pdf: figures
	latexmk -xelatex -interaction=nonstopmode $(PAPER).tex || \
	( xelatex -interaction=nonstopmode $(PAPER).tex && bibtex $(PAPER) && \
	  xelatex -interaction=nonstopmode $(PAPER).tex && xelatex -interaction=nonstopmode $(PAPER).tex )

# Same content as the PDF, as Word. build_docx.py inlines main.bbl, turns
# \cite{k} into [n], and rewrites figures to .png so citations + figures render
# in Word too (works with pandoc < 2.11, no citeproc needed).
docx: main.bbl figures
	python3 build_docx.py

main.bbl:
	$(MAKE) pdf

# Snapshot the current paper (sources + outputs) to versions/vNNN-<date>[-label]/
# BEFORE a rewrite so prior versions are never clobbered:  make snapshot LABEL=foo
snapshot:
	./snapshot.sh $(LABEL)

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.fls *.fdb_latexmk *.xdv sections/*.aux \
	      figures/*.aux figures/*.log .main_docx.tex

.PHONY: all pdf docx figures snapshot clean

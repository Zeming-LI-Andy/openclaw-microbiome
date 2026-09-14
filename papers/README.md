# papers/

English academic manuscript workspace for this repo.

## Compile in Cursor

1. Open `papers/main.tex`.
2. Save (auto-build is on) or click **Build LaTeX project** in LaTeX Workshop.
3. The PDF opens in a Cursor tab; aux files go to `papers/build/`.

Command line (after TeX Live is on `PATH`):

```powershell
cd D:\Projects\openclaw-microbiome\papers
latexmk -pdf -synctex=1 -interaction=nonstopmode -outdir=build main.tex
```

Switch engine in Cursor: `Ctrl+Shift+P` → **LaTeX Workshop: Build with recipe** → `latexmk (xelatex)`.

## Layout

| Path | Role |
|------|------|
| `main.tex` | Article body |
| `project-review.md` | Source-checked system summary and evidence gaps for the manuscript |
| `refs.bib` | BibLaTeX sources |
| `figures/` | Images (`\includegraphics`) |
| `.latexmkrc` | pdfLaTeX + biber, output in `build/` |

Default stack: **pdfLaTeX** + **biblatex/biber** (`authoryear`). Verify each added citation against its primary source before submitting.

#!/usr/bin/env bash
#
# Build an arXiv-ready submission from paper.md, using JOSS's own compiler.
#
# JOSS's intended arXiv route is EditorialBot's `@editorialbot generate preprint`,
# which is only available once a submission issue exists. Before then, the same
# output comes from Inara's `preprint` target, which this script runs.
#
# Output: arxiv/arxiv-submission.tar.gz — upload that file to arXiv directly.
# The bundle needs no .bib and no .bbl: citeproc bakes the reference list into
# the .tex as a CSLReferences environment, so pdflatex alone resolves everything
# in two passes.
#
# Usage:  ./make_arxiv.sh          (from the paper/ directory)

set -euo pipefail
cd "$(dirname "$0")"

OUT=arxiv
rm -rf "$OUT"
mkdir -p "$OUT"

echo "==> Generating preprint LaTeX with Inara"
docker run --rm \
  --volume "$PWD:/data" \
  --user "$(id -u):$(id -g)" \
  --env JOURNAL=joss \
  openjournals/inara -o preprint paper.md

# Inara writes paper.preprint.tex next to paper.md.
mv paper.preprint.tex "$OUT/paper.tex"

echo "==> Patching in \\pandocbounded"
# Inara's preprint.latex template omits pandoc's common.latex partial, which is
# where \pandocbounded is defined. Since pandoc 3.5 every figure is wrapped in
# that macro, so the generated .tex references a command the preamble never
# defines and the build dies with "Undefined control sequence" at the first
# \includegraphics. The JOSS PDF is unaffected: its template (default.latex)
# does include the partial. Definition below is copied verbatim from pandoc's
# built-in templates/common.latex. Drop this step if Inara fixes the template.
python3 - "$OUT/paper.tex" <<'PY'
import sys
path = sys.argv[1]
src = open(path).read()
if '\\newcommand*\\pandocbounded' in src:
    print("    already defined, nothing to do")
    raise SystemExit
if '\\pandocbounded' not in src:
    print("    macro not used by this build, nothing to do")
    raise SystemExit
DEF = r"""% --- pandoc >= 3.5 emits \pandocbounded; Inara's preprint template does not
% --- define it (it omits pandoc's common.latex partial). Definition copied
% --- verbatim from pandoc's built-in templates/common.latex.
\makeatletter
\newsavebox\pandoc@box
\newcommand*\pandocbounded[1]{% scales image to fit in text height/width
  \sbox\pandoc@box{#1}%
  \Gscale@div\@tempa{\textheight}{\dimexpr\ht\pandoc@box+\dp\pandoc@box\relax}%
  \Gscale@div\@tempb{\linewidth}{\wd\pandoc@box}%
  \ifdim\@tempb\p@<\@tempa\p@\let\@tempa\@tempb\fi% select the smaller of both
  \ifdim\@tempa\p@<\p@\scalebox{\@tempa}{\usebox\pandoc@box}%
  \else\usebox{\pandoc@box}%
  \fi%
}
% Set default figure placement to htbp
\def\fps@figure{htbp}
\makeatother

"""
open(path, 'w').write(src.replace('\\begin{document}', DEF + '\\begin{document}', 1))
print("    patched")
PY

echo "==> Collecting figures"
# Every image paper.md references, resolved relative to paper/.
grep -oE '\]\([^)]+\.(png|jpg|pdf)\)' paper.md | sed 's/^](//;s/)$//' | sort -u | while read -r fig; do
  cp "$fig" "$OUT/$(basename "$fig")"
  echo "    $fig"
done

echo "==> Test-compiling exactly as arXiv does (pdflatex, two passes)"
if command -v latexmk >/dev/null; then
  ( cd "$OUT" && latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex >build.log 2>&1 ) || {
    echo "!!! pdflatex FAILED — do not upload. Last errors:"
    grep -iE '^! |LaTeX Error' "$OUT/build.log" | head
    exit 1
  }
  if pdftotext "$OUT/paper.pdf" - 2>/dev/null | grep -q '???'; then
    echo "!!! unresolved citations in the PDF — do not upload"
    exit 1
  fi
  echo "    OK: $(pdfinfo "$OUT/paper.pdf" | awk '/Pages/{print $2}') pages, all citations resolved"
else
  echo "    skipped (no latexmk); the tarball is untested"
fi

echo "==> Packaging"
tar czf "$OUT/arxiv-submission.tar.gz" -C "$OUT" \
  paper.tex $(cd "$OUT" && ls *.png *.jpg *.pdf 2>/dev/null | grep -v '^paper\.pdf$' | tr '\n' ' ')

echo
echo "Upload this to arXiv: $PWD/$OUT/arxiv-submission.tar.gz"
echo "Local preview:        $PWD/$OUT/paper.pdf"

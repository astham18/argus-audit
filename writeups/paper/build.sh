#!/usr/bin/env bash
# Build main.pdf with Tectonic, then print the page readout.
# Usage: bash build.sh            (set TECTONIC=/path/to/tectonic to use a binary not on PATH)
set -euo pipefail
cd "$(dirname "$0")"

TECTONIC="${TECTONIC:-$HOME/bin/tectonic}"; command -v "$TECTONIC" >/dev/null 2>&1 || TECTONIC=tectonic
if ! command -v "$TECTONIC" >/dev/null 2>&1; then
  echo "Tectonic not found. Download the release binary to ~/bin/tectonic (see README)" >&2
  exit 1
fi

# Figures: regenerate a PDF only if its SVG is newer (needs uv and the cairo library).
for svg in figures/*.svg; do
  pdf="${svg%.svg}.pdf"
  if [ ! -f "$pdf" ] || [ "$svg" -nt "$pdf" ]; then
    echo "Converting $svg"
    (cd figures && uv run --no-project --python cpython-3.11-macos-x86_64-none --with cairosvg \
      python svg_to_pdf.py "$(basename "$svg")")
  fi
done

# Tectonic runs BibTeX and reruns LaTeX as needed; --keep-logs keeps main.log.
"$TECTONIC" --keep-logs --print main.tex > build.log 2>&1 || { tail -40 build.log; exit 1; }
echo "Built main.pdf"

overfull=$(grep -c "^Overfull" main.log || true)
echo "Overfull boxes: $overfull (details: grep -A2 ^Overfull main.log)"

# Page readout from the PDF bookmarks (one per top-level section, plus an end-of-main-text marker).
uv run --no-project --quiet --with pypdf python - <<'PY'
from pypdf import PdfReader
r = PdfReader("main.pdf")
total = len(r.pages)
tops = [(o.title, r.get_destination_page_number(o) + 1) for o in r.outline if not isinstance(o, list)]
end_main = next(p for t, p in tops if t == "[End of main text]")
first_app = next((p for t, p in tops if t[:2] in ("A ", "A.")), None)
print(f"\nTotal pages: {total}")
print(f"Main text (title through Conclusion): pages 1-{end_main}  ({end_main} pages; target about 10)")
print(f"Back matter (code and data, references, appendices): pages {end_main}-{total}")
if first_app:
    print(f"Appendices start on page {first_app}")
print("\nPage  Section")
for t, p in tops:
    if t != "[End of main text]":
        print(f"{p:>4}  {t}")
    else:
        print(f"{p:>4}  -- end of main text --")
PY

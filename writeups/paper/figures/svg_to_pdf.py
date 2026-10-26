"""Convert the paper's SVG figures to PDF.

The SVGs were drawn for the web: colours are CSS custom properties with a
dark-mode override, and value labels use `paint-order: stroke` for a halo.
cairosvg supports neither, so this script resolves every var(--x) to its
light-theme value, drops the dark-mode rules and the halo, and then converts.

Run from this folder:
    uv run --with cairosvg python svg_to_pdf.py            # all *.svg here
    uv run --with cairosvg python svg_to_pdf.py fig3_dose.svg
"""
import re
import sys
from pathlib import Path

import cairosvg

FONT = 'font-family:Helvetica,Arial,sans-serif'


def light_vars(style: str) -> dict:
    """Custom properties from the first rule block that defines any."""
    first = re.search(r'\{([^{}]*--[\w-]+\s*:[^{}]*)\}', style)
    return dict(re.findall(r'(--[\w-]+)\s*:\s*([^;}]+)', first.group(1))) if first else {}


def clean(svg: str) -> str:
    # a web-only `style="max-width:100%;height:auto"` on the root makes cairosvg draw nothing
    svg = re.sub(r'(<svg\b[^>]*?)\sstyle="[^"]*"', r'\1', svg, count=1)
    m = re.search(r'<style>(.*?)</style>', svg, re.S)
    if not m:
        return svg
    style = m.group(1)
    vars_ = light_vars(style)
    # drop the dark-mode media block and explicit dark-theme rules
    style = re.sub(r'@media\s*\(prefers-color-scheme:\s*dark\)\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', style)
    style = re.sub(r':root\[data-theme="dark"\][^{]*\{[^}]*\}', '', style)
    # drop the custom-property definitions themselves
    style = re.sub(r'--[\w-]+\s*:[^;}]+;?', '', style)
    # cairosvg ignores paint-order, so a stroke halo would paint over the text
    style = re.sub(r'paint-order:\s*stroke;?', '', style)
    style = re.sub(r'(\.val\{[^}]*?)stroke:[^;}]+;?stroke-width:[^;}]+;?stroke-linejoin:[^;}]+;?', r'\1', style)
    style = re.sub(r'font-family:[^;}]+', FONT, style)
    svg = svg[:m.start(1)] + style + svg[m.end(1):]

    def sub(mm):
        name = mm.group(1)
        return vars_.get(name, mm.group(2) or '#000').strip()

    for _ in range(3):  # nested var() references
        svg = re.sub(r'var\((--[\w-]+)(?:\s*,\s*([^)]+))?\)', sub, svg)
    svg = re.sub(r'font-family="[^"]*"', 'font-family="Helvetica, Arial, sans-serif"', svg)
    # cairo's text API has no glyph fallback and Helvetica has no arrow
    svg = re.sub(r'(<text\b[^>]*>[^<]*?)→', r'\1<tspan style="font-family:Arial Unicode MS">→</tspan>', svg)
    # the LaTeX caption numbers the figure, so drop an in-image "Figure N." title and crop its strip
    t = re.search(r'<text[^>]*class="ttl"[^>]*>Figure \d[^<]*</text>', svg)
    if t:
        svg = svg[:t.start()] + svg[t.end():]
        vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
        w, h = float(vb.group(1)), float(vb.group(2))
        svg = svg.replace(vb.group(0), f'viewBox="0 26 {w:g} {h - 26:g}"', 1)
        svg = re.sub(r'(<svg\b[^>]*?)height="[\d.]+"', rf'\g<1>height="{h - 26:g}"', svg, count=1)
    return svg


def main(paths):
    here = Path(__file__).resolve().parent
    files = [Path(p) for p in paths] or sorted(here.glob('*.svg'))
    for f in files:
        f = f if f.is_absolute() else here / f
        out = f.with_suffix('.pdf')
        cairosvg.svg2pdf(bytestring=clean(f.read_text()).encode(), write_to=str(out))
        print(f'{f.name} -> {out.name}')


if __name__ == '__main__':
    main(sys.argv[1:])

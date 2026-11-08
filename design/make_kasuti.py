#!/usr/bin/env python3
"""Generate static/kasuti.svg: the landing page's hero band.

Interlocked temple-tower triangles (tope-teni, from the Ilkal saree border)
drawn as Kasuti cross-stitches. One tile; the page repeats it along x.
"""

import os

CELL = 6      # px per stitch
ROWS = 9
COLS = 18
RED = "#D12A36"
TURMERIC = "#EDB120"


def stitch(col, row):
    x, y = col * CELL + 1, row * CELL + 1
    s = CELL - 2
    return f"M{x} {y}l{s} {s}M{x + s} {y}l-{s} {s}"


def distance(col, centre):
    """Horizontal distance on the repeating tile."""
    d = abs(col - centre)
    return min(d, COLS - d)


red, turmeric = [], []
for row in range(ROWS):
    for col in range(COLS):
        if distance(col, 9) <= row:              # tower pointing up
            red.append(stitch(col, row))
        elif distance(col, 0) <= ROWS - row - 2:  # tower pointing down, one stitch apart
            turmeric.append(stitch(col, row))

w, h = COLS * CELL, ROWS * CELL
svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
    f'fill="none" stroke-width="1.5" stroke-linecap="round">'
    f'<path stroke="{RED}" d="{"".join(red)}"/>'
    f'<path stroke="{TURMERIC}" d="{"".join(turmeric)}"/>'
    f"</svg>\n"
)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "kasuti.svg")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print(f"{os.path.normpath(out)}: {len(svg)} bytes, {w}x{h}")

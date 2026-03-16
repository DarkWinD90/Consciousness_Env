# USPTO PATENT DRAWING COMPLIANCE REPORT

**Date**: 2026-03-16
**Scope**: 21 SVG drawings across Patent A/B/C
**Validator mode**: strict (visual margin raster check + source SVG semantic checks)
**Checks**: page geometry, statutory margins, minimum text size, black/white-only palette, figure label, sheet numbering, diagram hygiene (signal crossings/collisions/leaders)

| Patent | Figure | Sheet | ViewBox 850x1100 | Margins | Min Text >=12.6 | B/W only | Label `FIG. X` | Sheet `n/N` | Diagram hygiene | Status |
|---|---:|---:|---|---|---|---|---|---|---|---|
| patent_a | FIG. 1 | 1/8 | PASS | FAIL | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 2 | 2/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 3 | 3/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 4 | 4/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 5 | 5/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 6 | 6/8 | PASS | FAIL | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 7 | 7/8 | PASS | FAIL | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 8 | 8/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_b | FIG. 1 | 1/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_b | FIG. 2 | 2/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_b | FIG. 3 | 3/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_b | FIG. 4 | 4/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_b | FIG. 5 | 5/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_b | FIG. 6 | 6/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_c | FIG. 1 | 1/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_c | FIG. 2 | 2/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_c | FIG. 3 | 3/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_c | FIG. 4 | 4/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_c | FIG. 5 | 5/7 | PASS | FAIL | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_c | FIG. 6 | 6/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_c | FIG. 7 | 7/7 | PASS | FAIL | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |

## Issues (failing checks)
- `patent_drawings/patent_a/fig1.svg`
  - margins: top content at y=96
  - diagram: signal path #1 has floating start/end
- `patent_drawings/patent_a/fig2.svg`
  - diagram: reference numeral 100 missing nearby leader line, reference numeral 1000 missing nearby leader line, reference numeral 1500 missing nearby leader line, reference numeral 500 missing nearby leader line, signal path #1 has floating start/end, signal path #2 has floating start/end, signal path #3 has floating start/end
- `patent_drawings/patent_a/fig3.svg`
  - diagram: component overlap/collision detected, reference numeral 52 overlaps element, reference numeral 54 overlaps element, reference numeral 56 overlaps element, reference numeral 58 overlaps element, reference numeral 64 overlaps element, signal path #1 has floating start/end, signal path #2 has floating start/end, signal path #9 has floating start/end, signal path crossing detected
- `patent_drawings/patent_a/fig4.svg`
  - diagram: component overlap/collision detected, reference numeral 22 overlaps element, reference numeral 72 overlaps element, reference numeral 74 overlaps element, reference numeral 76 overlaps element, reference numeral 78 overlaps element, reference numeral 80 overlaps element, reference numeral 82 overlaps element, reference numeral 84 overlaps element, reference numeral 86 overlaps element
- `patent_drawings/patent_a/fig5.svg`
  - diagram: component overlap/collision detected, reference numeral 100 overlaps element, reference numeral 102 overlaps element, reference numeral 104 overlaps element, reference numeral 132 overlaps element, reference numeral 134 overlaps element, reference numeral 136 overlaps element, reference numeral 138 overlaps element, reference numeral 96 overlaps element, reference numeral 98 overlaps element, signal path crossing detected
- `patent_drawings/patent_a/fig6.svg`
  - margins: left content at x=80
  - diagram: component overlap/collision detected, reference numeral 26 overlaps element, reference numeral 72 overlaps element, signal path #1 has floating start/end, signal path #10 has floating start/end, signal path #2 has floating start/end, signal path #3 has floating start/end, signal path #4 has floating start/end, signal path #8 has floating start/end, signal path #9 has floating start/end
- `patent_drawings/patent_a/fig7.svg`
  - margins: left content at x=89
  - diagram: reference numeral 0 missing nearby leader line, reference numeral 0 overlaps element, reference numeral 116 overlaps element, reference numeral 118 overlaps element, reference numeral 122 overlaps element, reference numeral 124 overlaps element
- `patent_drawings/patent_a/fig8.svg`
  - diagram: component overlap/collision detected, reference numeral 12 overlaps element, reference numeral 126 overlaps element, reference numeral 128 overlaps element, reference numeral 130 overlaps element, reference numeral 14 overlaps element, reference numeral 16 overlaps element, reference numeral 20 overlaps element, reference numeral 22 overlaps element, reference numeral 28 overlaps element, signal path crossing detected
- `patent_drawings/patent_b/fig1.svg`
  - diagram: signal path #7 has floating start/end
- `patent_drawings/patent_b/fig2.svg`
  - diagram: component overlap/collision detected
- `patent_drawings/patent_b/fig3.svg`
  - diagram: signal path #1 has floating start/end, signal path #2 has floating start/end, signal path #6 has floating start/end, signal path #7 has floating start/end, signal path #8 has floating start/end, signal path #9 has floating start/end, signal path crossing detected
- `patent_drawings/patent_b/fig4.svg`
  - diagram: signal path #4 has floating start/end, signal path #5 has floating start/end
- `patent_drawings/patent_b/fig5.svg`
  - diagram: reference numeral 0 missing nearby leader line, reference numeral 100 missing nearby leader line, reference numeral 15 missing nearby leader line, reference numeral 30 missing nearby leader line, reference numeral 80 missing nearby leader line
- `patent_drawings/patent_b/fig6.svg`
  - diagram: signal path #4 has floating start/end, signal path #5 has floating start/end, signal path #6 has floating start/end, signal path #8 has floating start/end, signal path #9 has floating start/end, signal path crossing detected
- `patent_drawings/patent_c/fig1.svg`
  - diagram: component overlap/collision detected, reference numeral 24 overlaps element
- `patent_drawings/patent_c/fig2.svg`
  - diagram: signal path #1 has floating start/end
- `patent_drawings/patent_c/fig3.svg`
  - diagram: reference numeral 0 missing nearby leader line, signal path #1 has floating start/end, signal path #2 has floating start/end, signal path #3 has floating start/end, signal path #4 has floating start/end, signal path #5 has floating start/end
- `patent_drawings/patent_c/fig4.svg`
  - diagram: reference numeral 0 missing nearby leader line, reference numeral 100 missing nearby leader line, reference numeral 250 missing nearby leader line, reference numeral 500 missing nearby leader line, signal path #1 has floating start/end, signal path #2 has floating start/end, signal path #3 has floating start/end, signal path #4 has floating start/end, signal path #5 has floating start/end, signal path #6 has floating start/end, signal path #7 has floating start/end, signal path crossing detected
- `patent_drawings/patent_c/fig5.svg`
  - margins: left content at x=98, top content at y=91
  - diagram: component overlap/collision detected, reference numeral 68 overlaps element, reference numeral 70 overlaps element, reference numeral 72 overlaps element, signal path #3 has floating start/end, signal path #4 has floating start/end, signal path #5 has floating start/end, signal path #6 has floating start/end, signal path #7 has floating start/end
- `patent_drawings/patent_c/fig6.svg`
  - diagram: component overlap/collision detected, reference numeral 82 overlaps element, signal path #1 has floating start/end, signal path #2 has floating start/end, signal path #3 has floating start/end, signal path #4 has floating start/end
- `patent_drawings/patent_c/fig7.svg`
  - margins: top content at y=90
  - diagram: signal path #10 has floating start/end, signal path #11 has floating start/end, signal path #2 has floating start/end, signal path #3 has floating start/end, signal path #9 has floating start/end

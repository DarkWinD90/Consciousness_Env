# USPTO PATENT DRAWING COMPLIANCE REPORT

**Date**: 2026-03-16
**Scope**: 21 SVG drawings across Patent A/B/C
**Validator mode**: strict (visual margin raster check + source SVG semantic checks)
**Checks**: page geometry, statutory margins, minimum text size, black/white-only palette, figure label, sheet numbering, diagram hygiene (signal crossings/collisions/leaders)

| Patent | Figure | Sheet | ViewBox 850x1100 | Margins | Min Text >=12.6 | B/W only | Label `FIG. X` | Sheet `n/N` | Diagram hygiene | Status |
|---|---:|---:|---|---|---|---|---|---|---|---|
| patent_a | FIG. 1 | 1/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_a | FIG. 2 | 2/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_a | FIG. 3 | 3/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 4 | 4/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 5 | 5/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 6 | 6/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 7 | 7/8 | PASS | FAIL | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 8 | 8/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_b | FIG. 1 | 1/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_b | FIG. 2 | 2/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_b | FIG. 3 | 3/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_b | FIG. 4 | 4/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_b | FIG. 5 | 5/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_b | FIG. 6 | 6/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_c | FIG. 1 | 1/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_c | FIG. 2 | 2/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_c | FIG. 3 | 3/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_c | FIG. 4 | 4/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_c | FIG. 5 | 5/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_c | FIG. 6 | 6/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_c | FIG. 7 | 7/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |

## Issues (failing checks)
- `patent_drawings/patent_a/fig3.svg`
  - diagram: component overlap/collision detected, signal path #11 has floating start/end, signal path #8 has floating start/end, signal path crossing detected
- `patent_drawings/patent_a/fig4.svg`
  - diagram: signal path #1 has floating start/end, signal path #2 has floating start/end, signal path crossing detected
- `patent_drawings/patent_a/fig5.svg`
  - diagram: signal path #1 has floating start/end, signal path #2 has floating start/end, signal path #3 has floating start/end, signal path #4 has floating start/end, signal path #5 has floating start/end, signal path crossing detected
- `patent_drawings/patent_a/fig6.svg`
  - diagram: signal path #1 has floating start/end, signal path #2 has floating start/end, signal path #3 has floating start/end, signal path #7 has floating start/end, signal path #8 has floating start/end
- `patent_drawings/patent_a/fig7.svg`
  - margins: left content at x=99
  - diagram: reference numeral 120 overlaps element
- `patent_drawings/patent_a/fig8.svg`
  - diagram: signal path #1 has floating start/end, signal path #2 has floating start/end, signal path #5 has floating start/end, signal path #6 has floating start/end, signal path crossing detected

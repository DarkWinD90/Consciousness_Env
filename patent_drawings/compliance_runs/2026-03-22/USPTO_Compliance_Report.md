# USPTO PATENT DRAWING COMPLIANCE REPORT

**Date**: 2026-03-22
**Scope**: 21 SVG drawings across Patent A/B/C
**Validator mode**: strict (visual margin raster check + source SVG semantic checks)
**Checks**: page geometry, statutory margins, minimum text size, black/white-only palette, figure label, sheet numbering, diagram hygiene (signal crossings/collisions/leaders)

| Patent | Figure | Sheet | ViewBox 850x1100 | Margins | Min Text >=12.6 | B/W only | Label `FIG. X` | Sheet `n/N` | Diagram hygiene | Status |
|---|---:|---:|---|---|---|---|---|---|---|---|
| patent_a | FIG. 1 | 1/8 | PASS | FAIL | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 2 | 2/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 3 | 3/8 | PASS | FAIL | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 4 | 4/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_a | FIG. 5 | 5/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_a | FIG. 6 | 6/8 | PASS | FAIL | PASS (min=14.0) | PASS | PASS | PASS | PASS | **FAIL** |
| patent_a | FIG. 7 | 7/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_a | FIG. 8 | 8/8 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_b | FIG. 1 | 1/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_b | FIG. 2 | 2/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_b | FIG. 3 | 3/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_b | FIG. 4 | 4/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_b | FIG. 5 | 5/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_b | FIG. 6 | 6/6 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_c | FIG. 1 | 1/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_c | FIG. 2 | 2/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_c | FIG. 3 | 3/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_c | FIG. 4 | 4/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | FAIL | **FAIL** |
| patent_c | FIG. 5 | 5/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_c | FIG. 6 | 6/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |
| patent_c | FIG. 7 | 7/7 | PASS | PASS | PASS (min=14.0) | PASS | PASS | PASS | PASS | **PASS** |

## Issues (failing checks)
- `patent_drawings/patent_a/fig1.svg`
  - margins: top content at y=96
  - diagram: signal path #1 has floating start/end
- `patent_drawings/patent_a/fig2.svg`
  - diagram: reference numeral 500 missing nearby leader line
- `patent_drawings/patent_a/fig3.svg`
  - margins: left content at x=36
  - diagram: signal path #1 has floating start/end, signal path #2 has floating start/end
- `patent_drawings/patent_a/fig6.svg`
  - margins: left content at x=93
- `patent_drawings/patent_a/fig7.svg`
  - diagram: reference numeral 120 overlaps element
- `patent_drawings/patent_b/fig1.svg`
  - diagram: signal path #7 has floating start/end
- `patent_drawings/patent_c/fig1.svg`
  - diagram: component overlap/collision detected
- `patent_drawings/patent_c/fig3.svg`
  - diagram: reference numeral 0 overlaps element, reference numeral 15 overlaps element, reference numeral 30 overlaps element, reference numeral 48 overlaps element, reference numeral 80 overlaps element
- `patent_drawings/patent_c/fig4.svg`
  - diagram: reference numeral 250 missing nearby leader line, reference numeral 500 missing nearby leader line

# Post-tool-sweep compliance scan — 2026-04-24T14:32:26Z

Validator: .claude/skills/patent-drawer/validators/full_compliance.py
Branch: claude/content-audit-continuation-fg9UO at f467f1b

## patent_a/fig1.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig1.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 31 text elements
[PASS] Font Size: All 31 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 11 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 11 have leader lines
[INFO] Found 11 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 1 present

============================================================
GEOMETRIC AUDIT: fig1.svg
============================================================

[INFO] Found 9 element boxes
[INFO] Found 35 signal path segments
[INFO] Found 31 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 5/5 checks passed
STATUS: GEOMETRY CLEAN
============================================================


------------------------------------------------------------
SUMMARY: 8/8 checks passed
STATUS: READY FOR USPTO SUBMISSION
============================================================

```

## patent_a/fig2.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig2.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 24 text elements
[PASS] Font Size: All 24 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 13 reference numeral(s) [scale=1.00x]
[FAIL] Reference Numerals: 9/13 missing leader lines
       - '32' at line 20
       - '40' at line 74
       - '38' at line 82
       - '36' at line 91
       - '42' at line 96
       - '44' at line 107
       - '50' at line 112
       - '46' at line 124
       - '48' at line 132
[INFO] Arrowheads: No markers and no arrow refs (may be intentional)
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 2 present

============================================================
GEOMETRIC AUDIT: fig2.svg
============================================================

[INFO] Found 0 element boxes
[INFO] Found 25 signal path segments
[INFO] Found 23 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[PASS] G3 Path Through Box: No paths cross through boxes
[FAIL] G4 Segment Overlaps: 1 overlap(s) found
       SEGMENT OVERLAP (V, 6u) at x=220: 'line_0' and 'line_9'
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 4/5 checks passed
STATUS: 1 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 6/8 checks passed
STATUS: 2 issue(s) require attention

Failed checks:
  - references
  - geometry
============================================================

```

## patent_a/fig3.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig3.svg
============================================================

[PASS] ViewBox: 0 0 2550 3300 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[FAIL] Margins: 7 violation(s) found
       - Right margin violation: x=2300.0 (max 2250.0)
       - Right margin violation: x=2260.0 (max 2250.0)
       - Right margin violation: x=2260.0 (max 2250.0)
       - Right margin violation: x=2296.0 (max 2250.0)
       - Right margin violation: x=2260.0 (max 2250.0)
       - Right margin violation: x=2260.0 (max 2250.0)
       - Right margin violation: x=2270.0 (max 2250.0)
[INFO] Found 31 text elements
[FAIL] Font Size: 2 element(s) below 14pt
       - Line 100: font-size=36.0 (min 42.0 at this scale)
       - Line 167: font-size=30.0 (min 42.0 at this scale)
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 10 reference numeral(s) [scale=3.00x]
[FAIL] Reference Numerals: 10/10 missing leader lines
       - '14' at line 31
       - '52' at line 58
       - '54' at line 81
       - '56' at line 102
       - '60' at line 119
       - '62' at line 132
       - '58' at line 153
       - '64' at line 172
       - '66' at line 192
       - '68' at line 203
[INFO] Found 7 arrow(s) using 1 marker id(s): ['ah']
[FAIL] Arrowheads: Non-standard dimensions
       - marker id='ah' markerWidth=10.0 (expected 6)
       - marker id='ah' markerHeight=7.0 (expected 4)
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 3 present

============================================================
GEOMETRIC AUDIT: fig3.svg
============================================================

[INFO] Found 5 element boxes
[INFO] Found 52 signal path segments
[INFO] Found 31 text elements

[FAIL] G1 Signal Crossings: 11 crossing(s) found
       CROSSING at (1190, 820): path 'line_6' (H at y=820, x=1140-1340) crosses path 'line_9' (V at x=1190, y=770-970)
       CROSSING at (1240, 820): path 'line_6' (H at y=820, x=1140-1340) crosses path 'line_10' (V at x=1240, y=770-970)
       CROSSING at (1290, 820): path 'line_6' (H at y=820, x=1140-1340) crosses path 'line_11' (V at x=1290, y=770-970)
       CROSSING at (1190, 870): path 'line_7' (H at y=870, x=1140-1340) crosses path 'line_9' (V at x=1190, y=770-970)
       CROSSING at (1240, 870): path 'line_7' (H at y=870, x=1140-1340) crosses path 'line_10' (V at x=1240, y=770-970)
       CROSSING at (1290, 870): path 'line_7' (H at y=870, x=1140-1340) crosses path 'line_11' (V at x=1290, y=770-970)
       CROSSING at (1190, 920): path 'line_8' (H at y=920, x=1140-1340) crosses path 'line_9' (V at x=1190, y=770-970)
       CROSSING at (1240, 920): path 'line_8' (H at y=920, x=1140-1340) crosses path 'line_10' (V at x=1240, y=770-970)
       CROSSING at (1290, 920): path 'line_8' (H at y=920, x=1140-1340) crosses path 'line_11' (V at x=1290, y=770-970)
       CROSSING at (1230, 1060): path 'line_23' (H at y=1060, x=540-1650) crosses path 'line_34' (V at x=1230, y=1020-1620)
       CROSSING at (540, 1620): path 'path_2' (H at y=1620, x=420-1230) crosses path 'line_24' (V at x=540, y=1060-1800)
[FAIL] G2 Arrow Endpoints: 1 gap(s) found
       ARROW GAP (1260px): arrow at (1780, 2320) is 1260px from nearest box edge (box at x=1480, y=600, w=340, h=460)
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 3/5 checks passed
STATUS: 12 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 3/8 checks passed
STATUS: 5 issue(s) require attention

Failed checks:
  - margins
  - fonts
  - references
  - arrowheads
  - geometry
============================================================

```

## patent_a/fig4.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig4.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[FAIL] Margins: 8 violation(s) found
       - Left margin violation: x=7.0 (min 100.0)
       - Left margin violation: x=7.0 (min 100.0)
       - Left margin violation: x=7.0 (min 100.0)
       - Left margin violation: x=7.0 (min 100.0)
       - Left margin violation: x=7.0 (min 100.0)
       - Left margin violation: x=7.0 (min 100.0)
       - Left margin violation: x=7.0 (min 100.0)
       - Left margin violation: x=7.0 (min 100.0)
[INFO] Found 30 text elements
[PASS] Font Size: All 30 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 12 reference numeral(s) [scale=1.00x]
[FAIL] Reference Numerals: 12/12 missing leader lines
       - '70' at line 20
       - '22' at line 34
       - '72' at line 46
       - '74' at line 65
       - '76' at line 103
       - '78' at line 132
       - '80' at line 144
       - '82' at line 157
       - '84' at line 170
       - '86' at line 183
       ... and 2 more
[INFO] Found 11 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 4 present

============================================================
GEOMETRIC AUDIT: fig4.svg
============================================================

[INFO] Found 8 element boxes
[INFO] Found 39 signal path segments
[INFO] Found 30 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[FAIL] G2 Arrow Endpoints: 4 gap(s) found
       ARROW GAP (40px): arrow at (500, 225) is 40px from nearest box edge (box at x=340, y=190, w=120, h=70)
       ARROW GAP (160px): arrow at (560, 320) is 160px from nearest box edge (box at x=130, y=150, w=590, h=530)
       ARROW GAP (120px): arrow at (560, 485) is 120px from nearest box edge (box at x=320, y=450, w=120, h=70)
       ARROW GAP (30px): arrow at (380, 820) is 30px from nearest box edge (box at x=310, y=730, w=140, h=60)
[PASS] G3 Path Through Box: No paths cross through boxes
[FAIL] G4 Segment Overlaps: 6 overlap(s) found
       SEGMENT OVERLAP (V, 14u) at x=7: 'line_16' and 'line_17'
       SEGMENT OVERLAP (V, 14u) at x=7: 'line_16' and 'line_18'
       SEGMENT OVERLAP (V, 14u) at x=7: 'line_16' and 'line_19'
       SEGMENT OVERLAP (V, 14u) at x=7: 'line_17' and 'line_18'
       SEGMENT OVERLAP (V, 14u) at x=7: 'line_17' and 'line_19'
       SEGMENT OVERLAP (V, 14u) at x=7: 'line_18' and 'line_19'
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 3/5 checks passed
STATUS: 10 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 5/8 checks passed
STATUS: 3 issue(s) require attention

Failed checks:
  - margins
  - references
  - geometry
============================================================

```

## patent_a/fig5.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig5.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 26 text elements
[PASS] Font Size: All 26 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 13 reference numeral(s) [scale=1.00x]
[FAIL] Reference Numerals: 13/13 missing leader lines
       - '90' at line 21
       - '92' at line 46
       - '94' at line 55
       - '136' at line 63
       - '138' at line 71
       - '104' at line 80
       - '98' at line 87
       - '100' at line 94
       - '102' at line 101
       - '96' at line 115
       ... and 3 more
[INFO] Found 3 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 5 present

============================================================
GEOMETRIC AUDIT: fig5.svg
============================================================

[INFO] Found 6 element boxes
[INFO] Found 39 signal path segments
[INFO] Found 24 text elements

[FAIL] G1 Signal Crossings: 2 crossing(s) found
       CROSSING at (280, 430): path 'line_3' (H at y=430, x=220-660) crosses path 'line_10' (V at x=280, y=180-520)
       CROSSING at (560, 430): path 'line_3' (H at y=430, x=220-660) crosses path 'line_11' (V at x=560, y=180-520)
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[PASS] G3 Path Through Box: No paths cross through boxes
[FAIL] G4 Segment Overlaps: 1 overlap(s) found
       SEGMENT OVERLAP (H, 230u) at y=670: 'line_20' and 'line_21'
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 3/5 checks passed
STATUS: 3 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 6/8 checks passed
STATUS: 2 issue(s) require attention

Failed checks:
  - references
  - geometry
============================================================

```

## patent_a/fig6.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig6.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 34 text elements
[PASS] Font Size: All 34 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 9 reference numeral(s) [scale=1.00x]
[FAIL] Reference Numerals: 9/9 missing leader lines
       - '108' at line 30
       - '26' at line 40
       - '110' at line 51
       - '114' at line 72
       - '16' at line 87
       - '22' at line 107
       - '72' at line 129
       - '28' at line 145
       - '112' at line 162
[INFO] Found 9 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 6 present

============================================================
GEOMETRIC AUDIT: fig6.svg
============================================================

[INFO] Found 12 element boxes
[INFO] Found 32 signal path segments
[INFO] Found 34 text elements

[FAIL] G1 Signal Crossings: 1 crossing(s) found
       CROSSING at (650, 504): path 'path_3' (H at y=504, x=540-740) crosses path 'line_7' (V at x=650, y=480-544)
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 4/5 checks passed
STATUS: 1 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 6/8 checks passed
STATUS: 2 issue(s) require attention

Failed checks:
  - references
  - geometry
============================================================

```

## patent_a/fig7.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig7.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 100 text elements
[PASS] Font Size: All 100 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 5 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 5 have leader lines
[INFO] Found 0 arrow(s) using 0 marker id(s): []
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 7 present

============================================================
GEOMETRIC AUDIT: fig7.svg
============================================================

[INFO] Found 3 element boxes
[INFO] Found 10 signal path segments
[INFO] Found 100 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[FAIL] G5 Text Overlaps: 1 overlap(s) found
       TEXT OVERLAP: '7/8' at (411,130) overlaps 'Measured' at (381,144)

------------------------------------------------------------
GEOMETRIC SUMMARY: 4/5 checks passed
STATUS: 1 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 7/8 checks passed
STATUS: 1 issue(s) require attention

Failed checks:
  - geometry
============================================================

```

## patent_a/fig8.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig8.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 31 text elements
[PASS] Font Size: All 31 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 11 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 11 have leader lines
[INFO] Found 10 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 8 present

============================================================
GEOMETRIC AUDIT: fig8.svg
============================================================

[INFO] Found 10 element boxes
[INFO] Found 25 signal path segments
[INFO] Found 31 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[FAIL] G2 Arrow Endpoints: 1 gap(s) found
       ARROW GAP (65px): arrow at (580, 550) is 65px from nearest box edge (box at x=570, y=440, w=130, h=45)
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 4/5 checks passed
STATUS: 1 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 7/8 checks passed
STATUS: 1 issue(s) require attention

Failed checks:
  - geometry
============================================================

```

## patent_b/fig1.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig1.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 19 text elements
[PASS] Font Size: All 19 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 8 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 8 have leader lines
[INFO] Found 7 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 1 present

============================================================
GEOMETRIC AUDIT: fig1.svg
============================================================

[INFO] Found 7 element boxes
[INFO] Found 9 signal path segments
[INFO] Found 19 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 5/5 checks passed
STATUS: GEOMETRY CLEAN
============================================================


------------------------------------------------------------
SUMMARY: 8/8 checks passed
STATUS: READY FOR USPTO SUBMISSION
============================================================

```

## patent_b/fig2.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig2.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 19 text elements
[PASS] Font Size: All 19 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 7 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 7 have leader lines
[INFO] Found 0 arrow(s) using 0 marker id(s): []
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 2 present

============================================================
GEOMETRIC AUDIT: fig2.svg
============================================================

[INFO] Found 5 element boxes
[INFO] Found 8 signal path segments
[INFO] Found 19 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[FAIL] G3 Path Through Box: 1 collision(s) found
       PATH THROUGH BOX: vertical path 'line_7' at x=260 (y=245-315) passes through box (x=150-700, y=250-310)
[FAIL] G4 Segment Overlaps: 1 overlap(s) found
       SEGMENT OVERLAP (V, 5u) at x=260: 'line_1' and 'line_7'
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 3/5 checks passed
STATUS: 2 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 7/8 checks passed
STATUS: 1 issue(s) require attention

Failed checks:
  - geometry
============================================================

```

## patent_b/fig3.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig3.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 22 text elements
[PASS] Font Size: All 22 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 9 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 9 have leader lines
[INFO] Found 7 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 3 present

============================================================
GEOMETRIC AUDIT: fig3.svg
============================================================

[INFO] Found 8 element boxes
[INFO] Found 13 signal path segments
[INFO] Found 22 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 5/5 checks passed
STATUS: GEOMETRY CLEAN
============================================================


------------------------------------------------------------
SUMMARY: 8/8 checks passed
STATUS: READY FOR USPTO SUBMISSION
============================================================

```

## patent_b/fig4.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig4.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 17 text elements
[PASS] Font Size: All 17 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 6 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 6 have leader lines
[INFO] Found 5 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 4 present

============================================================
GEOMETRIC AUDIT: fig4.svg
============================================================

[INFO] Found 6 element boxes
[INFO] Found 9 signal path segments
[INFO] Found 17 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 5/5 checks passed
STATUS: GEOMETRY CLEAN
============================================================


------------------------------------------------------------
SUMMARY: 8/8 checks passed
STATUS: READY FOR USPTO SUBMISSION
============================================================

```

## patent_b/fig5.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig5.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 39 text elements
[PASS] Font Size: All 39 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 9 reference numeral(s) [scale=1.00x]
[FAIL] Reference Numerals: 1/9 missing leader lines
       - '100' at line 43
[INFO] Found 6 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 5 present

============================================================
GEOMETRIC AUDIT: fig5.svg
============================================================

[INFO] Found 5 element boxes
[INFO] Found 16 signal path segments
[INFO] Found 39 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 5/5 checks passed
STATUS: GEOMETRY CLEAN
============================================================


------------------------------------------------------------
SUMMARY: 7/8 checks passed
STATUS: 1 issue(s) require attention

Failed checks:
  - references
============================================================

```

## patent_b/fig6.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig6.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 23 text elements
[PASS] Font Size: All 23 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 6 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 6 have leader lines
[INFO] Found 7 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 6 present

============================================================
GEOMETRIC AUDIT: fig6.svg
============================================================

[INFO] Found 7 element boxes
[INFO] Found 15 signal path segments
[INFO] Found 21 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 5/5 checks passed
STATUS: GEOMETRY CLEAN
============================================================


------------------------------------------------------------
SUMMARY: 8/8 checks passed
STATUS: READY FOR USPTO SUBMISSION
============================================================

```

## patent_c/fig1.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig1.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 25 text elements
[PASS] Font Size: All 25 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 8 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 8 have leader lines
[INFO] Found 7 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 1 present

============================================================
GEOMETRIC AUDIT: fig1.svg
============================================================

[INFO] Found 7 element boxes
[INFO] Found 19 signal path segments
[INFO] Found 25 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[PASS] G2 Arrow Endpoints: All arrows touch box edges
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 5/5 checks passed
STATUS: GEOMETRY CLEAN
============================================================


------------------------------------------------------------
SUMMARY: 8/8 checks passed
STATUS: READY FOR USPTO SUBMISSION
============================================================

```

## patent_c/fig2.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig2.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 34 text elements
[PASS] Font Size: All 34 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 9 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 9 have leader lines
[INFO] Found 6 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 2 present

============================================================
GEOMETRIC AUDIT: fig2.svg
============================================================

[INFO] Found 1 element boxes
[INFO] Found 5 signal path segments
[INFO] Found 34 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[FAIL] G2 Arrow Endpoints: 5 gap(s) found
       ARROW GAP (420px): arrow at (175, 310) is 420px from nearest box edge (box at x=175, y=730, w=500, h=120)
       ARROW GAP (450px): arrow at (545, 280) is 450px from nearest box edge (box at x=175, y=730, w=500, h=120)
       ARROW GAP (203px): arrow at (488, 527) is 203px from nearest box edge (box at x=175, y=730, w=500, h=120)
       ARROW GAP (355px): arrow at (290, 375) is 355px from nearest box edge (box at x=175, y=730, w=500, h=120)
       ARROW GAP (385px): arrow at (316, 345) is 385px from nearest box edge (box at x=175, y=730, w=500, h=120)
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 4/5 checks passed
STATUS: 5 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 7/8 checks passed
STATUS: 1 issue(s) require attention

Failed checks:
  - geometry
============================================================

```

## patent_c/fig3.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig3.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 29 text elements
[PASS] Font Size: All 29 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 11 reference numeral(s) [scale=1.00x]
[FAIL] Reference Numerals: 3/11 missing leader lines
       - '15' at line 50
       - '30' at line 52
       - '80' at line 54
[INFO] Found 2 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 3 present

============================================================
GEOMETRIC AUDIT: fig3.svg
============================================================

[INFO] Found 10 element boxes
[INFO] Found 18 signal path segments
[INFO] Found 28 text elements

[FAIL] G1 Signal Crossings: 8 crossing(s) found
       CROSSING at (160, 240): path 'line_1' (H at y=240, x=152-168) crosses path 'line_0' (V at x=160, y=150-680)
       CROSSING at (160, 390): path 'line_2' (H at y=390, x=152-168) crosses path 'line_0' (V at x=160, y=150-680)
       CROSSING at (160, 470): path 'line_3' (H at y=470, x=152-168) crosses path 'line_0' (V at x=160, y=150-680)
       CROSSING at (160, 580): path 'line_4' (H at y=580, x=152-168) crosses path 'line_0' (V at x=160, y=150-680)
       CROSSING at (240, 680): path 'line_5' (H at y=680, x=160-710) crosses path 'line_7' (V at x=240, y=675-690)
       CROSSING at (320, 680): path 'line_5' (H at y=680, x=160-710) crosses path 'line_8' (V at x=320, y=675-690)
       CROSSING at (540, 680): path 'line_5' (H at y=680, x=160-710) crosses path 'line_9' (V at x=540, y=675-690)
       CROSSING at (680, 680): path 'line_5' (H at y=680, x=160-710) crosses path 'line_10' (V at x=680, y=675-690)
[FAIL] G2 Arrow Endpoints: 2 gap(s) found
       ARROW GAP (5px): arrow at (160, 150) is 5px from nearest box edge (box at x=155, y=145, w=10, h=10)
       ARROW GAP (12px): arrow at (710, 680) is 12px from nearest box edge (box at x=705, y=692, w=10, h=10)
[PASS] G3 Path Through Box: No paths cross through boxes
[FAIL] G4 Segment Overlaps: 2 overlap(s) found
       SEGMENT OVERLAP (H, 8u) at y=580: 'line_4' and 'line_11'
       SEGMENT OVERLAP (V, 5u) at x=160: 'line_0' and 'line_6'
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 2/5 checks passed
STATUS: 12 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 6/8 checks passed
STATUS: 2 issue(s) require attention

Failed checks:
  - references
  - geometry
============================================================

```

## patent_c/fig4.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig4.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 28 text elements
[PASS] Font Size: All 28 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 10 reference numeral(s) [scale=1.00x]
[FAIL] Reference Numerals: 2/10 missing leader lines
       - '250' at line 41
       - '500' at line 42
[INFO] Found 4 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 4 present

============================================================
GEOMETRIC AUDIT: fig4.svg
============================================================

[INFO] Found 9 element boxes
[INFO] Found 16 signal path segments
[INFO] Found 26 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[FAIL] G2 Arrow Endpoints: 4 gap(s) found
       ARROW GAP (5px): arrow at (160, 130) is 5px from nearest box edge (box at x=155, y=125, w=10, h=10)
       ARROW GAP (5px): arrow at (680, 380) is 5px from nearest box edge (box at x=675, y=375, w=10, h=10)
       ARROW GAP (5px): arrow at (160, 560) is 5px from nearest box edge (box at x=155, y=555, w=10, h=10)
       ARROW GAP (380px): arrow at (680, 890) is 380px from nearest box edge (box at x=160, y=445, w=530, h=65)
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 4/5 checks passed
STATUS: 4 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 6/8 checks passed
STATUS: 2 issue(s) require attention

Failed checks:
  - references
  - geometry
============================================================

```

## patent_c/fig5.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig5.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 33 text elements
[PASS] Font Size: All 33 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 5 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 5 have leader lines
[INFO] Found 4 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 5 present

============================================================
GEOMETRIC AUDIT: fig5.svg
============================================================

[INFO] Found 3 element boxes
[INFO] Found 18 signal path segments
[INFO] Found 31 text elements

[FAIL] G1 Signal Crossings: 5 crossing(s) found
       CROSSING at (145, 260): path 'line_3' (H at y=260, x=135-155) crosses path 'path_0' (V at x=145, y=135-665)
       CROSSING at (145, 195): path 'line_5' (H at y=195, x=135-155) crosses path 'path_0' (V at x=145, y=135-665)
       CROSSING at (145, 550): path 'line_6' (H at y=550, x=135-155) crosses path 'path_0' (V at x=145, y=135-665)
       CROSSING at (145, 620): path 'line_8' (H at y=620, x=135-155) crosses path 'path_0' (V at x=145, y=135-665)
       CROSSING at (425, 670): path 'path_0' (H at y=670, x=150-705) crosses path 'line_9' (V at x=425, y=635-700)
[FAIL] G2 Arrow Endpoints: 3 gap(s) found
       ARROW GAP (65px): arrow at (425, 700) is 65px from nearest box edge (box at x=170, y=470, w=500, h=165)
       ARROW GAP (165px): arrow at (230, 800) is 165px from nearest box edge (box at x=170, y=470, w=500, h=165)
       ARROW GAP (165px): arrow at (620, 800) is 165px from nearest box edge (box at x=170, y=470, w=500, h=165)
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 3/5 checks passed
STATUS: 8 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 7/8 checks passed
STATUS: 1 issue(s) require attention

Failed checks:
  - geometry
============================================================

```

## patent_c/fig6.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig6.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 45 text elements
[PASS] Font Size: All 45 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 7 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 7 have leader lines
[INFO] Found 4 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 6 present

============================================================
GEOMETRIC AUDIT: fig6.svg
============================================================

[INFO] Found 24 element boxes
[INFO] Found 23 signal path segments
[INFO] Found 45 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[FAIL] G2 Arrow Endpoints: 4 gap(s) found
       ARROW GAP (5px): arrow at (655, 160) is 5px from nearest box edge (box at x=555, y=140, w=95, h=40)
       ARROW GAP (5px): arrow at (665, 290) is 5px from nearest box edge (box at x=590, y=270, w=70, h=40)
       ARROW GAP (5px): arrow at (635, 430) is 5px from nearest box edge (box at x=535, y=410, w=95, h=40)
       ARROW GAP (5px): arrow at (620, 560) is 5px from nearest box edge (box at x=475, y=540, w=140, h=40)
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[FAIL] G5 Text Overlaps: 1 overlap(s) found
       TEXT OVERLAP: 'Claude silent' at (235,186) overlaps 'Fallback engages' at (340,186)

------------------------------------------------------------
GEOMETRIC SUMMARY: 3/5 checks passed
STATUS: 5 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 7/8 checks passed
STATUS: 1 issue(s) require attention

Failed checks:
  - geometry
============================================================

```

## patent_c/fig7.svg
```

============================================================
USPTO COMPLIANCE REPORT: fig7.svg
============================================================

[PASS] ViewBox: 0 0 850 1100 (8.5:11 aspect)
[PASS] Page Size: 8.5in x 11in
[PASS] Margins: All content within 1-inch bounds
[INFO] Found 40 text elements
[PASS] Font Size: All 40 elements >= 14pt
[PASS] Font Family: All elements use Arial or Courier New
[INFO] Found 11 reference numeral(s) [scale=1.00x]
[PASS] Reference Numerals: All 11 have leader lines
[INFO] Found 9 arrow(s) using 1 marker id(s): ['ah']
[PASS] Arrowheads: Correct 6x4 sizing
[PASS] Colors: Black and white only
[PASS] Line Thickness: All lines >= minimum
[PASS] Figure Label: FIG. 7 present

============================================================
GEOMETRIC AUDIT: fig7.svg
============================================================

[INFO] Found 6 element boxes
[INFO] Found 20 signal path segments
[INFO] Found 40 text elements

[PASS] G1 Signal Crossings: No path-to-path crossings
[FAIL] G2 Arrow Endpoints: 3 gap(s) found
       ARROW GAP (105px): arrow at (365, 555) is 105px from nearest box edge (box at x=130, y=660, w=570, h=120)
       ARROW GAP (105px): arrow at (435, 555) is 105px from nearest box edge (box at x=130, y=660, w=570, h=120)
       ARROW GAP (505px): arrow at (515, 155) is 505px from nearest box edge (box at x=130, y=660, w=570, h=120)
[PASS] G3 Path Through Box: No paths cross through boxes
[PASS] G4 Segment Overlaps: No colinear path overlaps
[PASS] G5 Text Overlaps: No text elements overlap

------------------------------------------------------------
GEOMETRIC SUMMARY: 4/5 checks passed
STATUS: 3 issue(s) require fixing
============================================================


------------------------------------------------------------
SUMMARY: 7/8 checks passed
STATUS: 1 issue(s) require attention

Failed checks:
  - geometry
============================================================

```


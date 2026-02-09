---
name: patent-drawer
description: Generate and validate USPTO-compliant patent drawing SVGs (37 CFR 1.84). Use when creating new patent figures, validating existing SVGs, or fixing compliance issues. Enforces margins, fonts, reference numerals, arrowheads, and black-and-white requirements.
allowed-tools: Bash(python *), Read, Write, Edit, Glob, Grep
argument-hint: [action] [file-or-directory] [optional-args...]
disable-model-invocation: false
---

# USPTO Patent Drawing Validator & Generator

## Overview

This skill generates and validates patent drawing SVGs that comply with **37 CFR 1.84 USPTO standards**. All generated drawings are validated before output.

## Usage

### Validate a single figure
```
/patent-drawer validate patent_drawings/patent_a/fig1.svg
```

### Validate all figures in a patent directory
```
/patent-drawer audit patent_drawings/patent_b/
```

### Fix common compliance issues automatically
```
/patent-drawer fix patent_drawings/patent_c/fig3.svg
```

### Generate a new compliant figure from template
```
/patent-drawer generate block-diagram "System Architecture" patent_drawings/patent_a/fig9.svg
```

### Check specific requirement
```
/patent-drawer check-margins patent_drawings/patent_b/fig1.svg
/patent-drawer check-fonts patent_drawings/patent_b/fig1.svg
/patent-drawer check-numerals patent_drawings/patent_b/fig1.svg
```

## Compliance Requirements (37 CFR 1.84)

| Requirement | Standard | Implementation |
|-------------|----------|----------------|
| Page Size | 8.5" x 11" | `width="8.5in" height="11in"` |
| ViewBox | 850 x 1100 | `viewBox="0 0 850 1100"` |
| Margins | >= 1" all sides | All content x,y >= 100; x <= 750; y <= 1000 |
| Font Size | >= 14pt | `font-size="14"` minimum on all text |
| Font Family | Arial or Courier New | Arial for labels, Courier New for code/values |
| Reference Numerals | With leader lines | 3-digit numbers (100, 200, etc.) with 0.5px leader lines |
| Arrowheads | Consistent sizing | `markerWidth="6" markerHeight="4"` |
| Line Thickness | >= 0.3mm | `stroke-width` >= 1.13px |
| Colors | Black on white only | `#000000` or `black` strokes/text, `white` background |
| Figure Label | Bottom center | `FIG. N` at y="920" (with 50-unit translate) |

## Validation Output Format

```
=== USPTO Compliance Report: fig1.svg ===

[PASS] Page Size: 8.5in x 11in
[PASS] ViewBox: 0 0 850 1100
[PASS] Margins: All content within bounds
[FAIL] Font Size: 2 elements below 14pt (lines 23, 45)
[PASS] Font Family: All Arial/Courier New
[WARN] Reference Numerals: 3 numerals missing leader lines
[PASS] Arrowheads: Consistent 6x4 sizing
[PASS] Colors: Black and white only

Overall: 6/8 PASS, 1 FAIL, 1 WARN
Action Required: Fix font sizes on lines 23, 45
```

## Common Fixes Applied by `/patent-drawer fix`

1. **Font sizes below 14pt** → Changed to 14pt
2. **Missing leader lines** → Added 0.5px stroke lines from numeral to element
3. **Oversized arrowheads** → Reduced to 6x4 marker
4. **Y-axis labels outside margin** → Rotated 90 degrees
5. **Dashed tick marks** → Converted to solid lines

## SVG Template Structure

All compliant patent drawings follow this structure:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" viewBox="0 0 850 1100">
  <defs>
    <marker id="ah" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto">
      <polygon points="0 0, 6 2, 0 4" fill="black" />
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="white" />
  <text x="425" y="60" font-family="Arial, sans-serif" font-size="16" text-anchor="middle">N/M</text>
  <g transform="translate(0, 50)">
    <!-- CONTENT HERE: All x >= 100, y >= 50 (effective 100 with transform) -->

    <text x="425" y="920" font-family="Arial, sans-serif" font-size="20" font-weight="bold" text-anchor="middle">FIG. N</text>
  </g>
</svg>
```

## Reference Numeral Format

Reference numerals MUST have leader lines pointing to their associated elements:

```xml
<!-- Correct: Numeral with leader line -->
<text x="580" y="160" font-family="Arial, sans-serif" font-size="14" text-anchor="start">100</text>
<line x1="578" y1="160" x2="575" y2="170" stroke="black" stroke-width="0.5"/>

<!-- Incorrect: Floating numeral without leader -->
<text x="580" y="160" font-family="Arial, sans-serif" font-size="14" text-anchor="start">100</text>
```

## Patent-Specific Numbering Conventions

| Patent | Figure Range | Reference Numeral Series |
|--------|--------------|--------------------------|
| Patent A | Fig 1-8 | 100-series (100, 102, 104...) |
| Patent B | Fig 1-6 | 100-series for Fig 1; 200-series for Fig 2; etc. |
| Patent C | Fig 1-7 | 100-series for Fig 1; 200-series for Fig 2; etc. |

## Validators Available

Run individual validators with shell commands:

```bash
python .claude/skills/patent-drawer/validators/full_compliance.py <svg_file>
python .claude/skills/patent-drawer/validators/margin_validator.py <svg_file>
python .claude/skills/patent-drawer/validators/font_validator.py <svg_file>
python .claude/skills/patent-drawer/validators/reference_validator.py <svg_file>
python .claude/skills/patent-drawer/validators/arrowhead_validator.py <svg_file>
```

## Integration with Consciousness_Env

This skill is designed for the Consciousness_Env patent portfolio:

- **Patent A**: Self-Sustaining Neural-Motor Energy Harvesting Loop (8 figures)
- **Patent B**: Configurable Recursive Self-Observation in SNNs (6 figures)
- **Patent C**: Cognitive Fallback with Autonomous Self-Regulation (7 figures)

All 21 figures follow the same compliance standards defined here.

---
name: patent-drawer
description: Generate and validate USPTO-compliant patent drawing SVGs (37 CFR 1.84). Use when creating new patent figures, validating existing SVGs, or fixing compliance issues. Enforces margins, fonts, reference numerals, arrowheads, black-and-white requirements, geometric collisions, and signal path integrity.
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

### Run geometric collision check (signal paths, arrow endpoints, box crossings)
```
/patent-drawer check-geometry patent_drawings/patent_a/fig1.svg
```

---

## CRITICAL: Geometric Integrity Rules

These rules were previously missing from validation and caused repeated failures.
They are now **mandatory** for every figure before it can be considered complete.

### Rule G1: Signal paths MUST NOT cross other signal paths

Per **MPEP 608.02(V)** and **37 CFR 1.84(h)**, lines must not cross unless
absolutely unavoidable. If crossing is unavoidable, a semicircular bridge must
be used to show one line passing over another.

**How to check**: Extract all signal path segments (stroke-width >= 1.0,
excluding leader lines at 0.5). Break paths into horizontal (H) and vertical
(V) segments. For every H-V pair from **different** signal paths, check if:
- The H segment's x-range contains the V segment's x-coordinate, AND
- The V segment's y-range contains the H segment's y-coordinate

If both are true, the paths cross. **Endpoint touches (T-junctions where a
path connects to a box edge) are NOT crossings.**

**How to fix**: Reroute one path to a different x or y coordinate so paths
run parallel instead of crossing. Keep a minimum 10px gap between parallel
paths.

### Rule G2: Arrow endpoints MUST touch target box edges exactly

Arrows that terminate 2px or more from a box edge appear "floating" and
indicate sloppy drafting. The `y2` (or `x2`) of an arrow line must exactly
equal the target box's edge coordinate.

**Common mistake**: Leaving a gap like `y2="270"` when the box top is at
`y="272"`. This creates a 2px gap that is invisible at screen zoom but
violates drafting standards.

### Rule G3: Signal paths MUST NOT pass through element boxes

A signal path that enters one edge of a `<rect>` and exits another edge
creates a collision — the path appears to run through the element. Paths
must route **around** boxes, not through them.

**How to check**: For every signal path segment, check if it intersects
any `<rect>` element. A path that **terminates at** a box edge (connecting
to the element) is fine; a path that **passes through** is not.

**Common fix patterns**:
- Move the path's x-coordinate left/right of the box
- Route the path around the box with additional segments
- Relocate the interfering box

### Rule G4: Signal paths MUST NOT overlap other signal paths

Two signal path segments should not share the same line segment (e.g., two
different paths both running vertically at x=240 from y=470 to y=502).
Each path should have its own distinct route.

### Rule G5: No text-text or text-line overlaps

Text elements must not overlap each other or sit on top of signal path
lines. Approximate text width as ~8px per character at font-size 14.

---

## Text Content Rules (37 CFR 1.84(o) and MPEP 608.02(V))

**Descriptive legends must contain AS FEW WORDS AS POSSIBLE.**

### Allowed text in patent drawings:
- **Block/element names**: SENSOR, MOTOR, SPIKING NEURAL NETWORK, etc.
- **Reference numerals**: 10, 12, 14, etc. (with leader lines)
- **Sheet numbers**: 1/8, 2/8, etc.
- **Figure labels**: FIG. 1, FIG. 2, etc.
- **Brief directional labels**: Only when essential for understanding signal flow
- **Legend entries**: Line style descriptions (keep minimal)
- **Flow chart step labels**: Short imperative phrases

### NOT allowed:
- **Formulas or equations**: `signal_voltage = light/1000 x 5.0` — belongs in spec
- **Capacity/parameter values**: `100 mWh capacity` — belongs in spec
- **Layer descriptions**: `L4: LIF Neurons + STDP` — belongs in spec
- **Implementation details**: `Servo Actuation`, `Optical Transmission` — belongs in spec
- **Code snippets or variable names**: Any programming syntax

### Why this matters:
The examiner reviews drawings independently from the specification. Drawings
should be self-explanatory through **element names + reference numerals +
signal flow arrows** alone. Detailed descriptions in figures create a risk
that the figure contradicts the spec text, which can be used as grounds for
rejection under 35 U.S.C. 112.

---

## Compliance Requirements (37 CFR 1.84)

| Requirement | Standard | Implementation |
|-------------|----------|----------------|
| Page Size | 8.5" x 11" | `width="8.5in" height="11in"` |
| ViewBox | 850 x 1100 | `viewBox="0 0 850 1100"` |
| Margins | >= 1" all sides | All content x,y >= 100; x <= 750; y <= 1000 |
| Font Size | >= 14pt | `font-size="14"` minimum on all text |
| Font Family | Arial or Courier New | Arial for labels, Courier New for code/values |
| Reference Numerals | With leader lines | Even numbers with 0.5px leader lines |
| Arrowheads | Consistent sizing | `markerWidth="6" markerHeight="4"` |
| Line Thickness | >= 0.3mm | `stroke-width` >= 1.13px (1.5px recommended) |
| Colors | Black on white only | `#000000` or `black` strokes/text, `white` background |
| Figure Label | Bottom center | `FIG. N` at y="920" (with 50-unit translate) |
| Signal Paths | No crossings | Paths must not cross; use bridge convention if unavoidable |
| Arrow Endpoints | Touch box edges | `y2`/`x2` must equal target rect's edge coordinate |
| Path Routing | No through-box | Paths must route around element boxes, not through them |
| Text Content | Minimal | Block names + numerals only; no formulas or descriptions |

---

## Validation Checklist (Run ALL before declaring a figure complete)

### Level 1: Structural (automated validators)
- [ ] Page size, viewBox, margins
- [ ] Font sizes >= 14pt, font families correct
- [ ] Reference numerals have leader lines
- [ ] Arrowhead markers are 6x4
- [ ] Colors are black and white only
- [ ] Figure label present

### Level 2: Geometric (geometric validator + manual audit)
- [ ] **G1**: No signal-path-to-signal-path crossings
- [ ] **G2**: All arrow endpoints touch target box edges (zero gap)
- [ ] **G3**: No signal paths pass through element boxes
- [ ] **G4**: No overlapping signal path segments
- [ ] **G5**: No text-text or text-line overlaps

### Level 3: Content (manual review)
- [ ] All required reference numerals from NUMERAL_REGISTRY.md are present
- [ ] Numerals match the unified cross-figure scheme (NOT per-figure 100-series)
- [ ] No descriptive text, formulas, or implementation details
- [ ] Only block names, numerals, sheet number, figure label, and minimal legend

**A figure is NOT complete until all three levels pass.**

---

## Reference Numeral Conventions

### IMPORTANT: Unified Cross-Figure Numbering

Reference numerals are **unified across all figures within a patent**. The same
element gets the same numeral in every figure where it appears. This is required
by **37 CFR 1.84(p)(1)**.

**The authoritative source for all numerals is:**
`patent_drawings/NUMERAL_REGISTRY.md`

### Numbering rules:
- Even numbers only (USPTO convention)
- Sequential within each patent's scope
- Same element = same numeral across all figures
- First occurrence in a figure gets the full label; subsequent may use numeral only

### Examples from Patent A:
| Num | Element | Used in Figures |
|-----|---------|-----------------|
| 10 | Environment boundary | 1, 8 |
| 14 | Spiking neural network | 1, 3, 4, 8 |
| 22 | Piezoelectric element | 1, 4, 6, 8 |

### WRONG (old per-figure scheme — DO NOT USE):
```
Patent A Fig 1: 100, 102, 104...
Patent A Fig 2: 200, 202, 204...
```

### CORRECT (unified scheme):
```
Patent A: 10, 12, 14, 16... (same numeral everywhere)
Patent B: 10, 12, 14, 16... (independent from Patent A)
Patent C: 10, 12, 14, 16... (independent from Patent A/B)
```

---

## Reference Numeral Format

Reference numerals MUST have leader lines pointing to their associated elements:

```xml
<!-- Correct: Numeral with leader line -->
<text x="540" y="296" font-family="Arial, sans-serif" font-size="14"
      text-anchor="start" fill="black">14</text>
<line x1="538" y1="296" x2="532" y2="300" stroke="black" stroke-width="0.5"/>

<!-- Incorrect: Floating numeral without leader -->
<text x="540" y="296" font-family="Arial, sans-serif" font-size="14">14</text>
```

---

## SVG Template Structure

All compliant patent drawings follow this structure:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in"
     viewBox="0 0 850 1100">
  <defs>
    <marker id="ah" markerWidth="6" markerHeight="4" refX="6" refY="2"
            orient="auto">
      <polygon points="0 0, 6 2, 0 4" fill="black" />
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="white" />
  <text x="425" y="60" font-family="Arial, sans-serif" font-size="16"
        text-anchor="middle" fill="black">N/M</text>
  <g transform="translate(0, 50)">

    <!-- CONTENT: Block names + reference numerals + signal paths only -->
    <!-- All content: x >= 100, x <= 750, y >= 50 (100 absolute) -->
    <!-- Arrow endpoints must exactly match target box edges -->
    <!-- Signal paths must not cross each other or pass through boxes -->

    <text x="425" y="920" font-family="Arial, sans-serif" font-size="20"
          font-weight="bold" text-anchor="middle" fill="black">FIG. N</text>
  </g>
</svg>
```

---

## Signal Path Routing Guidelines

When laying out signal paths in a block diagram:

1. **Plan path corridors first** — before drawing, identify left-side, right-side,
   and top/bottom corridors for paths that need to loop around elements
2. **Maintain minimum 10px separation** between parallel paths to prevent ambiguity
3. **Three line styles** are standard for this project:
   - Solid (`stroke-width="1.5"`) — main signal path
   - Dashed (`stroke-dasharray="6,3"`) — thermal/energy cross-links
   - Dotted (`stroke-dasharray="3,3"`) — feedback/reflection paths
4. **Route outbound paths on the right side, return paths on the left side**
   to minimize crossings
5. **If a path must change direction**, use right-angle bends (no diagonal lines
   in block diagrams)
6. **Arrow terminates AT the box edge** — set the line endpoint coordinate to
   exactly match the target rect's x, y, x+width, or y+height

### Path routing verification procedure:
```
For each signal path segment:
  1. Extract all <rect> bounding boxes
  2. Check: does this segment enter one side of any rect and exit another?
     → If yes: COLLISION — reroute the path
  3. Check: does this segment share coordinates with any other signal path?
     → If yes at a crossing point: CROSSING — reroute one path
  4. Check: does the arrow endpoint match the target box edge exactly?
     → If gap > 0: FIX — adjust endpoint coordinate
```

---

## Validators Available

Run individual validators with shell commands:

```bash
# Structural validators (Level 1)
python .claude/skills/patent-drawer/validators/full_compliance.py <svg_file>
python .claude/skills/patent-drawer/validators/margin_validator.py <svg_file>
python .claude/skills/patent-drawer/validators/font_validator.py <svg_file>
python .claude/skills/patent-drawer/validators/reference_validator.py <svg_file>
python .claude/skills/patent-drawer/validators/arrowhead_validator.py <svg_file>

# Geometric validator (Level 2)
python .claude/skills/patent-drawer/validators/geometric_validator.py <svg_file>
```

---

## Why Geometric Issues Were Previously Missed

The original validators only performed **Level 1 structural checks** — they
parsed XML attributes (font-size values, color strings, marker dimensions) but
never computed the **spatial relationships between elements**. Specifically:

1. **Signal path crossings** require extracting every line/path segment,
   decomposing into H/V components, and testing all cross-path H-V pairs for
   intersection. This is computational geometry, not XML parsing.

2. **Arrow endpoint accuracy** requires matching each arrow's endpoint
   coordinates against the bounding boxes of target rects. The validators
   only checked that arrows had `marker-end` attributes, not WHERE they
   pointed.

3. **Path-through-box collisions** require testing line segments against rect
   bounding boxes for intersection. Again, geometry — not present in the
   original XML-only validators.

4. **Text overlap detection** requires estimating text bounding boxes from
   font-size, character count, and text-anchor, then testing for spatial
   overlap. The validators only checked font-size values.

The result was that a figure could score 7/7 PASS on structural checks while
having multiple geometric collisions that would cause USPTO rejection. The
geometric validator addresses this gap.

---

## Integration with Consciousness_Env

This skill is designed for the Consciousness_Env patent portfolio:

- **Patent A**: Self-Sustaining Neural-Motor Energy Harvesting Loop (8 figures)
- **Patent B**: Configurable Recursive Self-Observation in SNNs (6 figures)
- **Patent C**: Cognitive Fallback with Autonomous Self-Regulation (7 figures)

All 21 figures follow the same compliance standards defined here.

**Authoritative references:**
- Numeral registry: `patent_drawings/NUMERAL_REGISTRY.md`
- Patent A spec: `Patent_A_Spec_RECONCILED_v3_UPDATED-3.docx` (Google Drive)
- Patent B spec: `Patent_B_Spec_UPDATED.docx` (Google Drive)
- Patent C spec: `Patent_C_Spec_RECONCILED_v2.docx` (Google Drive)

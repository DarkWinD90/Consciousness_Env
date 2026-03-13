---
name: patent-collision-checker
description: Detects and fixes element collisions in USPTO patent SVG drawings. Identifies overlapping text, clipped elements, text-on-line collisions, and boundary violations that violate 37 CFR 1.84(p)(1) legibility requirements.
allowed-tools: Bash(python *), Read, Write, Edit, Glob, Grep
argument-hint: [check|fix] [--patent a|b|c] [--file <path>]
---

# Patent Drawing Collision Checker

## Description
Detects and fixes element collisions in USPTO patent SVG drawings. Collisions
violate 37 CFR 1.84(p)(1) which requires reference characters to be "plain and
legible" and not "crowded." This skill identifies overlapping text, clipped
elements, text-on-line collisions, and boundary violations, then provides
actionable fixes that maintain full USPTO compliance.

## Activation
- `/patent-collision-checker check` — Run collision detection on all patent drawings
- `/patent-collision-checker check --patent a|b|c` — Check a specific patent
- `/patent-collision-checker check --file <path>` — Check a single SVG
- `/patent-collision-checker fix` — Detect and fix all collisions interactively

## Collision Types Detected

### 1. Text-on-Text Overlap
Two text elements whose estimated bounding boxes overlap. Common causes:
- Reference numerals placed too close to labels
- Y-axis labels overlapping tick values
- Table rows with insufficient vertical spacing

### 2. Text-on-Shape Overlap
Text element overlapping a rectangle, circle, ellipse, or line. Common causes:
- Reference numerals clipping box boundaries
- Labels placed inside shapes they shouldn't intersect
- Rotated text crossing element boundaries

### 3. Boundary Clipping
Elements positioned partially outside the drawing area or parent container.
Common causes:
- Self-loop arrows extending beyond page margin
- Text elements near edges with insufficient clearance

### 4. Text-on-Line Overlap
Text overlapping connecting lines, arrows, or curves. Common causes:
- Axis labels overlapping graph data lines
- Reference numerals placed on signal pathways

### 5. Arrow Endpoint Misalignment (SEMANTIC)
Arrows that don't land at their intended destination. Common causes:
- Arrow endpoint coordinates don't match label positions
- Signal arrows landing at wrong pins on IC/microcontroller diagrams
- Connection lines stopping short of or overshooting target elements

### 6. Floating Labels (SEMANTIC)
Labels (GPIO, ADC, etc.) positioned far from their connection points:
- Pin labels floating near components instead of at IC entry points
- ADC/GPIO labels not adjacent to where arrows actually land
- Threshold: Label > 30px from nearest arrow endpoint = FAIL

### 7. Arrow Origin Gaps (SEMANTIC)
Arrows that don't start at component edges:
- Arrow origin inside a shape (should touch edge)
- Arrow origin floating near but not touching source element
- Gap between component boundary and arrow start point

## How It Works

The checker parses SVG XML and extracts bounding boxes for all elements:
- **Text**: Estimated from x, y, font-size, text-anchor, and character count.
  Accounts for `transform="rotate(...)"` attributes.
- **Rectangles**: Direct from x, y, width, height attributes
- **Circles/Ellipses**: From cx, cy, r (or rx, ry)
- **Lines**: From x1, y1, x2, y2 with stroke-width buffer
- **Polylines/Paths**: Bounding box from coordinate extraction

Overlap is calculated as intersection area / smaller element area. Collisions
are reported when overlap exceeds a configurable threshold (default: 15%).

## Fix Strategy

When fixing collisions, the skill applies these strategies in priority order:
1. **Nudge**: Move the smaller/less-anchored element by minimum distance
2. **Reposition**: Move reference numeral to a clear area near its element
3. **Resize spacing**: Increase vertical gap between table/list rows
4. **Compact text**: Reduce font-size only as last resort (minimum 10px)

All fixes preserve:
- 37 CFR 1.84 compliance (line weights, margins, legibility)
- Reference numeral associations (numeral stays near its element)
- Unified cross-figure even-number scheme (per NUMERAL_REGISTRY.md)
- ViewBox dimensions (850x1100, US Letter at 100 DPI)

## Output Format

```
=== PATENT C — FIG. 1 (fig1.svg) ===
[!] COLLISION: Text "Energy feedback" overlaps rect (SNN box 112)
    Overlap: 35% | Type: text-on-shape
    Fix: Shift text x from 170 to 145 (move left 25px)

[!] COLLISION: Rect (Buffer 108) overlaps rect (Fallback 106)
    Overlap: 22% | Type: shape-on-shape
    Fix: Move Buffer y from 600 to 610 (shift down 10px)

SUMMARY: 2 collisions found, 2 fixes proposed
```

## Dependencies
- Python 3.x (standard library only — uses xml.etree.ElementTree)
- No external packages required

---

## Hardware/Schematic Figure Validation

For figures showing hardware layouts (like Patent A FIG. 6), additional semantic
checks are required beyond visual collision detection:

### Arrow-to-Label Alignment Check

For each arrow (`<polyline>` or `<line>` with `marker-end`):
1. Extract endpoint coordinates (last point in polyline, or x2/y2 for line)
2. Find all pin labels (GP*, ADC*, VSYS, PWM, etc.) within 50px
3. **FAIL** if no label within 30px of arrow endpoint
4. **WARN** if label is 15-30px away (should be closer)

### Arrow Origin Validation

For each arrow originating from a component:
1. Find the source component (circle, rect) nearest to arrow start
2. Calculate distance from arrow start to component edge
3. **FAIL** if arrow starts inside component (should touch edge)
4. **WARN** if gap > 5px between component edge and arrow start

### Pin Label Consistency

For microcontroller diagrams:
1. Extract all GPIO/ADC pin labels from SVG
2. Compare against specification document
3. **FAIL** if spec mentions a pin not shown in drawing
4. **FAIL** if drawing shows pin not mentioned in spec

### Signal Type Validation

Verify connections make electrical sense:
- Analog sensors → ADC pins (GP26-28 on Pico)
- Digital signals → any GPIO
- Power connections → VSYS, 3V3, or GND
- **FAIL** if analog signal goes to digital-only pin

### Example Output for Semantic Issues

```
=== PATENT A — FIG. 6 (fig6.svg) ===
[!] SEMANTIC: Arrow endpoint (535, 370) has no adjacent pin label
    Nearest label "GP15" is 45px away
    Fix: Add "VSYS" label at (527, 378)

[!] SEMANTIC: Arrow from Piezo (602) starts at y=188, inside disc (edge at y=195)
    Fix: Change arrow start from (200, 188) to (200, 195)

[!] SEMANTIC: ADC1 label at (150, 505) is 180px from arrow endpoint (355, 420)
    Fix: Move ADC1 to (375, 412) near Pico entry point

SUMMARY: 3 semantic issues found, 3 fixes proposed
```

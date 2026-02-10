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
- Per-figure 100-series numbering convention
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

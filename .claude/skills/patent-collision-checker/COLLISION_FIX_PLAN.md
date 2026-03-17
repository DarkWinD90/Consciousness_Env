# Patent Drawing Collision Fix Plan

## Overview

This document outlines the systematic approach for detecting and fixing element
collisions in all 21 USPTO patent drawings using the enhanced pixel-level
validation technique.

---

## The Pixel-Level Validation Technique

### Why SVG Bounding Box Analysis Is Insufficient

The basic collision checker uses XML parsing to estimate element bounding boxes.
This approach has critical limitations:

1. **Rotated text bbox estimation is wrong**: Rotated text (like "Thermal Cross-Link")
   is treated as a horizontal rectangle, causing false positive collisions with
   elements that are actually perpendicular and non-overlapping.

2. **Intentional overlaps are flagged**: Text inside boxes (labels) is intentional
   patent drawing convention, but bbox analysis reports 100% overlap.

3. **Actual pixel clearance is unknown**: Two elements may have overlapping bboxes
   but still have sufficient visual clearance due to the actual glyph shapes.

### The Pixel-Level Technique

The user's technique (demonstrated on FIG. 1) solves these problems:

```python
# 1. Render SVG to high-resolution PNG (300 DPI = 3x scale)
#    viewBox 850x1100 → 2550x3300 pixels

# 2. Define element bounding boxes in viewBox coordinates
elements = [
    ("Sheet '1/8'", x_min, y_min, x_max, y_max),
    ("ENVIRONMENT cloud", x_min, y_min, x_max, y_max),
    # ... all elements
]

# 3. Check for bbox overlaps (excluding intentional patterns)
for pair in all_element_pairs:
    if boxes_overlap(pair) and not_intentional(pair):
        collisions.append(pair)

# 4. Measure actual pixel-level clearance at collision zones
def measure_gap_horizontal(y_center_vb, x_left_vb, x_right_vb):
    y_px = int(y_center_vb * 3)  # viewBox to pixel
    x_range = arr[y_px-3:y_px+3, x1_px:x2_px]  # horizontal scan
    dark_cols = np.where(np.any(row < 200, axis=0))[0]
    gaps = np.diff(dark_cols)
    max_gap = np.max(gaps) / 3.0  # back to viewBox units
    return max_gap
```

### Key Thresholds

| Gap (viewBox units) | Interpretation |
|---------------------|----------------|
| < 1.0 | CRITICAL - touching or overlapping |
| 1.0 - 5.0 | HIGH - too close for USPTO |
| 5.0 - 10.0 | MEDIUM - marginal, should improve |
| > 10.0 | OK - sufficient clearance |

37 CFR 1.84(p)(1) requires text to be "plain and legible" — gaps below 5 units
risk examiner objection.

---

## Collision Categories and Fix Strategies

### Category 1: Text-on-Text (Rotated)
**Cause**: Rotated labels (90° or -90°) overlap with horizontal text
**Example**: "RECURSIVE FEEDBACK" (rotated -90°) overlaps "THE LOOP"
**Fix Strategy**:
- Move the rotated text further away from the horizontal text
- Typical shift: 20-40 viewBox units

### Category 2: Reference Numeral-on-Line
**Cause**: Reference numerals (102, 104, etc.) cross dashed/dotted paths
**Example**: Ref 106 at x=610 overlaps thermal dashed line starting at x=600
**Fix Strategy**:
- Move reference numerals further from the line path
- Typical shift: 30-50 viewBox units in x or y

### Category 3: Label-on-Signal-Path
**Cause**: Text labels cross polyline signal arrows
**Example**: "GP0" inside Pico box near signal arrow
**Fix Strategy**:
- This is often intentional (label near component)
- Only fix if label actually obscures the signal line
- Move label perpendicular to signal direction

### Category 4: Axis-Label-on-Graph-Line
**Cause**: Y-axis labels or data annotations near graph curves
**Example**: "Energy Storage (mWh)" near grid lines
**Fix Strategy**:
- Often acceptable if label is parallel to axis
- Fix only if label crosses data curves
- Shift label away from data region

### Category 5: Leader-Line-on-Dotted-Path
**Cause**: Leader lines from reference numerals cross feedback paths
**Example**: 120 leader line endpoint at x=225 touches recursive dotted line at x=225
**Fix Strategy**:
- Move the dotted path further from the leader line zone
- Or shorten/redirect the leader line

---

## Figure-by-Figure Fix Priority

Based on enhanced collision checker results:

### HIGH PRIORITY (11+ issues, complex layouts)
| Figure | Issues | Primary Problem |
|--------|--------|-----------------|
| A/fig6 | 11 | Pin labels crossing signal paths in hardware diagram |
| A/fig2 | 10 | Graph annotations crossing data curves |

### MEDIUM PRIORITY (4-7 issues)
| Figure | Issues | Primary Problem |
|--------|--------|-----------------|
| C/fig4 | 7 | Zone labels crossing modulation curve |
| A/fig5 | 6 | Energy region labels crossing graph curves |
| C/fig2 | 6 | State transition annotations crossing arrows |
| A/fig3 | 4 | Network topology labels crossing connection paths |
| C/fig1 | 4 | Cognitive controller labels crossing paths |

### LOW PRIORITY (1-2 issues, likely acceptable)
| Figure | Issues | Primary Problem |
|--------|--------|-----------------|
| B/fig3 | 2 | External modulation label near path |
| C/fig7 | 2 | Mode labels near signal paths |
| A/fig4 | 1 | Plus sign on summation line |
| A/fig1 | 1 | Environment label near cloud path (already fixed) |

### NO ISSUES (10 figures)
A/fig7, A/fig8, B/fig1, B/fig2, B/fig4, B/fig5, B/fig6, C/fig3, C/fig5, C/fig6

---

## Integration with Skill Agent

### Enhanced patent-collision-checker Skill Workflow

```
1. PARSE: Load SVG, extract all elements with accurate bbox calculation
   - Handle rotated text properly (swap w/h for 90° rotation)
   - Track parent transforms

2. FILTER: Remove intentional patterns from collision candidates
   - Text inside rectangles (labels in component boxes)
   - Reference numerals adjacent to their components
   - Leader lines touching their numerals
   - Axis labels on graph figures

3. DETECT: Find remaining overlaps above threshold
   - Text-on-text: threshold 10% overlap
   - Text-on-line: threshold 10% overlap, exclude axis labels
   - Reference-on-path: any overlap is concerning

4. VALIDATE (if rendering available):
   - Render SVG to high-res PNG
   - Measure actual pixel gaps at detected collision zones
   - Upgrade/downgrade severity based on pixel measurements

5. REPORT: Generate fix suggestions with specific coordinates
   - "Move 'RECURSIVE FEEDBACK' from x=210 to x=175"
   - "Shift ref 106 from x=610 to x=660"

6. FIX (interactive mode):
   - Apply suggested edits to SVG
   - Re-validate after each fix
   - Stop when all collisions resolved
```

### Adding Pixel Validation Without CairoSVG

Since CairoSVG requires Cairo library (not available on Windows by default),
alternative approaches:

1. **Inkscape CLI** (cross-platform):
   ```bash
   inkscape fig1.svg --export-type=png --export-dpi=300 -o fig1.png
   ```

2. **Browser automation** (Puppeteer/Playwright):
   ```javascript
   await page.setViewportSize({ width: 2550, height: 3300 });
   await page.goto('file:///.../fig1.svg');
   await page.screenshot({ path: 'fig1.png' });
   ```

3. **Pre-rendered reference images**:
   - Render all SVGs once using any method
   - Store in `patent_drawings/.rendered/`
   - Collision checker uses pre-rendered images

---

## Systematic Fix Procedure

For each figure with issues:

### Step 1: Generate Element Map
```python
elements = [
    ("element_name", x_min, y_min, x_max, y_max),
    # ... define all elements in the figure
]
```

### Step 2: Run Collision Matrix
```python
for i, j in all_pairs:
    if boxes_overlap(elements[i], elements[j]):
        if not is_intentional(elements[i], elements[j]):
            collisions.append((i, j, overlap_area))
```

### Step 3: Measure Pixel Gaps (if rendered image available)
```python
for collision in collisions:
    gap = measure_gap(collision.zone, rendered_pixels)
    collision.pixel_gap = gap
    collision.severity = classify_severity(gap)
```

### Step 4: Generate Fix Plan
```python
for collision in sorted(collisions, key=lambda c: -c.severity):
    print(f"Fix: {collision.fix_suggestion}")
    # e.g., "Move 'RECURSIVE FEEDBACK' x from 210 to 175"
```

### Step 5: Apply Fixes
```python
for fix in fix_plan:
    edit_svg(svg_path, fix.old_value, fix.new_value)
```

### Step 6: Re-validate
```python
# Run collision check again
# Verify all previous collisions are resolved
# Check for new collisions introduced by fixes
```

---

## Recommended Fix Order

1. **A/fig1** - DONE (reference implementation)
2. **A/fig6** - Hardware diagram, highest issue count
3. **A/fig2** - Energy comparison graph
4. **C/fig4** - Modulation curve with zone labels
5. **A/fig5** - Activity-dependent dynamics graph
6. **C/fig2** - State transition diagram
7. **A/fig3** - SNN architecture
8. **C/fig1** - System architecture with fallback
9. **B/fig3** - Dynamic modulation sources
10. **C/fig7** - End-to-end signal flow
11. **A/fig4** - Energy harvesting circuit

---

## Success Criteria

After all fixes:
- Enhanced collision checker reports 0 issues at medium+ severity
- Pixel-level validation shows all gaps >= 5 viewBox units
- All drawings pass USPTO 37 CFR 1.84 compliance audit
- No visual regression in drawing clarity or layout

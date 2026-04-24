#!/usr/bin/env python3
"""Validate USPTO margin requirements for patent drawing SVGs.

37 CFR 1.84(g): Margins must be at least 1 inch on all sides.
In our 850x1100 viewBox (100 units per inch), this means:
- Left margin: x >= 100
- Right margin: x <= 750
- Top margin: y >= 100 (or y >= 50 with translate(0, 50))
- Bottom margin: y <= 1000
"""

import sys
import re
from pathlib import Path


def _detect_scale(svg_content):
    """Return viewBox width/height/scale factor.

    The reference coordinate system is 850x1100 (100 units/inch).
    Scale = viewBox_width / 850.  All hardcoded thresholds expressed in
    reference units are multiplied by `scale` to get threshold values in
    the actual viewBox units.
    """
    m = re.search(r'viewBox="([^"]+)"', svg_content)
    if not m:
        return 850.0, 1100.0, 1.0
    parts = m.group(1).strip().split()
    if len(parts) != 4:
        return 850.0, 1100.0, 1.0
    try:
        _, _, vb_w, vb_h = (float(p) for p in parts)
    except ValueError:
        return 850.0, 1100.0, 1.0
    scale = vb_w / 850.0 if vb_w > 0 else 1.0
    return vb_w, vb_h, scale


def extract_coordinates(svg_content):
    """Extract all coordinate attributes and check them against
    scale-aware 1-inch USPTO margins (37 CFR 1.84(g))."""
    issues = []

    vb_w, vb_h, scale = _detect_scale(svg_content)

    # Reference thresholds (850x1100 scale): left>=100, right<=750,
    # top>=100, bottom<=1000. Header (y<=60) and footer (y>970) skipped.
    left_min = 100 * scale
    right_max = 750 * scale
    top_min = 100 * scale
    bottom_max = 1000 * scale
    header_cutoff = 60 * scale
    footer_cutoff = 970 * scale

    # Remove <defs>...</defs> — pattern/marker definitions, not content
    content_without_defs = re.sub(r'<defs>.*?</defs>', '', svg_content, flags=re.DOTALL)

    # Detect any top-level <g transform="translate(dx, dy)"> wrapper so that
    # inner content coordinates are shifted to their rendered position
    # before margin checks. Typical patterns: translate(0, 50) for 850x1100
    # and translate(300, 300) for 2550x3300.
    x_offset = 0.0
    y_offset = 0.0
    tm = re.search(
        r'<g[^>]*\btransform="translate\(\s*(-?[\d.]+)\s*[,\s]\s*(-?[\d.]+)\s*\)"',
        svg_content,
    )
    if tm:
        x_offset = float(tm.group(1))
        y_offset = float(tm.group(2))

    x_coords = re.findall(r'\bx="([\d.]+)"', content_without_defs)
    y_coords = re.findall(r'\by="([\d.]+)"', content_without_defs)
    x1_coords = re.findall(r'\bx1="([\d.]+)"', content_without_defs)
    y1_coords = re.findall(r'\by1="([\d.]+)"', content_without_defs)
    x2_coords = re.findall(r'\bx2="([\d.]+)"', content_without_defs)
    y2_coords = re.findall(r'\by2="([\d.]+)"', content_without_defs)
    cx_coords = re.findall(r'\bcx="([\d.]+)"', content_without_defs)
    cy_coords = re.findall(r'\bcy="([\d.]+)"', content_without_defs)

    rect_matches = re.findall(
        r'<rect[^>]*x="([\d.]+)"[^>]*width="([\d.]+)"',
        content_without_defs,
    )

    for x in x_coords + x1_coords + x2_coords + cx_coords:
        x_val = float(x) + x_offset
        if x_val < left_min:
            issues.append(f"Left margin violation: x={x_val:.1f} (min {left_min:.1f})")
        if x_val > right_max:
            issues.append(f"Right margin violation: x={x_val:.1f} (max {right_max:.1f})")

    for x, width in rect_matches:
        right_edge = float(x) + float(width) + x_offset
        if right_edge > right_max:
            issues.append(
                f"Right margin violation: rect extends to x={right_edge:.1f} "
                f"(max {right_max:.1f})"
            )

    for y in y_coords + y1_coords + y2_coords + cy_coords:
        y_val = float(y) + y_offset
        if y_val <= header_cutoff or y_val > footer_cutoff:
            continue
        if y_val < top_min:
            issues.append(f"Top margin violation: y={y_val:.1f} (min {top_min:.1f})")
        if y_val > bottom_max:
            issues.append(f"Bottom margin violation: y={y_val:.1f} (max {bottom_max:.1f})")

    return issues


def validate_margins(svg_file):
    """Main validation function."""
    try:
        content = Path(svg_file).read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return False

    # Check viewBox. USPTO 37 CFR 1.84(f) requires 8.5in x 11in sheets.
    # Any aspect-correct viewBox is acceptable as long as the rendered
    # size is 8.5x11 inches. We accept 0 0 W H when W:H ≈ 850:1100
    # (ratio 0.7727). This correctly accepts 0 0 2550 3300 (300 DPI).
    viewbox_match = re.search(r'viewBox="([^"]+)"', content)
    if viewbox_match:
        viewbox = viewbox_match.group(1).strip()
        parts = viewbox.split()
        valid = False
        if len(parts) == 4:
            try:
                _, _, vb_w, vb_h = (float(p) for p in parts)
                if vb_w > 0 and vb_h > 0:
                    ratio = vb_w / vb_h
                    if abs(ratio - 850 / 1100) < 0.01:
                        valid = True
            except ValueError:
                pass
        if valid:
            print(f"[PASS] ViewBox: {viewbox} (8.5:11 aspect)")
        else:
            print(f"[FAIL] ViewBox: {viewbox} (expected 8.5:11 aspect ratio, "
                  f"e.g. '0 0 850 1100' or '0 0 2550 3300')")
            return False
    else:
        print("[FAIL] ViewBox: Not found")
        return False

    # Check page size
    width_match = re.search(r'width="([^"]+)"', content)
    height_match = re.search(r'height="([^"]+)"', content)
    if width_match and height_match:
        width = width_match.group(1)
        height = height_match.group(1)
        if width == "8.5in" and height == "11in":
            print(f"[PASS] Page Size: {width} x {height}")
        else:
            print(f"[WARN] Page Size: {width} x {height} (expected 8.5in x 11in)")

    # Check coordinate bounds
    issues = extract_coordinates(content)

    if not issues:
        print("[PASS] Margins: All content within 1-inch bounds")
        return True
    else:
        print(f"[FAIL] Margins: {len(issues)} violation(s) found")
        for issue in issues[:10]:  # Show first 10
            print(f"       - {issue}")
        if len(issues) > 10:
            print(f"       ... and {len(issues) - 10} more")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python margin_validator.py <svg_file>")
        sys.exit(1)

    success = validate_margins(sys.argv[1])
    sys.exit(0 if success else 1)

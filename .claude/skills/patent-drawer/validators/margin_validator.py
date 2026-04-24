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


def extract_coordinates(svg_content):
    """Extract all x, y, x1, y1, x2, y2, cx, cy coordinates from SVG."""
    issues = []

    # Remove <defs>...</defs> section - these are pattern/marker definitions, not content
    content_without_defs = re.sub(r'<defs>.*?</defs>', '', svg_content, flags=re.DOTALL)

    # Check for transform offset
    has_transform = 'transform="translate(0, 50)"' in svg_content
    y_offset = 50 if has_transform else 0

    # Find all coordinate attributes (excluding defs content)
    # x="value" patterns
    x_coords = re.findall(r'\bx="([\d.]+)"', content_without_defs)
    y_coords = re.findall(r'\by="([\d.]+)"', content_without_defs)
    x1_coords = re.findall(r'\bx1="([\d.]+)"', content_without_defs)
    y1_coords = re.findall(r'\by1="([\d.]+)"', content_without_defs)
    x2_coords = re.findall(r'\bx2="([\d.]+)"', content_without_defs)
    y2_coords = re.findall(r'\by2="([\d.]+)"', content_without_defs)
    cx_coords = re.findall(r'\bcx="([\d.]+)"', content_without_defs)
    cy_coords = re.findall(r'\bcy="([\d.]+)"', content_without_defs)

    # Check rect elements for x + width bounds
    rect_matches = re.findall(r'<rect[^>]*x="([\d.]+)"[^>]*width="([\d.]+)"', content_without_defs)

    # Check all x coordinates
    all_x = x_coords + x1_coords + x2_coords + cx_coords
    for x in all_x:
        x_val = float(x)
        if x_val < 100:
            issues.append(f"Left margin violation: x={x_val} (min 100)")
        if x_val > 750:
            issues.append(f"Right margin violation: x={x_val} (max 750)")

    # Check rect right edges
    for x, width in rect_matches:
        right_edge = float(x) + float(width)
        if right_edge > 750:
            issues.append(f"Right margin violation: rect extends to x={right_edge} (max 750)")

    # Check all y coordinates (accounting for transform)
    all_y = y_coords + y1_coords + y2_coords + cy_coords
    for y in all_y:
        y_val = float(y) + y_offset
        # Skip page number at top (y<=60) and FIG label at bottom (y>970)
        if y_val <= 60 or y_val > 970:
            continue
        if y_val < 100:
            issues.append(f"Top margin violation: y={y_val} (min 100)")
        if y_val > 1000:
            issues.append(f"Bottom margin violation: y={y_val} (max 1000)")

    return issues


def validate_margins(svg_file):
    """Main validation function."""
    try:
        content = Path(svg_file).read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return False

    # Check viewBox
    viewbox_match = re.search(r'viewBox="([^"]+)"', content)
    if viewbox_match:
        viewbox = viewbox_match.group(1)
        if viewbox == "0 0 850 1100":
            print(f"[PASS] ViewBox: {viewbox}")
        else:
            print(f"[FAIL] ViewBox: {viewbox} (expected '0 0 850 1100')")
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

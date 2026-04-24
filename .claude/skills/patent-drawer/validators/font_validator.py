#!/usr/bin/env python3
"""Validate USPTO font requirements for patent drawing SVGs.

37 CFR 1.84(p): Numbers, letters, and reference characters must be
at least 0.32 cm (approximately 14 points) in height.

Allowed fonts:
- Arial, sans-serif (for labels and descriptive text)
- Courier New, monospace (for code, values, and formulas)
"""

import sys
import re
from pathlib import Path


def _detect_scale(content):
    """Detect viewBox width and return scale factor vs reference 850 units."""
    m = re.search(r'viewBox="([^"]+)"', content)
    if not m:
        return 1.0
    parts = m.group(1).strip().split()
    if len(parts) != 4:
        return 1.0
    try:
        vb_w = float(parts[2])
        return vb_w / 850.0 if vb_w > 0 else 1.0
    except ValueError:
        return 1.0


def validate_fonts(svg_file):
    """Validate font sizes (37 CFR 1.84(p)) — >= 14pt equivalent.

    Scale-aware: thresholds in reference 850-unit viewBox multiplied by
    the SVG's actual viewBox width / 850.
    """
    try:
        content = Path(svg_file).read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return False

    scale = _detect_scale(content)
    min_font_size = 14 * scale

    # Find all text elements with font attributes
    text_pattern = r'<text[^>]*>'
    text_elements = re.findall(text_pattern, content)

    size_issues = []
    family_issues = []

    for i, elem in enumerate(text_elements, 1):
        # Extract font-size — accept int or decimal
        size_match = re.search(r'font-size="([\d.]+)"', elem)
        if size_match:
            size = float(size_match.group(1))
            if size < min_font_size:
                # Find line number
                pos = content.find(elem)
                line_num = content[:pos].count('\n') + 1
                size_issues.append(
                    f"Line {line_num}: font-size={size} "
                    f"(min {min_font_size:.1f} at this scale)"
                )

        # Extract font-family
        family_match = re.search(r'font-family="([^"]+)"', elem)
        if family_match:
            family = family_match.group(1)
            valid_families = [
                'Arial', 'Arial, sans-serif',
                'Courier New', 'Courier New, monospace'
            ]
            if family not in valid_families:
                pos = content.find(elem)
                line_num = content[:pos].count('\n') + 1
                family_issues.append(f"Line {line_num}: font-family='{family}'")

    # Report results
    total_text = len(text_elements)
    print(f"[INFO] Found {total_text} text elements")

    if not size_issues:
        print(f"[PASS] Font Size: All {total_text} elements >= 14pt")
    else:
        print(f"[FAIL] Font Size: {len(size_issues)} element(s) below 14pt")
        for issue in size_issues[:5]:
            print(f"       - {issue}")
        if len(size_issues) > 5:
            print(f"       ... and {len(size_issues) - 5} more")

    if not family_issues:
        print(f"[PASS] Font Family: All elements use Arial or Courier New")
    else:
        print(f"[WARN] Font Family: {len(family_issues)} non-standard font(s)")
        for issue in family_issues[:5]:
            print(f"       - {issue}")

    return len(size_issues) == 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python font_validator.py <svg_file>")
        sys.exit(1)

    success = validate_fonts(sys.argv[1])
    sys.exit(0 if success else 1)

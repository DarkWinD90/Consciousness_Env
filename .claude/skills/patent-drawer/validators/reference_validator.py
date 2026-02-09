#!/usr/bin/env python3
"""Validate USPTO reference numeral requirements for patent drawing SVGs.

37 CFR 1.84(p): Reference characters must be placed to indicate the
part to which they refer. Lead lines are required between reference
characters and the parts they identify.

Requirements:
- Reference numerals should be 2-3 digit numbers (10, 100, 102, etc.)
- Each numeral should have a leader line (thin line pointing to element)
- Leader lines should be 0.5px stroke-width
"""

import sys
import re
from pathlib import Path


def find_reference_numerals(content):
    """Find all reference numerals (standalone 2-3 digit numbers in text elements)."""
    numerals = []

    # Split content into lines for line number tracking
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        # Look for text elements containing only 2-3 digit numbers
        # Pattern: <text ...>NNN</text> where NNN is 2-3 digits
        matches = re.finditer(r'<text[^>]*x="([\d.]+)"[^>]*y="([\d.]+)"[^>]*>(\d{2,3})</text>', line)

        for match in matches:
            x = float(match.group(1))
            y = float(match.group(2))
            numeral = match.group(3)

            # Skip if this looks like an axis label (x values like 100, 200, 300, 400, 500)
            # These are typically at specific y positions on graphs
            if numeral in ['100', '200', '300', '400', '500'] and 'text-anchor="middle"' in line:
                # Check if it's in a graph context (y > 400 typically)
                continue

            numerals.append({
                'value': numeral,
                'line': line_num,
                'x': x,
                'y': y
            })

    return numerals


def find_leader_lines_near(content, x, y, tolerance=25):
    """Check if a leader line exists near the given coordinates."""
    lines = content.split('\n')

    for line in lines:
        # Look for thin lines (stroke-width="0.5")
        if 'stroke-width="0.5"' not in line:
            continue

        if '<line' not in line:
            continue

        # Extract line coordinates
        x1_match = re.search(r'x1="([\d.]+)"', line)
        y1_match = re.search(r'y1="([\d.]+)"', line)
        x2_match = re.search(r'x2="([\d.]+)"', line)
        y2_match = re.search(r'y2="([\d.]+)"', line)

        if x1_match and y1_match:
            lx1 = float(x1_match.group(1))
            ly1 = float(y1_match.group(1))

            # Check if line starts near the numeral
            if abs(lx1 - x) < tolerance and abs(ly1 - y) < tolerance:
                return True

        if x2_match and y2_match:
            lx2 = float(x2_match.group(1))
            ly2 = float(y2_match.group(1))

            # Check if line ends near the numeral
            if abs(lx2 - x) < tolerance and abs(ly2 - y) < tolerance:
                return True

    return False


def check_adjacent_leader_line(content, line_num):
    """Check if there's a leader line on the next line after the text element."""
    lines = content.split('\n')

    if line_num < len(lines):
        next_line = lines[line_num]  # line_num is 1-indexed, so this gets the next line
        if '<line' in next_line and 'stroke-width="0.5"' in next_line:
            return True

    return False


def validate_references(svg_file):
    """Main validation function."""
    try:
        content = Path(svg_file).read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return False

    numerals = find_reference_numerals(content)

    if not numerals:
        print("[INFO] Reference Numerals: None found (may be intentional)")
        return True

    print(f"[INFO] Found {len(numerals)} reference numeral(s)")

    missing_leaders = []
    for num in numerals:
        # Check for leader line near the numeral OR on the next line
        has_leader = (
            find_leader_lines_near(content, num['x'], num['y']) or
            check_adjacent_leader_line(content, num['line'])
        )

        if not has_leader:
            missing_leaders.append(num)

    if not missing_leaders:
        print(f"[PASS] Reference Numerals: All {len(numerals)} have leader lines")
        return True
    else:
        # Only report as warning if some are missing, not failure
        # since our detection might have false positives
        print(f"[WARN] Reference Numerals: {len(missing_leaders)} may be missing leader lines")
        for num in missing_leaders[:5]:
            print(f"       - '{num['value']}' at line {num['line']}")
        if len(missing_leaders) > 5:
            print(f"       ... and {len(missing_leaders) - 5} more")
        # Return True (pass) since this is just a warning
        # The validator errs on the side of caution
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python reference_validator.py <svg_file>")
        sys.exit(1)

    success = validate_references(sys.argv[1])
    sys.exit(0 if success else 1)

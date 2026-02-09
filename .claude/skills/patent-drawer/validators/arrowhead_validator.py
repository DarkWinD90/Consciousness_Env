#!/usr/bin/env python3
"""Validate USPTO arrowhead requirements for patent drawing SVGs.

37 CFR 1.84(q): Lead lines should be straight and not cross each other.
Arrows at the ends of lines should be used to indicate direction.

Standard arrowhead specification:
- markerWidth="6"
- markerHeight="4"
- refX="6" refY="2"
- Consistent across all figures
"""

import sys
import re
from pathlib import Path


def validate_arrowheads(svg_file):
    """Validate arrowhead marker definitions."""
    try:
        content = Path(svg_file).read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return False

    # Find marker definitions
    marker_pattern = r'<marker[^>]*id="ah"[^>]*>'
    marker_match = re.search(marker_pattern, content)

    if not marker_match:
        print("[WARN] Arrowheads: No marker definition found (id='ah')")
        return True

    marker_elem = marker_match.group(0)

    # Check dimensions
    width_match = re.search(r'markerWidth="(\d+)"', marker_elem)
    height_match = re.search(r'markerHeight="(\d+)"', marker_elem)
    refx_match = re.search(r'refX="(\d+)"', marker_elem)
    refy_match = re.search(r'refY="(\d+)"', marker_elem)

    issues = []

    if width_match:
        width = int(width_match.group(1))
        if width != 6:
            issues.append(f"markerWidth={width} (expected 6)")
    else:
        issues.append("markerWidth not specified")

    if height_match:
        height = int(height_match.group(1))
        if height != 4:
            issues.append(f"markerHeight={height} (expected 4)")
    else:
        issues.append("markerHeight not specified")

    if refx_match:
        refx = int(refx_match.group(1))
        if refx != 6:
            issues.append(f"refX={refx} (expected 6)")

    if refy_match:
        refy = int(refy_match.group(1))
        if refy != 2:
            issues.append(f"refY={refy} (expected 2)")

    # Count arrows in use
    arrow_count = content.count('marker-end="url(#ah)"')
    print(f"[INFO] Found {arrow_count} arrow(s) using marker")

    if not issues:
        print(f"[PASS] Arrowheads: Correct 6x4 sizing")
        return True
    else:
        print(f"[FAIL] Arrowheads: Non-standard dimensions")
        for issue in issues:
            print(f"       - {issue}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python arrowhead_validator.py <svg_file>")
        sys.exit(1)

    success = validate_arrowheads(sys.argv[1])
    sys.exit(0 if success else 1)

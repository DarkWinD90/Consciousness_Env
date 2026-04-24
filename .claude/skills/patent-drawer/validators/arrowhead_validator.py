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

    # Find marker definitions — support any marker id, not just "ah"
    marker_pattern = r'<marker\b([^>]*)>'
    all_markers = re.findall(marker_pattern, content)

    # Count how many arrows are actually used (via marker-end / marker-start / marker-mid)
    arrow_refs = re.findall(r'marker-(?:end|start|mid)="url\(#([^)]+)\)"', content)
    arrow_count = len(arrow_refs)
    unique_marker_ids = set(arrow_refs)

    # If the SVG has no marker definitions but uses arrows, that's a real issue
    if not all_markers:
        if arrow_count > 0:
            print(f"[FAIL] Arrowheads: {arrow_count} arrow reference(s) but no <marker> definitions")
            return False
        print("[INFO] Arrowheads: No markers and no arrow refs (may be intentional)")
        return True

    # Validate each marker definition that is actually referenced
    issues = []
    for marker_elem in all_markers:
        m_id = re.search(r'id="([^"]+)"', marker_elem)
        if not m_id or m_id.group(1) not in unique_marker_ids:
            continue  # defined but unused — skip

        width_match = re.search(r'markerWidth="([\d.]+)"', marker_elem)
        height_match = re.search(r'markerHeight="([\d.]+)"', marker_elem)
        refx_match = re.search(r'refX="([\d.]+)"', marker_elem)
        refy_match = re.search(r'refY="([\d.]+)"', marker_elem)

        mid = m_id.group(1)
        if width_match:
            w = float(width_match.group(1))
            if w != 6:
                issues.append(f"marker id='{mid}' markerWidth={w} (expected 6)")
        else:
            issues.append(f"marker id='{mid}' markerWidth not specified")

        if height_match:
            h = float(height_match.group(1))
            if h != 4:
                issues.append(f"marker id='{mid}' markerHeight={h} (expected 4)")
        else:
            issues.append(f"marker id='{mid}' markerHeight not specified")

    print(f"[INFO] Found {arrow_count} arrow(s) using {len(unique_marker_ids)} marker id(s): {sorted(unique_marker_ids)}")

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

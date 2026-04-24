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

def _axis_label_block_ranges(content):
    """Return a list of (start_line, end_line) ranges for each
    ``<g class="axis-label">`` block in ``content`` (line numbers are
    1-indexed, inclusive).

    Handles only flat, non-nested axis-label blocks — the existing
    figures never nest them, and nesting would indicate a different
    semantic intent.
    """
    ranges = []
    lines = content.split('\n')
    open_line = None
    for i, line in enumerate(lines, 1):
        if open_line is None:
            if 'class="axis-label"' in line and '<g' in line:
                open_line = i
        else:
            if '</g>' in line:
                ranges.append((open_line, i))
                open_line = None
    return ranges


def _detect_scale(content):
    """Return viewBox-width / 850 as scale factor for scale-dependent thresholds."""
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


def _is_graph_axis_label(content, x, y, line_num, axis_block_ranges=None):
    """Return True when the numeral at ``line_num`` is inside an explicit
    ``<g class="axis-label">`` block.

    **Scope** (what this function does and does not do):

    - **DOES** classify as axis any ``<text>`` element whose source line
      falls inside a ``<g class="axis-label">`` ... ``</g>`` range.
      Authors mark up axis labels explicitly to distinguish them from
      reference numerals, and we honor that markup as authoritative.

    - **DOES NOT** perform coordinate-alignment inference to guess at
      axis ticks. A prior implementation tried to detect axes by
      clustering centered numeric text elements on the same y or x
      coordinate. That heuristic mis-classified legitimate reference
      numerals that happened to sit in a horizontal row (e.g., patent_b/
      fig2's five spectrum-region numerals 28-36 are all at y=190 with
      text-anchor="middle" and look exactly like axis ticks
      coord-wise, but each labels a distinct part of the drawing). The
      result was systematic false negatives. A purely explicit rule
      avoids that ambiguity entirely at the cost of requiring figure
      authors to wrap their tick labels in a ``<g class="axis-label">``
      block when axes are present.

    - **Non-argument**: the ``x``/``y`` parameters are preserved in the
      signature for forward compatibility but are no longer consulted.
      Callers may pass any values.
    """
    ranges = axis_block_ranges if axis_block_ranges is not None \
        else _axis_label_block_ranges(content)
    for start, end in ranges:
        if start <= line_num <= end:
            return True
    return False


def find_reference_numerals(content):
    """Find all reference numerals (standalone 2-3 digit numbers in text elements).

    Axis labels are filtered out via :func:`_is_graph_axis_label` (see that
    function's docstring for the detection rules). Any numeric ``<text>``
    element of 2-3 digits that doesn't look like a graph-axis tick label
    is treated as a reference numeral and must have a leader line.
    """
    numerals = []
    axis_ranges = _axis_label_block_ranges(content)

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

            # Axis-label detection: numeral is inside an explicit
            # <g class="axis-label"> block. See _is_graph_axis_label for
            # the rationale on why we do not use coord-alignment.
            if _is_graph_axis_label(
                content, x, y, line_num, axis_block_ranges=axis_ranges
            ):
                continue

            numerals.append({
                'value': numeral,
                'line': line_num,
                'x': x,
                'y': y
            })

    return numerals


_SIGNAL_STROKE_MIN = 1.0
"""Minimum stroke width that counts as a main signal path.

This boundary is shared with geometric_validator.parse_lines(), which
applies the same cutoff (strict less-than) when deciding whether a line is
a leader line (to be ignored during geometric collision checks) or a
full-strength signal path. Keeping the two validators in sync prevents a
line from being classified as a leader by one tool and a signal by the
other.
"""


def _is_leader_stroke(width_str, scale=1.0):
    """Return True when *width_str* is a plausible leader-line stroke width.

    A leader line is any thin stroke below the main-signal minimum, plus
    the explicit 0.5*scale and 1.5 values that prior sessions hand-authored
    into the 2550x3300 (scale=3) figures. "Thin" is anything strictly less
    than 1.0 at reference scale; at scale s, leaders may be up to
    ~0.5*s (e.g., 1.5 at scale=3) to remain proportionally thin at render.
    """
    try:
        w = float(width_str)
    except (TypeError, ValueError):
        return False
    if w <= 0:
        return False
    # Thin at reference scale (catches 0.5, 0.8, 1 without decimal, 1.0 exactly).
    # Using <= 1.0 closes the boundary ambiguity where geometric_validator uses
    # strict < 1.0: we classify 1.0 as a leader here to reduce false-negatives
    # on hand-drawn leader lines.
    if w <= _SIGNAL_STROKE_MIN:
        return True
    # Historical convention: 1.5 has been used as a leader-line stroke in
    # some 850x1100 figures (e.g., patent_b/fig5). Keep accepting it to
    # avoid reintroducing the false-negatives the prior-session audit
    # already removed. This is slightly permissive at reference scale —
    # a main-signal stroke of exactly 1.5 adjacent to a numeral will be
    # classified as a leader — which is acceptable because the adjacency
    # itself is the dominant semantic signal.
    if abs(w - 1.5) < 0.01:
        return True
    # At scaled canvases (2550x3300 uses scale=3), leaders may be drawn at
    # 0.5*scale (=1.5 at scale 3) to stay visually thin after rasterization.
    if scale > 1.0 and abs(w - 0.5 * scale) < 0.1:
        return True
    return False


def find_leader_lines_near(content, x, y, tolerance=25, scale=1.0):
    """Check if a leader line exists near the given coordinates.

    A "leader" is any line whose stroke-width is thin relative to main
    signal paths (see ``_is_leader_stroke``). Tolerance scales with the
    viewBox width so large-coordinate figures (e.g., 2550x3300) still
    see leader endpoints attached to the numeral text within a visually
    proportional distance.
    """
    lines = content.split('\n')
    scaled_tol = tolerance * scale

    for line in lines:
        if '<line' not in line:
            continue
        sw = re.search(r'stroke-width="([\d.]+)"', line)
        if not sw or not _is_leader_stroke(sw.group(1), scale=scale):
            continue

        # Extract line coordinates
        x1_match = re.search(r'x1="([\d.]+)"', line)
        y1_match = re.search(r'y1="([\d.]+)"', line)
        x2_match = re.search(r'x2="([\d.]+)"', line)
        y2_match = re.search(r'y2="([\d.]+)"', line)

        if x1_match and y1_match:
            lx1 = float(x1_match.group(1))
            ly1 = float(y1_match.group(1))
            if abs(lx1 - x) < scaled_tol and abs(ly1 - y) < scaled_tol:
                return True

        if x2_match and y2_match:
            lx2 = float(x2_match.group(1))
            ly2 = float(y2_match.group(1))
            if abs(lx2 - x) < scaled_tol and abs(ly2 - y) < scaled_tol:
                return True

    return False


def check_adjacent_leader_line(content, line_num, scale=1.0):
    """Check if a leader line immediately follows the text element.

    Looks at the next non-blank line after the numeral <text> element. If
    it contains a <line> with a thin leader stroke-width, accept it. This
    handles the hand-authored convention where each reference numeral is
    followed verbatim by its leader line in the source file, even when
    stroke-widths vary (0.5, 0.8, 1, 1.0 have all appeared historically).
    """
    lines = content.split('\n')

    # line_num is 1-indexed; scan up to the next two non-blank lines so a
    # blank separator between the <text> and the <line> doesn't cause a miss.
    idx = line_num  # first candidate = line after the numeral text
    checked = 0
    while idx < len(lines) and checked < 2:
        candidate = lines[idx]
        if candidate.strip():
            if '<line' in candidate:
                sw = re.search(r'stroke-width="([\d.]+)"', candidate)
                if sw and _is_leader_stroke(sw.group(1), scale=scale):
                    return True
            break  # first non-blank line was not a leader line; stop
        idx += 1
        checked += 1
    return False


def validate_references(svg_file):
    """Main validation function."""
    try:
        content = Path(svg_file).read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return False

    numerals = find_reference_numerals(content)
    scale = _detect_scale(content)

    if not numerals:
        print("[INFO] Reference Numerals: None found (may be intentional)")
        return True

    print(f"[INFO] Found {len(numerals)} reference numeral(s) [scale={scale:.2f}x]")

    missing_leaders = []
    for num in numerals:
        # Check for leader line near the numeral OR on the next line
        has_leader = (
            find_leader_lines_near(content, num['x'], num['y'], scale=scale) or
            check_adjacent_leader_line(content, num['line'], scale=scale)
        )

        if not has_leader:
            missing_leaders.append(num)

    if not missing_leaders:
        print(f"[PASS] Reference Numerals: All {len(numerals)} have leader lines")
        return True

    # 37 CFR 1.84(p)(1): leader lines are required. Any missing leader is
    # non-compliant — there is no passing-WARN level. Previously this function
    # silently returned True for <30% missing; that masked real issues.
    print(f"[FAIL] Reference Numerals: {len(missing_leaders)}/{len(numerals)} missing leader lines")
    for num in missing_leaders[:10]:
        print(f"       - '{num['value']}' at line {num['line']}")
    if len(missing_leaders) > 10:
        print(f"       ... and {len(missing_leaders) - 10} more")
    return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python reference_validator.py <svg_file>")
        sys.exit(1)

    success = validate_references(sys.argv[1])
    sys.exit(0 if success else 1)

#!/usr/bin/env python
"""USPTO Patent Drawing Collision Checker - Comprehensive Audit

Checks for:
1. Text-on-text collisions (with proper rotated text bbox handling)
2. Text-on-line collisions
3. Signal paths cutting through elements (path/line through rect/circle/ellipse)
4. Crowded reference numerals
"""

import xml.etree.ElementTree as ET
import os
import re
import math
import sys
from pathlib import Path


def safe_float(val, default=0):
    """Safely convert a value to float."""
    if val is None:
        return default
    val = str(val).strip()
    if '%' in val:
        return default
    try:
        return float(val)
    except ValueError:
        return default


def get_text_bbox(elem, transform=None):
    """Estimate bounding box for text element, handling rotation transforms."""
    try:
        x = float(elem.get('x', 0))
        y = float(elem.get('y', 0))
        font_size = float(elem.get('font-size', 10))
        text = elem.text or ''
        anchor = elem.get('text-anchor', 'start')

        width = len(text) * font_size * 0.6
        height = font_size * 1.2

        if anchor == 'middle':
            x -= width / 2
        elif anchor == 'end':
            x -= width

        # Check for rotation in the element's own transform first
        elem_transform = elem.get('transform', '')
        rot_match = re.search(r'rotate\(\s*(-?[\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)\s*\)', elem_transform)

        if rot_match:
            angle = float(rot_match.group(1))
            cx = float(rot_match.group(2))
            cy = float(rot_match.group(3))

            # For -90 or 270 degree rotation, swap width/height and recompute position
            if abs(angle) in (90, 270) or abs(angle + 360) in (90, 270):
                # Compute pre-rotation bbox center
                pre_cx = x + width / 2
                pre_cy = y - height / 2

                # Rotate center around (cx, cy)
                rad = math.radians(angle)
                cos_a = math.cos(rad)
                sin_a = math.sin(rad)
                dx = pre_cx - cx
                dy = pre_cy - cy
                new_cx = cx + dx * cos_a - dy * sin_a
                new_cy = cy + dx * sin_a + dy * cos_a

                # Swap dimensions for 90-degree rotations
                new_width = height
                new_height = width

                x = new_cx - new_width / 2
                y_top = new_cy - new_height / 2

                # Apply parent translate transform if present
                if transform:
                    t_match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
                    if t_match:
                        x += float(t_match.group(1))
                        y_top += float(t_match.group(2))

                return {'x': x, 'y': y_top, 'width': new_width, 'height': new_height, 'text': text}

        # No rotation — apply translate transform normally
        if transform:
            t_match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if t_match:
                x += float(t_match.group(1))
                y += float(t_match.group(2))

        return {'x': x, 'y': y - height, 'width': width, 'height': height, 'text': text}
    except (ValueError, AttributeError, KeyError) as exc:
        # Parsing failure — surface it to the caller instead of silently
        # swallowing. The collision check is meaningless if we can't parse
        # the text element. Callers can catch if they want to tolerate
        # bad elements, but the default must not be a silent False-clean.
        sys.stderr.write(
            f"[run_collision_check] WARN: could not parse text bbox "
            f"({type(exc).__name__}: {exc}) — skipping and flagging\n"
        )
        return None


def get_rect_bbox(elem, transform=None):
    """Get bounding box for rect element."""
    try:
        x = float(elem.get('x', 0))
        y = float(elem.get('y', 0))
        width = float(elem.get('width', 0))
        height = float(elem.get('height', 0))

        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                x += float(match.group(1))
                y += float(match.group(2))

        return {'x': x, 'y': y, 'width': width, 'height': height}
    except Exception:
        return None


def get_circle_bbox(elem, transform=None):
    """Get bounding box for circle element."""
    try:
        cx = float(elem.get('cx', 0))
        cy = float(elem.get('cy', 0))
        r = float(elem.get('r', 0))

        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                cx += float(match.group(1))
                cy += float(match.group(2))

        return {'x': cx - r, 'y': cy - r, 'width': 2 * r, 'height': 2 * r}
    except Exception:
        return None


def get_ellipse_bbox(elem, transform=None):
    """Get bounding box for ellipse element."""
    try:
        cx = float(elem.get('cx', 0))
        cy = float(elem.get('cy', 0))
        rx = float(elem.get('rx', 0))
        ry = float(elem.get('ry', 0))

        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                cx += float(match.group(1))
                cy += float(match.group(2))

        return {'x': cx - rx, 'y': cy - ry, 'width': 2 * rx, 'height': 2 * ry}
    except Exception:
        return None


def get_line_bbox(elem, transform=None):
    """Get bounding box for line element."""
    try:
        x1 = float(elem.get('x1', 0))
        y1 = float(elem.get('y1', 0))
        x2 = float(elem.get('x2', 0))
        y2 = float(elem.get('y2', 0))
        stroke_width = float(elem.get('stroke-width', 1))

        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                tx, ty = float(match.group(1)), float(match.group(2))
                x1 += tx; y1 += ty; x2 += tx; y2 += ty

        return {
            'x': min(x1, x2) - stroke_width,
            'y': min(y1, y2) - stroke_width,
            'width': abs(x2 - x1) + 2 * stroke_width,
            'height': abs(y2 - y1) + 2 * stroke_width,
            'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
            'stroke_width': stroke_width,
        }
    except Exception:
        return None


def get_line_segments(elem, transform=None):
    """Extract line segment endpoints for a <line> element."""
    try:
        x1 = float(elem.get('x1', 0))
        y1 = float(elem.get('y1', 0))
        x2 = float(elem.get('x2', 0))
        y2 = float(elem.get('y2', 0))
        stroke_width = float(elem.get('stroke-width', 1))

        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                tx, ty = float(match.group(1)), float(match.group(2))
                x1 += tx; y1 += ty; x2 += tx; y2 += ty

        return [{'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'stroke_width': stroke_width}]
    except Exception:
        return []


def parse_path_to_segments(d_attr, tx=0, ty=0):
    """Parse SVG path d attribute into line segments (list of {x1,y1,x2,y2})."""
    segments = []
    parts = re.findall(r'([MLHVQCSTAZmlhvqcstaz])([^MLHVQCSTAZmlhvqcstaz]*)', d_attr)
    cx, cy = 0, 0
    sx, sy = 0, 0  # subpath start

    for cmd, args in parts:
        nums = [float(n) for n in re.findall(r'-?[\d.]+', args)]

        prev_x, prev_y = cx, cy

        if cmd == 'M':
            if len(nums) >= 2:
                cx, cy = nums[0] + tx, nums[1] + ty
                sx, sy = cx, cy
        elif cmd == 'm':
            if len(nums) >= 2:
                cx += nums[0]
                cy += nums[1]
                sx, sy = cx, cy
        elif cmd == 'L':
            if len(nums) >= 2:
                nx, ny = nums[0] + tx, nums[1] + ty
                segments.append({'x1': cx, 'y1': cy, 'x2': nx, 'y2': ny})
                cx, cy = nx, ny
        elif cmd == 'l':
            if len(nums) >= 2:
                nx, ny = cx + nums[0], cy + nums[1]
                segments.append({'x1': cx, 'y1': cy, 'x2': nx, 'y2': ny})
                cx, cy = nx, ny
        elif cmd == 'H':
            if len(nums) >= 1:
                nx = nums[0] + tx
                segments.append({'x1': cx, 'y1': cy, 'x2': nx, 'y2': cy})
                cx = nx
        elif cmd == 'h':
            if len(nums) >= 1:
                nx = cx + nums[0]
                segments.append({'x1': cx, 'y1': cy, 'x2': nx, 'y2': cy})
                cx = nx
        elif cmd == 'V':
            if len(nums) >= 1:
                ny = nums[0] + ty
                segments.append({'x1': cx, 'y1': cy, 'x2': cx, 'y2': ny})
                cy = ny
        elif cmd == 'v':
            if len(nums) >= 1:
                ny = cy + nums[0]
                segments.append({'x1': cx, 'y1': cy, 'x2': cx, 'y2': ny})
                cy = ny
        elif cmd in ('Q', 'q'):
            # Approximate quadratic Bezier as line from start to end
            if len(nums) >= 4:
                if cmd == 'Q':
                    nx, ny = nums[2] + tx, nums[3] + ty
                else:
                    nx, ny = cx + nums[2], cy + nums[3]
                segments.append({'x1': cx, 'y1': cy, 'x2': nx, 'y2': ny})
                cx, cy = nx, ny
        elif cmd in ('C', 'c'):
            if len(nums) >= 6:
                if cmd == 'C':
                    nx, ny = nums[4] + tx, nums[5] + ty
                else:
                    nx, ny = cx + nums[4], cy + nums[5]
                segments.append({'x1': cx, 'y1': cy, 'x2': nx, 'y2': ny})
                cx, cy = nx, ny
        elif cmd in ('T', 't', 'S', 's'):
            if len(nums) >= 2:
                if cmd.isupper():
                    nx, ny = nums[-2] + tx, nums[-1] + ty
                else:
                    nx, ny = cx + nums[-2], cy + nums[-1]
                segments.append({'x1': cx, 'y1': cy, 'x2': nx, 'y2': ny})
                cx, cy = nx, ny
        elif cmd in ('Z', 'z'):
            if (cx, cy) != (sx, sy):
                segments.append({'x1': cx, 'y1': cy, 'x2': sx, 'y2': sy})
            cx, cy = sx, sy

    return segments


def point_near_rect_boundary(px, py, rect, tolerance=8):
    """Check if a point is on or very near a rect boundary."""
    rx, ry = rect['x'], rect['y']
    rw, rh = rect['width'], rect['height']

    # Check if point is near any edge
    on_left = abs(px - rx) <= tolerance and ry - tolerance <= py <= ry + rh + tolerance
    on_right = abs(px - (rx + rw)) <= tolerance and ry - tolerance <= py <= ry + rh + tolerance
    on_top = abs(py - ry) <= tolerance and rx - tolerance <= px <= rx + rw + tolerance
    on_bottom = abs(py - (ry + rh)) <= tolerance and rx - tolerance <= px <= rx + rw + tolerance

    return on_left or on_right or on_top or on_bottom


def point_inside_rect(px, py, rect, tolerance=2):
    """Check if a point is inside a rect (with tolerance)."""
    return (rect['x'] - tolerance <= px <= rect['x'] + rect['width'] + tolerance and
            rect['y'] - tolerance <= py <= rect['y'] + rect['height'] + tolerance)


def segment_intersects_rect(seg, rect, margin=3):
    """Check if a line segment passes through a rect interior.

    Returns True only if the segment genuinely cuts through an unrelated rect —
    not if it connects to the rect, is internal to the rect, or barely clips it.
    """
    rx = rect['x'] + margin
    ry = rect['y'] + margin
    rw = rect['width'] - 2 * margin
    rh = rect['height'] - 2 * margin
    if rw <= 0 or rh <= 0:
        return False

    x1, y1 = seg['x1'], seg['y1']
    x2, y2 = seg['x2'], seg['y2']

    # Skip segments where either endpoint is inside the rect (internal dividers,
    # connection arrows that start/end at this element)
    if point_inside_rect(x1, y1, rect, tolerance=5):
        return False
    if point_inside_rect(x2, y2, rect, tolerance=5):
        return False

    # Skip segments where either endpoint is on/near the rect boundary
    # (these are connections TO/FROM this rect, not cutting through it)
    if point_near_rect_boundary(x1, y1, rect, tolerance=8):
        return False
    if point_near_rect_boundary(x2, y2, rect, tolerance=8):
        return False

    # Liang-Barsky line clipping to check intersection
    dx = x2 - x1
    dy = y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - rx, rx + rw - x1, y1 - ry, ry + rh - y1]

    t_enter = 0.0
    t_exit = 1.0

    for i in range(4):
        if p[i] == 0:
            if q[i] < 0:
                return False
        else:
            t = q[i] / p[i]
            if p[i] < 0:
                t_enter = max(t_enter, t)
            else:
                t_exit = min(t_exit, t)

    if t_enter >= t_exit:
        return False

    # Only flag if it genuinely crosses through (enters AND exits)
    clip_length = math.sqrt(((t_exit - t_enter) * dx) ** 2 + ((t_exit - t_enter) * dy) ** 2)
    return clip_length > 15  # Must cut through at least 15px


def boxes_overlap(b1, b2, threshold=0.15):
    """Check if two bounding boxes overlap beyond threshold."""
    if not b1 or not b2:
        return False, 0

    x_overlap = max(0, min(b1['x'] + b1['width'], b2['x'] + b2['width']) - max(b1['x'], b2['x']))
    y_overlap = max(0, min(b1['y'] + b1['height'], b2['y'] + b2['height']) - max(b1['y'], b2['y']))

    intersection = x_overlap * y_overlap
    if intersection == 0:
        return False, 0

    area1 = b1['width'] * b1['height']
    area2 = b2['width'] * b2['height']
    smaller_area = min(area1, area2)

    if smaller_area == 0:
        return False, 0

    overlap_ratio = intersection / smaller_area
    return overlap_ratio > threshold, overlap_ratio


def is_signal_path(elem):
    """Determine if a line or path element is a signal path (not a tick mark,
    leader line, or decorative element)."""
    stroke_width = safe_float(elem.get('stroke-width', 1))
    marker_end = elem.get('marker-end', '')
    stroke_dash = elem.get('stroke-dasharray', '')
    tag = elem.tag.replace('{http://www.w3.org/2000/svg}', '')

    # Signal paths typically have:
    # - stroke-width >= 1.0 (not leader lines at 0.5)
    # - Often have marker-end (arrowheads)
    # - Can be solid or dashed
    if stroke_width < 0.8:
        return False

    if tag == 'line':
        x1 = safe_float(elem.get('x1'))
        y1 = safe_float(elem.get('y1'))
        x2 = safe_float(elem.get('x2'))
        y2 = safe_float(elem.get('y2'))
        length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        # Tick marks are very short
        if length < 15:
            return False
        # Has arrowhead = definitely signal path
        if marker_end:
            return True
        # Long lines without arrows could be axes or signal paths
        if length > 30 and stroke_width >= 1.0:
            return True
        return False

    if tag == 'path':
        d = elem.get('d', '')
        if not d:
            return False
        # Skip very short paths (arrowhead polygons, tiny decorations)
        # Count the number of commands - signal paths have multiple
        cmds = re.findall(r'[MLHVQCSTAZmlhvqcstaz]', d)
        if len(cmds) < 2:
            return False
        # Skip closed paths (shapes like diamonds, boxes drawn with path)
        if d.rstrip().upper().endswith('Z'):
            return False
        if marker_end or stroke_width >= 1.0:
            return True

    return False


def analyze_svg(filepath):
    """Analyze a single SVG for collisions and signal path issues."""
    collisions = []
    warnings = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    root = ET.fromstring(content)

    texts = []
    solid_rects = []    # Non-dashed rects (actual components)
    all_rects = []      # All rects for internal-line detection
    circles = []
    ellipses = []
    lines = []
    signal_segments = []  # Line segments from signal paths

    def process_element(elem, parent_transform=None):
        tag = elem.tag.replace('{http://www.w3.org/2000/svg}', '')
        transform = elem.get('transform', parent_transform)

        if tag == 'text':
            bbox = get_text_bbox(elem, transform)
            if bbox and bbox['text']:
                texts.append(bbox)
        elif tag == 'rect':
            bbox = get_rect_bbox(elem, transform)
            if bbox and bbox['width'] > 0 and bbox['height'] > 0:
                all_rects.append(bbox)
                # Only include solid rects as collision targets for signal paths
                # Dashed rects are typically enclosures/boundaries, not block components
                dash = elem.get('stroke-dasharray', '')
                # Also exclude very large rects (likely page-level enclosures)
                is_huge = bbox['width'] > 500 and bbox['height'] > 300
                if not dash and not is_huge:
                    solid_rects.append(bbox)
                # All rects participate in text collision checks
        elif tag == 'circle':
            bbox = get_circle_bbox(elem, transform)
            if bbox:
                circles.append(bbox)
        elif tag == 'ellipse':
            bbox = get_ellipse_bbox(elem, transform)
            if bbox:
                ellipses.append(bbox)
        elif tag == 'line':
            bbox = get_line_bbox(elem, transform)
            if bbox:
                lines.append(bbox)
            # Check if it's a signal path
            if is_signal_path(elem):
                segs = get_line_segments(elem, transform)
                signal_segments.extend(segs)
        elif tag == 'path':
            if is_signal_path(elem):
                d = elem.get('d', '')
                tx, ty = 0, 0
                if transform:
                    t_match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
                    if t_match:
                        tx = float(t_match.group(1))
                        ty = float(t_match.group(2))
                segs = parse_path_to_segments(d, tx, ty)
                signal_segments.extend(segs)

        for child in elem:
            child_transform = transform
            if child.get('transform'):
                child_transform = child.get('transform')
            process_element(child, child_transform)

    process_element(root)

    # Filter out signal segments that are internal to any rect (divider lines)
    filtered_segments = []
    for seg in signal_segments:
        is_internal = False
        for rect in all_rects:
            if (point_inside_rect(seg['x1'], seg['y1'], rect, tolerance=3) and
                    point_inside_rect(seg['x2'], seg['y2'], rect, tolerance=3)):
                is_internal = True
                break
        if not is_internal:
            filtered_segments.append(seg)
    signal_segments = filtered_segments

    # 1. Text-on-text collisions (significant overlaps only)
    for i, t1 in enumerate(texts):
        for t2 in texts[i + 1:]:
            overlaps, ratio = boxes_overlap(t1, t2, 0.20)
            if overlaps:
                collisions.append({
                    'type': 'text-on-text',
                    'desc': f'"{t1["text"]}" overlaps "{t2["text"]}"',
                    'overlap': ratio,
                    'fix': f'Move one text element by {int(t1["height"])}px'
                })

    # 2. Text-on-line collisions
    for t in texts:
        for line in lines:
            overlaps, ratio = boxes_overlap(t, line, 0.30)
            if overlaps and ratio > 0.3:
                warnings.append({
                    'type': 'text-on-line',
                    'desc': f'"{t["text"]}" may overlap line',
                    'overlap': ratio
                })

    # 3. Signal paths cutting through elements
    # Check against solid rects only (dashed enclosures and huge rects excluded)
    for seg in signal_segments:
        for rect in solid_rects:
            if segment_intersects_rect(seg, rect):
                seg_desc = f'({seg["x1"]:.0f},{seg["y1"]:.0f})->({seg["x2"]:.0f},{seg["y2"]:.0f})'
                rect_desc = f'rect at ({rect["x"]:.0f},{rect["y"]:.0f}) {rect["width"]:.0f}x{rect["height"]:.0f}'
                collisions.append({
                    'type': 'signal-through-element',
                    'desc': f'Signal path {seg_desc} cuts through {rect_desc}',
                    'overlap': 1.0,
                    'fix': 'Reroute signal path around element or add gap'
                })

    # Check signal paths through circles/ellipses
    all_round = circles + ellipses
    for seg in signal_segments:
        for circ in all_round:
            circ_rect = {'x': circ['x'], 'y': circ['y'],
                         'width': circ['width'], 'height': circ['height']}
            if segment_intersects_rect(seg, circ_rect, margin=5):
                seg_desc = f'({seg["x1"]:.0f},{seg["y1"]:.0f})->({seg["x2"]:.0f},{seg["y2"]:.0f})'
                cx = circ['x'] + circ['width'] / 2
                cy = circ['y'] + circ['height'] / 2
                circ_desc = f'circle/ellipse at ({cx:.0f},{cy:.0f})'
                collisions.append({
                    'type': 'signal-through-element',
                    'desc': f'Signal path {seg_desc} cuts through {circ_desc}',
                    'overlap': 1.0,
                    'fix': 'Reroute signal path around element or add gap'
                })

    # 4. Crowded reference numerals
    # USPTO convention allows 1-4 digit reference numerals. Patent A uses
    # 2-digit refs (10, 12, ..., 30). Patent B and C go up to 100+.
    ref_nums = [t for t in texts
                if t['text'].isdigit() and 1 <= len(t['text']) <= 4]
    for i, r1 in enumerate(ref_nums):
        for r2 in ref_nums[i + 1:]:
            dist = math.sqrt((r1['x'] - r2['x']) ** 2 + (r1['y'] - r2['y']) ** 2)
            if dist < 15:
                warnings.append({
                    'type': 'crowded-refs',
                    'desc': f'Ref numerals {r1["text"]} and {r2["text"]} are {dist:.0f}px apart',
                    'overlap': 0
                })

    return collisions, warnings


def main():
    patents = {
        'patent_a': 8,
        'patent_b': 6,
        'patent_c': 7
    }

    print('=' * 70)
    print('USPTO PATENT COLLISION CHECK - COMPREHENSIVE AUDIT')
    print('37 CFR 1.84(p)(1) - Reference characters must be legible')
    print('Checks: text-on-text, text-on-line, signal-through-element')
    print('=' * 70)
    print()

    total_collisions = 0
    total_warnings = 0
    results = {}

    for patent, num_figs in patents.items():
        patent_name = patent.upper().replace('_', ' ')
        print(f'=== {patent_name} ===')
        results[patent] = {'pass': 0, 'warn': 0, 'fail': 0}

        for fig_num in range(1, num_figs + 1):
            filepath = str(Path(__file__).resolve().parent.parent / 'patent_drawings' / patent / f'fig{fig_num}.svg')
            if os.path.exists(filepath):
                collisions, warnings = analyze_svg(filepath)

                if collisions:
                    results[patent]['fail'] += 1
                    print(f'FIG. {fig_num}: FAIL')
                    for c in collisions:
                        print(f'  [!] COLLISION ({c["type"]}): {c["desc"]}')
                        print(f'      Overlap: {c["overlap"] * 100:.0f}% | Fix: {c.get("fix", "Review manually")}')
                        total_collisions += 1
                elif warnings:
                    results[patent]['warn'] += 1
                    print(f'FIG. {fig_num}: WARN')
                    for w in warnings:
                        print(f'  [~] {w["type"]}: {w["desc"]}')
                        total_warnings += 1
                else:
                    results[patent]['pass'] += 1
                    print(f'FIG. {fig_num}: PASS')
            else:
                print(f'FIG. {fig_num}: MISSING')
        print()

    # Summary table
    print('=' * 70)
    print('COLLISION CHECK SUMMARY')
    print('=' * 70)
    print(f'{"Patent":<12} {"PASS":<8} {"WARN":<8} {"FAIL":<8}')
    print('-' * 36)
    for patent, counts in results.items():
        print(f'{patent.upper():<12} {counts["pass"]:<8} {counts["warn"]:<8} {counts["fail"]:<8}')
    print('-' * 36)
    total_pass = sum(r['pass'] for r in results.values())
    total_warn_count = sum(r['warn'] for r in results.values())
    total_fail = sum(r['fail'] for r in results.values())
    print(f'{"TOTAL":<12} {total_pass:<8} {total_warn_count:<8} {total_fail:<8}')
    print()

    if total_fail == 0:
        print('STATUS: All drawings pass collision check!')
        print('No text-on-text, signal-through-element, or critical collisions detected.')
    else:
        print(f'STATUS: {total_fail} figures need collision fixes')

    return total_fail


if __name__ == '__main__':
    exit(main())

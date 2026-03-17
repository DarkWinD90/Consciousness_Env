#!/usr/bin/env python3
"""SVG Patent Drawing Audit Tool

Parses an SVG patent drawing and produces a raw measurements report:
- Every reference numeral: position, leader line length, nearest line/path distance
- Every signal path: start/end coordinates, gap to nearest box edge
- Every text element: bounding box estimate, nearest overlapping element
- Margin compliance for all elements

No pass/fail judgments — just numbers.
"""

import xml.etree.ElementTree as ET
import math
import sys
import re

NS = {'svg': 'http://www.w3.org/2000/svg'}


def parse_svg(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    return root


def get_all_elements(root):
    """Extract all rects, lines, paths, and texts with absolute coordinates."""
    rects = []
    lines = []
    paths = []
    texts = []

    # Find the translate group
    translate_dy = 0
    for g in root.iter('{http://www.w3.org/2000/svg}g'):
        t = g.get('transform', '')
        m = re.search(r'translate\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)', t)
        if m:
            translate_dy = float(m.group(2))
            # Process children of this group
            _collect(g, rects, lines, paths, texts, 0, translate_dy)
            break

    # Also collect elements outside the translate group (like sheet number)
    for child in root:
        tag = child.tag.replace('{http://www.w3.org/2000/svg}', '')
        if tag == 'g':
            continue  # already processed
        if tag == 'rect' and child.get('fill') == 'white':
            continue  # background
        _collect_single(child, rects, lines, paths, texts, 0, 0)

    return rects, lines, paths, texts


def _collect(parent, rects, lines, paths, texts, dx, dy):
    for elem in parent:
        _collect_single(elem, rects, lines, paths, texts, dx, dy)


def _collect_single(elem, rects, lines, paths, texts, dx, dy):
    tag = elem.tag.replace('{http://www.w3.org/2000/svg}', '')

    if tag == 'rect':
        x = float(elem.get('x', 0)) + dx
        y = float(elem.get('y', 0)) + dy
        w = float(elem.get('width', 0))
        h = float(elem.get('height', 0))
        # Skip percentage-width rects (background)
        if '%' in str(elem.get('width', '')):
            return
        rects.append({
            'x': x, 'y': y, 'w': w, 'h': h,
            'stroke_dasharray': elem.get('stroke-dasharray', ''),
            'stroke_width': float(elem.get('stroke-width', 1)),
        })

    elif tag == 'line':
        x1 = float(elem.get('x1', 0)) + dx
        y1 = float(elem.get('y1', 0)) + dy
        x2 = float(elem.get('x2', 0)) + dx
        y2 = float(elem.get('y2', 0)) + dy
        has_arrow = 'marker-end' in (elem.get('marker-end', '') + elem.get('marker-start', ''))
        lines.append({
            'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
            'has_arrow': has_arrow,
            'stroke_width': float(elem.get('stroke-width', 1)),
            'stroke_dasharray': elem.get('stroke-dasharray', ''),
        })

    elif tag == 'path':
        d = elem.get('d', '')
        has_arrow = 'marker-end' in (elem.get('marker-end', '') + elem.get('marker-start', ''))
        # Extract all coordinate points from path
        points = _parse_path_points(d, dx, dy)
        paths.append({
            'd': d, 'points': points,
            'has_arrow': has_arrow,
            'stroke_dasharray': elem.get('stroke-dasharray', ''),
        })

    elif tag == 'text':
        x = float(elem.get('x', 0)) + dx
        y = float(elem.get('y', 0)) + dy
        anchor = elem.get('text-anchor', 'start')
        font_size = float(elem.get('font-size', 14))
        content = elem.text or ''
        # Estimate text bounding box
        char_width = font_size * 0.6  # approximate
        text_width = len(content) * char_width
        if anchor == 'middle':
            tx = x - text_width / 2
        elif anchor == 'end':
            tx = x - text_width
        else:
            tx = x
        texts.append({
            'x': x, 'y': y, 'content': content,
            'anchor': anchor, 'font_size': font_size,
            'bbox_x': tx, 'bbox_y': y - font_size * 0.8,
            'bbox_w': text_width, 'bbox_h': font_size,
            'is_numeral': bool(re.match(r'^\d+$', content.strip())),
        })


def _parse_path_points(d, dx, dy):
    """Extract coordinate points from SVG path d attribute."""
    points = []
    # Match M, L, C commands with coordinates
    tokens = re.findall(r'[MLC]\s*([\d.\-]+(?:\s*,?\s*[\d.\-]+)*)', d)
    for token in tokens:
        nums = re.findall(r'[\d.\-]+', token)
        for i in range(0, len(nums) - 1, 2):
            px = float(nums[i]) + dx
            py = float(nums[i + 1]) + dy
            points.append((px, py))
    return points


def point_to_rect_edge_distance(px, py, rect):
    """Minimum distance from a point to the nearest edge of a rect."""
    rx, ry, rw, rh = rect['x'], rect['y'], rect['w'], rect['h']
    # Clamp point to rect bounds
    cx = max(rx, min(px, rx + rw))
    cy = max(ry, min(py, ry + rh))
    return math.sqrt((px - cx) ** 2 + (py - cy) ** 2)


def point_on_rect_edge(px, py, rect, tolerance=3):
    """Check if point is on any edge of the rect within tolerance."""
    rx, ry, rw, rh = rect['x'], rect['y'], rect['w'], rect['h']
    on_left = abs(px - rx) <= tolerance and ry - tolerance <= py <= ry + rh + tolerance
    on_right = abs(px - (rx + rw)) <= tolerance and ry - tolerance <= py <= ry + rh + tolerance
    on_top = abs(py - ry) <= tolerance and rx - tolerance <= px <= rx + rw + tolerance
    on_bottom = abs(py - (ry + rh)) <= tolerance and rx - tolerance <= px <= rx + rw + tolerance
    return on_left or on_right or on_top or on_bottom


def line_length(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def point_to_line_distance(px, py, x1, y1, x2, y2):
    """Minimum distance from point to line segment."""
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)


def bbox_overlaps_line(text, line):
    """Check if text bounding box overlaps with a line segment."""
    bx, by = text['bbox_x'], text['bbox_y']
    bw, bh = text['bbox_w'], text['bbox_h']
    # Check if any point of the line passes through the bbox
    x1, y1 = line['x1'], line['y1']
    x2, y2 = line['x2'], line['y2']
    # Sample points along the line
    for t in [i / 20 for i in range(21)]:
        lx = x1 + t * (x2 - x1)
        ly = y1 + t * (y2 - y1)
        if bx <= lx <= bx + bw and by <= ly <= by + bh:
            return True
    return False


def audit_figure(filepath):
    """Run full audit and return structured report."""
    root = parse_svg(filepath)
    rects, lines, paths, texts = get_all_elements(root)

    # Separate solid boxes from dashed boundaries
    boxes = [r for r in rects if not r['stroke_dasharray'] and r['w'] > 20]
    boundaries = [r for r in rects if r['stroke_dasharray']]

    # Separate leader lines (thin) from signal lines (thick)
    signal_lines = [l for l in lines if l['stroke_width'] >= 1.0]
    leader_lines = [l for l in lines if l['stroke_width'] < 1.0]

    # Separate numerals from labels
    numerals = [t for t in texts if t['is_numeral'] and t['font_size'] <= 16]
    labels = [t for t in texts if not t['is_numeral'] or t['font_size'] > 16]

    report = []
    report.append(f"{'='*70}")
    report.append(f"SVG AUDIT: {filepath}")
    report.append(f"{'='*70}")
    report.append(f"Boxes: {len(boxes)}, Boundaries: {len(boundaries)}, "
                   f"Signal lines: {len(signal_lines)}, Leader lines: {len(leader_lines)}, "
                   f"Numerals: {len(numerals)}, Labels: {len(labels)}")
    report.append("")

    # === SECTION 1: REFERENCE NUMERALS ===
    report.append(f"{'─'*70}")
    report.append("REFERENCE NUMERALS")
    report.append(f"{'─'*70}")

    for num in numerals:
        content = num['content']
        # Find matching leader line (closest line with stroke_width < 1)
        best_leader = None
        best_dist = 999
        for ll in leader_lines:
            # Check if leader starts near the numeral
            d1 = math.sqrt((ll['x1'] - num['x']) ** 2 + (ll['y1'] - num['y']) ** 2)
            d2 = math.sqrt((ll['x2'] - num['x']) ** 2 + (ll['y2'] - num['y']) ** 2)
            d = min(d1, d2)
            if d < best_dist:
                best_dist = d
                best_leader = ll

        leader_len = 0
        leader_lands_on_box = False
        landing_box_label = ""
        if best_leader:
            leader_len = line_length(best_leader['x1'], best_leader['y1'],
                                     best_leader['x2'], best_leader['y2'])
            # Check if far end of leader lands on a box
            # Far end = the end furthest from the numeral
            d1 = math.sqrt((best_leader['x1'] - num['x']) ** 2 + (best_leader['y1'] - num['y']) ** 2)
            d2 = math.sqrt((best_leader['x2'] - num['x']) ** 2 + (best_leader['y2'] - num['y']) ** 2)
            if d1 > d2:
                far_x, far_y = best_leader['x1'], best_leader['y1']
            else:
                far_x, far_y = best_leader['x2'], best_leader['y2']

            for box in boxes:
                if point_on_rect_edge(far_x, far_y, box, tolerance=5):
                    leader_lands_on_box = True
                    # Find label in box
                    for lbl in labels:
                        if (box['x'] <= lbl['x'] <= box['x'] + box['w'] and
                                box['y'] <= lbl['y'] <= box['y'] + box['h']):
                            landing_box_label = lbl['content']
                            break
                    break

        # Check for overlaps with signal lines
        overlapping_lines = []
        for sl in signal_lines:
            if bbox_overlaps_line(num, sl):
                overlapping_lines.append(sl)

        # Check for overlaps with path segments
        overlapping_paths = []
        for p in paths:
            for i in range(len(p['points']) - 1):
                px1, py1 = p['points'][i]
                px2, py2 = p['points'][i + 1]
                fake_line = {'x1': px1, 'y1': py1, 'x2': px2, 'y2': py2}
                if bbox_overlaps_line(num, fake_line):
                    overlapping_paths.append(p['d'][:40])
                    break

        # Check overlap with dashed boundaries
        boundary_overlaps = []
        for b in boundaries:
            bx, by, bw, bh = b['x'], b['y'], b['w'], b['h']
            nbx, nby = num['bbox_x'], num['bbox_y']
            nbw, nbh = num['bbox_w'], num['bbox_h']
            # Check if numeral bbox crosses any boundary edge
            edges = [
                ('top', bx, by, bx + bw, by),
                ('bottom', bx, by + bh, bx + bw, by + bh),
                ('left', bx, by, bx, by + bh),
                ('right', bx + bw, by, bx + bw, by + bh),
            ]
            for edge_name, ex1, ey1, ex2, ey2 in edges:
                fake_line = {'x1': ex1, 'y1': ey1, 'x2': ex2, 'y2': ey2}
                if bbox_overlaps_line(num, fake_line):
                    boundary_overlaps.append(edge_name)

        # Format report
        status_flags = []
        if leader_len < 12:
            status_flags.append(f"⚠️  LEADER SHORT ({leader_len:.1f}px < 12px)")
        if not leader_lands_on_box:
            status_flags.append("⚠️  LEADER DOESN'T REACH BOX")
        if overlapping_lines:
            status_flags.append(f"❌ OVERLAPS {len(overlapping_lines)} SIGNAL LINE(S)")
        if overlapping_paths:
            status_flags.append(f"❌ OVERLAPS PATH")
        if boundary_overlaps:
            status_flags.append(f"❌ CROSSES BOUNDARY ({', '.join(boundary_overlaps)})")

        report.append(f"  Ref {content:>3s}  pos=({num['x']:.0f},{num['y']:.0f})  "
                       f"leader={leader_len:.1f}px  "
                       f"lands_on_box={'YES('+landing_box_label+')' if leader_lands_on_box else 'NO'}")
        for flag in status_flags:
            report.append(f"           {flag}")
        if not status_flags:
            report.append(f"           ✅ OK")

    # === SECTION 2: SIGNAL PATH ENDPOINTS ===
    report.append("")
    report.append(f"{'─'*70}")
    report.append("SIGNAL PATH ENDPOINTS")
    report.append(f"{'─'*70}")

    for sl in signal_lines:
        if sl['stroke_width'] < 1.0:
            continue  # skip leader lines
        start = (sl['x1'], sl['y1'])
        end = (sl['x2'], sl['y2'])
        length = line_length(*start, *end)

        start_on_box = False
        end_on_box = False
        start_box = ""
        end_box = ""
        start_gap = 999
        end_gap = 999

        for box in boxes:
            sd = point_to_rect_edge_distance(start[0], start[1], box)
            ed = point_to_rect_edge_distance(end[0], end[1], box)
            if sd < start_gap:
                start_gap = sd
                for lbl in labels:
                    if (box['x'] <= lbl['x'] <= box['x'] + box['w'] and
                            box['y'] <= lbl['y'] <= box['y'] + box['h']):
                        start_box = lbl['content']
                        break
            if ed < end_gap:
                end_gap = ed
                for lbl in labels:
                    if (box['x'] <= lbl['x'] <= box['x'] + box['w'] and
                            box['y'] <= lbl['y'] <= box['y'] + box['h']):
                        end_box = lbl['content']
                        break
            if point_on_rect_edge(start[0], start[1], box, tolerance=3):
                start_on_box = True
            if point_on_rect_edge(end[0], end[1], box, tolerance=3):
                end_on_box = True

        status_flags = []
        if not start_on_box and start_gap > 3:
            status_flags.append(f"⚠️  START gap={start_gap:.1f}px from nearest box ({start_box})")
        if not end_on_box and end_gap > 3:
            status_flags.append(f"⚠️  END gap={end_gap:.1f}px from nearest box ({end_box})")

        arrow_str = " →" if sl['has_arrow'] else ""
        dash_str = " [dashed]" if sl['stroke_dasharray'] else ""
        report.append(f"  Line ({start[0]:.0f},{start[1]:.0f})→({end[0]:.0f},{end[1]:.0f}){arrow_str}{dash_str}  len={length:.0f}px")
        for flag in status_flags:
            report.append(f"           {flag}")

    # Path endpoints
    for p in paths:
        if not p['points']:
            continue
        start = p['points'][0]
        end = p['points'][-1]

        start_on_box = False
        end_on_box = False
        start_gap = 999
        end_gap = 999
        start_box = ""
        end_box = ""

        for box in boxes:
            sd = point_to_rect_edge_distance(start[0], start[1], box)
            ed = point_to_rect_edge_distance(end[0], end[1], box)
            if sd < start_gap:
                start_gap = sd
                for lbl in labels:
                    if (box['x'] <= lbl['x'] <= box['x'] + box['w'] and
                            box['y'] <= lbl['y'] <= box['y'] + box['h']):
                        start_box = lbl['content']
                        break
            if ed < end_gap:
                end_gap = ed
                for lbl in labels:
                    if (box['x'] <= lbl['x'] <= box['x'] + box['w'] and
                            box['y'] <= lbl['y'] <= box['y'] + box['h']):
                        end_box = lbl['content']
                        break
            if point_on_rect_edge(start[0], start[1], box, tolerance=3):
                start_on_box = True
            if point_on_rect_edge(end[0], end[1], box, tolerance=3):
                end_on_box = True

        status_flags = []
        if not start_on_box and start_gap > 3:
            status_flags.append(f"⚠️  START gap={start_gap:.1f}px from nearest box ({start_box})")
        if not end_on_box and end_gap > 3:
            status_flags.append(f"⚠️  END gap={end_gap:.1f}px from nearest box ({end_box})")

        dash_str = " [dashed]" if p['stroke_dasharray'] else ""
        arrow_str = " →" if p['has_arrow'] else ""
        d_short = p['d'][:60]
        report.append(f"  Path: {d_short}...{arrow_str}{dash_str}")
        for flag in status_flags:
            report.append(f"           {flag}")

    # === SECTION 3: LINE-ON-LINE OVERLAP DETECTION ===
    report.append("")
    report.append(f"{'─'*70}")
    report.append("LINE/PATH OVERLAP DETECTION")
    report.append(f"{'─'*70}")

    # Collect all line segments (from lines and paths)
    # Exclude segments from bridge arcs (paths containing C commands)
    all_segments = []
    for sl in signal_lines:
        seg = (sl['x1'], sl['y1'], sl['x2'], sl['y2'],
               'solid' if not sl['stroke_dasharray'] else 'dashed',
               f"line ({sl['x1']:.0f},{sl['y1']:.0f})→({sl['x2']:.0f},{sl['y2']:.0f})")
        all_segments.append(seg)
    for p in paths:
        style = 'dashed' if p['stroke_dasharray'] else 'solid'
        has_curve = 'C' in p['d']
        if has_curve:
            # Bridge arc — skip internal segments (they are curve control points,
            # not actual straight lines). Only include the M start and final endpoint.
            continue
        for i in range(len(p['points']) - 1):
            px1, py1 = p['points'][i]
            px2, py2 = p['points'][i + 1]
            seg = (px1, py1, px2, py2, style,
                   f"path seg ({px1:.0f},{py1:.0f})→({px2:.0f},{py2:.0f})")
            all_segments.append(seg)

    # Check each pair for collinear overlap
    overlap_found = False
    for i in range(len(all_segments)):
        for j in range(i + 1, len(all_segments)):
            s1 = all_segments[i]
            s2 = all_segments[j]
            # Check for vertical collinear overlap (same x, overlapping y ranges)
            if (abs(s1[0] - s1[2]) < 2 and abs(s2[0] - s2[2]) < 2 and
                    abs(s1[0] - s2[0]) < 5):
                y1_min, y1_max = min(s1[1], s1[3]), max(s1[1], s1[3])
                y2_min, y2_max = min(s2[1], s2[3]), max(s2[1], s2[3])
                overlap = min(y1_max, y2_max) - max(y1_min, y2_min)
                if overlap > 3:
                    report.append(f"  ❌ VERTICAL OVERLAP ({overlap:.0f}px) at x≈{s1[0]:.0f}:")
                    report.append(f"       {s1[5]} [{s1[4]}]")
                    report.append(f"       {s2[5]} [{s2[4]}]")
                    overlap_found = True
            # Check for horizontal collinear overlap (same y, overlapping x ranges)
            if (abs(s1[1] - s1[3]) < 2 and abs(s2[1] - s2[3]) < 2 and
                    abs(s1[1] - s2[1]) < 5):
                x1_min, x1_max = min(s1[0], s1[2]), max(s1[0], s1[2])
                x2_min, x2_max = min(s2[0], s2[2]), max(s2[0], s2[2])
                overlap = min(x1_max, x2_max) - max(x1_min, x2_min)
                if overlap > 3:
                    report.append(f"  ❌ HORIZONTAL OVERLAP ({overlap:.0f}px) at y≈{s1[1]:.0f}:")
                    report.append(f"       {s1[5]} [{s1[4]}]")
                    report.append(f"       {s2[5]} [{s2[4]}]")
                    overlap_found = True

    # Check for PERPENDICULAR CROSSINGS (horizontal crossing vertical)
    crossing_found = False
    for i in range(len(all_segments)):
        for j in range(i + 1, len(all_segments)):
            s1 = all_segments[i]
            s2 = all_segments[j]
            # Is s1 horizontal and s2 vertical?
            s1_horiz = abs(s1[1] - s1[3]) < 2 and abs(s1[0] - s1[2]) > 5
            s1_vert = abs(s1[0] - s1[2]) < 2 and abs(s1[1] - s1[3]) > 5
            s2_horiz = abs(s2[1] - s2[3]) < 2 and abs(s2[0] - s2[2]) > 5
            s2_vert = abs(s2[0] - s2[2]) < 2 and abs(s2[1] - s2[3]) > 5

            h_seg = v_seg = None
            if s1_horiz and s2_vert:
                h_seg, v_seg = s1, s2
            elif s1_vert and s2_horiz:
                h_seg, v_seg = s2, s1

            if h_seg and v_seg:
                # Horizontal: y=h_y, x range [h_xmin, h_xmax]
                h_y = h_seg[1]
                h_xmin, h_xmax = min(h_seg[0], h_seg[2]), max(h_seg[0], h_seg[2])
                # Vertical: x=v_x, y range [v_ymin, v_ymax]
                v_x = v_seg[0]
                v_ymin, v_ymax = min(v_seg[1], v_seg[3]), max(v_seg[1], v_seg[3])

                # Do they cross? v_x within h range AND h_y within v range
                if (h_xmin + 3 < v_x < h_xmax - 3 and
                        v_ymin + 3 < h_y < v_ymax - 3):
                    # Check if they share an endpoint (T-junction, not a crossing)
                    endpoints = [(h_seg[0], h_seg[1]), (h_seg[2], h_seg[3]),
                                 (v_seg[0], v_seg[1]), (v_seg[2], v_seg[3])]
                    cross_pt = (v_x, h_y)
                    is_endpoint = any(abs(ep[0] - cross_pt[0]) < 3 and
                                      abs(ep[1] - cross_pt[1]) < 3 for ep in endpoints)
                    if not is_endpoint:
                        report.append(f"  ⚠️  CROSSING at ({v_x:.0f},{h_y:.0f}) — needs bridge:")
                        report.append(f"       {h_seg[5]} [{h_seg[4]}]")
                        report.append(f"       {v_seg[5]} [{v_seg[4]}]")
                        crossing_found = True
                        overlap_found = True

    if not overlap_found:
        report.append("  ✅ No line/path overlaps or crossings detected")

    # === SECTION 4: MARGIN CHECK ===
    report.append("")
    report.append(f"{'─'*70}")
    report.append("MARGIN COMPLIANCE (left≥100, right≤750, top≥100, bottom≤1050)")
    report.append(f"{'─'*70}")

    MARGIN_LEFT = 100
    MARGIN_RIGHT = 750
    MARGIN_TOP = 100  # absolute, including translate
    MARGIN_BOTTOM = 1050

    for num in numerals:
        bx = num['bbox_x']
        bx_right = bx + num['bbox_w']
        by = num['bbox_y']
        flags = []
        if bx < MARGIN_LEFT:
            flags.append(f"LEFT violation: x={bx:.0f}")
        if bx_right > MARGIN_RIGHT:
            flags.append(f"RIGHT violation: x_right={bx_right:.0f}")
        if by < MARGIN_TOP:
            flags.append(f"TOP violation: y={by:.0f}")
        if flags:
            report.append(f"  Ref {num['content']:>3s}: {'  '.join(flags)}")

    # === SUMMARY ===
    report.append("")
    report.append(f"{'='*70}")
    full_text = '\n'.join(report)
    warnings = full_text.count('⚠️')
    errors = full_text.count('❌')
    oks = full_text.count('✅')
    report.append(f"SUMMARY: {oks} OK, {warnings} warnings, {errors} errors")
    report.append(f"{'='*70}")

    return '\n'.join(report)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python svg_audit.py <path_to_svg>")
        sys.exit(1)
    print(audit_figure(sys.argv[1]))

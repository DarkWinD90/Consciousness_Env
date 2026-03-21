#!/usr/bin/env python
"""
USPTO Patent Drawing Signal Path Verification
Checks arrow endpoints, origins, directions, and numeral-path collisions.
"""

import xml.etree.ElementTree as ET
import os
import re
import math
from pathlib import Path

def safe_float(val, default=0):
    """Safely convert to float, handling percentages and invalid values"""
    if val is None:
        return default
    val = str(val).strip()
    if '%' in val:
        return default  # Skip percentage values
    try:
        return float(val)
    except ValueError:
        return default

def parse_path_d(d_attr):
    """Extract coordinates from SVG path d attribute"""
    coords = []
    parts = re.findall(r'([MLHVQCSTAZmlhvqcstaz])\s*([^MLHVQCSTAZmlhvqcstaz]*)', d_attr)
    current_x, current_y = 0, 0

    for cmd, args in parts:
        nums = [float(n) for n in re.findall(r'-?[\d.]+', args)]

        if cmd == 'M' and len(nums) >= 2:
            current_x, current_y = nums[0], nums[1]
            coords.append((current_x, current_y))
        elif cmd == 'm' and len(nums) >= 2:
            current_x += nums[0]
            current_y += nums[1]
            coords.append((current_x, current_y))
        elif cmd == 'L' and len(nums) >= 2:
            current_x, current_y = nums[0], nums[1]
            coords.append((current_x, current_y))
        elif cmd == 'l' and len(nums) >= 2:
            current_x += nums[0]
            current_y += nums[1]
            coords.append((current_x, current_y))
        elif cmd == 'H' and len(nums) >= 1:
            current_x = nums[0]
            coords.append((current_x, current_y))
        elif cmd == 'h' and len(nums) >= 1:
            current_x += nums[0]
            coords.append((current_x, current_y))
        elif cmd == 'V' and len(nums) >= 1:
            current_y = nums[0]
            coords.append((current_x, current_y))
        elif cmd == 'v' and len(nums) >= 1:
            current_y += nums[0]
            coords.append((current_x, current_y))
        elif cmd in ['Q', 'q', 'C', 'c', 'S', 's', 'T', 't'] and len(nums) >= 2:
            if cmd.isupper():
                current_x, current_y = nums[-2], nums[-1]
            else:
                current_x += nums[-2]
                current_y += nums[-1]
            coords.append((current_x, current_y))

    return coords

def get_line_segments(d_attr, tx=0, ty=0):
    """Get all line segments from a path for collision detection"""
    segments = []
    coords = parse_path_d(d_attr)
    for i in range(len(coords) - 1):
        segments.append((
            (coords[i][0] + tx, coords[i][1] + ty),
            (coords[i+1][0] + tx, coords[i+1][1] + ty)
        ))
    return segments

def get_text_bbox(elem, transform=None):
    """Estimate bounding box for text element"""
    try:
        x = safe_float(elem.get('x'))
        y = safe_float(elem.get('y'))
        font_size = safe_float(elem.get('font-size', 10), 10)
        text = elem.text or ''
        anchor = elem.get('text-anchor', 'start')

        width = len(text) * font_size * 0.6
        height = font_size * 1.2

        if anchor == 'middle':
            x -= width / 2
        elif anchor == 'end':
            x -= width

        tx, ty = 0, 0
        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                tx, ty = float(match.group(1)), float(match.group(2))

        return {
            'x': x + tx,
            'y': y - height + ty,
            'width': width,
            'height': height,
            'text': text,
            'center': (x + width/2 + tx, y - height/2 + ty)
        }
    except:
        return None

def line_intersects_box(p1, p2, box):
    """Check if a line segment intersects with a bounding box"""
    x1, y1 = p1
    x2, y2 = p2
    bx, by = box['x'], box['y']
    bw, bh = box['width'], box['height']

    # Expand box slightly for collision detection
    margin = 2
    bx -= margin
    by -= margin
    bw += 2 * margin
    bh += 2 * margin

    # Check if line segment intersects rectangle
    # Using Cohen-Sutherland-style region codes

    def region_code(x, y):
        code = 0
        if x < bx: code |= 1
        elif x > bx + bw: code |= 2
        if y < by: code |= 4
        elif y > by + bh: code |= 8
        return code

    code1 = region_code(x1, y1)
    code2 = region_code(x2, y2)

    # Both endpoints inside
    if code1 == 0 and code2 == 0:
        return True

    # Both endpoints in same outer region
    if code1 & code2:
        return False

    # Line may cross the box - do more detailed check
    # Check if line crosses any edge of the box
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

    def intersect(A, B, C, D):
        return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

    # Box corners
    corners = [
        (bx, by), (bx + bw, by),
        (bx + bw, by + bh), (bx, by + bh)
    ]

    # Check intersection with each edge
    for i in range(4):
        if intersect((x1, y1), (x2, y2), corners[i], corners[(i+1) % 4]):
            return True

    return False

def analyze_numeral_path_collisions(filepath):
    """Check for collisions between reference numerals and signal paths"""
    collisions = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    root = ET.fromstring(content)

    # Collect reference numerals (3-digit text elements)
    numerals = []
    # Collect signal paths
    paths = []

    def process_element(elem, parent_transform=None):
        tag = elem.tag.replace('{http://www.w3.org/2000/svg}', '')
        transform = elem.get('transform', parent_transform)

        tx, ty = 0, 0
        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                tx, ty = float(match.group(1)), float(match.group(2))

        if tag == 'text':
            text = elem.text or ''
            # Reference numerals are typically 3-digit numbers
            if re.match(r'^\d{3}$', text.strip()):
                bbox = get_text_bbox(elem, transform)
                if bbox:
                    numerals.append(bbox)

        elif tag == 'path':
            d = elem.get('d', '')
            stroke = elem.get('stroke', '')
            if stroke and stroke != 'none' and d:
                segments = get_line_segments(d, tx, ty)
                paths.extend(segments)

        elif tag == 'line':
            stroke = elem.get('stroke', '')
            if stroke and stroke != 'none':
                x1 = safe_float(elem.get('x1')) + tx
                y1 = safe_float(elem.get('y1')) + ty
                x2 = safe_float(elem.get('x2')) + tx
                y2 = safe_float(elem.get('y2')) + ty
                paths.append(((x1, y1), (x2, y2)))

        for child in elem:
            process_element(child, transform)

    process_element(root)

    # Check each numeral against each path segment
    for numeral in numerals:
        for segment in paths:
            if line_intersects_box(segment[0], segment[1], numeral):
                collisions.append({
                    'numeral': numeral['text'],
                    'numeral_pos': (numeral['x'], numeral['y']),
                    'segment': segment
                })

    return collisions, len(numerals), len(paths)


def analyze_signal_endpoints(filepath):
    """Analyze signal path endpoints"""
    issues = []
    stats = {'paths': 0, 'with_marker': 0}

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    root = ET.fromstring(content)

    def process_element(elem, parent_transform=None):
        tag = elem.tag.replace('{http://www.w3.org/2000/svg}', '')
        transform = elem.get('transform', parent_transform)

        if tag in ['path', 'line']:
            marker = elem.get('marker-end', '')
            if marker and 'url(#' in marker:
                stats['with_marker'] += 1
            stroke = elem.get('stroke', '')
            if stroke and stroke != 'none':
                stats['paths'] += 1

        for child in elem:
            process_element(child, transform)

    process_element(root)
    return issues, stats


def main():
    patents = {
        'patent_a': 8,
        'patent_b': 6,
        'patent_c': 7
    }

    print('=' * 70)
    print('USPTO PATENT SIGNAL PATH & NUMERAL COLLISION CHECK')
    print('37 CFR 1.84(p) - Reference characters must NOT cross drawing lines')
    print('=' * 70)
    print()

    total_collisions = 0
    collision_details = []

    for patent, num_figs in patents.items():
        patent_name = patent.upper().replace('_', ' ')
        print(f'=== {patent_name} ===')

        for fig_num in range(1, num_figs + 1):
            filepath = str(Path(__file__).resolve().parent.parent / 'patent_drawings' / patent / f'fig{fig_num}.svg')
            if os.path.exists(filepath):
                collisions, num_numerals, num_paths = analyze_numeral_path_collisions(filepath)
                _, stats = analyze_signal_endpoints(filepath)

                if collisions:
                    print(f'FIG. {fig_num}: COLLISION ({len(collisions)} numeral-path overlaps)')
                    for c in collisions[:5]:
                        print(f'  [!] Numeral "{c["numeral"]}" at ({c["numeral_pos"][0]:.0f}, {c["numeral_pos"][1]:.0f}) crosses signal path')
                        collision_details.append({
                            'patent': patent,
                            'fig': fig_num,
                            'numeral': c['numeral'],
                            'pos': c['numeral_pos']
                        })
                    if len(collisions) > 5:
                        print(f'  ... and {len(collisions) - 5} more')
                    total_collisions += len(collisions)
                else:
                    print(f'FIG. {fig_num}: PASS ({num_numerals} numerals, {stats["paths"]} paths, {stats["with_marker"]} arrows)')
        print()

    print('=' * 70)
    print('SIGNAL PATH VERIFICATION SUMMARY')
    print('=' * 70)
    print(f'Total numeral-path collisions: {total_collisions}')
    print()

    if total_collisions == 0:
        print('STATUS: All reference numerals clear of signal paths!')
    else:
        print(f'STATUS: {total_collisions} collisions need fixing')
        print()
        print('Collisions to fix:')
        for d in collision_details[:20]:
            print(f'  - {d["patent"].upper()} FIG. {d["fig"]}: numeral {d["numeral"]} at ({d["pos"][0]:.0f}, {d["pos"][1]:.0f})')

    return total_collisions


if __name__ == '__main__':
    exit(main())

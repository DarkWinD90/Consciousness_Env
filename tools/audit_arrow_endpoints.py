#!/usr/bin/env python
"""
Comprehensive audit of arrow endpoints in USPTO patent drawings.
Identifies arrows that don't land at their target element boundaries.
"""

import xml.etree.ElementTree as ET
import os
import re


def safe_float(val, default=0):
    """Safely convert a value to float, handling percentages and None."""
    if val is None:
        return default
    val = str(val).strip()
    if '%' in val:
        return default
    try:
        return float(val)
    except ValueError:
        return default


def parse_path_commands(d_attr):
    """Parse SVG path d attribute into absolute coordinates."""
    coords = []
    parts = re.findall(r'([MLHVQCSTAZmlhvqcstaz])([^MLHVQCSTAZmlhvqcstaz]*)', d_attr)
    current_x, current_y = 0, 0
    start_x, start_y = 0, 0

    for cmd, args in parts:
        nums = [float(n) for n in re.findall(r'-?[\d.]+', args)]

        if cmd == 'M':
            if len(nums) >= 2:
                current_x, current_y = nums[0], nums[1]
                start_x, start_y = current_x, current_y
                coords.append(('M', current_x, current_y))
        elif cmd == 'm':
            if len(nums) >= 2:
                current_x += nums[0]
                current_y += nums[1]
                start_x, start_y = current_x, current_y
                coords.append(('M', current_x, current_y))
        elif cmd == 'L':
            if len(nums) >= 2:
                current_x, current_y = nums[0], nums[1]
                coords.append(('L', current_x, current_y))
        elif cmd == 'l':
            if len(nums) >= 2:
                current_x += nums[0]
                current_y += nums[1]
                coords.append(('L', current_x, current_y))
        elif cmd == 'H':
            if len(nums) >= 1:
                current_x = nums[0]
                coords.append(('H', current_x, current_y))
        elif cmd == 'h':
            if len(nums) >= 1:
                current_x += nums[0]
                coords.append(('H', current_x, current_y))
        elif cmd == 'V':
            if len(nums) >= 1:
                current_y = nums[0]
                coords.append(('V', current_x, current_y))
        elif cmd == 'v':
            if len(nums) >= 1:
                current_y += nums[0]
                coords.append(('V', current_x, current_y))
        elif cmd in ['Q', 'C', 'S', 'T']:
            if len(nums) >= 2:
                current_x, current_y = nums[-2], nums[-1]
                coords.append((cmd, current_x, current_y))
        elif cmd in ['q', 'c', 's', 't']:
            if len(nums) >= 2:
                current_x += nums[-2]
                current_y += nums[-1]
                coords.append((cmd.upper(), current_x, current_y))
        elif cmd == 'Z' or cmd == 'z':
            current_x, current_y = start_x, start_y
            coords.append(('Z', current_x, current_y))

    return coords


def get_path_endpoint(d_attr, tx=0, ty=0):
    """Get the endpoint of a path (where arrow would land)."""
    coords = parse_path_commands(d_attr)
    if coords:
        last = coords[-1]
        return (last[1] + tx, last[2] + ty)
    return None


def get_path_startpoint(d_attr, tx=0, ty=0):
    """Get the start point of a path."""
    coords = parse_path_commands(d_attr)
    if coords:
        first = coords[0]
        return (first[1] + tx, first[2] + ty)
    return None


def get_elements_with_bounds(root, ns=''):
    """Extract all elements with their bounding boxes."""
    elements = []

    def process_element(elem, parent_tx=0, parent_ty=0):
        tag = elem.tag.replace('{http://www.w3.org/2000/svg}', '')
        transform = elem.get('transform', '')

        tx, ty = parent_tx, parent_ty
        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                tx = parent_tx + float(match.group(1))
                ty = parent_ty + float(match.group(2))

        if tag == 'rect':
            x = safe_float(elem.get('x', 0)) + tx
            y = safe_float(elem.get('y', 0)) + ty
            w = safe_float(elem.get('width', 0))
            h = safe_float(elem.get('height', 0))
            elements.append({
                'type': 'rect',
                'x': x, 'y': y, 'width': w, 'height': h,
                'left': x, 'right': x + w, 'top': y, 'bottom': y + h
            })

        elif tag == 'circle':
            cx = safe_float(elem.get('cx', 0)) + tx
            cy = safe_float(elem.get('cy', 0)) + ty
            r = safe_float(elem.get('r', 0))
            elements.append({
                'type': 'circle',
                'cx': cx, 'cy': cy, 'r': r,
                'left': cx - r, 'right': cx + r, 'top': cy - r, 'bottom': cy + r
            })

        elif tag == 'ellipse':
            cx = safe_float(elem.get('cx', 0)) + tx
            cy = safe_float(elem.get('cy', 0)) + ty
            rx = safe_float(elem.get('rx', 0))
            ry = safe_float(elem.get('ry', 0))
            elements.append({
                'type': 'ellipse',
                'cx': cx, 'cy': cy, 'rx': rx, 'ry': ry,
                'left': cx - rx, 'right': cx + rx, 'top': cy - ry, 'bottom': cy + ry
            })

        for child in elem:
            process_element(child, tx, ty)

    process_element(root)
    return elements


def find_nearest_element(point, elements, tolerance=15):
    """Find the nearest element to a point."""
    px, py = point
    best_dist = float('inf')
    best_elem = None

    for elem in elements:
        # Check distance to element edges
        if elem['type'] in ['rect', 'circle', 'ellipse']:
            # Distance to left edge
            if elem['top'] <= py <= elem['bottom']:
                d = abs(px - elem['left'])
                if d < best_dist:
                    best_dist = d
                    best_elem = elem
                d = abs(px - elem['right'])
                if d < best_dist:
                    best_dist = d
                    best_elem = elem

            # Distance to top/bottom edge
            if elem['left'] <= px <= elem['right']:
                d = abs(py - elem['top'])
                if d < best_dist:
                    best_dist = d
                    best_elem = elem
                d = abs(py - elem['bottom'])
                if d < best_dist:
                    best_dist = d
                    best_elem = elem

    return best_elem, best_dist


def analyze_arrows(filepath):
    """Analyze all arrows in an SVG file."""
    issues = []
    arrow_count = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    root = ET.fromstring(content)
    elements = get_elements_with_bounds(root)

    def process_element(elem, parent_tx=0, parent_ty=0):
        nonlocal arrow_count
        tag = elem.tag.replace('{http://www.w3.org/2000/svg}', '')
        transform = elem.get('transform', '')

        tx, ty = parent_tx, parent_ty
        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                tx = parent_tx + float(match.group(1))
                ty = parent_ty + float(match.group(2))

        marker_end = elem.get('marker-end', '')
        if 'url(#arrow)' in marker_end:
            arrow_count += 1

            if tag == 'path':
                d = elem.get('d', '')
                endpoint = get_path_endpoint(d, tx, ty)
                startpoint = get_path_startpoint(d, tx, ty)

                if endpoint:
                    nearest, dist = find_nearest_element(endpoint, elements)
                    if dist > 10:
                        issues.append({
                            'type': 'endpoint',
                            'point': endpoint,
                            'path': d,
                            'distance': dist,
                            'nearest_type': nearest['type'] if nearest else 'none'
                        })

            elif tag == 'line':
                x2 = safe_float(elem.get('x2', 0)) + tx
                y2 = safe_float(elem.get('y2', 0)) + ty
                endpoint = (x2, y2)

                nearest, dist = find_nearest_element(endpoint, elements)
                if dist > 10:
                    issues.append({
                        'type': 'endpoint',
                        'point': endpoint,
                        'element': 'line',
                        'distance': dist,
                        'nearest_type': nearest['type'] if nearest else 'none'
                    })

        for child in elem:
            process_element(child, tx, ty)

    process_element(root)
    return issues, arrow_count, len(elements)


def main():
    patents = {
        'patent_a': 8,
        'patent_b': 6,
        'patent_c': 7
    }

    print('=' * 70)
    print('USPTO PATENT ARROW ENDPOINT AUDIT')
    print('Checking that all arrows land at element boundaries')
    print('=' * 70)
    print()

    total_issues = 0
    all_issues = []

    for patent, num_figs in patents.items():
        patent_name = patent.upper().replace('_', ' ')
        print(f'=== {patent_name} ===')

        for fig_num in range(1, num_figs + 1):
            filepath = f'D:/Consciousness_Env/patent_drawings/{patent}/fig{fig_num}.svg'
            if os.path.exists(filepath):
                issues, arrow_count, elem_count = analyze_arrows(filepath)

                if issues:
                    print(f'FIG. {fig_num}: {len(issues)} ISSUES ({arrow_count} arrows, {elem_count} elements)')
                    for issue in issues[:5]:
                        pt = issue['point']
                        print(f'  [!] Arrow endpoint ({pt[0]:.0f}, {pt[1]:.0f}) - {issue["distance"]:.0f}px from nearest {issue["nearest_type"]}')
                        all_issues.append({
                            'patent': patent,
                            'fig': fig_num,
                            'issue': issue
                        })
                    if len(issues) > 5:
                        print(f'  ... and {len(issues) - 5} more')
                    total_issues += len(issues)
                else:
                    print(f'FIG. {fig_num}: PASS ({arrow_count} arrows land correctly)')

        print()

    print('=' * 70)
    print('ARROW ENDPOINT AUDIT SUMMARY')
    print('=' * 70)
    print(f'Total arrow endpoint issues: {total_issues}')
    print()

    if total_issues == 0:
        print('STATUS: All arrows land at element boundaries!')
    else:
        print(f'STATUS: {total_issues} arrows need endpoint adjustment')

    return total_issues


if __name__ == '__main__':
    exit(main())

#!/usr/bin/env python3
"""
Patent Drawing Collision Checker
Detects element collisions in USPTO patent SVG drawings.
"""

import xml.etree.ElementTree as ET
import re
import os
from pathlib import Path


def parse_transform(transform_str):
    """Extract translation from transform attribute."""
    if not transform_str:
        return 0, 0
    match = re.search(r'translate\s*\(\s*([\d.-]+)\s*,?\s*([\d.-]+)?\s*\)', transform_str)
    if match:
        tx = float(match.group(1))
        ty = float(match.group(2)) if match.group(2) else 0
        return tx, ty
    return 0, 0


def get_text_bbox(elem, parent_transform=(0, 0)):
    """Estimate bounding box for text element."""
    try:
        x = float(elem.get('x', 0))
        y = float(elem.get('y', 0))
        font_size = float(elem.get('font-size', 14))
        text = elem.text or ''

        # Apply parent transform
        x += parent_transform[0]
        y += parent_transform[1]

        # Estimate width based on character count (rough approximation)
        char_width = font_size * 0.6
        width = len(text) * char_width
        height = font_size

        # Handle text-anchor
        anchor = elem.get('text-anchor', 'start')
        if anchor == 'middle':
            x -= width / 2
        elif anchor == 'end':
            x -= width

        # Check for rotation transform on the element itself
        transform = elem.get('transform', '')
        rotate_match = re.search(r'rotate\s*\(\s*(-?[\d.]+)(?:\s*,?\s*([\d.]+)\s*,?\s*([\d.]+))?\s*\)', transform)
        if rotate_match:
            angle = float(rotate_match.group(1))
            # Get rotation center if specified
            cx = float(rotate_match.group(2)) if rotate_match.group(2) else x
            cy = float(rotate_match.group(3)) if rotate_match.group(3) else y

            # For 90 or -90 degree rotation, swap width and height and adjust position
            if abs(abs(angle) - 90) < 5:  # Allow small tolerance
                # Rotated text: position based on rotation center
                if angle > 0:  # rotate(90) - text goes down
                    x = cx - height / 2
                    y = cy
                else:  # rotate(-90) - text goes up
                    x = cx - height / 2
                    y = cy - width
                width, height = height, width

        # Height is approximately font-size, y is baseline
        top = y - font_size * 0.8  # Approximate ascender

        return {'type': 'text', 'text': text[:20], 'x': x, 'y': top, 'w': width, 'h': height}
    except (ValueError, TypeError):
        return None


def get_rect_bbox(elem, parent_transform=(0, 0)):
    """Get bounding box for rectangle."""
    try:
        x = float(elem.get('x', 0)) + parent_transform[0]
        y = float(elem.get('y', 0)) + parent_transform[1]
        w = float(elem.get('width', 0))
        h = float(elem.get('height', 0))
        return {'type': 'rect', 'x': x, 'y': y, 'w': w, 'h': h}
    except (ValueError, TypeError):
        return None


def get_circle_bbox(elem, parent_transform=(0, 0)):
    """Get bounding box for circle."""
    try:
        cx = float(elem.get('cx', 0)) + parent_transform[0]
        cy = float(elem.get('cy', 0)) + parent_transform[1]
        r = float(elem.get('r', 0))
        return {'type': 'circle', 'x': cx - r, 'y': cy - r, 'w': 2*r, 'h': 2*r}
    except (ValueError, TypeError):
        return None


def get_line_bbox(elem, parent_transform=(0, 0)):
    """Get bounding box for line with stroke buffer."""
    try:
        x1 = float(elem.get('x1', 0)) + parent_transform[0]
        y1 = float(elem.get('y1', 0)) + parent_transform[1]
        x2 = float(elem.get('x2', 0)) + parent_transform[0]
        y2 = float(elem.get('y2', 0)) + parent_transform[1]
        stroke_width = float(elem.get('stroke-width', 1))

        buffer = stroke_width + 2  # Add buffer for collision detection
        x = min(x1, x2) - buffer
        y = min(y1, y2) - buffer
        w = abs(x2 - x1) + 2 * buffer
        h = abs(y2 - y1) + 2 * buffer

        return {'type': 'line', 'x': x, 'y': y, 'w': w, 'h': h, 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
    except (ValueError, TypeError):
        return None


def get_polyline_bbox(elem, parent_transform=(0, 0)):
    """Get bounding box for polyline."""
    try:
        points_str = elem.get('points', '')
        if not points_str:
            return None

        # Parse points
        coords = re.findall(r'([\d.-]+)[,\s]+([\d.-]+)', points_str)
        if not coords:
            return None

        xs = [float(c[0]) + parent_transform[0] for c in coords]
        ys = [float(c[1]) + parent_transform[1] for c in coords]

        stroke_width = float(elem.get('stroke-width', 1))
        buffer = stroke_width + 2

        return {
            'type': 'polyline',
            'x': min(xs) - buffer,
            'y': min(ys) - buffer,
            'w': max(xs) - min(xs) + 2 * buffer,
            'h': max(ys) - min(ys) + 2 * buffer,
            'points': list(zip(xs, ys))
        }
    except (ValueError, TypeError):
        return None


def boxes_overlap(box1, box2, threshold=0.15):
    """Check if two bounding boxes overlap beyond threshold."""
    # Calculate intersection
    x_left = max(box1['x'], box2['x'])
    y_top = max(box1['y'], box2['y'])
    x_right = min(box1['x'] + box1['w'], box2['x'] + box2['w'])
    y_bottom = min(box1['y'] + box1['h'], box2['y'] + box2['h'])

    if x_right <= x_left or y_bottom <= y_top:
        return False, 0

    intersection = (x_right - x_left) * (y_bottom - y_top)
    area1 = box1['w'] * box1['h']
    area2 = box2['w'] * box2['h']
    smaller_area = min(area1, area2)

    if smaller_area <= 0:
        return False, 0

    overlap_ratio = intersection / smaller_area
    return overlap_ratio > threshold, overlap_ratio


def point_near_line(px, py, x1, y1, x2, y2, threshold=10):
    """Check if point is near a line segment."""
    # Vector from line start to point
    dx = x2 - x1
    dy = y2 - y1
    line_len_sq = dx*dx + dy*dy

    if line_len_sq == 0:
        return ((px - x1)**2 + (py - y1)**2) < threshold**2

    # Project point onto line
    t = max(0, min(1, ((px - x1)*dx + (py - y1)*dy) / line_len_sq))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy

    dist_sq = (px - proj_x)**2 + (py - proj_y)**2
    return dist_sq < threshold**2


def text_overlaps_line(text_box, line_box):
    """Check if text overlaps with a line."""
    if 'x1' not in line_box:
        return False, 0

    # Check if text center is near the line
    text_cx = text_box['x'] + text_box['w'] / 2
    text_cy = text_box['y'] + text_box['h'] / 2

    if point_near_line(text_cx, text_cy,
                       line_box['x1'], line_box['y1'],
                       line_box['x2'], line_box['y2'],
                       threshold=text_box['h']):
        return True, 0.5

    return False, 0


def check_svg_collisions(svg_path):
    """Check an SVG file for element collisions."""
    collisions = []

    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return [{'error': f'Parse error: {e}'}]

    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # Collect all elements with bounding boxes
    elements = []

    def process_element(elem, parent_transform=(0, 0)):
        # Check for group transform
        transform = elem.get('transform', '')
        tx, ty = parse_transform(transform)
        current_transform = (parent_transform[0] + tx, parent_transform[1] + ty)

        tag = elem.tag.replace('{http://www.w3.org/2000/svg}', '')

        if tag == 'text':
            bbox = get_text_bbox(elem, current_transform)
            if bbox and bbox.get('text'):
                elements.append(bbox)
        elif tag == 'rect':
            bbox = get_rect_bbox(elem, current_transform)
            if bbox and bbox['w'] > 0 and bbox['h'] > 0:
                elements.append(bbox)
        elif tag == 'circle':
            bbox = get_circle_bbox(elem, current_transform)
            if bbox:
                elements.append(bbox)
        elif tag == 'line':
            bbox = get_line_bbox(elem, current_transform)
            if bbox:
                elements.append(bbox)
        elif tag == 'polyline':
            bbox = get_polyline_bbox(elem, current_transform)
            if bbox:
                elements.append(bbox)

        # Process children
        for child in elem:
            process_element(child, current_transform)

    process_element(root)

    # Check for collisions
    texts = [e for e in elements if e['type'] == 'text']
    shapes = [e for e in elements if e['type'] in ('rect', 'circle')]
    lines = [e for e in elements if e['type'] in ('line', 'polyline')]

    # Text-on-text
    for i, t1 in enumerate(texts):
        for t2 in texts[i+1:]:
            overlaps, ratio = boxes_overlap(t1, t2, threshold=0.10)
            if overlaps:
                collisions.append({
                    'type': 'text-on-text',
                    'elem1': t1.get('text', '?'),
                    'elem2': t2.get('text', '?'),
                    'overlap': f'{ratio*100:.1f}%'
                })

    # Text-on-shape
    for t in texts:
        for s in shapes:
            overlaps, ratio = boxes_overlap(t, s, threshold=0.15)
            if overlaps:
                collisions.append({
                    'type': 'text-on-shape',
                    'elem1': t.get('text', '?'),
                    'elem2': f"{s['type']} at ({s['x']:.0f},{s['y']:.0f})",
                    'overlap': f'{ratio*100:.1f}%'
                })

    # Text-on-line
    for t in texts:
        for l in lines:
            overlaps, ratio = text_overlaps_line(t, l)
            if overlaps:
                collisions.append({
                    'type': 'text-on-line',
                    'elem1': t.get('text', '?'),
                    'elem2': f"{l['type']}",
                    'overlap': 'detected'
                })

    return collisions


def main():
    """Run collision check on all patent drawings."""
    base_path = Path(__file__).parent.parent / 'patent_drawings'

    patents = [
        ('patent_a', 8),
        ('patent_b', 6),
        ('patent_c', 7)
    ]

    total_collisions = 0

    for patent_dir, num_figs in patents:
        patent_path = base_path / patent_dir
        patent_letter = patent_dir[-1].upper()

        print(f"\n{'='*50}")
        print(f"PATENT {patent_letter}")
        print('='*50)

        for fig_num in range(1, num_figs + 1):
            svg_file = patent_path / f'fig{fig_num}.svg'

            if not svg_file.exists():
                print(f"\n[!] FIG. {fig_num}: FILE NOT FOUND")
                continue

            collisions = check_svg_collisions(svg_file)

            if collisions:
                print(f"\n=== FIG. {fig_num} ({svg_file.name}) ===")
                for c in collisions:
                    if 'error' in c:
                        print(f"  [ERROR] {c['error']}")
                    else:
                        print(f"  [!] COLLISION: {c['type']}")
                        print(f"      {c['elem1']} <-> {c['elem2']}")
                        print(f"      Overlap: {c['overlap']}")
                total_collisions += len(collisions)
            else:
                print(f"FIG. {fig_num}: PASS (0 collisions)")

    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print('='*50)
    print(f"Total figures checked: 21")
    print(f"Total collisions found: {total_collisions}")

    if total_collisions == 0:
        print("\n[OK] All drawings pass collision check")
    else:
        print(f"\n[!] {total_collisions} collision(s) need attention")


if __name__ == '__main__':
    main()

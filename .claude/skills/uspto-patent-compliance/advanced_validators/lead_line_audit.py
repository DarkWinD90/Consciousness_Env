#!/usr/bin/env python3
"""
Check 2: Lead Line Audit

Per 37 CFR 1.84(q), reference numerals must have lead lines
unless proximity to the element makes the association unambiguous.

This validator checks each reference numeral for:
1. A thin line (stroke-width <= 1.0) connecting to it, OR
2. Clear spatial proximity to a shape (within 50px)
"""

import xml.etree.ElementTree as ET
import re
import sys
import math
from pathlib import Path


# Constants
LEAD_LINE_MAX_STROKE = 1.0
PROXIMITY_THRESHOLD_PX = 50
NUMERAL_LINE_TOLERANCE = 20  # How close line endpoint must be to numeral

PATENTS = {
    'a': ('patent_a', 8),
    'b': ('patent_b', 6),
    'c': ('patent_c', 7),
}


def get_text_bbox(elem, parent_transform=(0, 0)):
    """Get bounding box for text element."""
    try:
        x = float(elem.get('x', 0)) + parent_transform[0]
        y = float(elem.get('y', 0)) + parent_transform[1]
        font_size = float(elem.get('font-size', 14))
        text = elem.text or ''

        char_width = font_size * 0.6
        width = len(text) * char_width
        height = font_size

        anchor = elem.get('text-anchor', 'start')
        if anchor == 'middle':
            x -= width / 2
        elif anchor == 'end':
            x -= width

        return {
            'x': x,
            'y': y - height * 0.8,
            'w': width,
            'h': height,
            'cx': x + width / 2,
            'cy': y - height * 0.4,
            'text': text
        }
    except (ValueError, TypeError):
        return None


def get_shape_bbox(elem, parent_transform=(0, 0)):
    """Get bounding box for shape element."""
    tag = elem.tag.split('}')[-1]

    try:
        if tag == 'rect':
            x = float(elem.get('x', 0)) + parent_transform[0]
            y = float(elem.get('y', 0)) + parent_transform[1]
            w = float(elem.get('width', 0))
            h = float(elem.get('height', 0))
            return {'type': 'rect', 'x': x, 'y': y, 'w': w, 'h': h}

        elif tag == 'circle':
            cx = float(elem.get('cx', 0)) + parent_transform[0]
            cy = float(elem.get('cy', 0)) + parent_transform[1]
            r = float(elem.get('r', 0))
            return {'type': 'circle', 'x': cx - r, 'y': cy - r, 'w': 2*r, 'h': 2*r}

        elif tag == 'ellipse':
            cx = float(elem.get('cx', 0)) + parent_transform[0]
            cy = float(elem.get('cy', 0)) + parent_transform[1]
            rx = float(elem.get('rx', 0))
            ry = float(elem.get('ry', 0))
            return {'type': 'ellipse', 'x': cx - rx, 'y': cy - ry, 'w': 2*rx, 'h': 2*ry}

        elif tag == 'polygon':
            points_str = elem.get('points', '')
            coords = re.findall(r'([\d.-]+)', points_str)
            if len(coords) >= 4:
                xs = [float(coords[i]) + parent_transform[0] for i in range(0, len(coords), 2)]
                ys = [float(coords[i]) + parent_transform[1] for i in range(1, len(coords), 2)]
                return {'type': 'polygon', 'x': min(xs), 'y': min(ys),
                        'w': max(xs) - min(xs), 'h': max(ys) - min(ys)}

    except (ValueError, TypeError):
        pass

    return None


def get_line_info(elem, parent_transform=(0, 0)):
    """Get line information including endpoints and stroke width."""
    tag = elem.tag.split('}')[-1]

    try:
        stroke_width = float(elem.get('stroke-width', 1))

        if tag == 'line':
            x1 = float(elem.get('x1', 0)) + parent_transform[0]
            y1 = float(elem.get('y1', 0)) + parent_transform[1]
            x2 = float(elem.get('x2', 0)) + parent_transform[0]
            y2 = float(elem.get('y2', 0)) + parent_transform[1]
            return {'type': 'line', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'stroke_width': stroke_width}

    except (ValueError, TypeError):
        pass

    return None


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


def distance_point_to_bbox(px, py, bbox):
    """Calculate minimum distance from point to bounding box edge."""
    x1, y1 = bbox['x'], bbox['y']
    x2, y2 = x1 + bbox['w'], y1 + bbox['h']

    # Clamp point to bbox
    cx = max(x1, min(px, x2))
    cy = max(y1, min(py, y2))

    return math.hypot(px - cx, py - cy)


def is_reference_numeral(text):
    """Check if text is a reference numeral (2-3 digit number)."""
    if not text:
        return False
    text = text.strip()
    return bool(re.match(r'^\d{2,3}$', text))


def point_near_text(px, py, text_bbox, tolerance):
    """Check if a point is near a text bounding box."""
    cx = text_bbox['cx']
    cy = text_bbox['cy']
    dist = math.hypot(px - cx, py - cy)
    return dist < tolerance


def check_lead_lines(svg_path):
    """Check if all reference numerals have lead lines or clear proximity."""
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return {'error': str(e)}

    numerals = []
    shapes = []
    thin_lines = []

    def process_element(elem, parent_transform=(0, 0)):
        transform = elem.get('transform', '')
        tx, ty = parse_transform(transform)
        current_transform = (parent_transform[0] + tx, parent_transform[1] + ty)

        tag = elem.tag.split('}')[-1]

        if tag == 'text':
            text = elem.text
            if is_reference_numeral(text):
                bbox = get_text_bbox(elem, current_transform)
                if bbox:
                    numerals.append(bbox)

        elif tag in ('rect', 'circle', 'ellipse', 'polygon'):
            bbox = get_shape_bbox(elem, current_transform)
            if bbox and bbox['w'] > 0 and bbox['h'] > 0:
                shapes.append(bbox)

        elif tag == 'line':
            line = get_line_info(elem, current_transform)
            if line and line['stroke_width'] <= LEAD_LINE_MAX_STROKE:
                thin_lines.append(line)

        for child in elem:
            process_element(child, current_transform)

    process_element(root)

    results = {
        'with_lead_line': [],
        'with_proximity': [],
        'warnings': [],
        'numerals_count': len(numerals)
    }

    for numeral in numerals:
        # Check for lead line
        has_lead_line = False
        for line in thin_lines:
            # Check if either endpoint is near numeral
            if (point_near_text(line['x1'], line['y1'], numeral, NUMERAL_LINE_TOLERANCE) or
                point_near_text(line['x2'], line['y2'], numeral, NUMERAL_LINE_TOLERANCE)):
                has_lead_line = True
                break

        if has_lead_line:
            results['with_lead_line'].append(numeral['text'])
            continue

        # Check for proximity to shape
        min_dist = float('inf')
        for shape in shapes:
            dist = distance_point_to_bbox(numeral['cx'], numeral['cy'], shape)
            min_dist = min(min_dist, dist)

        if min_dist <= PROXIMITY_THRESHOLD_PX:
            results['with_proximity'].append((numeral['text'], f"{min_dist:.0f}px"))
        else:
            results['warnings'].append((numeral['text'], f"{min_dist:.0f}px from nearest shape"))

    return results


def run_check(patent_dir, num_figs, patent_letter):
    """Run lead line audit on all figures in a patent."""
    base_path = Path(__file__).parent.parent.parent.parent.parent / 'patent_drawings'
    patent_path = base_path / patent_dir

    total_with_lead = 0
    total_with_prox = 0
    total_warn = 0

    print(f"\n{'='*60}")
    print(f"PATENT {patent_letter.upper()}: Lead Line Audit")
    print('='*60)

    for fig_num in range(1, num_figs + 1):
        svg_file = patent_path / f'fig{fig_num}.svg'

        if not svg_file.exists():
            print(f"\n[!] FIG. {fig_num}: FILE NOT FOUND")
            continue

        results = check_lead_lines(svg_file)

        if 'error' in results:
            print(f"\n[!] FIG. {fig_num}: {results['error']}")
            continue

        print(f"\n--- FIG. {fig_num} ({svg_file.name}) ---")
        print(f"  Reference numerals found: {results['numerals_count']}")

        if results['with_lead_line']:
            print(f"  [PASS] With lead line: {', '.join(results['with_lead_line'])}")
            total_with_lead += len(results['with_lead_line'])

        if results['with_proximity']:
            for num, dist in results['with_proximity']:
                print(f"  [PASS] Proximity rule: {num} ({dist} from shape)")
            total_with_prox += len(results['with_proximity'])

        if results['warnings']:
            for num, dist in results['warnings']:
                print(f"  [WARN] {num}: {dist} - may need lead line")
            total_warn += len(results['warnings'])

    return total_with_lead, total_with_prox, total_warn


def main():
    """Main entry point."""
    args = sys.argv[1:]

    print("="*60)
    print("CHECK 2: LEAD LINE AUDIT")
    print("Per 37 CFR 1.84(q)")
    print("="*60)

    patents_to_check = []
    if '--all' in args or not args:
        patents_to_check = list(PATENTS.keys())
    elif '--patent' in args:
        idx = args.index('--patent')
        if idx + 1 < len(args):
            p = args[idx + 1].lower()
            if p in PATENTS:
                patents_to_check = [p]

    total_lead = 0
    total_prox = 0
    total_warn = 0

    for patent_key in patents_to_check:
        patent_dir, num_figs = PATENTS[patent_key]
        lead, prox, warn = run_check(patent_dir, num_figs, patent_key)
        total_lead += lead
        total_prox += prox
        total_warn += warn

    print(f"\n{'='*60}")
    print("SUMMARY: Lead Line Audit")
    print('='*60)
    print(f"  Numerals with lead lines: {total_lead}")
    print(f"  Numerals passing proximity rule: {total_prox}")
    print(f"  Warnings (may need attention): {total_warn}")

    if total_warn == 0:
        print(f"\n[OK] All reference numerals have proper associations")
        return 0
    else:
        print(f"\n[WARN] {total_warn} numeral(s) may need review")
        return 0  # Warnings don't fail the check


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Check 5: Ambiguous Numeral Placement

Flags reference numerals that are equidistant from multiple shapes,
making it unclear which element they reference.

Per 37 CFR 1.84(p): Reference characters must be plain and legible,
and their association with elements must be clear.
"""

import xml.etree.ElementTree as ET
import re
import sys
import math
from pathlib import Path


# Constants
AMBIGUITY_TOLERANCE = 0.15   # 15% tolerance
BORDERLINE_TOLERANCE = 0.25  # 25% tolerance

PATENTS = {
    'a': ('patent_a', 8),
    'b': ('patent_b', 6),
    'c': ('patent_c', 7),
}


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


def get_text_center(elem, parent_transform=(0, 0)):
    """Get center point of text element."""
    try:
        x = float(elem.get('x', 0)) + parent_transform[0]
        y = float(elem.get('y', 0)) + parent_transform[1]
        font_size = float(elem.get('font-size', 14))
        text = elem.text or ''

        char_width = font_size * 0.6
        width = len(text) * char_width

        anchor = elem.get('text-anchor', 'start')
        if anchor == 'middle':
            cx = x
        elif anchor == 'end':
            cx = x - width / 2
        else:
            cx = x + width / 2

        cy = y - font_size * 0.4

        return {'text': text, 'cx': cx, 'cy': cy}
    except (ValueError, TypeError):
        return None


def get_shape_center(elem, parent_transform=(0, 0)):
    """Get center point and info for shape element."""
    tag = elem.tag.split('}')[-1]

    try:
        if tag == 'rect':
            x = float(elem.get('x', 0)) + parent_transform[0]
            y = float(elem.get('y', 0)) + parent_transform[1]
            w = float(elem.get('width', 0))
            h = float(elem.get('height', 0))
            if w > 0 and h > 0:
                return {'type': 'rect', 'cx': x + w/2, 'cy': y + h/2, 'w': w, 'h': h}

        elif tag == 'circle':
            cx = float(elem.get('cx', 0)) + parent_transform[0]
            cy = float(elem.get('cy', 0)) + parent_transform[1]
            r = float(elem.get('r', 0))
            if r > 0:
                return {'type': 'circle', 'cx': cx, 'cy': cy, 'r': r}

        elif tag == 'polygon':
            points_str = elem.get('points', '')
            coords = re.findall(r'([\d.-]+)', points_str)
            if len(coords) >= 4:
                xs = [float(coords[i]) + parent_transform[0] for i in range(0, len(coords), 2)]
                ys = [float(coords[i]) + parent_transform[1] for i in range(1, len(coords), 2)]
                return {'type': 'polygon', 'cx': sum(xs)/len(xs), 'cy': sum(ys)/len(ys)}

    except (ValueError, TypeError):
        pass

    return None


def is_reference_numeral(text):
    """Check if text is a reference numeral (2-3 digit number)."""
    if not text:
        return False
    text = text.strip()
    return bool(re.match(r'^\d{2,3}$', text))


def distance(p1, p2):
    """Euclidean distance between two points."""
    return math.hypot(p1['cx'] - p2['cx'], p1['cy'] - p2['cy'])


def check_ambiguous_placement(svg_path):
    """Check for ambiguously placed reference numerals."""
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return {'error': str(e)}

    numerals = []
    shapes = []

    def process_element(elem, parent_transform=(0, 0)):
        transform = elem.get('transform', '')
        tx, ty = parse_transform(transform)
        current_transform = (parent_transform[0] + tx, parent_transform[1] + ty)

        tag = elem.tag.split('}')[-1]

        if tag == 'text':
            text = elem.text
            if is_reference_numeral(text):
                center = get_text_center(elem, current_transform)
                if center:
                    numerals.append(center)

        elif tag in ('rect', 'circle', 'polygon'):
            shape = get_shape_center(elem, current_transform)
            if shape:
                shapes.append(shape)

        for child in elem:
            process_element(child, current_transform)

    process_element(root)

    results = {
        'clear': [],
        'borderline': [],
        'ambiguous': [],
        'numerals_count': len(numerals)
    }

    for numeral in numerals:
        if len(shapes) < 2:
            results['clear'].append(numeral['text'])
            continue

        # Calculate distances to all shapes
        distances = []
        for shape in shapes:
            dist = distance(numeral, shape)
            distances.append((dist, shape))

        distances.sort(key=lambda x: x[0])

        d1, shape1 = distances[0]
        d2, shape2 = distances[1]

        if d1 == 0:
            # Numeral is exactly at shape center - clear
            results['clear'].append(numeral['text'])
            continue

        # Calculate ratio
        ratio = (d2 - d1) / d1

        if ratio < AMBIGUITY_TOLERANCE:
            results['ambiguous'].append({
                'numeral': numeral['text'],
                'd1': d1,
                'd2': d2,
                'ratio': ratio
            })
        elif ratio < BORDERLINE_TOLERANCE:
            results['borderline'].append({
                'numeral': numeral['text'],
                'd1': d1,
                'd2': d2,
                'ratio': ratio
            })
        else:
            results['clear'].append(numeral['text'])

    return results


def run_check(patent_dir, num_figs, patent_letter):
    """Run ambiguity check on all figures in a patent."""
    base_path = Path(__file__).parent.parent.parent.parent.parent / 'patent_drawings'
    patent_path = base_path / patent_dir

    total_clear = 0
    total_borderline = 0
    total_ambiguous = 0

    print(f"\n{'='*60}")
    print(f"PATENT {patent_letter.upper()}: Ambiguous Numeral Placement")
    print('='*60)

    for fig_num in range(1, num_figs + 1):
        svg_file = patent_path / f'fig{fig_num}.svg'

        if not svg_file.exists():
            print(f"\n[!] FIG. {fig_num}: FILE NOT FOUND")
            continue

        results = check_ambiguous_placement(svg_file)

        if 'error' in results:
            print(f"\n[!] FIG. {fig_num}: {results['error']}")
            continue

        print(f"\n--- FIG. {fig_num} ({svg_file.name}) ---")
        print(f"  Reference numerals: {results['numerals_count']}")

        if results['clear']:
            print(f"  [PASS] Clear placement: {len(results['clear'])}")
            total_clear += len(results['clear'])

        if results['borderline']:
            for item in results['borderline']:
                print(f"  [INFO] Borderline: {item['numeral']} (ratio: {item['ratio']:.2f})")
            total_borderline += len(results['borderline'])

        if results['ambiguous']:
            for item in results['ambiguous']:
                print(f"  [WARN] Ambiguous: {item['numeral']} - equidistant from 2 shapes")
                print(f"         d1={item['d1']:.0f}px, d2={item['d2']:.0f}px, ratio={item['ratio']:.2f}")
            total_ambiguous += len(results['ambiguous'])

    return total_clear, total_borderline, total_ambiguous


def main():
    """Main entry point."""
    args = sys.argv[1:]

    print("="*60)
    print("CHECK 5: AMBIGUOUS NUMERAL PLACEMENT")
    print("Per 37 CFR 1.84(p)")
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

    total_clear = 0
    total_borderline = 0
    total_ambiguous = 0

    for patent_key in patents_to_check:
        patent_dir, num_figs = PATENTS[patent_key]
        clear, borderline, ambiguous = run_check(patent_dir, num_figs, patent_key)
        total_clear += clear
        total_borderline += borderline
        total_ambiguous += ambiguous

    print(f"\n{'='*60}")
    print("SUMMARY: Ambiguous Numeral Placement")
    print('='*60)
    print(f"  Clear placement: {total_clear}")
    print(f"  Borderline: {total_borderline}")
    print(f"  Ambiguous: {total_ambiguous}")

    if total_ambiguous == 0:
        print(f"\n[OK] No ambiguous numeral placements detected")
        return 0
    else:
        print(f"\n[WARN] {total_ambiguous} numeral(s) may be ambiguously placed")
        return 0


if __name__ == '__main__':
    sys.exit(main())

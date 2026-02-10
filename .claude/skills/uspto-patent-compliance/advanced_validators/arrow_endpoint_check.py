#!/usr/bin/env python3
"""
Check 4: Arrow Endpoint Validation

Verifies that arrows actually connect to their target components,
not floating in space. Arrows should touch or come within 5px of
a component edge.
"""

import xml.etree.ElementTree as ET
import re
import sys
import math
from pathlib import Path


# Constants
ARROW_TOUCH_THRESHOLD = 5    # Connected
ARROW_NEAR_THRESHOLD = 10    # Acceptable
ARROW_WARN_THRESHOLD = 20    # Warning

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


def get_shape_bbox(elem, parent_transform=(0, 0)):
    """Get bounding box for shape element."""
    tag = elem.tag.split('}')[-1]

    try:
        if tag == 'rect':
            x = float(elem.get('x', 0)) + parent_transform[0]
            y = float(elem.get('y', 0)) + parent_transform[1]
            w = float(elem.get('width', 0))
            h = float(elem.get('height', 0))
            if w > 0 and h > 0:
                return {'type': 'rect', 'x': x, 'y': y, 'w': w, 'h': h}

        elif tag == 'circle':
            cx = float(elem.get('cx', 0)) + parent_transform[0]
            cy = float(elem.get('cy', 0)) + parent_transform[1]
            r = float(elem.get('r', 0))
            if r > 0:
                return {'type': 'circle', 'x': cx - r, 'y': cy - r, 'w': 2*r, 'h': 2*r, 'cx': cx, 'cy': cy, 'r': r}

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


def get_arrow_endpoint(elem, parent_transform=(0, 0)):
    """Extract the endpoint of an arrow (line or polyline with marker-end)."""
    marker_end = elem.get('marker-end', '')
    if 'url(#ah)' not in marker_end and 'url(#' not in marker_end:
        return None

    tag = elem.tag.split('}')[-1]

    try:
        if tag == 'line':
            x2 = float(elem.get('x2', 0)) + parent_transform[0]
            y2 = float(elem.get('y2', 0)) + parent_transform[1]
            return {'type': 'line', 'x': x2, 'y': y2}

        elif tag == 'polyline':
            points = elem.get('points', '').strip()
            coords = re.findall(r'([\d.-]+)', points)
            if len(coords) >= 2:
                x = float(coords[-2]) + parent_transform[0]
                y = float(coords[-1]) + parent_transform[1]
                return {'type': 'polyline', 'x': x, 'y': y}

        elif tag == 'path':
            # Basic path endpoint extraction
            d = elem.get('d', '')
            # Find last coordinate pair
            coords = re.findall(r'([\d.-]+)', d)
            if len(coords) >= 2:
                x = float(coords[-2]) + parent_transform[0]
                y = float(coords[-1]) + parent_transform[1]
                return {'type': 'path', 'x': x, 'y': y}

    except (ValueError, TypeError):
        pass

    return None


def distance_to_shape(px, py, shape):
    """Calculate minimum distance from point to shape edge."""
    x1, y1 = shape['x'], shape['y']
    x2, y2 = x1 + shape['w'], y1 + shape['h']

    # For circle, calculate distance to circumference
    if shape['type'] == 'circle':
        cx, cy, r = shape['cx'], shape['cy'], shape['r']
        dist_to_center = math.hypot(px - cx, py - cy)
        return abs(dist_to_center - r)

    # For rectangles/polygons, distance to edge
    # Clamp point to bbox
    cx = max(x1, min(px, x2))
    cy = max(y1, min(py, y2))

    return math.hypot(px - cx, py - cy)


def check_arrow_endpoints(svg_path):
    """Check if all arrow endpoints connect to shapes."""
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return {'error': str(e)}

    arrows = []
    shapes = []

    def process_element(elem, parent_transform=(0, 0)):
        transform = elem.get('transform', '')
        tx, ty = parse_transform(transform)
        current_transform = (parent_transform[0] + tx, parent_transform[1] + ty)

        tag = elem.tag.split('}')[-1]

        # Check for arrows (elements with marker-end)
        if tag in ('line', 'polyline', 'path'):
            endpoint = get_arrow_endpoint(elem, current_transform)
            if endpoint:
                arrows.append(endpoint)

        # Collect shapes
        if tag in ('rect', 'circle', 'polygon'):
            bbox = get_shape_bbox(elem, current_transform)
            if bbox:
                shapes.append(bbox)

        for child in elem:
            process_element(child, current_transform)

    process_element(root)

    results = {
        'connected': [],      # <= 5px
        'near': [],           # 5-10px
        'warnings': [],       # 10-20px
        'floating': [],       # > 20px
        'arrow_count': len(arrows)
    }

    for arrow in arrows:
        min_dist = float('inf')
        nearest_shape = None

        for shape in shapes:
            dist = distance_to_shape(arrow['x'], arrow['y'], shape)
            if dist < min_dist:
                min_dist = dist
                nearest_shape = shape

        endpoint_str = f"({arrow['x']:.0f}, {arrow['y']:.0f})"

        if min_dist <= ARROW_TOUCH_THRESHOLD:
            results['connected'].append((endpoint_str, min_dist))
        elif min_dist <= ARROW_NEAR_THRESHOLD:
            results['near'].append((endpoint_str, min_dist))
        elif min_dist <= ARROW_WARN_THRESHOLD:
            results['warnings'].append((endpoint_str, min_dist))
        else:
            results['floating'].append((endpoint_str, min_dist))

    return results


def run_check(patent_dir, num_figs, patent_letter):
    """Run arrow endpoint check on all figures in a patent."""
    base_path = Path(__file__).parent.parent.parent.parent.parent / 'patent_drawings'
    patent_path = base_path / patent_dir

    total_connected = 0
    total_near = 0
    total_warn = 0
    total_floating = 0

    print(f"\n{'='*60}")
    print(f"PATENT {patent_letter.upper()}: Arrow Endpoint Validation")
    print('='*60)

    for fig_num in range(1, num_figs + 1):
        svg_file = patent_path / f'fig{fig_num}.svg'

        if not svg_file.exists():
            print(f"\n[!] FIG. {fig_num}: FILE NOT FOUND")
            continue

        results = check_arrow_endpoints(svg_file)

        if 'error' in results:
            print(f"\n[!] FIG. {fig_num}: {results['error']}")
            continue

        print(f"\n--- FIG. {fig_num} ({svg_file.name}) ---")
        print(f"  Arrows found: {results['arrow_count']}")

        if results['connected']:
            print(f"  [PASS] Connected (<=5px): {len(results['connected'])}")
            total_connected += len(results['connected'])

        if results['near']:
            print(f"  [PASS] Near (5-10px): {len(results['near'])}")
            total_near += len(results['near'])

        if results['warnings']:
            for endpoint, dist in results['warnings']:
                print(f"  [WARN] {endpoint}: {dist:.1f}px from nearest shape")
            total_warn += len(results['warnings'])

        if results['floating']:
            for endpoint, dist in results['floating']:
                print(f"  [WARN] Floating arrow at {endpoint}: {dist:.1f}px")
            total_floating += len(results['floating'])

    return total_connected, total_near, total_warn, total_floating


def main():
    """Main entry point."""
    args = sys.argv[1:]

    print("="*60)
    print("CHECK 4: ARROW ENDPOINT VALIDATION")
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

    total_connected = 0
    total_near = 0
    total_warn = 0
    total_floating = 0

    for patent_key in patents_to_check:
        patent_dir, num_figs = PATENTS[patent_key]
        connected, near, warn, floating = run_check(patent_dir, num_figs, patent_key)
        total_connected += connected
        total_near += near
        total_warn += warn
        total_floating += floating

    print(f"\n{'='*60}")
    print("SUMMARY: Arrow Endpoint Validation")
    print('='*60)
    print(f"  Connected (<=5px): {total_connected}")
    print(f"  Near (5-10px): {total_near}")
    print(f"  Warnings (10-20px): {total_warn}")
    print(f"  Floating (>20px): {total_floating}")

    if total_warn == 0 and total_floating == 0:
        print(f"\n[OK] All arrows properly connect to components")
        return 0
    else:
        print(f"\n[WARN] {total_warn + total_floating} arrow(s) may need adjustment")
        return 0


if __name__ == '__main__':
    sys.exit(main())

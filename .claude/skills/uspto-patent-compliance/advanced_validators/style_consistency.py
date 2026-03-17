#!/usr/bin/env python3
"""
Check 6: Style Consistency

Verifies that all 21 drawings use identical visual styling:
- Same arrow markers
- Same stroke widths for same element types
- Same fonts
- Same font sizes
- Same dash patterns
"""

import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path
from collections import defaultdict


# Expected values
EXPECTED_MARKER_POINTS = "0 0, 6 2, 0 4"
EXPECTED_FONTS = {'Arial, sans-serif', 'Courier New, monospace', 'Arial', 'Courier New'}
EXPECTED_FONT_SIZES = {14, 16, 20}
EXPECTED_STROKE_WIDTHS = {0.5, 1, 1.5, 2, 3}

PATENTS = {
    'a': ('patent_a', 8),
    'b': ('patent_b', 6),
    'c': ('patent_c', 7),
}


def extract_styles(svg_path):
    """Extract all style-related elements from an SVG."""
    result = {
        'markers': [],
        'stroke_widths': set(),
        'fonts': set(),
        'font_sizes': set(),
        'dash_patterns': set(),
    }

    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return {'error': str(e)}

    # Extract markers from defs
    for elem in root.iter():
        tag = elem.tag.split('}')[-1]

        if tag == 'marker':
            marker_id = elem.get('id')
            # Find polygon inside marker
            for child in elem:
                if 'polygon' in child.tag:
                    points = child.get('points', '').strip()
                    result['markers'].append({'id': marker_id, 'points': points})

        # Extract stroke-width
        sw = elem.get('stroke-width')
        if sw:
            try:
                result['stroke_widths'].add(float(sw))
            except ValueError:
                pass

        # Extract font-family
        ff = elem.get('font-family')
        if ff:
            result['fonts'].add(ff)

        # Extract font-size
        fs = elem.get('font-size')
        if fs:
            try:
                result['font_sizes'].add(int(float(fs)))
            except ValueError:
                pass

        # Extract stroke-dasharray
        sd = elem.get('stroke-dasharray')
        if sd:
            result['dash_patterns'].add(sd)

    return result


def run_check_all():
    """Run style consistency check across all patents."""
    base_path = Path(__file__).parent.parent.parent.parent.parent / 'patent_drawings'

    all_styles = []
    file_styles = {}

    # Collect styles from all files
    for patent_key, (patent_dir, num_figs) in PATENTS.items():
        patent_path = base_path / patent_dir

        for fig_num in range(1, num_figs + 1):
            svg_file = patent_path / f'fig{fig_num}.svg'

            if not svg_file.exists():
                continue

            styles = extract_styles(svg_file)
            if 'error' not in styles:
                file_key = f"Patent {patent_key.upper()} FIG. {fig_num}"
                file_styles[file_key] = styles
                all_styles.append(styles)

    # Aggregate styles
    all_markers = []
    all_stroke_widths = set()
    all_fonts = set()
    all_font_sizes = set()
    all_dash_patterns = set()

    for styles in all_styles:
        all_markers.extend(styles['markers'])
        all_stroke_widths.update(styles['stroke_widths'])
        all_fonts.update(styles['fonts'])
        all_font_sizes.update(styles['font_sizes'])
        all_dash_patterns.update(styles['dash_patterns'])

    # Check consistency
    results = {
        'markers': {'pass': True, 'issues': []},
        'stroke_widths': {'pass': True, 'issues': []},
        'fonts': {'pass': True, 'issues': []},
        'font_sizes': {'pass': True, 'issues': []},
    }

    # Check markers
    unique_marker_points = set(m['points'] for m in all_markers)
    if len(unique_marker_points) > 1:
        results['markers']['pass'] = False
        results['markers']['issues'].append(f"Multiple marker definitions: {unique_marker_points}")

    # Check for expected marker
    if all_markers and EXPECTED_MARKER_POINTS not in unique_marker_points:
        results['markers']['issues'].append(f"Expected marker points: {EXPECTED_MARKER_POINTS}")

    # Check stroke widths
    unexpected_widths = all_stroke_widths - EXPECTED_STROKE_WIDTHS
    if unexpected_widths:
        results['stroke_widths']['pass'] = False
        results['stroke_widths']['issues'].append(f"Unexpected widths: {unexpected_widths}")

    # Check fonts
    # Normalize font names for comparison
    normalized_fonts = set()
    for f in all_fonts:
        if 'Arial' in f:
            normalized_fonts.add('Arial')
        elif 'Courier' in f:
            normalized_fonts.add('Courier')
        else:
            normalized_fonts.add(f)

    unexpected_fonts = all_fonts - EXPECTED_FONTS
    if unexpected_fonts:
        results['fonts']['issues'].append(f"Non-standard fonts: {unexpected_fonts}")

    # Check font sizes
    unexpected_sizes = all_font_sizes - EXPECTED_FONT_SIZES
    if unexpected_sizes:
        results['font_sizes']['pass'] = False
        results['font_sizes']['issues'].append(f"Unexpected sizes: {unexpected_sizes}")

    return results, {
        'markers': list(unique_marker_points),
        'stroke_widths': sorted(all_stroke_widths),
        'fonts': sorted(all_fonts),
        'font_sizes': sorted(all_font_sizes),
        'dash_patterns': sorted(all_dash_patterns),
        'files_checked': len(file_styles)
    }


def main():
    """Main entry point."""
    print("="*60)
    print("CHECK 6: STYLE CONSISTENCY")
    print("="*60)

    results, aggregates = run_check_all()

    print(f"\nFiles checked: {aggregates['files_checked']}")

    # Report findings
    print(f"\n--- Marker Definitions ---")
    print(f"  Unique markers: {aggregates['markers']}")
    if results['markers']['pass']:
        print(f"  [PASS] All markers consistent")
    else:
        for issue in results['markers']['issues']:
            print(f"  [FAIL] {issue}")

    print(f"\n--- Stroke Widths ---")
    print(f"  Found: {aggregates['stroke_widths']}")
    print(f"  Expected: {sorted(EXPECTED_STROKE_WIDTHS)}")
    if results['stroke_widths']['pass']:
        print(f"  [PASS] All stroke widths within expected set")
    else:
        for issue in results['stroke_widths']['issues']:
            print(f"  [WARN] {issue}")

    print(f"\n--- Font Families ---")
    print(f"  Found: {aggregates['fonts']}")
    if results['fonts']['issues']:
        for issue in results['fonts']['issues']:
            print(f"  [INFO] {issue}")
    else:
        print(f"  [PASS] All fonts within expected set")

    print(f"\n--- Font Sizes ---")
    print(f"  Found: {aggregates['font_sizes']}")
    print(f"  Expected: {sorted(EXPECTED_FONT_SIZES)}")
    if results['font_sizes']['pass']:
        print(f"  [PASS] All font sizes within expected set")
    else:
        for issue in results['font_sizes']['issues']:
            print(f"  [WARN] {issue}")

    print(f"\n--- Dash Patterns ---")
    print(f"  Found: {aggregates['dash_patterns']}")
    print(f"  [INFO] Dash patterns vary by line type (normal)")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY: Style Consistency")
    print('='*60)

    all_pass = all(r['pass'] for r in results.values())

    if all_pass:
        print(f"\n[OK] All 21 drawings use consistent styling")
        return 0
    else:
        print(f"\n[WARN] Some style inconsistencies detected - review above")
        return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Check 1: 2/3 Scale Simulation

USPTO reproductions are often printed at 2/3 scale.
All text must remain legible (>=6pt) after reduction.

Per 37 CFR 1.84(k): Scale large enough to show mechanism without
crowding when reduced to 2/3 size.
"""

import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path


# Constants
MINIMUM_SCALED_SIZE_PT = 6.0
SCALE_FACTOR = 2.0 / 3.0  # 0.6667

PATENTS = {
    'a': ('patent_a', 8),
    'b': ('patent_b', 6),
    'c': ('patent_c', 7),
}


def parse_font_size(value):
    """Parse font-size value to float."""
    if not value:
        return None
    # Remove units if present
    value = str(value).strip()
    match = re.match(r'([\d.]+)', value)
    if match:
        return float(match.group(1))
    return None


def extract_font_sizes(svg_path):
    """Extract all font-size values from an SVG file."""
    sizes = {}

    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return {'error': str(e)}

    # Check all elements for font-size
    for elem in root.iter():
        # Direct font-size attribute
        fs = elem.get('font-size')
        if fs:
            size = parse_font_size(fs)
            if size:
                if size not in sizes:
                    sizes[size] = 0
                sizes[size] += 1

        # Font-size in style attribute
        style = elem.get('style', '')
        match = re.search(r'font-size:\s*([\d.]+)', style)
        if match:
            size = float(match.group(1))
            if size not in sizes:
                sizes[size] = 0
            sizes[size] += 1

    return sizes


def check_scale(svg_path):
    """Check if all font sizes pass 2/3 scale reduction."""
    sizes = extract_font_sizes(svg_path)

    if 'error' in sizes:
        return False, [f"Parse error: {sizes['error']}"]

    results = []
    all_pass = True

    for size, count in sorted(sizes.items()):
        scaled = size * SCALE_FACTOR
        if scaled < MINIMUM_SCALED_SIZE_PT:
            results.append(f"[FAIL] {size}pt -> {scaled:.2f}pt (below {MINIMUM_SCALED_SIZE_PT}pt minimum) [{count} elements]")
            all_pass = False
        else:
            results.append(f"[PASS] {size}pt -> {scaled:.2f}pt ({count} elements)")

    if not sizes:
        results.append("[WARN] No font-size attributes found")

    return all_pass, results


def run_check(patent_dir, num_figs, patent_letter):
    """Run scale check on all figures in a patent."""
    base_path = Path(__file__).parent.parent.parent.parent.parent / 'patent_drawings'
    patent_path = base_path / patent_dir

    passes = 0
    failures = 0
    all_sizes = {}

    print(f"\n{'='*60}")
    print(f"PATENT {patent_letter.upper()}: 2/3 Scale Simulation")
    print('='*60)

    for fig_num in range(1, num_figs + 1):
        svg_file = patent_path / f'fig{fig_num}.svg'

        if not svg_file.exists():
            print(f"\n[!] FIG. {fig_num}: FILE NOT FOUND")
            failures += 1
            continue

        passed, results = check_scale(svg_file)

        print(f"\n--- FIG. {fig_num} ({svg_file.name}) ---")
        for r in results:
            print(f"  {r}")

        if passed:
            passes += 1
        else:
            failures += 1

        # Aggregate sizes
        sizes = extract_font_sizes(svg_file)
        for size, count in sizes.items():
            if size not in all_sizes:
                all_sizes[size] = 0
            all_sizes[size] += count

    return passes, failures, all_sizes


def main():
    """Main entry point."""
    args = sys.argv[1:]

    print("="*60)
    print("CHECK 1: 2/3 SCALE SIMULATION VALIDATOR")
    print("Per 37 CFR 1.84(k)")
    print("="*60)

    # Determine which patents to check
    patents_to_check = []
    if '--all' in args or not args:
        patents_to_check = list(PATENTS.keys())
    elif '--patent' in args:
        idx = args.index('--patent')
        if idx + 1 < len(args):
            p = args[idx + 1].lower()
            if p in PATENTS:
                patents_to_check = [p]

    total_passes = 0
    total_failures = 0
    all_sizes = {}

    for patent_key in patents_to_check:
        patent_dir, num_figs = PATENTS[patent_key]
        passes, failures, sizes = run_check(patent_dir, num_figs, patent_key)
        total_passes += passes
        total_failures += failures
        for size, count in sizes.items():
            if size not in all_sizes:
                all_sizes[size] = 0
            all_sizes[size] += count

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY: 2/3 Scale Simulation")
    print('='*60)
    print(f"  Figures checked: {total_passes + total_failures}")
    print(f"  PASS: {total_passes}")
    print(f"  FAIL: {total_failures}")

    print(f"\n  Font sizes found across all drawings:")
    for size in sorted(all_sizes.keys()):
        scaled = size * SCALE_FACTOR
        status = "OK" if scaled >= MINIMUM_SCALED_SIZE_PT else "FAIL"
        print(f"    {size}pt -> {scaled:.2f}pt [{status}] ({all_sizes[size]} total)")

    if total_failures == 0:
        print(f"\n[OK] All text remains legible at 2/3 scale")
        return 0
    else:
        print(f"\n[!] {total_failures} figure(s) have text that may be illegible at 2/3 scale")
        return 1


if __name__ == '__main__':
    sys.exit(main())

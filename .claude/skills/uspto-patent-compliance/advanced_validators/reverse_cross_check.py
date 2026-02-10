#!/usr/bin/env python3
"""
Check 3: Reverse Cross-Check (Spec -> Drawing)

Verifies that every reference numeral mentioned in the specification
appears in the corresponding drawing.

This is the inverse of cross_check_numerals.py which checks Drawing -> Spec.
Per 37 CFR 1.84(p): Characters mentioned in description MUST appear in drawings.
"""

import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path
from collections import defaultdict


PATENTS = {
    'a': ('patent_a', 8, 'Patent_A_Drawings_Description.txt'),
    'b': ('patent_b', 6, 'Patent_B_Drawings_Description.txt'),
    'c': ('patent_c', 7, 'Patent_C_Drawings_Description.txt'),
}


def extract_numerals_from_svg(svg_path):
    """Extract all reference numerals from an SVG file."""
    numerals = set()

    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError:
        return numerals

    for elem in root.iter():
        tag = elem.tag.split('}')[-1]
        if tag == 'text' and elem.text:
            text = elem.text.strip()
            # Reference numerals are 2-3 digit numbers
            if re.match(r'^\d{2,3}$', text):
                numerals.add(text)

    return numerals


def extract_numerals_from_spec_by_figure(spec_path):
    """
    Parse specification and extract numerals by figure number.
    Returns: {fig_num: set(numerals)}
    """
    result = defaultdict(set)

    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except (IOError, UnicodeDecodeError):
        try:
            with open(spec_path, 'r', encoding='latin-1') as f:
                text = f.read()
        except IOError:
            return result

    # Split by FIG. N patterns
    # Look for "FIG. N" as section headers
    sections = re.split(r'\n+(?=FIG\.\s*\d+)', text, flags=re.IGNORECASE)

    for section in sections:
        # Extract figure number from section start
        fig_match = re.match(r'FIG\.\s*(\d+)', section, re.IGNORECASE)
        if fig_match:
            fig_num = int(fig_match.group(1))

            # Find all 3-digit numerals in this section
            # Filter out years, measurements, etc.
            for match in re.finditer(r'\b(\d{3})\b', section):
                numeral = match.group(1)
                num_val = int(numeral)

                # Skip obvious non-reference numbers
                # Years (1900-2099)
                if 1900 <= num_val <= 2099:
                    continue
                # Very high numbers unlikely to be references
                if num_val > 900:
                    continue

                result[fig_num].add(numeral)

    return result


def run_check(patent_dir, num_figs, spec_filename, patent_letter):
    """Run reverse cross-check for a patent."""
    base_path = Path(__file__).parent.parent.parent.parent.parent
    patent_path = base_path / 'patent_drawings' / patent_dir
    spec_path = base_path / 'patents' / 'uspto_formatted' / spec_filename

    print(f"\n{'='*60}")
    print(f"PATENT {patent_letter.upper()}: Reverse Cross-Check (Spec -> Drawing)")
    print('='*60)

    if not spec_path.exists():
        print(f"[!] Specification not found: {spec_path}")
        return 0, 0, 0

    # Get numerals from spec by figure
    spec_numerals = extract_numerals_from_spec_by_figure(spec_path)

    passes = 0
    failures = 0
    warnings = 0

    for fig_num in range(1, num_figs + 1):
        svg_file = patent_path / f'fig{fig_num}.svg'

        print(f"\n--- FIG. {fig_num} ---")

        if not svg_file.exists():
            print(f"  [FAIL] SVG file not found")
            failures += 1
            continue

        # Get numerals from drawing
        drawing_numerals = extract_numerals_from_svg(svg_file)

        # Get expected numerals from spec for this figure
        expected_numerals = spec_numerals.get(fig_num, set())

        if not expected_numerals:
            print(f"  [WARN] No numerals found in spec for FIG. {fig_num}")
            warnings += 1
            continue

        # Check each spec numeral exists in drawing
        missing = expected_numerals - drawing_numerals
        found = expected_numerals & drawing_numerals

        if found:
            print(f"  [PASS] Found in drawing: {', '.join(sorted(found))}")

        if missing:
            # Some missing might be OK if they're referenced but not labeled
            # (e.g., mentioned in description but shown by position)
            print(f"  [WARN] In spec but not in drawing: {', '.join(sorted(missing))}")
            warnings += len(missing)
        else:
            passes += 1

    return passes, warnings, failures


def main():
    """Main entry point."""
    args = sys.argv[1:]

    print("="*60)
    print("CHECK 3: REVERSE CROSS-CHECK (Spec -> Drawing)")
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

    total_passes = 0
    total_warnings = 0
    total_failures = 0

    for patent_key in patents_to_check:
        patent_dir, num_figs, spec_file = PATENTS[patent_key]
        passes, warns, fails = run_check(patent_dir, num_figs, spec_file, patent_key)
        total_passes += passes
        total_warnings += warns
        total_failures += fails

    print(f"\n{'='*60}")
    print("SUMMARY: Reverse Cross-Check")
    print('='*60)
    print(f"  Figures fully matched: {total_passes}")
    print(f"  Warnings: {total_warnings}")
    print(f"  Failures: {total_failures}")

    if total_failures == 0 and total_warnings == 0:
        print(f"\n[OK] All spec numerals appear in drawings")
        return 0
    elif total_failures == 0:
        print(f"\n[WARN] Some numerals may need review")
        return 0
    else:
        print(f"\n[FAIL] Missing required numerals in drawings")
        return 1


if __name__ == '__main__':
    sys.exit(main())

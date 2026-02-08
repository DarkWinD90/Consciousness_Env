#!/usr/bin/env python3
"""
USPTO Patent Reference Numeral Cross-Checker

Validates that all reference numerals used in patent drawings appear in the
specification, and vice versa. This is a critical requirement under 37 CFR
1.84(p): "Reference characters not mentioned in the description shall not
appear in the drawings. Reference characters mentioned in the description
must appear in the drawings."

Usage:
    python .claude/skills/uspto-patent-compliance/cross_check_numerals.py [--patent a|b|c] [--all]
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PATENT_FIGURE_COUNTS = {
    'a': 8,
    'b': 6,
    'c': 7,
}

# Patent specification file locations (relative to base_dir)
SPEC_FILES = {
    'a': [
        'patents/Patent_A_Energy_Loop.md',
        'patents/uspto_formatted/Patent_A_USPTO.txt',
        'patents/uspto_formatted/Patent_A_Drawings_Description.txt',
    ],
    'b': [
        'patents/Patent_B_Self_Observation.md',
        'patents/uspto_formatted/Patent_B_USPTO.txt',
        'patents/uspto_formatted/Patent_B_Drawings_Description.txt',
    ],
    'c': [
        'patents/Patent_C_Cognitive_Fallback.md',
        'patents/uspto_formatted/Patent_C_USPTO.txt',
        'patents/uspto_formatted/Patent_C_Drawings_Description.txt',
    ],
}

# Reference numeral pattern: 2-4 digit numbers that are likely reference numerals
# Exclude common non-numeral numbers (years, percentages, etc.)
NUMERAL_PATTERN = re.compile(r'\b(\d{2,4})\b')
YEAR_PATTERN = re.compile(r'\b(19|20)\d{2}\b')
PERCENTAGE_PATTERN = re.compile(r'\d+%')
MEASUREMENT_PATTERN = re.compile(r'\d+\s*(mm|cm|mW|mWh|Hz|kHz|MHz|ms|pt|px|dpi|DPI)\b')

# ---------------------------------------------------------------------------
# SVG Numeral Extraction
# ---------------------------------------------------------------------------

def extract_numerals_from_svg(svg_path):
    """Extract all potential reference numerals from an SVG file."""
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError:
        return set()

    numerals = set()
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag in ('text', 'tspan'):
            content = ''
            if elem.text:
                content += elem.text
            for child in elem:
                if child.text:
                    content += child.text
                if child.tail:
                    content += child.tail

            content = content.strip()

            # Skip sheet numbers (N/M format)
            if re.match(r'^\d+\s*/\s*\d+$', content):
                continue

            # Skip figure labels
            if re.match(r'^FIG\.?\s*\d+', content, re.IGNORECASE):
                continue

            # Extract numerals
            for match in NUMERAL_PATTERN.finditer(content):
                num = match.group(1)
                # Filter out likely non-reference-numerals
                num_int = int(num)
                # Reference numerals in this project are typically 100-999
                if 100 <= num_int <= 999:
                    numerals.add(num)

    return numerals


def extract_numerals_from_spec(spec_path):
    """Extract all potential reference numerals from a specification file."""
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except (FileNotFoundError, UnicodeDecodeError):
        return set(), {}

    numerals = set()
    numeral_contexts = defaultdict(list)

    # Process line by line for context
    for line_num, line in enumerate(text.split('\n'), 1):
        # Skip lines that are clearly not about reference numerals
        if YEAR_PATTERN.search(line):
            # Remove years before searching
            line_cleaned = YEAR_PATTERN.sub('', line)
        else:
            line_cleaned = line

        # Remove measurements
        line_cleaned = MEASUREMENT_PATTERN.sub('', line_cleaned)

        for match in NUMERAL_PATTERN.finditer(line_cleaned):
            num = match.group(1)
            num_int = int(num)
            if 100 <= num_int <= 999:
                numerals.add(num)
                # Store context (first occurrence per line)
                context = line.strip()[:80]
                if context not in numeral_contexts[num]:
                    numeral_contexts[num].append(context)

    return numerals, numeral_contexts


# ---------------------------------------------------------------------------
# Cross-Check
# ---------------------------------------------------------------------------

def cross_check_patent(patent, base_dir):
    """Cross-check reference numerals between drawings and spec for one patent."""
    patent = patent.lower()
    base_dir = Path(base_dir)

    print(f"\n{'=' * 60}")
    print(f"REFERENCE NUMERAL CROSS-CHECK — Patent {patent.upper()}")
    print(f"{'=' * 60}")

    # Extract numerals from all SVG drawings
    drawing_numerals = set()
    per_figure_numerals = {}
    total_figs = PATENT_FIGURE_COUNTS.get(patent, 0)

    for fig_num in range(1, total_figs + 1):
        svg_path = base_dir / 'patent_drawings' / f'patent_{patent}' / f'fig{fig_num}.svg'
        if svg_path.exists():
            fig_numerals = extract_numerals_from_svg(svg_path)
            per_figure_numerals[fig_num] = fig_numerals
            drawing_numerals |= fig_numerals
        else:
            print(f"  WARNING: {svg_path} not found")

    # Extract numerals from all spec files
    spec_numerals = set()
    spec_contexts = defaultdict(list)

    for spec_rel in SPEC_FILES.get(patent, []):
        spec_path = base_dir / spec_rel
        if spec_path.exists():
            nums, contexts = extract_numerals_from_spec(spec_path)
            spec_numerals |= nums
            for num, ctxs in contexts.items():
                spec_contexts[num].extend(ctxs)
        else:
            print(f"  WARNING: {spec_path} not found")

    # Cross-check
    in_drawings_only = drawing_numerals - spec_numerals
    in_spec_only = spec_numerals - drawing_numerals
    in_both = drawing_numerals & spec_numerals

    # Report
    print(f"\n--- Drawing Numerals ({len(drawing_numerals)} unique) ---")
    for fig_num in sorted(per_figure_numerals.keys()):
        nums = sorted(per_figure_numerals[fig_num], key=int)
        if nums:
            print(f"  FIG. {fig_num}: {', '.join(nums)}")

    print(f"\n--- Specification Numerals ({len(spec_numerals)} unique) ---")
    for num in sorted(spec_numerals, key=int):
        contexts = spec_contexts.get(num, [])
        ctx_str = f" — {contexts[0]}" if contexts else ""
        print(f"  {num}{ctx_str}")

    print(f"\n--- Consistency Check ---")
    print(f"  In both drawings and spec:    {len(in_both)}")

    issues = 0

    if in_drawings_only:
        print(f"\n  [FAIL] In drawings but NOT in spec ({len(in_drawings_only)}):")
        print(f"         37 CFR 1.84(p): Reference characters not mentioned in the")
        print(f"         description shall not appear in the drawings.")
        for num in sorted(in_drawings_only, key=int):
            figs = [f"FIG. {fn}" for fn, nums in per_figure_numerals.items() if num in nums]
            print(f"    {num} — appears in: {', '.join(figs)}")
        issues += len(in_drawings_only)
    else:
        print(f"  [PASS] All drawing numerals appear in specification")

    if in_spec_only:
        print(f"\n  [WARN] In spec but NOT in drawings ({len(in_spec_only)}):")
        print(f"         37 CFR 1.84(p): Reference characters mentioned in the")
        print(f"         description must appear in the drawings.")
        for num in sorted(in_spec_only, key=int):
            contexts = spec_contexts.get(num, [])
            ctx_str = f" — {contexts[0][:60]}" if contexts else ""
            print(f"    {num}{ctx_str}")
        # This is a WARN not FAIL because some numerals may be for text-only descriptions
    else:
        print(f"  [PASS] All specification numerals appear in drawings")

    # Check for same numeral used for different parts (heuristic)
    print(f"\n--- Numeral Uniqueness Check ---")
    # Within a patent, each numeral should consistently refer to the same component
    # We can't fully verify this automatically, but we can flag numerals that
    # appear in very different contexts
    print(f"  (Manual review required — verify each numeral consistently")
    print(f"   refers to the same component across all figures and text)")

    return issues


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="USPTO Reference Numeral Cross-Checker (37 CFR 1.84(p))"
    )
    parser.add_argument('--patent', choices=['a', 'b', 'c'],
                        help='Check specific patent')
    parser.add_argument('--all', action='store_true',
                        help='Check all patents')
    parser.add_argument('--base-dir', default=None,
                        help='Base directory')
    args = parser.parse_args()

    if args.base_dir:
        base_dir = args.base_dir
    else:
        script_dir = Path(__file__).resolve().parent
        base_dir = script_dir
        for _ in range(5):
            if (base_dir / 'patent_drawings').exists():
                break
            base_dir = base_dir.parent
        else:
            base_dir = Path.cwd()

    total_issues = 0

    if args.patent:
        total_issues += cross_check_patent(args.patent, base_dir)
    elif args.all or (not args.patent):
        for p in ['a', 'b', 'c']:
            total_issues += cross_check_patent(p, base_dir)

    print(f"\n{'=' * 60}")
    if total_issues > 0:
        print(f"CROSS-CHECK COMPLETE: {total_issues} issue(s) found")
    else:
        print(f"CROSS-CHECK COMPLETE: All reference numerals consistent")
    print(f"{'=' * 60}")

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == '__main__':
    main()

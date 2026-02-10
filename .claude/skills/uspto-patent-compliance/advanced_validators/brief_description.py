#!/usr/bin/env python3
"""
Check 7: Brief Description Coverage

Verifies that:
1. Every figure mentioned in Brief Description has a corresponding SVG
2. Every SVG file is mentioned in the Brief Description
3. Each figure has proper "FIG. N is a [TYPE] diagram" description
"""

import re
import sys
from pathlib import Path


PATENTS = {
    'a': ('patent_a', 8, 'Patent_A_Drawings_Description.txt', 'Patent_A_Energy_Loop.md'),
    'b': ('patent_b', 6, 'Patent_B_Drawings_Description.txt', 'Patent_B_Self_Observation.md'),
    'c': ('patent_c', 7, 'Patent_C_Drawings_Description.txt', 'Patent_C_Cognitive_Fallback.md'),
}


def extract_brief_description_figures(spec_path):
    """
    Extract figure numbers and descriptions from Brief Description section.
    Returns: {fig_num: description}
    """
    figures = {}

    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except (IOError, UnicodeDecodeError):
        try:
            with open(spec_path, 'r', encoding='latin-1') as f:
                text = f.read()
        except IOError:
            return figures

    # Find Brief Description section
    # Look for various section header formats
    brief_match = re.search(
        r'(?:BRIEF DESCRIPTION OF (?:THE )?DRAWINGS?|Brief Description)(.*?)(?:DETAILED DESCRIPTION|Detailed Description|$)',
        text,
        re.DOTALL | re.IGNORECASE
    )

    if brief_match:
        brief_text = brief_match.group(1)
    else:
        # Try to find FIG. references anywhere in document
        brief_text = text

    # Extract "FIG. N is a..." patterns
    for match in re.finditer(
        r'FIG\.?\s*(\d+)\s+is\s+(?:an?\s+)?([^.]+(?:diagram|chart|view|illustration|block|flow|graph|schematic|table)[^.]*)',
        brief_text,
        re.IGNORECASE
    ):
        fig_num = int(match.group(1))
        description = match.group(2).strip()
        figures[fig_num] = description

    # Also catch simpler patterns
    for match in re.finditer(
        r'FIG\.?\s*(\d+)\s*[-—:]\s*([^.\n]+)',
        brief_text,
        re.IGNORECASE
    ):
        fig_num = int(match.group(1))
        if fig_num not in figures:
            description = match.group(2).strip()
            figures[fig_num] = description

    return figures


def list_svg_figures(patent_dir):
    """List all figure numbers that have SVG files."""
    figures = set()
    base_path = Path(__file__).parent.parent.parent.parent.parent / 'patent_drawings'
    patent_path = base_path / patent_dir

    for svg in patent_path.glob('fig*.svg'):
        match = re.match(r'fig(\d+)\.svg', svg.name)
        if match:
            figures.add(int(match.group(1)))

    return figures


def run_check(patent_dir, num_figs, spec_filename, main_spec, patent_letter):
    """Run brief description coverage check for a patent."""
    base_path = Path(__file__).parent.parent.parent.parent.parent

    # Try both spec files
    spec_paths = [
        base_path / 'patents' / 'uspto_formatted' / spec_filename,
        base_path / 'patents' / main_spec,
    ]

    spec_figures = {}
    spec_path_used = None

    for sp in spec_paths:
        if sp.exists():
            spec_figures = extract_brief_description_figures(sp)
            if spec_figures:
                spec_path_used = sp
                break

    svg_figures = list_svg_figures(patent_dir)

    print(f"\n{'='*60}")
    print(f"PATENT {patent_letter.upper()}: Brief Description Coverage")
    print('='*60)

    if spec_path_used:
        print(f"  Spec file: {spec_path_used.name}")
    else:
        print(f"  [WARN] No specification file found")

    print(f"  Figures in spec: {sorted(spec_figures.keys()) if spec_figures else 'None found'}")
    print(f"  SVG files found: {sorted(svg_figures)}")
    print(f"  Expected figures: 1-{num_figs}")

    passes = 0
    warnings = 0
    failures = 0

    # Check each expected figure
    for fig_num in range(1, num_figs + 1):
        has_svg = fig_num in svg_figures
        has_desc = fig_num in spec_figures

        if has_svg and has_desc:
            print(f"\n  FIG. {fig_num}:")
            print(f"    [PASS] SVG exists: fig{fig_num}.svg")
            print(f"    [PASS] Description: {spec_figures[fig_num][:60]}...")
            passes += 1
        elif has_svg and not has_desc:
            print(f"\n  FIG. {fig_num}:")
            print(f"    [PASS] SVG exists: fig{fig_num}.svg")
            print(f"    [WARN] Not found in Brief Description")
            warnings += 1
        elif not has_svg and has_desc:
            print(f"\n  FIG. {fig_num}:")
            print(f"    [FAIL] SVG missing")
            print(f"    [PASS] Description: {spec_figures[fig_num][:60]}...")
            failures += 1
        else:
            print(f"\n  FIG. {fig_num}:")
            print(f"    [FAIL] SVG missing")
            print(f"    [FAIL] Not in Brief Description")
            failures += 1

    # Check for orphan SVGs (extra figures beyond expected)
    extra_svgs = svg_figures - set(range(1, num_figs + 1))
    if extra_svgs:
        for fig_num in sorted(extra_svgs):
            print(f"\n  FIG. {fig_num}:")
            print(f"    [WARN] Extra SVG found (beyond expected {num_figs})")
            warnings += 1

    return passes, warnings, failures


def main():
    """Main entry point."""
    args = sys.argv[1:]

    print("="*60)
    print("CHECK 7: BRIEF DESCRIPTION COVERAGE")
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
        patent_dir, num_figs, spec_file, main_spec = PATENTS[patent_key]
        passes, warns, fails = run_check(patent_dir, num_figs, spec_file, main_spec, patent_key)
        total_passes += passes
        total_warnings += warns
        total_failures += fails

    print(f"\n{'='*60}")
    print("SUMMARY: Brief Description Coverage")
    print('='*60)
    print(f"  Fully documented: {total_passes}")
    print(f"  Warnings: {total_warnings}")
    print(f"  Missing: {total_failures}")

    if total_failures == 0 and total_warnings == 0:
        print(f"\n[OK] All figures properly documented in Brief Description")
        return 0
    elif total_failures == 0:
        print(f"\n[WARN] Some figures may need Brief Description updates")
        return 0
    else:
        print(f"\n[FAIL] Missing figures or descriptions")
        return 1


if __name__ == '__main__':
    sys.exit(main())

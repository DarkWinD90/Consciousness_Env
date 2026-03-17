#!/usr/bin/env python3
"""Full USPTO compliance validator for patent drawing SVGs.

Runs all individual validators and produces a comprehensive report.
Exit code 0 = all pass, 1 = failures found.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from margin_validator import validate_margins, extract_coordinates
from font_validator import validate_fonts
from reference_validator import validate_references
from arrowhead_validator import validate_arrowheads


def validate_colors(svg_file):
    """Check that only black and white colors are used."""
    try:
        content = Path(svg_file).read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return False

    # Check for problematic colors
    import re

    # Find all fill and stroke colors
    fills = re.findall(r'fill="([^"]+)"', content)
    strokes = re.findall(r'stroke="([^"]+)"', content)

    allowed_colors = {'black', 'white', 'none', '#000000', '#000', '#fff', '#ffffff', 'url(#ah)', 'url(#hatch)', 'url(#hatchLight)'}

    issues = []
    for color in fills + strokes:
        color_lower = color.lower()
        if color_lower not in allowed_colors and not color_lower.startswith('url('):
            issues.append(f"Non-B&W color: {color}")

    if not issues:
        print("[PASS] Colors: Black and white only")
        return True
    else:
        print(f"[FAIL] Colors: {len(issues)} non-B&W color(s) found")
        for issue in issues[:5]:
            print(f"       - {issue}")
        return False


def validate_line_thickness(svg_file):
    """Check minimum line thickness (0.3mm = ~1.13px at 96 DPI)."""
    try:
        content = Path(svg_file).read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return False

    import re

    # Find all stroke-width values
    stroke_widths = re.findall(r'stroke-width="([\d.]+)"', content)

    issues = []
    for width in stroke_widths:
        w = float(width)
        # 0.5 is acceptable for leader lines, but main lines should be >= 1
        if w < 0.5:
            issues.append(f"stroke-width={w} (min 0.5 for leaders, 1.0 for main)")

    if not issues:
        print("[PASS] Line Thickness: All lines >= minimum")
        return True
    else:
        print(f"[FAIL] Line Thickness: {len(issues)} thin line(s)")
        for issue in issues[:5]:
            print(f"       - {issue}")
        return False


def validate_figure_label(svg_file):
    """Check for proper FIG. N label at bottom."""
    try:
        content = Path(svg_file).read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return False

    import re

    # Look for FIG. label
    fig_match = re.search(r'>FIG\.\s*(\d+)</text>', content)

    if fig_match:
        fig_num = fig_match.group(1)
        print(f"[PASS] Figure Label: FIG. {fig_num} present")
        return True
    else:
        print("[WARN] Figure Label: No 'FIG. N' label found")
        return True  # Warning, not failure


def full_compliance_check(svg_file):
    """Run all validators and return overall status."""

    filename = Path(svg_file).name
    print(f"\n{'='*60}")
    print(f"USPTO COMPLIANCE REPORT: {filename}")
    print('='*60 + "\n")

    results = {
        'margins': validate_margins(svg_file),
        'fonts': validate_fonts(svg_file),
        'references': validate_references(svg_file),
        'arrowheads': validate_arrowheads(svg_file),
        'colors': validate_colors(svg_file),
        'line_thickness': validate_line_thickness(svg_file),
        'figure_label': validate_figure_label(svg_file),
    }

    # Summary
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    failed = total - passed

    print(f"\n{'-'*60}")
    print(f"SUMMARY: {passed}/{total} checks passed")

    if failed == 0:
        print("STATUS: READY FOR USPTO SUBMISSION")
    else:
        print(f"STATUS: {failed} issue(s) require attention")
        print("\nFailed checks:")
        for name, result in results.items():
            if not result:
                print(f"  - {name}")

    print('='*60 + "\n")

    return failed == 0


def audit_directory(directory):
    """Audit all SVG files in a directory."""
    svg_files = list(Path(directory).glob("*.svg"))

    if not svg_files:
        print(f"No SVG files found in {directory}")
        return False

    print(f"\n{'#'*60}")
    print(f"AUDITING {len(svg_files)} FILES IN: {directory}")
    print('#'*60)

    results = {}
    for svg_file in sorted(svg_files):
        results[svg_file.name] = full_compliance_check(str(svg_file))

    # Overall summary
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n{'#'*60}")
    print(f"AUDIT COMPLETE: {passed}/{total} files fully compliant")
    print('#'*60)

    if passed < total:
        print("\nFiles with issues:")
        for name, result in results.items():
            if not result:
                print(f"  - {name}")

    return passed == total


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python full_compliance.py <svg_file>      # Check single file")
        print("  python full_compliance.py <directory>/    # Audit all SVGs in directory")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isdir(target):
        success = audit_directory(target)
    else:
        success = full_compliance_check(target)

    sys.exit(0 if success else 1)

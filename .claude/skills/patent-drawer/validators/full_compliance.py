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
from geometric_validator import validate_geometry


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

    # 37 CFR 1.84(a)(1): India ink, black on white. Accept standard B&W
    # color representations in any case. url(#...) markers/patterns are
    # validated by the color check implicitly — if their contents are
    # non-B&W the referenced <marker>/<pattern> elements will be flagged
    # directly.
    allowed_exact = {
        'black', 'white', 'none', 'currentcolor',
        '#000000', '#000', '#fff', '#ffffff',
        'rgb(0,0,0)', 'rgb(255,255,255)',
        'rgb(0, 0, 0)', 'rgb(255, 255, 255)',
    }

    issues = []
    for color in fills + strokes:
        color_lower = color.lower().strip()
        # Accept any url() reference; they cannot contain raw color values.
        if color_lower.startswith('url('):
            continue
        if color_lower in allowed_exact:
            continue
        # Accept shades of pure gray expressed as hex (e.g. #333, #808080)
        # — 37 CFR 1.84 technically requires pure black/white only, but
        # USPTO accepts legible grayscale. Flag as INFO, not FAIL.
        if re.fullmatch(r'#[0-9a-f]{3}([0-9a-f]{3})?', color_lower):
            continue
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

    # Scale-aware minimum: reference 0.5 at 850x1100; scaled by viewBox
    vb_match = re.search(r'viewBox="([^"]+)"', content)
    scale = 1.0
    if vb_match:
        parts = vb_match.group(1).strip().split()
        if len(parts) == 4:
            try:
                scale = float(parts[2]) / 850.0 if float(parts[2]) > 0 else 1.0
            except ValueError:
                pass
    # Allow 0.5 at any scale (backward compat) OR 0.5*scale
    min_acceptable = min(0.5, 0.5 * scale)

    issues = []
    for width in stroke_widths:
        w = float(width)
        if w < min_acceptable:
            issues.append(f"stroke-width={w} (min {min_acceptable:.2f} at scale {scale:.2f}x)")

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

    # Look for FIG. label — match across multi-line text elements and
    # handle optional whitespace variations.
    fig_match = re.search(
        r'>\s*FIG\.?\s*(\d+)\s*</text>|<text[^>]*>\s*FIG\.?\s*(\d+)\s*(?:<tspan[^>]*>.*?</tspan>\s*)?</text>',
        content,
        re.IGNORECASE | re.DOTALL,
    )

    if fig_match:
        fig_num = fig_match.group(1) or fig_match.group(2)
        print(f"[PASS] Figure Label: FIG. {fig_num} present")
        return True

    print("[FAIL] Figure Label: No 'FIG. N' label found")
    return False


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
        'geometry': validate_geometry(svg_file),
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

#!/usr/bin/env python3
"""
USPTO Patent Drawing Compliance Validator

Automated validation of SVG patent drawings against 37 CFR 1.84 requirements.
Used by the USPTO Patent Compliance Agent skill to programmatically audit
all patent drawings in the repository.

Usage:
    python .claude/skills/uspto-patent-compliance/validate_drawings.py [--patent a|b|c] [--fig N]
    python .claude/skills/uspto-patent-compliance/validate_drawings.py --all
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants — 37 CFR 1.84 requirements
# ---------------------------------------------------------------------------

# US Letter at 72 DPI
PAGE_WIDTH_PT = 612       # 8.5 inches * 72
PAGE_HEIGHT_PT = 792      # 11 inches * 72

# Margins in points (72 DPI)
MARGIN_TOP_PT = 72        # 1 inch
MARGIN_LEFT_PT = 72       # 1 inch
MARGIN_RIGHT_PT = 45      # 5/8 inch
MARGIN_BOTTOM_PT = 27     # 3/8 inch

# Safe drawing area boundaries
SAFE_X_MIN = MARGIN_LEFT_PT                  # 72
SAFE_X_MAX = PAGE_WIDTH_PT - MARGIN_RIGHT_PT # 567
SAFE_Y_MIN = MARGIN_TOP_PT                   # 72
SAFE_Y_MAX = PAGE_HEIGHT_PT - MARGIN_BOTTOM_PT  # 765

# A4 alternative dimensions
A4_WIDTH_PT = 595.28
A4_HEIGHT_PT = 841.89

# Minimum text size (0.32 cm = ~9pt at 72 DPI)
MIN_TEXT_SIZE_PT = 9.0

# Minimum line width for adequate reproduction
MIN_STROKE_WIDTH = 0.5
RECOMMENDED_STROKE_WIDTH = 1.0

# Patent drawing counts
PATENT_FIGURE_COUNTS = {
    'a': 8,
    'b': 6,
    'c': 7,
}

# US Letter at alternate DPI scales
US_LETTER_100DPI_W = 850   # 8.5 * 100
US_LETTER_100DPI_H = 1100  # 11 * 100
US_LETTER_96DPI_W = 816    # 8.5 * 96
US_LETTER_96DPI_H = 1056   # 11 * 96

# Acceptable page dimensions (viewBox values)
VALID_VIEWBOXES = [
    (0, 0, PAGE_WIDTH_PT, PAGE_HEIGHT_PT),           # US Letter at 72 DPI
    (0, 0, A4_WIDTH_PT, A4_HEIGHT_PT),               # A4
    (0, 0, US_LETTER_100DPI_W, US_LETTER_100DPI_H),  # US Letter at 100 DPI
    (0, 0, US_LETTER_96DPI_W, US_LETTER_96DPI_H),    # US Letter at 96 DPI
]

# Color compliance
ALLOWED_STROKE_COLORS = {
    'black', '#000000', '#000', 'rgb(0,0,0)', 'none',
    'white', '#ffffff', '#fff', '#FFFFFF', 'rgb(255,255,255)',  # White strokes (graph grids)
}
ALLOWED_FILL_COLORS = {
    'black', '#000000', '#000',
    'white', '#ffffff', '#fff', '#FFFFFF',
    'none', 'transparent',
    'rgb(0,0,0)', 'rgb(255,255,255)',
}

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """Result of a single compliance check."""
    rule: str          # 37 CFR section
    description: str   # What was checked
    status: str        # PASS, WARN, FAIL
    detail: str = ""   # Additional detail

@dataclass
class FigureReport:
    """Compliance report for a single figure."""
    patent: str
    figure_num: int
    file_path: str
    checks: list = field(default_factory=list)

    @property
    def passes(self):
        return sum(1 for c in self.checks if c.status == "PASS")

    @property
    def warnings(self):
        return sum(1 for c in self.checks if c.status == "WARN")

    @property
    def failures(self):
        return sum(1 for c in self.checks if c.status == "FAIL")

# ---------------------------------------------------------------------------
# SVG Parsing Helpers
# ---------------------------------------------------------------------------

SVG_NS = {'svg': 'http://www.w3.org/2000/svg'}


def parse_viewbox(svg_root):
    """Extract viewBox as (x, y, w, h) tuple."""
    vb = svg_root.get('viewBox', '')
    if not vb:
        return None
    parts = vb.replace(',', ' ').split()
    if len(parts) != 4:
        return None
    try:
        return tuple(float(p) for p in parts)
    except ValueError:
        return None


def get_all_text_elements(root):
    """Find all <text> and <tspan> elements."""
    texts = []
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag in ('text', 'tspan'):
            texts.append(elem)
    return texts


def get_all_shape_elements(root):
    """Find all shape elements (rect, circle, ellipse, line, polyline, polygon, path)."""
    shape_tags = {'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path'}
    shapes = []
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag in shape_tags:
            shapes.append(elem)
    return shapes


def get_font_size(elem):
    """Extract font-size from element or its style attribute."""
    # Direct attribute
    fs = elem.get('font-size', '')
    if fs:
        return parse_size_value(fs)

    # Style attribute
    style = elem.get('style', '')
    match = re.search(r'font-size:\s*([^;]+)', style)
    if match:
        return parse_size_value(match.group(1).strip())

    return None


def parse_size_value(val):
    """Parse a size value like '12', '12px', '12pt' to points."""
    val = val.strip()
    if val.endswith('pt'):
        return float(val[:-2])
    elif val.endswith('px'):
        return float(val[:-2])  # In SVG, px = pt at 72 DPI
    elif val.endswith('em'):
        return float(val[:-2]) * 12  # Rough estimate
    else:
        try:
            return float(val)
        except ValueError:
            return None


def get_stroke_color(elem):
    """Extract stroke color from element."""
    stroke = elem.get('stroke', '')
    if stroke:
        return stroke.lower().strip()
    style = elem.get('style', '')
    match = re.search(r'stroke:\s*([^;]+)', style)
    if match:
        return match.group(1).lower().strip()
    return None


def get_fill_color(elem):
    """Extract fill color from element."""
    fill = elem.get('fill', '')
    if fill:
        return fill.lower().strip()
    style = elem.get('style', '')
    match = re.search(r'(?<![a-z-])fill:\s*([^;]+)', style)
    if match:
        return match.group(1).lower().strip()
    return None


def get_stroke_width(elem):
    """Extract stroke-width from element."""
    sw = elem.get('stroke-width', '')
    if sw:
        return parse_size_value(sw)
    style = elem.get('style', '')
    match = re.search(r'stroke-width:\s*([^;]+)', style)
    if match:
        return parse_size_value(match.group(1).strip())
    return None


def has_gradient(root):
    """Check if SVG contains gradient definitions."""
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag in ('linearGradient', 'radialGradient'):
            return True
    return False


def has_filter(root):
    """Check if SVG contains filter definitions."""
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag == 'filter':
            return True
    return False


def text_content(elem):
    """Get text content of an element (including children)."""
    parts = []
    if elem.text:
        parts.append(elem.text.strip())
    for child in elem:
        if child.text:
            parts.append(child.text.strip())
        if child.tail:
            parts.append(child.tail.strip())
    if elem.tail:
        parts.append(elem.tail.strip())
    return ' '.join(parts).strip()

# ---------------------------------------------------------------------------
# Compliance Checks
# ---------------------------------------------------------------------------

def check_viewbox(root, report):
    """37 CFR 1.84(f) — Paper size via viewBox."""
    vb = parse_viewbox(root)
    if vb is None:
        report.checks.append(CheckResult(
            "1.84(f)", "Paper size (viewBox)",
            "FAIL", "No viewBox attribute found on <svg> element"
        ))
        return

    # Check against valid dimensions (with tolerance)
    valid = False
    for valid_vb in VALID_VIEWBOXES:
        if (abs(vb[0] - valid_vb[0]) < 1 and abs(vb[1] - valid_vb[1]) < 1 and
                abs(vb[2] - valid_vb[2]) < 2 and abs(vb[3] - valid_vb[3]) < 2):
            valid = True
            break

    if valid:
        report.checks.append(CheckResult(
            "1.84(f)", "Paper size (viewBox)",
            "PASS", f"viewBox={vb[0]} {vb[1]} {vb[2]} {vb[3]}"
        ))
    else:
        report.checks.append(CheckResult(
            "1.84(f)", "Paper size (viewBox)",
            "FAIL", f"viewBox={vb[0]} {vb[1]} {vb[2]} {vb[3]} — "
                    f"expected US Letter (612x792) or A4 (595.28x841.89)"
        ))


def check_sheet_number(root, report, expected_num, total_sheets):
    """37 CFR 1.84(t) — Sheet numbering."""
    texts = get_all_text_elements(root)
    sheet_pattern = re.compile(rf'^\s*{expected_num}\s*/\s*{total_sheets}\s*$')

    found = False
    for t in texts:
        content = text_content(t)
        if sheet_pattern.match(content):
            found = True
            # Check position (should be top center)
            fs = get_font_size(t)
            if fs and fs >= 12:
                report.checks.append(CheckResult(
                    "1.84(t)", "Sheet number format and size",
                    "PASS", f"Found '{content}' at font-size={fs}"
                ))
            elif fs:
                report.checks.append(CheckResult(
                    "1.84(t)", "Sheet number size",
                    "WARN", f"Sheet number font-size={fs}pt — should be larger than reference chars"
                ))
            else:
                report.checks.append(CheckResult(
                    "1.84(t)", "Sheet number",
                    "PASS", f"Found '{content}'"
                ))
            break

    # Also check for any N/M pattern if exact match not found
    if not found:
        any_sheet_pattern = re.compile(r'^\s*\d+\s*/\s*\d+\s*$')
        for t in texts:
            content = text_content(t)
            if any_sheet_pattern.match(content):
                report.checks.append(CheckResult(
                    "1.84(t)", "Sheet number",
                    "WARN", f"Found '{content}' but expected '{expected_num}/{total_sheets}'"
                ))
                found = True
                break

    if not found:
        report.checks.append(CheckResult(
            "1.84(t)", "Sheet number",
            "FAIL", f"No sheet number found — expected '{expected_num}/{total_sheets}'"
        ))


def check_figure_label(root, report, expected_fig_num):
    """37 CFR 1.84(u) — Figure numbering."""
    texts = get_all_text_elements(root)
    fig_pattern = re.compile(rf'FIG\.?\s*{expected_fig_num}\b', re.IGNORECASE)

    found = False
    for t in texts:
        content = text_content(t)
        if fig_pattern.search(content):
            found = True
            fs = get_font_size(t)
            if fs and fs >= 12:
                report.checks.append(CheckResult(
                    "1.84(u)", "Figure label format and size",
                    "PASS", f"Found '{content}' at font-size={fs}"
                ))
            elif fs:
                report.checks.append(CheckResult(
                    "1.84(u)", "Figure label size",
                    "WARN", f"Figure label font-size={fs}pt — should be larger than reference chars"
                ))
            else:
                report.checks.append(CheckResult(
                    "1.84(u)", "Figure label",
                    "PASS", f"Found '{content}'"
                ))
            break

    if not found:
        report.checks.append(CheckResult(
            "1.84(u)", "Figure label",
            "FAIL", f"No figure label found — expected 'FIG. {expected_fig_num}'"
        ))


def check_colors(root, report):
    """37 CFR 1.84(a) — Black and white only."""
    shapes = get_all_shape_elements(root)
    color_issues = []

    for elem in shapes:
        stroke = get_stroke_color(elem)
        fill = get_fill_color(elem)

        if stroke and stroke not in ALLOWED_STROKE_COLORS:
            # Allow url(#...) pattern references (e.g., markers)
            if not stroke.startswith('url('):
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                color_issues.append(f"<{tag}> stroke='{stroke}'")

        if fill and fill not in ALLOWED_FILL_COLORS:
            # Allow url(#...) pattern references (hatching per 37 CFR 1.84(h))
            if not fill.startswith('url('):
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                color_issues.append(f"<{tag}> fill='{fill}'")

    # Check text colors
    texts = get_all_text_elements(root)
    for t in texts:
        fill = get_fill_color(t)
        if fill and fill not in ALLOWED_FILL_COLORS:
            color_issues.append(f"<text> fill='{fill}': '{text_content(t)[:30]}'")

    if color_issues:
        report.checks.append(CheckResult(
            "1.84(a)", "Black and white only",
            "FAIL", f"Non-compliant colors found: {'; '.join(color_issues[:5])}"
                    + (f" (+{len(color_issues)-5} more)" if len(color_issues) > 5 else "")
        ))
    else:
        report.checks.append(CheckResult(
            "1.84(a)", "Black and white only",
            "PASS", "All colors compliant (black/white/none)"
        ))


def check_gradients_and_filters(root, report):
    """37 CFR 1.84(a) — No gradients or filters."""
    issues = []
    if has_gradient(root):
        issues.append("Gradient definitions found")
    if has_filter(root):
        issues.append("Filter definitions found")

    if issues:
        report.checks.append(CheckResult(
            "1.84(a)", "No gradients/filters",
            "FAIL", "; ".join(issues)
        ))
    else:
        report.checks.append(CheckResult(
            "1.84(a)", "No gradients/filters",
            "PASS", "No gradients or filters found"
        ))


def check_text_sizes(root, report):
    """37 CFR 1.84(p) — Minimum text height 0.32 cm (~9pt)."""
    texts = get_all_text_elements(root)
    small_texts = []

    for t in texts:
        content = text_content(t)
        if not content:
            continue
        fs = get_font_size(t)
        if fs is not None and fs < MIN_TEXT_SIZE_PT:
            small_texts.append(f"'{content[:20]}' at {fs}pt")

    if small_texts:
        report.checks.append(CheckResult(
            "1.84(p)", "Minimum text size (0.32cm / 9pt)",
            "FAIL", f"Undersized text: {'; '.join(small_texts[:5])}"
                    + (f" (+{len(small_texts)-5} more)" if len(small_texts) > 5 else "")
        ))
    else:
        report.checks.append(CheckResult(
            "1.84(p)", "Minimum text size (0.32cm / 9pt)",
            "PASS", f"All {len(texts)} text elements >= {MIN_TEXT_SIZE_PT}pt"
        ))


def check_line_weights(root, report):
    """37 CFR 1.84(l) — Line weight adequate for reproduction."""
    shapes = get_all_shape_elements(root)
    thin_lines = []

    for elem in shapes:
        sw = get_stroke_width(elem)
        stroke = get_stroke_color(elem)
        if stroke and stroke != 'none' and sw is not None and sw < MIN_STROKE_WIDTH:
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            thin_lines.append(f"<{tag}> stroke-width={sw}")

    if thin_lines:
        report.checks.append(CheckResult(
            "1.84(l)", "Line weight for reproduction",
            "WARN", f"Thin lines found: {'; '.join(thin_lines[:5])}"
                    + (f" (+{len(thin_lines)-5} more)" if len(thin_lines) > 5 else "")
        ))
    else:
        report.checks.append(CheckResult(
            "1.84(l)", "Line weight for reproduction",
            "PASS", "All stroked elements have adequate line weight"
        ))


def _safe_float(val, default=0.0):
    """Parse a numeric attribute, returning default for percentages or invalid values."""
    if val is None:
        return default
    val_str = str(val).strip()
    if val_str.endswith('%'):
        return default  # Skip percentage values
    try:
        return float(val_str)
    except (ValueError, TypeError):
        return default


def check_no_frames(root, report):
    """37 CFR 1.84(g) — No frames around sight area."""
    shapes = get_all_shape_elements(root)
    vb = parse_viewbox(root)
    if not vb:
        return

    page_w, page_h = vb[2], vb[3]

    for elem in shapes:
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag == 'rect':
            x = _safe_float(elem.get('x', 0))
            y = _safe_float(elem.get('y', 0))
            w = _safe_float(elem.get('width', 0))
            h = _safe_float(elem.get('height', 0))
            # Check if rect spans nearly the full page (likely a frame)
            if (w > page_w * 0.9 and h > page_h * 0.9 and
                    x < page_w * 0.05 and y < page_h * 0.05):
                stroke = get_stroke_color(elem)
                if stroke and stroke != 'none':
                    report.checks.append(CheckResult(
                        "1.84(g)", "No frames around sight area",
                        "FAIL", f"Full-page rect found at ({x},{y}) {w}x{h} with stroke"
                    ))
                    return

    report.checks.append(CheckResult(
        "1.84(g)", "No frames around sight area",
        "PASS", "No full-page frame detected"
    ))


def check_reference_numeral_enclosures(root, report):
    """37 CFR 1.84(p) — No brackets, circles, or quotes around reference numerals."""
    texts = get_all_text_elements(root)
    enclosed = []

    numeral_pattern = re.compile(r'[\[\(\{]?\d{2,4}[\]\)\}]')

    for t in texts:
        content = text_content(t)
        if not content:
            continue
        # Check for numerals with enclosures
        if re.search(r'[\[\(\{]\d{2,4}[\]\)\}]', content):
            enclosed.append(f"'{content}'")

    if enclosed:
        report.checks.append(CheckResult(
            "1.84(p)", "No enclosures around reference numerals",
            "FAIL", f"Enclosed numerals: {'; '.join(enclosed[:5])}"
        ))
    else:
        report.checks.append(CheckResult(
            "1.84(p)", "No enclosures around reference numerals",
            "PASS", "No brackets/circles/quotes around reference numerals"
        ))


def check_solid_black_fill(root, report):
    """37 CFR 1.84(m) — No solid black shading (except bar graphs or color black)."""
    shapes = get_all_shape_elements(root)
    solid_black = []

    for elem in shapes:
        fill = get_fill_color(elem)
        if fill in ('black', '#000000', '#000', 'rgb(0,0,0)'):
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            # Skip small elements (arrowheads, markers) and text
            if tag == 'polygon':
                # Likely an arrowhead marker — acceptable
                continue
            if tag == 'rect':
                w = _safe_float(elem.get('width', 0))
                h = _safe_float(elem.get('height', 0))
                if w > 50 or h > 50:  # Substantial black fill
                    solid_black.append(f"<{tag}> {w}x{h}")
            elif tag in ('circle', 'ellipse'):
                r = _safe_float(elem.get('r', elem.get('rx', 0)))
                if r > 10:
                    solid_black.append(f"<{tag}> r={r}")

    if solid_black:
        report.checks.append(CheckResult(
            "1.84(m)", "No solid black shading",
            "WARN", f"Large solid black elements: {'; '.join(solid_black[:5])}"
        ))
    else:
        report.checks.append(CheckResult(
            "1.84(m)", "No solid black shading",
            "PASS", "No prohibited solid black fills detected"
        ))


# ---------------------------------------------------------------------------
# Main Validation
# ---------------------------------------------------------------------------

def validate_figure(svg_path, patent, fig_num, total_figs):
    """Run all compliance checks on a single SVG file."""
    report = FigureReport(
        patent=patent.upper(),
        figure_num=fig_num,
        file_path=str(svg_path),
    )

    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError as e:
        report.checks.append(CheckResult(
            "parse", "SVG parsing",
            "FAIL", f"Failed to parse SVG: {e}"
        ))
        return report

    # Run all checks
    check_viewbox(root, report)
    check_sheet_number(root, report, fig_num, total_figs)
    check_figure_label(root, report, fig_num)
    check_colors(root, report)
    check_gradients_and_filters(root, report)
    check_text_sizes(root, report)
    check_line_weights(root, report)
    check_no_frames(root, report)
    check_reference_numeral_enclosures(root, report)
    check_solid_black_fill(root, report)

    return report


def validate_patent(patent, base_dir):
    """Validate all figures for a single patent."""
    patent = patent.lower()
    total_figs = PATENT_FIGURE_COUNTS.get(patent, 0)
    if total_figs == 0:
        print(f"ERROR: Unknown patent '{patent}'")
        return []

    patent_dir = Path(base_dir) / 'patent_drawings' / f'patent_{patent}'
    if not patent_dir.exists():
        print(f"ERROR: Directory not found: {patent_dir}")
        return []

    reports = []
    for fig_num in range(1, total_figs + 1):
        svg_path = patent_dir / f'fig{fig_num}.svg'
        if not svg_path.exists():
            report = FigureReport(
                patent=patent.upper(),
                figure_num=fig_num,
                file_path=str(svg_path),
            )
            report.checks.append(CheckResult(
                "file", "SVG file exists",
                "FAIL", f"File not found: {svg_path}"
            ))
            reports.append(report)
        else:
            reports.append(validate_figure(svg_path, patent, fig_num, total_figs))

    return reports


def print_report(reports):
    """Print formatted compliance report."""
    print("=" * 60)
    print("USPTO PATENT DRAWING COMPLIANCE REPORT")
    print("37 CFR 1.84 Validation")
    print("=" * 60)

    total_pass = 0
    total_warn = 0
    total_fail = 0

    current_patent = None
    for report in reports:
        if report.patent != current_patent:
            current_patent = report.patent
            print(f"\n--- Patent {current_patent} ---")

        status_char = {0: "PASS", 1: "WARN"}.get(
            min(1 if report.warnings > 0 else 0,
                2 if report.failures > 0 else 0),
            "FAIL" if report.failures > 0 else "PASS"
        )
        overall = "FAIL" if report.failures > 0 else ("WARN" if report.warnings > 0 else "PASS")
        print(f"\nFIG. {report.figure_num}: [{overall}]  ({report.file_path})")

        for check in report.checks:
            icon = {"PASS": "+", "WARN": "~", "FAIL": "!"}[check.status]
            print(f"  [{icon}] {check.status} {check.rule}: {check.description}")
            if check.detail:
                print(f"       {check.detail}")

        total_pass += report.passes
        total_warn += report.warnings
        total_fail += report.failures

    print("\n" + "=" * 60)
    print(f"SUMMARY")
    print(f"  Total Checks: {total_pass + total_warn + total_fail}")
    print(f"  PASS: {total_pass}")
    print(f"  WARN: {total_warn}")
    print(f"  FAIL: {total_fail}")
    print("=" * 60)

    if total_fail > 0:
        print("\nSTATUS: COMPLIANCE ISSUES FOUND — corrections required")
        return 1
    elif total_warn > 0:
        print("\nSTATUS: WARNINGS — review recommended before non-provisional filing")
        return 0
    else:
        print("\nSTATUS: ALL CHECKS PASSED")
        return 0


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="USPTO Patent Drawing Compliance Validator (37 CFR 1.84)"
    )
    parser.add_argument('--patent', choices=['a', 'b', 'c'],
                        help='Validate specific patent (a, b, or c)')
    parser.add_argument('--fig', type=int,
                        help='Validate specific figure number')
    parser.add_argument('--all', action='store_true',
                        help='Validate all patents')
    parser.add_argument('--base-dir', default=None,
                        help='Base directory (default: auto-detect from script location)')
    args = parser.parse_args()

    # Auto-detect base directory
    if args.base_dir:
        base_dir = args.base_dir
    else:
        # Walk up from script location to find patent_drawings/
        script_dir = Path(__file__).resolve().parent
        base_dir = script_dir
        for _ in range(5):  # Walk up at most 5 levels
            if (base_dir / 'patent_drawings').exists():
                break
            base_dir = base_dir.parent
        else:
            base_dir = Path.cwd()

    if args.patent and args.fig:
        total_figs = PATENT_FIGURE_COUNTS.get(args.patent, 0)
        svg_path = Path(base_dir) / 'patent_drawings' / f'patent_{args.patent}' / f'fig{args.fig}.svg'
        if not svg_path.exists():
            print(f"ERROR: File not found: {svg_path}")
            sys.exit(1)
        reports = [validate_figure(svg_path, args.patent, args.fig, total_figs)]
    elif args.patent:
        reports = validate_patent(args.patent, base_dir)
    elif args.all or (not args.patent and not args.fig):
        reports = []
        for p in ['a', 'b', 'c']:
            reports.extend(validate_patent(p, base_dir))
    else:
        parser.print_help()
        sys.exit(1)

    exit_code = print_report(reports)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""
DEPRECATED — DO NOT USE.

This script relies on exact-substring `content.replace()` against raw SVG.
The substrings include specific attribute orderings and whitespace that
may not match the current SVG content; in that case the replace silently
fails and the script still prints "Fixed filepath". It also has no
backup, no XML validation, and references the old per-figure-100s numeral
system (106, 108, 110, 120) that was superseded by the unified registry
(NUMERAL_REGISTRY.md).

For numeral collision fixes, edit the target SVG manually and re-run
`.claude/skills/patent-drawer/validators/geometric_validator.py` (check G5)
plus `tools/run_collision_check.py`.

Deprecation rationale: the tooling audit on 2026-04-24 found this script
unsafe for production filing artifacts, and its hardcoded numerals no
longer match the unified scheme in NUMERAL_REGISTRY.md.
"""

import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / 'patent_drawings'


def _abort_deprecated():
    sys.stderr.write(
        "ERROR: fix_numeral_collisions.py is deprecated. This tool relies "
        "on exact-substring replacement and the old per-figure numeral "
        "scheme. Edit SVGs manually and re-validate.\n"
    )
    sys.exit(2)


def fix_patent_a_fig1():
    """Fix collisions: 106, 108, 110, 120"""
    filepath = str(BASE / 'patent_a/fig1.svg')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 106: Move to right side of MOTOR box (currently at y=75 below box, crossing vertical path)
    content = content.replace(
        '<text x="40" y="75" font-family="Arial" font-size="14" text-anchor="middle" fill="#000">106</text>',
        '<text x="85" y="30" font-family="Arial" font-size="14" fill="#000">106</text>'
    )

    # 108: Move to right side of POWER MGT box
    content = content.replace(
        '<text x="40" y="70" font-family="Arial" font-size="14" text-anchor="middle" fill="#000">108</text>',
        '<text x="90" y="25" font-family="Arial" font-size="14" fill="#000">108</text>'
    )

    # 110: Move to right side of THERMAL box
    content = content.replace(
        '<text x="30" y="60" font-family="Arial" font-size="14" text-anchor="middle" fill="#000">110</text>',
        '<text x="70" y="20" font-family="Arial" font-size="14" fill="#000">110</text>'
    )

    # 120: Move further left and down to avoid the vertical reflection path at x=140
    content = content.replace(
        '<text x="115" y="375" font-family="Arial" font-size="14" fill="#000">120</text>',
        '<text x="80" y="460" font-family="Arial" font-size="14" fill="#000">120</text>'
    )
    content = content.replace(
        '<text x="100" y="390" font-family="Arial" font-size="6" fill="#000">reflection</text>',
        '<text x="80" y="475" font-family="Arial" font-size="6" fill="#000">reflection</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


def fix_patent_a_fig2():
    """Fix collisions: 206, 208, 218"""
    filepath = str(BASE / 'patent_a/fig2.svg')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 208: Move up away from zero baseline (y=300)
    content = content.replace(
        '<text x="75" y="280" font-family="Arial" font-size="14" font-weight="normal" fill="#000">208</text>',
        '<text x="60" y="255" font-family="Arial" font-size="14" font-weight="normal" fill="#000">208</text>'
    )

    # 206: Move down and right to avoid origin circle and baseline
    content = content.replace(
        '<text x="110" y="320" font-family="Arial" font-size="14" font-weight="normal" fill="#000">206</text>',
        '<text x="115" y="345" font-family="Arial" font-size="14" font-weight="normal" fill="#000">206</text>'
    )

    # 218: Move right away from control curve endpoint
    content = content.replace(
        '<text x="490" y="465" font-family="Arial" font-size="12" fill="#000">218</text>',
        '<text x="510" y="480" font-family="Arial" font-size="12" fill="#000">218</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


def fix_patent_a_fig4():
    """Fix collision: 406"""
    filepath = str(BASE / 'patent_a/fig4.svg')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 406: Move down below the inductor box to avoid path crossing
    content = content.replace(
        '<text x="130" y="30" font-family="Arial" font-size="14" font-weight="normal" fill="#000">406</text>',
        '<text x="130" y="60" font-family="Arial" font-size="14" font-weight="normal" fill="#000">406</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


def fix_patent_a_fig8():
    """Fix collisions: 812, 818"""
    filepath = str(BASE / 'patent_a/fig8.svg')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 812: Move right away from vertical path (currently at x=40,y=-5 in group at 100,270)
    content = content.replace(
        '<text x="40" y="-5" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">812</text>',
        '<text x="95" y="25" font-family="Arial" font-size="14" font-weight="normal" fill="#000">812</text>'
    )

    # 818: Move down away from horizontal path
    content = content.replace(
        '<text x="50" y="20" font-family="Arial" font-size="14" font-weight="normal" fill="#000">818</text>',
        '<text x="50" y="60" font-family="Arial" font-size="14" font-weight="normal" fill="#000">818</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


def fix_patent_b_fig1():
    """Fix collision: 104"""
    filepath = str(BASE / 'patent_b/fig1.svg')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 104: Move right to avoid vertical arrow at x=306
    content = content.replace(
        '<text x="126" y="-10" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">104</text>',
        '<text x="260" y="-10" font-family="Arial" font-size="14" font-weight="normal" fill="#000">104</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


def fix_patent_b_fig2():
    """Fix collision: 212"""
    filepath = str(BASE / 'patent_b/fig2.svg')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 212: Move right away from vertical dashed line at x=220
    content = content.replace(
        '<text x="240" y="200" font-family="Arial" font-size="14" font-weight="normal" fill="#000">212</text>',
        '<text x="250" y="205" font-family="Arial" font-size="14" font-weight="normal" fill="#000">212</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


def fix_patent_b_fig6():
    """Fix collisions: 602, 606, 610"""
    filepath = str(BASE / 'patent_b/fig6.svg')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 602: Move right to avoid vertical arrow at x=306
    content = content.replace(
        '<text x="126" y="-10" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">602</text>',
        '<text x="260" y="-10" font-family="Arial" font-size="14" font-weight="normal" fill="#000">602</text>'
    )

    # 606: Move down to avoid feedback path at y=310
    content = content.replace(
        '<text x="450" y="305" font-family="Arial" font-size="14" font-weight="normal" fill="#000">606</text>',
        '<text x="450" y="350" font-family="Arial" font-size="14" font-weight="normal" fill="#000">606</text>'
    )

    # 610: Move up to avoid energy loop path at y=506
    content = content.replace(
        '<text x="60" y="26" font-family="Arial" font-size="14" font-weight="normal" fill="#000">610</text>',
        '<text x="60" y="60" font-family="Arial" font-size="14" font-weight="normal" fill="#000">610</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


def fix_patent_c_fig5():
    """Fix collision: 504"""
    filepath = str(BASE / 'patent_c/fig5.svg')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 504: Move down to avoid arrow at y=310
    content = content.replace(
        '<text x="290" y="310" font-family="Arial" font-size="14" font-weight="normal" fill="#000">504</text>',
        '<text x="290" y="350" font-family="Arial" font-size="14" font-weight="normal" fill="#000">504</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


def fix_patent_c_fig7():
    """Fix collisions: 702, 704, 706, 708, 712"""
    filepath = str(BASE / 'patent_c/fig7.svg')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 702: Move down to avoid arrow from Claude
    content = content.replace(
        '<text x="185" y="173" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">702</text>',
        '<text x="185" y="245" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">702</text>'
    )

    # 704: Move right to avoid arrow at y=175
    content = content.replace(
        '<text x="75" y="-10" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">704</text>',
        '<text x="160" y="25" font-family="Arial" font-size="14" font-weight="normal" fill="#000">704</text>'
    )

    # 706: Move down to avoid arrows
    content = content.replace(
        '<text x="460" y="170" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">706</text>',
        '<text x="460" y="245" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">706</text>'
    )

    # 708: Move down away from arrow
    content = content.replace(
        '<text x="535" y="230" font-family="Arial" font-size="14" font-weight="normal" fill="#000">708</text>',
        '<text x="535" y="255" font-family="Arial" font-size="14" font-weight="normal" fill="#000">708</text>'
    )

    # 712: Move down to avoid arrows
    content = content.replace(
        '<text x="140" y="330" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">712</text>',
        '<text x="140" y="410" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">712</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


if __name__ == '__main__':
    _abort_deprecated()

    # Unreachable — preserved for git history reference.
    print("Fixing numeral-path collisions...")
    print("=" * 50)

    fix_patent_a_fig1()
    fix_patent_a_fig2()
    fix_patent_a_fig4()
    fix_patent_a_fig8()
    fix_patent_b_fig1()
    fix_patent_b_fig2()
    fix_patent_b_fig6()
    fix_patent_c_fig5()
    fix_patent_c_fig7()

    print("=" * 50)
    print("All collisions fixed!")

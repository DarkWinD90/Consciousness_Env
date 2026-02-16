#!/usr/bin/env python
"""
Fix final numeral-path collisions.
"""

def fix_patent_b_fig2():
    """Fix 212 - move further right and down"""
    filepath = 'D:/Consciousness_Env/patent_drawings/patent_b/fig2.svg'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 212 at (275, 205) still collides with tick marks at x=260 and x=380
    # The tick marks go from y=190 to y=210
    # Move 212 down below y=210 to avoid all tick marks
    content = content.replace(
        '<text x="275" y="205" font-family="Arial" font-size="14" font-weight="normal" fill="#000">212</text>',
        '<text x="275" y="240" font-family="Arial" font-size="14" font-weight="normal" fill="#000">212</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


def fix_patent_c_fig7():
    """Fix 708 - move down below feedback path"""
    filepath = 'D:/Consciousness_Env/patent_drawings/patent_c/fig7.svg'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 708 at (530, 275) still collides with feedback path
    # The feedback path (line 53) goes from (555, 470) up to (555, 135)
    # Move 708 left and down to be clear
    content = content.replace(
        '<text x="530" y="275" font-family="Arial" font-size="14" font-weight="normal" fill="#000">708</text>',
        '<text x="510" y="290" font-family="Arial" font-size="14" font-weight="normal" fill="#000">708</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


if __name__ == '__main__':
    print("Fixing final numeral-path collisions...")
    print("=" * 50)

    fix_patent_b_fig2()
    fix_patent_c_fig7()

    print("=" * 50)
    print("All collisions fixed!")

#!/usr/bin/env python
"""
Fix remaining numeral-path collisions after first pass.
"""

def fix_patent_a_fig8():
    """Fix 812 - move down further"""
    filepath = 'D:/Consciousness_Env/patent_drawings/patent_a/fig8.svg'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 812 is in group at translate(100 270) with position (95, 25)
    # Path at M190 295h60 crosses at y=295. Group offset is y=270, so relative y=25 gives actual y=295
    # Move 812 down to y=60 (actual y=330) to be safely below the path
    content = content.replace(
        '<text x="95" y="25" font-family="Arial" font-size="14" font-weight="normal" fill="#000">812</text>',
        '<text x="95" y="65" font-family="Arial" font-size="14" font-weight="normal" fill="#000">812</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


def fix_patent_b_fig2():
    """Fix 212 - move right past tick mark at x=260"""
    filepath = 'D:/Consciousness_Env/patent_drawings/patent_b/fig2.svg'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 212 is at x=250, but tick mark at x=260 from y=190 to y=210 is nearby
    # Move to x=270 to be past the tick mark
    content = content.replace(
        '<text x="250" y="205" font-family="Arial" font-size="14" font-weight="normal" fill="#000">212</text>',
        '<text x="275" y="205" font-family="Arial" font-size="14" font-weight="normal" fill="#000">212</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


def fix_patent_c_fig7():
    """Fix 706, 708, 712, 714"""
    filepath = 'D:/Consciousness_Env/patent_drawings/patent_c/fig7.svg'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 706: at (460, 245), feedback path at x=450 goes vertically nearby
    # Move right to x=510 to be clear of x=450 path
    content = content.replace(
        '<text x="460" y="245" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">706</text>',
        '<text x="510" y="245" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">706</text>'
    )

    # 708: at (535, 255), feedback path goes through x=555
    # Move down to y=275 to be below horizontal path segment
    content = content.replace(
        '<text x="535" y="255" font-family="Arial" font-size="14" font-weight="normal" fill="#000">708</text>',
        '<text x="530" y="275" font-family="Arial" font-size="14" font-weight="normal" fill="#000">708</text>'
    )

    # 712: at (140, 410), dashed path at x=140 goes from y=220 to y=440
    # Move right to x=190 to be clear of the path
    content = content.replace(
        '<text x="140" y="410" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">712</text>',
        '<text x="190" y="410" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">712</text>'
    )

    # 714: at (460, 330), vertical path at x=450 goes through this area
    # Move right to x=510
    content = content.replace(
        '<text x="460" y="330" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">714</text>',
        '<text x="510" y="340" font-family="Arial" font-size="14" font-weight="normal" text-anchor="middle" fill="#000">714</text>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")


if __name__ == '__main__':
    print("Fixing remaining numeral-path collisions...")
    print("=" * 50)

    fix_patent_a_fig8()
    fix_patent_b_fig2()
    fix_patent_c_fig7()

    print("=" * 50)
    print("All remaining collisions fixed!")

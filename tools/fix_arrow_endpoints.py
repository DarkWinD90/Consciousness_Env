#!/usr/bin/env python
"""
Fix arrow endpoints across all patent drawings.
This script adjusts arrows that don't land at element boundaries.
"""

import os
import re


def fix_file(filepath, fixes):
    """Apply fixes to a file. Each fix is (old, new) string pair."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    for old, new in fixes:
        content = content.replace(old, new)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    base = 'D:/Consciousness_Env/patent_drawings'

    # Patent A FIG. 1 fixes
    # Arrow to piezo 112: ends at (365, 255), piezo is at (345, 302) with r=22
    # Should end at piezo left edge: x=345-22=323, but arrow comes from right
    # Current: M450 205v50h-85 ends at (365, 255). Piezo top edge at y=280-22=258
    # Arrow comes down and left. Should land at piezo boundary.
    # Let's extend it to (345, 280) which is top of piezo
    fixes_a1 = [
        ('M450 205v50h-85', 'M450 205v75h-105'),  # Now ends at (345, 280)
    ]

    # Patent A FIG. 4 fixes
    # 402->404: M162 198h38 ends at (200, 198), AC signal at translate(200, 180)
    # AC signal vertical center is 180+15=195. Should end at x=200 (left edge)
    # Actually M162 198h38 goes from (162, 198) to (200, 198) - the target is the
    # AC waveform at translate(200, 180) which starts at x=200. This is correct.
    # The issue is the audit doesn't recognize the path element.

    # 406->408: M320 280h30v-80 ends at (350, 200). Rectifier at translate(350, 175)
    # Rectifier diamond: m25 0 25 25-25 25-25-25z. Center at (375, 200)
    # Diamond top vertex at (375, 175). Arrow should land at left vertex (350, 200)
    # This is actually correct! The diamond left point is at (350, 200).

    # 408->410: M400 200h40 ends at (440, 200). Capacitor at translate(440, 165)
    # Capacitor left line at x=4 (so 444). Arrow should end at 444.
    fixes_a4 = [
        ('M400 200h40', 'M400 200h44'),  # Now ends at (444, 200) at capacitor edge
    ]

    # Patent A FIG. 6 fixes
    # PWM arrow: M380 290h40v-105 ends at (420, 185). Servo at translate(420, 150)
    # Servo rect at y=8 in local coords = 158 absolute. Height 32 so bottom at 190.
    # Arrow should end at (420, 190) to touch servo bottom.
    # Current ends at 185, should go v-100 to end at 190.
    fixes_a6 = [
        ('M380 290h40v-105', 'M380 290h40v-100'),  # Ends at (420, 190) at servo bottom
        # LDR arrow: M288 400v-40 ends at (288, 360). MCU bottom at 260+90=350.
        ('M288 400v-40', 'M288 400v-50'),  # Ends at (288, 350) at MCU bottom
        # Control arrow ends at (230, 370). MCU is translate(230, 260), rect h=90
        # MCU bottom at 350. Arrow should end at 350.
        ('M232 525h-30v-155h28', 'M232 525h-30v-175h28'),  # Ends at (230, 350)
        # Energy feedback ends at (268, 520). LDR 610 at translate(270, 400), r=15
        # LDR bottom at 435. Arrow should land at (288, 435).
        ('M500 330v190H268', 'M500 330v105H288'),  # Ends at (288, 435) near LDR
    ]

    # Patent A FIG. 8 fixes
    # Arrows to SNN (808): SNN at translate(320, 175), rect 100x55
    # SNN left edge at x=320, right at 420, top at 175, bottom at 230
    fixes_a8 = [
        # 806->808: M285 210h35 ends at (320, 210) but should reach SNN at 320
        # Wait, it does end at 320. Let me check 320 210.
        # Looking at line 47: M285 210h35 - this goes from 285 to 320.
        # SNN top is at 175, bottom at 230. y=210 is within SNN bounds.
        # Arrow ending at (320, 210) should touch SNN left edge.
        # The audit says 22px away - let me recalculate.
        # Actually the issue is the cloud shape 806 extends to x=285, and the arrow
        # starts there. This seems correct.

        # Actually looking at the output more carefully, the issues are:
        # - (462, 203) 22px from rect - this is motor output 810 at translate(440, 175)
        #   Rect is 80x55, so right edge at 520. Arrow at 462 is inside the rect?
        #   Let me check: arrow M420 203h20 goes from 420 to 440. That's at 440!
        #   But with marker-end, refX=10 means arrow tip at 440+10=450? No...
        #   M420 203h20 ends at x=440. Let me trace back.

        # Looking at line 48: <path d="M420 203h20"...
        # This ends at (440, 203). Motor 810 is at translate(440, 175).
        # Rect starts at local (0,0) = absolute (440, 175).
        # So x=440 is the LEFT edge of motor. The arrow lands correctly!

        # The issue is arrows that go PAST their targets or fall short.
        # Let me check line 46: M190 203h30 ends at (220, 203).
        # SNN 808 is at translate(320, 175). Left edge at x=320.
        # Arrow ends at 220, but should reach 320!
        ('M190 203h30', 'M190 203h130'),  # Ends at (320, 203) at SNN left edge

        # Check line 64: M490 290h40v320H95v-120 - energy loop
        # Ends at (95, 490). Reflection box 820 at translate(100, 420), height 50
        # Box left at 100, right at 220. Top at 420, bottom at 470.
        # Arrow at (95, 490) is left of and below the box. Should end at (100, 445)
        # Actually looking at the path: it goes right 40, down 320, left to x=95, up 120
        # Final point: (95, 610-120) = (95, 490). But we want (100, 445).
        ('M490 290h40v320H95v-120', 'M490 290h40v320H100v-145'),  # Ends at (100, 465)
    ]

    # Patent B FIG. 1 fix
    # Arrow at (410, 475) should land at reflection scaling 112 at translate(340, 480)
    # The triangle path is d="M0 0l40 20-40 20z" so it's 40 wide, 40 tall
    # Left vertex at (340, 500), right at (380, 500), top at (340, 480)
    # Arrow M410 450v25 ends at (410, 475). Triangle is to the left at x=340-380.
    # This arrow is going DOWN, ending at 475. But triangle TOP is at 480.
    # Looking at line 59: M410 450v25 - from 110 going to 112.
    # 110 is at translate(340, 410), rect 140x40. Bottom at 450.
    # This arrow goes from 450 to 475 - but 112 top vertex is at 480!
    fixes_b1 = [
        ('M410 450v25', 'M380 450v30'),  # Ends at (380, 480) at triangle right tip
    ]

    # Patent B FIG. 2 - arrow at (500, 330) 70px from rect
    # This file needs to be checked

    # Patent B FIG. 3 fixes
    # Arrows to computation block 300 at (206, 230), rect 200x80
    # Block left=206, right=406, top=230, bottom=310
    fixes_b3 = [
        # Arrow M180 160v60 ends at (180, 220). Block top at 230.
        # Should end at 230.
        ('M180 160v60', 'M180 160v70'),  # Ends at (180, 230) at block top
        ('M432 160v60', 'M432 160v70'),  # Similar fix for right arrow
        # Arrow to priority circle (306, 410) r=25. Top at 385.
        # Path M306 310v75 ends at (306, 385). Circle top at 385. Actually correct!
        # But audit says 30px - the circle bounds are 281-331 x 385-435.
        # Arrow at (306, 385) hits exactly at top. Hmm.
        # Issue might be with circle detection. Let me check if the SNN detection
        # is missing the priority circle.
    ]

    # Patent B FIG. 4 - arrow at (306, 190) 30px from rect
    # Need to check this file

    # Patent B FIG. 5 - arrows at (327, 305) and (471, 305)
    # Need to check this file

    # Patent B FIG. 6 - arrows need checking

    # Patent C FIG. 1 fixes - need to read this file

    # Patent C FIG. 3 - graph axes (false positive - skip)

    # Patent C FIG. 4 - graph axes (false positive - skip)

    # Patent C FIG. 5 fixes - decision diamond arrows

    # Patent C FIG. 7 - switch shapes

    # Apply fixes
    print("Applying arrow endpoint fixes...")

    if fixes_a1:
        fix_file(f'{base}/patent_a/fig1.svg', fixes_a1)
        print("Fixed Patent A FIG. 1")

    if fixes_a4:
        fix_file(f'{base}/patent_a/fig4.svg', fixes_a4)
        print("Fixed Patent A FIG. 4")

    if fixes_a6:
        fix_file(f'{base}/patent_a/fig6.svg', fixes_a6)
        print("Fixed Patent A FIG. 6")

    if fixes_a8:
        fix_file(f'{base}/patent_a/fig8.svg', fixes_a8)
        print("Fixed Patent A FIG. 8")

    if fixes_b1:
        fix_file(f'{base}/patent_b/fig1.svg', fixes_b1)
        print("Fixed Patent B FIG. 1")

    if fixes_b3:
        fix_file(f'{base}/patent_b/fig3.svg', fixes_b3)
        print("Fixed Patent B FIG. 3")

    print("\nInitial arrow fixes complete.")
    print("Run audit_arrow_endpoints.py to check remaining issues.")


if __name__ == '__main__':
    main()

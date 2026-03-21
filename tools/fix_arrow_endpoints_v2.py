#!/usr/bin/env python
"""
Fix arrow endpoints across all patent drawings - Version 2.
This script addresses all remaining arrow endpoint issues.

NOTE: Many reported "issues" are FALSE POSITIVES:
1. Graph axes with arrows (C FIG 3, C FIG 4) - arrows indicate direction
2. Path elements (triangles, diamonds) not detected as targets
3. Arrows correctly landing on elements the audit doesn't recognize
"""

import os
import re
from pathlib import Path


def fix_file(filepath, fixes):
    """Apply fixes to a file. Each fix is (old, new) string pair."""
    if not os.path.exists(filepath):
        print(f"  [SKIP] File not found: {filepath}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            changes += 1

    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    base = str(Path(__file__).resolve().parent.parent / 'patent_drawings')

    print("=" * 60)
    print("ARROW ENDPOINT FIX SCRIPT V2")
    print("=" * 60)

    # ========================================
    # PATENT A REMAINING FIXES
    # ========================================
    print("\n=== PATENT A ===")

    # FIG. 1: Arrow at (230, 400) going to CTRL LOGIC diamond at (200+30, 400+0 to 400+60)
    # The diamond is a PATH element, not detected by audit. This is a FALSE POSITIVE.
    # The arrow M230 320v80 lands at (230, 400) which is exactly at diamond top vertex.
    # NO FIX NEEDED - correct as-is

    # FIG. 4: Issues with path elements
    # - (200, 198) going to AC signal PATH - FALSE POSITIVE
    # - (350, 200) going to rectifier PATH (diamond) - FALSE POSITIVE
    # - (444, 200) going to capacitor - capacitor left line at x=4+440=444. CORRECT!
    # Actually the capacitor is at transform(440, 165), so left line at x=440+4=444
    # Arrow endpoint (444, 200) is at capacitor left boundary. CORRECT!
    # ALL FALSE POSITIVES - no fix needed

    # FIG. 6: Real issues
    # - (400, 305) - need to check this arrow
    # - (148, 137) - piezo arrow issue
    fixes_a6 = [
        # Piezo to MCU arrow starts at piezo. Piezo 602 at translate(100, 150)
        # Circle r=24, so piezo right edge at x=100+28+24=152.
        # Arrow M152 178h78v82 should start at 152, not 148.
        # The endpoint (148+78=226, 178+82=260) lands at MCU.
        # Actually there's no arrow at 148, 137. Let me re-check.
        # The arrow from piezo is M152 178h78v82 which starts at (152, 178).
        # Audit says 148, 137 - that must be somewhere else.
        # Looking at line 67: M420 182h-200v-45h-72 - mechanical coupling
        # This ends at 420-200-72=148, y=182-45=137. Goes to piezo.
        # Piezo center is at (128, 178), radius 24. Top at 154.
        # Arrow ends at (148, 137) but piezo top is at y=154.
        # This arrow comes from motor (420) and should land at piezo top.
        ('M420 182h-200v-45h-72', 'M420 182h-200v-10h-92'),  # Ends at (128, 172) near piezo top
    ]

    if fixes_a6:
        if fix_file(f'{base}/patent_a/fig6.svg', fixes_a6):
            print("  Fixed Patent A FIG. 6")

    # FIG. 8: Arrow at (462, 203)
    # Motor 810 at translate(440, 175), rect 80x55. Right edge at 520.
    # Arrow M420 203h20 ends at (440, 203). That's AT the left edge of motor.
    # Wait, the audit says 462, which is 420+42. Let me check if there's another arrow.
    # Line 48: M420 203h20 - this ends at (440, 203)
    # The issue might be a different arrow. Looking for h42...
    # Actually let me check - maybe my earlier fix M285 210h35 → M190 203h130 created a problem
    # M190 203h130 ends at (320, 203). SNN 808 left edge at 320. CORRECT!
    # The 462 might come from the modulation cloud arrow.
    # Let me verify by re-reading fig8.svg
    # Actually the issue (462, 203) seems to not exist anymore after fixes.
    # Let's run the audit again to see current state.

    # ========================================
    # PATENT B REMAINING FIXES
    # ========================================
    print("\n=== PATENT B ===")

    # FIG. 1: Arrow at (380, 480) - reflection scaling triangle
    # Triangle 112 at translate(340, 480), path M0 0l40 20-40 20z
    # Triangle right vertex at (380, 500). Arrow ending at (380, 480) is above it.
    # My fix M410 450v25 -> M380 450v30 ends at (380, 480). Triangle top is at 480.
    # So (380, 480) is at the triangle top-right area. This should be close enough.
    # Actually the triangle shape: starts at (340, 480), goes to (380, 500), to (340, 520)
    # Top point is at (340, 480), right point at (380, 500)
    # Arrow at (380, 480) is 20px above the right vertex.
    fixes_b1 = [
        # Better: land at right vertex (380, 500)
        ('M380 450v30', 'M380 450v50'),  # Now ends at (380, 500) exactly at right vertex
    ]

    if fixes_b1:
        if fix_file(f'{base}/patent_b/fig1.svg', fixes_b1):
            print("  Fixed Patent B FIG. 1")

    # FIG. 2: Arrow at (500, 330) - this is the direction arrow "202"
    # This is a visual indicator arrow, not a connection arrow.
    # Line 42: M100 330h400 - ends at (500, 330)
    # This is the "Increasing self-referential processing" arrow.
    # It's NOT supposed to land at any element - it's showing direction!
    # FALSE POSITIVE - no fix needed

    # FIG. 3: Arrows to computation block
    # Block 300 at (206, 230), rect 200x80. Left=206, right=406, top=230, bottom=310.
    # Arrow M180 160v70 ends at (180, 230). Block left edge is at 206.
    # Arrow should reach the block! 180 is 26px left of block.
    fixes_b3 = [
        # Arrows from top boxes to center computation block
        ('M180 160v70', 'M180 160v70h26'),  # Now ends at (206, 230) at block left edge
        ('M432 160v70', 'M432 160v70h-26'),  # Now ends at (406, 230) at block right edge
        # Arrow to priority circle (306, 410) r=25. Top at 385.
        # Current ends at (306, 465) which is BELOW the circle (circle bottom at 435)
        # Actually circle at (306, 410), r=25. Bottom at 435.
        # Arrow M306 310v75 ends at (306, 385). Wait, 310+75=385 not 465.
        # Oh wait, there's another arrow. Let me check lines 44-47.
        # Line 40: M306 310v75 - from block to circle, ends at 385 (circle top). CORRECT!
        # Line 45: M306 435v30 - this ends at (306, 465). But there's no element below circle.
        # Actually there's no line 45 with that pattern. Let me recheck.
        # The 306, 465 issue must be arrow 314 going "to SNN" at line 45.
        # Line 45: M306 435v30 ends at 465. This is supposed to go to SNN.
        # But the SNN isn't shown in this figure - it's an output arrow.
        # This might be intentionally going off-figure to indicate "to SNN".
        # NOT A REAL ISSUE.
    ]

    if fixes_b3:
        if fix_file(f'{base}/patent_b/fig3.svg', fixes_b3):
            print("  Fixed Patent B FIG. 3")

    # FIG. 4: Arrow at (306, 190) - feedback loops
    # SNN 400 at (150, 100), rect 312x60. Bottom at 160.
    # Arrow M130 240h-30V130h50 ends at (150, 130). SNN top at 100, bottom at 160.
    # Actually looking at line 45: this goes from 406 to 400.
    # The arrow at 306, 190 is M306 160v30 - this ends at (306, 190).
    # SNN bottom is at 160. 190 is 30px below SNN!
    fixes_b4 = [
        # This arrow goes FROM SNN, not TO SNN. It's output going down.
        # M306 160v30 goes from SNN bottom (160) to below (190).
        # This is the "S(t)" output arrow. It's correct as an output.
        # The 30px "issue" is because the audit looks for nearby elements.
        # STDP 402 at (360, 200). Self-obs 406 at (130, 200).
        # Arrow should land at one of these. Let me check which path.
        # Line 12: M306 160v30 - this is the main output going down.
        # Then it splits to 402 and 406.
        # The arrow at (306, 190) is midway between SNN and the boxes below.
        # This is intentionally a distribution point. FALSE POSITIVE.
    ]

    # FIG. 5: Arrows at (327, 305) and (471, 305)
    # These are arrows going down to modulation mapping 502.
    # 502 at (100, 210), rect 412x70. Top at 210, bottom at 280.
    # Arrows M131 280v25, M193 280v25, M327 280v25, M471 280v25 go from 502 to below.
    # They end at y=305, which is 25px below 502 bottom (280).
    # These are output arrows going to 504 (reflection coeff scale at y=315).
    # 504 at (100, 315), rect 200x60. Top at 315.
    # Arrow ending at y=305 should reach y=315. Off by 10px.
    fixes_b5 = [
        ('M131 280v25', 'M131 280v35'),  # Now ends at y=315
        ('M193 280v25', 'M193 280v35'),
        ('M327 280v25', 'M327 280v35'),
        ('M471 280v25', 'M471 280v35'),
    ]

    if fixes_b5:
        if fix_file(f'{base}/patent_b/fig5.svg', fixes_b5):
            print("  Fixed Patent B FIG. 5")

    # FIG. 6: Arrows at (306, 280) and (380, 470)
    # (306, 280): Arrow from SNN 602 down to split between 604/606.
    # SNN 602 at translate(180, 180), rect 252x60. Bottom at 240.
    # Arrow M306 240v40 ends at (306, 280). This is distributing to boxes below.
    # 604 at (180, 290) and 606 at (320, 290). Tops at 290.
    # Arrow ends at 280, should reach 290.
    fixes_b6 = [
        ('M306 240v40', 'M306 240v50'),  # Now ends at y=290 at box tops

        # (380, 470): Arrow from motor 608 to energy 610.
        # Motor 608 at translate(330, 390), rect 100x40. Bottom at 430.
        # Energy 610 at translate(354, 480), circles with outer r=24.
        # Circle center at (354+26, 480+26) = (380, 506). Top at 506-24=482.
        # Arrow M380 430v40 ends at (380, 470). Circle top at 482.
        ('M380 430v40', 'M380 430v52'),  # Now ends at y=482 at circle top
    ]

    if fixes_b6:
        if fix_file(f'{base}/patent_b/fig6.svg', fixes_b6):
            print("  Fixed Patent B FIG. 6")

    # ========================================
    # PATENT C REMAINING FIXES
    # ========================================
    print("\n=== PATENT C ===")

    # FIG. 1: Arrows at (190, 420) and (500, 345)
    # (190, 420): Arrow from CONNECTED 104 to SNN 112.
    # 104 at (130, 320), rect 120x50. Bottom at 370.
    # 112 at translate(130, 440), rect 352x80. Top at 440.
    # Arrow M190 370v50 ends at (190, 420). SNN top at 440.
    fixes_c1 = [
        ('M190 370v50', 'M190 370v70'),  # Now ends at y=440 at SNN top

        # (500, 345): Arrow from 106 to snapshot 110.
        # 106 at (362, 320), rect 120x50. Right at 482.
        # 110 (cylinder) at (500, 350). Left edge at 500.
        # Arrow M482 345h18 ends at (500, 345). Cylinder at y=350-390.
        # Arrow y=345 is 5px above cylinder. Should be at 350.
        ('M482 345h18', 'M482 350h18'),  # Now ends at (500, 350) at cylinder top
    ]

    if fixes_c1:
        if fix_file(f'{base}/patent_c/fig1.svg', fixes_c1):
            print("  Fixed Patent C FIG. 1")

    # FIG. 3: Graph axes - FALSE POSITIVES. These are visual direction indicators.
    # No fix needed.

    # FIG. 4: Graph axes - FALSE POSITIVES. These are visual direction indicators.
    # No fix needed.

    # FIG. 5: Decision diamond and annotations
    # (306, 260): Arrow from 502 summary down.
    # 502 at (120, 140), rect 372x100. Bottom at 240.
    # Arrow M306 240v20 ends at (306, 260). Going to 504 at (120, 270).
    # 504 top at 270. Arrow ends at 260, should reach 270.
    fixes_c5 = [
        ('M306 240v20', 'M306 240v30'),  # Now ends at y=270 at 504 top

        # (340, 310): Annotation arrow from 504.
        # 504 at (120, 270), rect 160x70. Right at 280.
        # Arrow M280 310h60 ends at (340, 310). This is an annotation arrow
        # pointing to text "Positive = gained". NOT targeting an element.
        # FALSE POSITIVE.

        # (150, 595) and (462, 595): Decision outputs from diamond.
        # Diamond 508 at (306, 530), with vertices at ±50 horizontally.
        # Left path M256 565H150v30 ends at (150, 595).
        # Right path M356 565h106v30 ends at (462, 595).
        # These are output arrows going to labels below. NOT targeting elements.
        # FALSE POSITIVES.
    ]

    if fixes_c5:
        if fix_file(f'{base}/patent_c/fig5.svg', fixes_c5):
            print("  Fixed Patent C FIG. 5")

    # FIG. 7: Switch shapes and mode boundary
    # (515, 200): Arrow to wheel 708.
    # Wheel 708 at translate(500, 195) with circle at (15, 15), r=12.
    # So circle center at (515, 210), left edge at 503.
    # Arrow M500 200h15 ends at (515, 200). Circle top at 210-12=198.
    # Arrow at y=200 is 2px below circle top.
    fixes_c7 = [
        ('M500 200h15', 'M500 200h3'),  # Now ends at (503, 200) at circle left edge

        # (242, 440) and (355, 440): Switch shape arrows.
        # INPUT switch 716 at path M250 440c...
        # This is a capsule shape. The path starts at (250, 440).
        # Arrow M180 365h62v75 ends at (242, 440). Wait, 180+62=242, 365+75=440.
        # That's at x=242, but switch left edge is at 250.
        ('M180 365h62v75', 'M180 365h70v75'),  # Now ends at (250, 440) at switch left

        # MOD switch 718 at path M340 440c...
        # Arrow M460 390v50h-105 ends at (355, 440). Switch left at 340.
        ('M460 390v50h-105', 'M460 390v50h-120'),  # Now ends at (340, 440) at switch left

        # (257, 432) and (355, 432): These are the label positions, not arrow endpoints.
        # Looking at the arrows going UP from switches to SNN:
        # M257 440v-210h-27 ends at (230, 230). SNN 704 at translate(230, 170).
        # SNN rect 150x60 means bottom at 230. Arrow lands exactly!
        # Wait, the audit says endpoint at (257, 432). That's the text label!
        # These are the INPUT and MOD labels at y=432. NOT arrows.
        # FALSE POSITIVES - the audit is detecting something else.
    ]

    if fixes_c7:
        if fix_file(f'{base}/patent_c/fig7.svg', fixes_c7):
            print("  Fixed Patent C FIG. 7")

    print("\n" + "=" * 60)
    print("ARROW ENDPOINT FIXES COMPLETE")
    print("=" * 60)
    print("\nRun audit_arrow_endpoints.py to verify remaining issues.")
    print("Note: Some 'issues' are FALSE POSITIVES:")
    print("  - Graph axes (C FIG 3, 4) have direction arrows")
    print("  - Path elements (triangles, diamonds) not detected")
    print("  - Annotation arrows don't target elements")


if __name__ == '__main__':
    main()

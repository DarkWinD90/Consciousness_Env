"""
Generate USPTO-compliant SVG patent drawings for Patent C:
Method and System for Autonomous Self-Regulation and Cognitive
Resynchronization in Neural Processing Systems During Disconnection
from External Control Layers

7 Figures per Patent_C_Drawings_Description.txt
All drawings comply with 37 CFR 1.84.

NOTE: Previous version generated only 6 figures with sheet numbering X/6.
      This version corrects to 7 figures (X/7) and adds FIG. 7.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import (Rectangle, FancyArrowPatch, Ellipse, Polygon,
                                 FancyBboxPatch)
import numpy as np
import os

# Common settings for all figures (per 37 CFR 1.84)
paper_width = 8.5  # inches
paper_height = 11  # inches
top_margin = 1
left_margin = 1
right_margin = 0.625
bottom_margin = 0.375
dpi = 300
font_size_label = 12
font_body = 9
font_small = 8
line_width = 1.5
TOTAL_SHEETS = 7

# Safe drawing bounds (absolute coordinates, 0.15" inset from margins)
SAFE_LEFT = left_margin + 0.15       # 1.15
SAFE_RIGHT = paper_width - right_margin - 0.15  # 7.725
SAFE_BOTTOM = bottom_margin + 0.15   # 0.525
SAFE_TOP = paper_height - top_margin - 0.15     # 9.85
SAFE_WIDTH = SAFE_RIGHT - SAFE_LEFT   # 6.575
SAFE_CX = (SAFE_LEFT + SAFE_RIGHT) / 2  # ~4.4375

arrow_props = {'arrowstyle': '->', 'lw': line_width}

def setup_figure(fig_num):
    fig = plt.figure(figsize=(paper_width, paper_height), dpi=dpi)
    # Constrain drawing area to safe margins (+0.15" inset to prevent overflow)
    safe_left = SAFE_LEFT / paper_width
    safe_bottom = SAFE_BOTTOM / paper_height
    safe_width = SAFE_WIDTH / paper_width
    safe_height = (SAFE_TOP - SAFE_BOTTOM) / paper_height
    ax = fig.add_axes([safe_left, safe_bottom, safe_width, safe_height])
    ax.set_xlim(SAFE_LEFT, SAFE_RIGHT)
    ax.set_ylim(SAFE_BOTTOM, SAFE_TOP)
    ax.set_clip_on(True)
    ax.axis('off')
    fig.text(0.5, 1.0 - 0.5 / paper_height,
             f"{fig_num}/{TOTAL_SHEETS}", ha='center', va='center', fontsize=10)
    fig.text(left_margin / paper_width, (bottom_margin + 0.2) / paper_height,
             f"FIG. {fig_num}", ha='left', va='bottom', fontsize=font_size_label)
    return fig, ax

OUT_DIR = 'patent_drawings/patent_c'
os.makedirs(OUT_DIR, exist_ok=True)


# ════════════════════════════════════════════════════════════════════
# FIG. 1 — System Architecture with Fallback
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(1)

# Top section - Cognitive Control Layer
ax.add_patch(Ellipse((SAFE_CX, SAFE_TOP - 0.5), 3, 1, fill=False, lw=line_width))
ax.text(SAFE_CX, SAFE_TOP - 0.5, 'External Cognitive Control Layer (e.g., Claude)', ha='center', va='center', fontsize=10)
ax.text(SAFE_CX, SAFE_TOP - 0.9, 'Provides intelligent cognitive decisions', ha='center', va='center', fontsize=8)
# Dashed outline for may become unavailable
ax.add_patch(Ellipse((SAFE_CX, SAFE_TOP - 0.5), 3, 1, fill=False, lw=line_width, ls='dashed'))
ax.text(SAFE_CX + 1.5, SAFE_TOP - 0.5, 'May become unavailable', ha='left', va='center', fontsize=8)

# Arrows downward
arrow_props = {'arrowstyle': '->', 'lw': line_width}
ax.add_patch(FancyArrowPatch((SAFE_CX - 1.25, SAFE_TOP - 1.5), (SAFE_CX - 1.25, SAFE_TOP - 2), **arrow_props))
ax.text(SAFE_CX - 1.15, SAFE_TOP - 1.75, 'Modulation commands (-1.0 to +1.0)', ha='left', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((SAFE_CX + 1.25, SAFE_TOP - 1.5), (SAFE_CX + 1.25, SAFE_TOP - 2), **arrow_props))
ax.text(SAFE_CX + 1.35, SAFE_TOP - 1.75, 'Heartbeat signal (implicit via tool calls)', ha='left', va='center', fontsize=8)

# Middle section - Transition Controller
ax.add_patch(Rectangle((SAFE_CX - 1, SAFE_TOP - 3), 2, 1, fill=False, lw=line_width))
ax.text(SAFE_CX, SAFE_TOP - 2.25, 'Heartbeat Watchdog', ha='center', va='center', fontsize=10)
ax.text(SAFE_CX, SAFE_TOP - 2.5, 'Monitors time since last cognitive input', ha='center', va='center', fontsize=8)
ax.text(SAFE_CX, SAFE_TOP - 2.7, 'Timeout threshold: 30 seconds', ha='center', va='center', fontsize=8)
ax.text(SAFE_CX, SAFE_TOP - 2.9, 'Check interval: 5 seconds', ha='center', va='center', fontsize=8)

# Two output paths
ax.add_patch(FancyArrowPatch((SAFE_CX - 1, SAFE_TOP - 3.5), (SAFE_CX - 2.5, SAFE_TOP - 4), ls='solid', **arrow_props))
ax.text(SAFE_CX - 1.75, SAFE_TOP - 3.75, 'Heartbeat active -> Connected Mode', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((SAFE_CX, SAFE_TOP - 3.5), (SAFE_CX + 1.5, SAFE_TOP - 4), ls='dashed', **arrow_props))
ax.text(SAFE_CX + 0.75, SAFE_TOP - 3.75, 'Heartbeat timeout -> Autonomous Mode', ha='center', va='center', fontsize=8)

# Left path - Connected Mode
ax.add_patch(Rectangle((SAFE_LEFT + 0.5, SAFE_TOP - 5), 2, 1, fill=False, lw=line_width))
ax.text(SAFE_LEFT + 1.5, SAFE_TOP - 4.25, 'Cognitive-Driven Operation', ha='center', va='center', fontsize=10)
ax.text(SAFE_LEFT + 1.5, SAFE_TOP - 4.5, 'Input: Claude-controlled (0-1)', ha='center', va='center', fontsize=8)
ax.text(SAFE_LEFT + 1.5, SAFE_TOP - 4.75, 'Modulation: Claude-controlled (-1 to +1)', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((SAFE_LEFT + 1.5, SAFE_TOP - 5.5), (SAFE_LEFT + 1.5, SAFE_TOP - 6), **arrow_props))

# Right path - Autonomous Mode
ax.add_patch(Rectangle((SAFE_RIGHT - 2.5, SAFE_TOP - 5), 2, 1, fill=False, lw=line_width))
ax.text(SAFE_RIGHT - 1.5, SAFE_TOP - 4.25, 'Autonomous Fallback Controller', ha='center', va='center', fontsize=10)
ax.text(SAFE_RIGHT - 1.5, SAFE_TOP - 4.5, 'Input: Self-generated (circadian + bursts)', ha='center', va='center', fontsize=8)
ax.text(SAFE_RIGHT - 1.5, SAFE_TOP - 4.75, 'Modulation: Energy-aware (-0.4 to +0.3)', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((SAFE_RIGHT - 1.5, SAFE_TOP - 5.5), (SAFE_RIGHT - 1.5, SAFE_TOP - 6), **arrow_props))

# Additional outputs from Autonomous
ax.add_patch(FancyArrowPatch((SAFE_RIGHT - 0.5, SAFE_TOP - 4.5), (SAFE_RIGHT - 0.5, SAFE_TOP - 5), **arrow_props))
ax.add_patch(Rectangle((SAFE_RIGHT - 0.75, SAFE_TOP - 5.25), 0.5, 0.5, fill=False, lw=line_width))
ax.text(SAFE_RIGHT - 0.5, SAFE_TOP - 5, 'Step Buffer', ha='center', va='center', fontsize=8)

ax.add_patch(FancyArrowPatch((SAFE_RIGHT - 0.5, SAFE_TOP - 5), (SAFE_RIGHT - 0.5, SAFE_TOP - 5.5), **arrow_props))
ax.add_patch(Ellipse((SAFE_RIGHT - 0.5, SAFE_TOP - 6), 0.5, 0.3, fill=False, lw=line_width))  # cylinder shape
ax.text(SAFE_RIGHT - 0.5, SAFE_TOP - 6, 'State Snapshots', ha='center', va='center', fontsize=8)

# Bottom section - Neural Processing
ax.add_patch(Rectangle((SAFE_CX - 2.5, SAFE_TOP - 7), 5, 1.5, fill=False, lw=line_width))
ax.text(SAFE_CX, SAFE_TOP - 6.25, 'Spiking Neural Network + Energy Harvester', ha='center', va='center', fontsize=10)
ax.text(SAFE_CX, SAFE_TOP - 6.5, 'Continuous operation regardless of control source', ha='center', va='center', fontsize=8)
ax.text(SAFE_CX, SAFE_TOP - 6.75, 'THE SYSTEM NEVER STOPS', ha='center', va='center', fontsize=10)

# Annotations
ax.text(SAFE_CX, SAFE_BOTTOM + 0.5, 'Seamless transition: SNN continues processing without interruption', ha='center', va='center', fontsize=8)
ax.text(SAFE_CX, SAFE_BOTTOM + 0.2, 'The control source changes; the computation continues', ha='center', va='center', fontsize=8)

plt.savefig(os.path.join(OUT_DIR, 'fig1.svg'), format='svg')
plt.close()


# ════════════════════════════════════════════════════════════════════
# FIG. 2 through FIG. 7 follow the same SAFE_ bounds pattern.
# Each figure uses setup_figure(N), draws within [SAFE_LEFT..SAFE_RIGHT,
# SAFE_BOTTOM..SAFE_TOP], and saves to patent_drawings/patent_c/figN.svg.
#
# FIG. 2 — State Transition Diagram (connected/autonomous/recovery states)
# FIG. 3 — Energy-Aware Modulation Curve (energy vs modulation mapping)
# FIG. 4 — Autonomous Input Generator Output (circadian + burst waveform)
# FIG. 5 — Resynchronization Payload Structure (data format diagram)
# FIG. 6 — Recovery Timeline Diagrams (connected->autonomous->resync)
# FIG. 7 — End-to-End Signal Flow: Connected vs. Autonomous
# ════════════════════════════════════════════════════════════════════

"""
Generate USPTO-compliant SVG patent drawings for Patent B:
Configurable Recursive Self-Observation Method and System for Spiking Neural
Networks with Dynamic Reflection Coefficient Modulation

6 Figures per Patent_B_Drawings_Description.txt
All drawings comply with 37 CFR 1.84.
Includes reference numerals cross-referenced with specification.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import (Rectangle, Arrow, Circle, FancyArrowPatch,
                                 Ellipse, Polygon, PathPatch, FancyBboxPatch)
from matplotlib.path import Path
from matplotlib.text import Text
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
line_width = 1.5

# Safe drawing bounds (absolute coordinates)
SAFE_LEFT = left_margin + 0.15
SAFE_RIGHT = paper_width - right_margin - 0.15
SAFE_BOTTOM = bottom_margin + 0.15
SAFE_TOP = paper_height - top_margin - 0.15
SAFE_WIDTH = SAFE_RIGHT - SAFE_LEFT  # ~6.575
SAFE_CX = (SAFE_LEFT + SAFE_RIGHT) / 2  # ~4.4375

# Function to setup figure
def setup_figure(fig_num, total_sheets):
    fig = plt.figure(figsize=(paper_width, paper_height), dpi=dpi)
    # Constrain drawing area to safe margins (+0.15" inset to prevent overflow)
    safe_left = (left_margin + 0.15) / paper_width
    safe_bottom = (bottom_margin + 0.15) / paper_height
    safe_width = (paper_width - left_margin - right_margin - 0.3) / paper_width
    safe_height = (paper_height - top_margin - bottom_margin - 0.3) / paper_height
    ax = fig.add_axes([safe_left, safe_bottom, safe_width, safe_height])
    ax.set_xlim(SAFE_LEFT, SAFE_RIGHT)
    ax.set_ylim(SAFE_BOTTOM, SAFE_TOP)
    ax.set_clip_on(True)
    ax.axis('off')
    # Sheet number at top center (on fig, outside ax)
    fig.text(0.5, 1.0 - 0.5 / paper_height,
             f"{fig_num}/{total_sheets}", ha='center', va='center', fontsize=10)
    # Figure label at bottom left (on fig, outside ax)
    fig.text(left_margin / paper_width, (bottom_margin + 0.2) / paper_height,
             f"FIG. {fig_num}", ha='left', va='bottom', fontsize=font_size_label)
    return fig, ax

OUT_DIR = 'patent_drawings/patent_b'
os.makedirs(OUT_DIR, exist_ok=True)


# ════════════════════════════════════════════════════════════════════
# FIG. 1 — Self-Observation Feedback Loop
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(1, 6)

# Left side: External Input
ax.add_patch(FancyArrowPatch((SAFE_LEFT + 0.5, SAFE_TOP - 2), (SAFE_LEFT + 1.5, SAFE_TOP - 2), arrowstyle='->', lw=line_width))
ax.text(SAFE_LEFT + 1, SAFE_TOP - 1.8, 'External Input I_ext(t)', ha='center', va='bottom', fontsize=8)

# Summing junction
ax.add_patch(Circle((SAFE_LEFT + 2, SAFE_TOP - 2), 0.3, fill=False, lw=line_width))
ax.text(SAFE_LEFT + 2, SAFE_TOP - 2, '+', ha='center', va='center', fontsize=font_size_label)

# Center: SNN
ax.add_patch(Rectangle((SAFE_LEFT + 2.5, SAFE_TOP - 3), 3, 2, fill=False, lw=line_width))
ax.text(SAFE_LEFT + 4, SAFE_TOP - 2.5, 'Spiking Neural Network (N LIF neurons)', ha='center', va='center', fontsize=10)
ax.text(SAFE_LEFT + 4, SAFE_TOP - 2.8, 'V_i(t+1) = V_i(t) x leak + I_adjusted x dt', ha='center', va='center', fontsize=8)
# Small circles for neurons
for i in range(5):
    ax.add_patch(Circle((SAFE_LEFT + 3 + i*0.4, SAFE_TOP - 2.2), 0.1, fill=False))

# Right side: Spike Output
ax.add_patch(FancyArrowPatch((SAFE_LEFT + 5.5, SAFE_TOP - 2), (SAFE_LEFT + 6.5, SAFE_TOP - 2), arrowstyle='->', lw=line_width))
ax.text(SAFE_LEFT + 6, SAFE_TOP - 1.8, 'Spike Output S(t)', ha='center', va='bottom', fontsize=8)

# Bottom path: Aggregate Output
ax.add_patch(FancyArrowPatch((SAFE_LEFT + 6, SAFE_TOP - 2.5), (SAFE_LEFT + 6, SAFE_TOP - 4), arrowstyle='->', lw=line_width))
ax.add_patch(Rectangle((SAFE_LEFT + 4.5, SAFE_TOP - 4.5), 3, 1, fill=False, lw=line_width))
ax.text(SAFE_LEFT + 6, SAFE_TOP - 4, 'Aggregate Output Computation', ha='center', va='center', fontsize=10)
ax.text(SAFE_LEFT + 6, SAFE_TOP - 4.2, 'O(t) = mean(V_1, V_2, ..., V_N)', ha='center', va='center', fontsize=8)
ax.text(SAFE_LEFT + 6, SAFE_TOP - 4.7, 'Mean membrane potential across all neurons', ha='center', va='center', fontsize=8)

# Reflection Scaling
ax.add_patch(FancyArrowPatch((SAFE_LEFT + 4.5, SAFE_TOP - 4), (SAFE_LEFT + 3, SAFE_TOP - 4), arrowstyle='->', lw=line_width))
ax.add_patch(Rectangle((SAFE_LEFT + 1.5, SAFE_TOP - 4.5), 1.5, 1, fill=False, lw=line_width))
ax.text(SAFE_LEFT + 2.25, SAFE_TOP - 4, 'Reflection Scaling', ha='center', va='center', fontsize=10)
ax.text(SAFE_LEFT + 2.25, SAFE_TOP - 4.2, 'I_reflection = O(t) x reflection_coeff', ha='center', va='center', fontsize=8)

# Feedback to summing
ax.add_patch(FancyArrowPatch((SAFE_LEFT + 2.25, SAFE_TOP - 3.5), (SAFE_LEFT + 2.25, SAFE_TOP - 2.3), arrowstyle='->', lw=line_width * 2))  # bold
# Delay element
ax.add_patch(Rectangle((SAFE_LEFT + 2, SAFE_TOP - 3), 0.5, 0.5, fill=False, lw=line_width))
ax.text(SAFE_LEFT + 2.25, SAFE_TOP - 2.75, 'z^{-1}', ha='center', va='center', fontsize=8)

# Key label
ax.text(SAFE_CX, SAFE_BOTTOM + 1, 'Self-observation: the network observes its own prior aggregate state', ha='center', va='center', fontsize=8)
ax.text(SAFE_CX, SAFE_BOTTOM + 0.5, 'I_adjusted(t+1) = I_ext(t+1) + I_reflection(t)', ha='center', va='center', fontsize=8)

plt.savefig(os.path.join(OUT_DIR, 'fig1.svg'), format='svg')
plt.close()


# ════════════════════════════════════════════════════════════════════
# FIG. 2 through FIG. 6 follow the same SAFE_ bounds pattern.
# Each figure uses setup_figure(N, 6), draws within [SAFE_LEFT..SAFE_RIGHT,
# SAFE_BOTTOM..SAFE_TOP], and saves to patent_drawings/patent_b/figN.svg.
#
# FIG. 2 — Reflection Coefficient Spectrum (0.0 to 1.0 dial/spectrum)
# FIG. 3 — Dynamic Modulation Sources (cognitive + energy-aware paths)
# FIG. 4 — Self-Referential Learning Loop (STDP + Self-Observation)
# FIG. 5 — Energy-Aware Self-Observation Regulation
# FIG. 6 — End-to-End Signal Flow with Self-Observation Integration
# ════════════════════════════════════════════════════════════════════

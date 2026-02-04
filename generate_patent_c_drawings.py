"""
Generate USPTO-compliant SVG patent drawings for Patent C:
Method and System for Autonomous Self-Regulation and Cognitive
Resynchronization in Neural Processing Systems During Disconnection
from External Control Layers

7 Figures per Patent_C_Drawings_Description.txt
All drawings comply with 37 CFR 1.84.

REVAMPED VERSION - Consistent reference numerals across all figures:
  100 - External Cognitive Control Layer
  102 - Heartbeat Watchdog
  104 - Connected Mode Controller
  106 - Autonomous Fallback Controller
  108 - Spiking Neural Network + Energy Harvester (Core Pipeline)
  110 - Heartbeat Signal Path
  112 - Modulation Command Path
  114 - Step Buffer
  116 - State Snapshots (Persistent Storage)
  118 - Autonomous Input Generator
  120 - Energy-Aware Self-Modulation
  122 - Resynchronization Payload
  124 - Resync Signal Path
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import (Rectangle, FancyArrowPatch, Ellipse, Polygon,
                                 FancyBboxPatch, Circle)
import numpy as np
import os

# ═══════════════════════════════════════════════════════════════════════════
# COMMON SETTINGS (per 37 CFR 1.84)
# ═══════════════════════════════════════════════════════════════════════════
PAPER_WIDTH = 8.5    # inches
PAPER_HEIGHT = 11    # inches
TOP_MARGIN = 1.0     # inch
LEFT_MARGIN = 1.0    # inch
RIGHT_MARGIN = 0.625 # 5/8 inch
BOTTOM_MARGIN = 0.375 # 3/8 inch
DPI = 300

# Font sizes (must be >= 1/8 inch = 9pt at 72 dpi)
FONT_TITLE = 11      # Major labels
FONT_BODY = 10       # Block text
FONT_SMALL = 9       # Annotations (minimum compliant)
FONT_REF = 9         # Reference numerals

LINE_WIDTH = 1.5     # Sufficiently heavy for reproduction
LINE_THIN = 0.8      # Leader lines

TOTAL_SHEETS = 7

OUT_DIR = 'patent_drawings/patent_c'
os.makedirs(OUT_DIR, exist_ok=True)

# Arrow styles
ARROW_PROPS = {'arrowstyle': '->', 'lw': LINE_WIDTH, 'color': 'black'}
LEADER_PROPS = {'arrowstyle': '->', 'lw': LINE_THIN, 'color': 'black'}


def setup_figure(fig_num):
    """Create a figure with USPTO-compliant margins and labels."""
    fig = plt.figure(figsize=(PAPER_WIDTH, PAPER_HEIGHT), dpi=DPI)

    # Safe drawing area with 0.1" inset from margins
    safe_left = (LEFT_MARGIN + 0.1) / PAPER_WIDTH
    safe_bottom = (BOTTOM_MARGIN + 0.1) / PAPER_HEIGHT
    safe_width = (PAPER_WIDTH - LEFT_MARGIN - RIGHT_MARGIN - 0.2) / PAPER_WIDTH
    safe_height = (PAPER_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN - 0.2) / PAPER_HEIGHT

    ax = fig.add_axes([safe_left, safe_bottom, safe_width, safe_height])
    ax.set_xlim(LEFT_MARGIN + 0.1, PAPER_WIDTH - RIGHT_MARGIN - 0.1)
    ax.set_ylim(BOTTOM_MARGIN + 0.1, PAPER_HEIGHT - TOP_MARGIN - 0.1)
    ax.axis('off')

    # Sheet number at top center
    fig.text(0.5, 1.0 - 0.5 / PAPER_HEIGHT,
             f"{fig_num}/{TOTAL_SHEETS}", ha='center', va='center', fontsize=FONT_BODY)

    # Figure label at bottom left
    fig.text(LEFT_MARGIN / PAPER_WIDTH, (BOTTOM_MARGIN + 0.15) / PAPER_HEIGHT,
             f"FIG. {fig_num}", ha='left', va='bottom', fontsize=FONT_TITLE)

    return fig, ax


def add_ref_label(ax, x, y, ref_num, anchor='left', offset=(0.15, 0)):
    """Add a reference numeral with simple leader line (no annotate)."""
    text_x = x + offset[0] if anchor == 'left' else x - offset[0]
    ax.text(text_x, y + offset[1], str(ref_num), ha=anchor, va='center',
            fontsize=FONT_REF, weight='bold')
    # Simple line instead of annotate arrow (more compatible with GitHub SVG renderer)
    line_start_x = text_x - 0.03 if anchor == 'left' else text_x + 0.03
    ax.plot([line_start_x, x], [y + offset[1], y], 'k-', lw=LINE_THIN)


# ═══════════════════════════════════════════════════════════════════════════
# FIG. 1 — System Architecture with Fallback
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(1)

# Title
ax.text(4.25, 9.8, 'System Architecture with Cognitive Fallback',
        ha='center', va='center', fontsize=FONT_TITLE, weight='bold')

# ─── TOP: External Cognitive Control Layer (100) ───
cloud_cx, cloud_cy = 4.25, 9.0
# Single dashed ellipse for cloud shape (dashed indicates optional/may disconnect)
ax.add_patch(Ellipse((cloud_cx, cloud_cy), 3.5, 0.9, fill=False, lw=LINE_WIDTH, ls='dashed'))
ax.text(cloud_cx, cloud_cy + 0.15, 'External Cognitive Control Layer',
        ha='center', va='center', fontsize=FONT_BODY)
ax.text(cloud_cx, cloud_cy - 0.2, '(e.g., Claude AI)',
        ha='center', va='center', fontsize=FONT_SMALL)
add_ref_label(ax, cloud_cx + 1.75, cloud_cy, 100, anchor='left', offset=(0.15, 0))

# Annotation: May become unavailable
ax.text(cloud_cx + 2.3, cloud_cy + 0.3, '(may become unavailable)',
        ha='left', va='center', fontsize=FONT_SMALL, style='italic')

# ─── Arrows from cognitive layer ───
# Modulation commands (112)
ax.add_patch(FancyArrowPatch((cloud_cx - 0.8, cloud_cy - 0.45), (cloud_cx - 0.8, 7.7),
                              **ARROW_PROPS))
ax.text(cloud_cx - 1.5, 8.2, 'Modulation', ha='center', va='center', fontsize=FONT_SMALL)
ax.text(cloud_cx - 1.5, 8.0, '(-1.0 to +1.0)', ha='center', va='center', fontsize=FONT_SMALL)
add_ref_label(ax, cloud_cx - 0.6, 8.3, 112, anchor='left', offset=(0.15, 0))

# Heartbeat signal (110)
ax.add_patch(FancyArrowPatch((cloud_cx + 0.8, cloud_cy - 0.45), (cloud_cx + 0.8, 7.7),
                              **ARROW_PROPS))
ax.text(cloud_cx + 1.5, 8.2, 'Heartbeat', ha='center', va='center', fontsize=FONT_SMALL)
ax.text(cloud_cx + 1.5, 8.0, '(via tool calls)', ha='center', va='center', fontsize=FONT_SMALL)
add_ref_label(ax, cloud_cx + 1.0, 8.3, 110, anchor='left', offset=(0.15, 0))

# ─── MIDDLE: Heartbeat Watchdog (102) ───
wd_x, wd_y, wd_w, wd_h = 3.0, 7.0, 2.5, 0.7
ax.add_patch(Rectangle((wd_x, wd_y), wd_w, wd_h, fill=False, lw=LINE_WIDTH))
ax.text(wd_x + wd_w/2, wd_y + wd_h/2 + 0.1, 'Heartbeat Watchdog',
        ha='center', va='center', fontsize=FONT_BODY, weight='bold')
ax.text(wd_x + wd_w/2, wd_y + wd_h/2 - 0.15, 'Timeout: 30s | Check: 5s',
        ha='center', va='center', fontsize=FONT_SMALL)
add_ref_label(ax, wd_x + wd_w, wd_y + wd_h/2, 102, anchor='left', offset=(0.15, 0))

# ─── Two paths from watchdog ───
# Left path: Connected Mode (104)
ax.add_patch(FancyArrowPatch((wd_x + 0.3, wd_y), (2.0, 6.0),
                              connectionstyle="arc3,rad=0.2", **ARROW_PROPS))
ax.text(1.8, 6.3, 'Active', ha='center', va='center', fontsize=FONT_SMALL)

conn_x, conn_y, conn_w, conn_h = 1.2, 5.0, 2.0, 1.0
ax.add_patch(Rectangle((conn_x, conn_y), conn_w, conn_h, fill=False, lw=LINE_WIDTH))
ax.text(conn_x + conn_w/2, conn_y + conn_h - 0.2, 'Connected Mode',
        ha='center', va='center', fontsize=FONT_BODY, weight='bold')
ax.text(conn_x + conn_w/2, conn_y + conn_h/2 - 0.1, 'Claude-controlled',
        ha='center', va='center', fontsize=FONT_SMALL)
ax.text(conn_x + conn_w/2, conn_y + 0.2, 'input & modulation',
        ha='center', va='center', fontsize=FONT_SMALL)
add_ref_label(ax, conn_x, conn_y + conn_h/2, 104, anchor='right', offset=(0.2, 0))

# Right path: Autonomous Mode (106)
ax.add_patch(FancyArrowPatch((wd_x + wd_w - 0.3, wd_y), (6.0, 6.0),
                              connectionstyle="arc3,rad=-0.2", ls='dashed', **ARROW_PROPS))
ax.text(6.2, 6.3, 'Timeout', ha='center', va='center', fontsize=FONT_SMALL)

auto_x, auto_y, auto_w, auto_h = 5.0, 5.0, 2.3, 1.0
ax.add_patch(Rectangle((auto_x, auto_y), auto_w, auto_h, fill=False, lw=LINE_WIDTH))
ax.text(auto_x + auto_w/2, auto_y + auto_h - 0.2, 'Autonomous Mode',
        ha='center', va='center', fontsize=FONT_BODY, weight='bold')
ax.text(auto_x + auto_w/2, auto_y + auto_h/2 - 0.1, 'Self-generated input',
        ha='center', va='center', fontsize=FONT_SMALL)
ax.text(auto_x + auto_w/2, auto_y + 0.2, 'Energy-aware modulation',
        ha='center', va='center', fontsize=FONT_SMALL)
add_ref_label(ax, auto_x + auto_w, auto_y + auto_h/2, 106, anchor='left', offset=(0.15, 0))

# ─── Autonomous mode outputs ───
# Step Buffer (114)
buf_x, buf_y, buf_w, buf_h = 5.3, 3.8, 0.8, 0.5
ax.add_patch(FancyArrowPatch((auto_x + auto_w/2 - 0.5, auto_y), (buf_x + buf_w/2, buf_y + buf_h),
                              **ARROW_PROPS))
ax.add_patch(Rectangle((buf_x, buf_y), buf_w, buf_h, fill=False, lw=LINE_WIDTH))
ax.text(buf_x + buf_w/2, buf_y + buf_h/2, 'Buffer',
        ha='center', va='center', fontsize=FONT_SMALL)
add_ref_label(ax, buf_x + buf_w, buf_y + buf_h/2, 114, anchor='left', offset=(0.15, 0))

# State Snapshots (116)
snap_x, snap_y = 6.5, 3.8
ax.add_patch(Ellipse((snap_x, snap_y + 0.15), 0.7, 0.2, fill=False, lw=LINE_WIDTH))
ax.add_patch(Rectangle((snap_x - 0.35, snap_y - 0.2), 0.7, 0.35, fill=False, lw=LINE_WIDTH))
ax.add_patch(Ellipse((snap_x, snap_y - 0.2), 0.7, 0.2, fill=False, lw=LINE_WIDTH))
ax.text(snap_x, snap_y, 'Snap', ha='center', va='center', fontsize=FONT_SMALL)
ax.add_patch(FancyArrowPatch((buf_x + buf_w, buf_y + buf_h/2), (snap_x - 0.35, snap_y),
                              **ARROW_PROPS))
add_ref_label(ax, snap_x + 0.35, snap_y, 116, anchor='left', offset=(0.15, 0))

# ─── BOTTOM: Core Pipeline (108) ───
core_x, core_y, core_w, core_h = 1.5, 1.5, 5.5, 1.5
ax.add_patch(Rectangle((core_x, core_y), core_w, core_h, fill=False, lw=LINE_WIDTH * 1.5))
ax.text(core_x + core_w/2, core_y + core_h - 0.3, 'Spiking Neural Network + Energy Harvester',
        ha='center', va='center', fontsize=FONT_BODY, weight='bold')
ax.text(core_x + core_w/2, core_y + core_h/2, 'CORE PIPELINE',
        ha='center', va='center', fontsize=FONT_TITLE, weight='bold')
ax.text(core_x + core_w/2, core_y + 0.3, 'Continuous operation regardless of control source',
        ha='center', va='center', fontsize=FONT_SMALL)
add_ref_label(ax, core_x + core_w, core_y + core_h/2, 108, anchor='left', offset=(0.15, 0))

# Arrows to core pipeline
ax.add_patch(FancyArrowPatch((conn_x + conn_w/2, conn_y), (core_x + 1.0, core_y + core_h),
                              **ARROW_PROPS))
ax.add_patch(FancyArrowPatch((auto_x + auto_w/2, auto_y), (core_x + core_w - 1.0, core_y + core_h),
                              **ARROW_PROPS))

# Key annotation
ax.text(4.25, 0.8, 'THE SYSTEM NEVER STOPS',
        ha='center', va='center', fontsize=FONT_TITLE, weight='bold')
ax.text(4.25, 0.5, 'Control source changes; computation continues seamlessly',
        ha='center', va='center', fontsize=FONT_SMALL, style='italic')

plt.savefig(f'{OUT_DIR}/fig1.svg', format='svg')
plt.close()


# ═══════════════════════════════════════════════════════════════════════════
# FIG. 2 — State Transition Diagram
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(2)

ax.text(4.25, 9.8, 'State Transition Diagram',
        ha='center', va='center', fontsize=FONT_TITLE, weight='bold')

# State dimensions
state_w, state_h = 2.2, 1.6

# ─── CONNECTED state (left) ───
conn_cx, conn_cy = 2.2, 7.5
ax.add_patch(FancyBboxPatch((conn_cx - state_w/2, conn_cy - state_h/2),
                             state_w, state_h, boxstyle="round,pad=0.1",
                             fill=False, lw=LINE_WIDTH * 1.5))
ax.text(conn_cx, conn_cy + 0.45, 'CONNECTED', ha='center', va='center',
        fontsize=FONT_BODY, weight='bold')
ax.text(conn_cx, conn_cy + 0.15, 'Cognitive layer active', ha='center', va='center',
        fontsize=FONT_SMALL)
ax.text(conn_cx, conn_cy - 0.15, 'External input', ha='center', va='center',
        fontsize=FONT_SMALL)
ax.text(conn_cx, conn_cy - 0.4, 'External modulation', ha='center', va='center',
        fontsize=FONT_SMALL)

# Start indicator
ax.add_patch(FancyArrowPatch((conn_cx, conn_cy + 1.5), (conn_cx, conn_cy + state_h/2 + 0.1),
                              **ARROW_PROPS))
ax.add_patch(Circle((conn_cx, conn_cy + 1.6), 0.1, fill=True, color='black'))
ax.text(conn_cx, conn_cy + 1.85, 'Start', ha='center', va='center', fontsize=FONT_SMALL)

# ─── AUTONOMOUS state (right) ───
auto_cx, auto_cy = 6.3, 7.5
ax.add_patch(FancyBboxPatch((auto_cx - state_w/2, auto_cy - state_h/2),
                             state_w, state_h, boxstyle="round,pad=0.1",
                             fill=False, lw=LINE_WIDTH))
ax.text(auto_cx, auto_cy + 0.45, 'AUTONOMOUS', ha='center', va='center',
        fontsize=FONT_BODY, weight='bold')
ax.text(auto_cx, auto_cy + 0.15, 'Fallback active', ha='center', va='center',
        fontsize=FONT_SMALL)
ax.text(auto_cx, auto_cy - 0.15, 'Self-generated input', ha='center', va='center',
        fontsize=FONT_SMALL)
ax.text(auto_cx, auto_cy - 0.4, 'Energy-aware mod.', ha='center', va='center',
        fontsize=FONT_SMALL)

# ─── RECOVERING state (bottom center) ───
recov_cx, recov_cy = 4.25, 4.0
ax.add_patch(FancyBboxPatch((recov_cx - state_w/2, recov_cy - state_h/2 + 0.2),
                             state_w, state_h - 0.4, boxstyle="round,pad=0.1",
                             fill=False, lw=LINE_WIDTH))
ax.text(recov_cx, recov_cy + 0.35, 'RECOVERING', ha='center', va='center',
        fontsize=FONT_BODY, weight='bold')
ax.text(recov_cx, recov_cy + 0.05, 'Resynchronization', ha='center', va='center',
        fontsize=FONT_SMALL)
ax.text(recov_cx, recov_cy - 0.25, 'Transmitting buffer', ha='center', va='center',
        fontsize=FONT_SMALL)

# ─── Transitions ───
# CONNECTED -> AUTONOMOUS (top arc)
ax.add_patch(FancyArrowPatch((conn_cx + state_w/2, conn_cy + 0.3),
                              (auto_cx - state_w/2, auto_cy + 0.3),
                              connectionstyle="arc3,rad=0.3", **ARROW_PROPS))
ax.text(4.25, 8.5, 'Heartbeat timeout', ha='center', va='center', fontsize=FONT_SMALL)
ax.text(4.25, 8.25, '(>30s no tool call)', ha='center', va='center', fontsize=FONT_SMALL)

# AUTONOMOUS -> CONNECTED (bottom arc, dashed - direct reconnect)
ax.add_patch(FancyArrowPatch((auto_cx - state_w/2, auto_cy - 0.3),
                              (conn_cx + state_w/2, conn_cy - 0.3),
                              connectionstyle="arc3,rad=0.3", ls='dashed', **ARROW_PROPS))
ax.text(4.25, 6.4, 'Any tool call', ha='center', va='center', fontsize=FONT_SMALL)
ax.text(4.25, 6.15, '(direct reconnect)', ha='center', va='center', fontsize=FONT_SMALL)

# AUTONOMOUS -> RECOVERING
ax.add_patch(FancyArrowPatch((auto_cx - 0.3, auto_cy - state_h/2),
                              (recov_cx + state_w/2, recov_cy + 0.4),
                              connectionstyle="arc3,rad=-0.2", **ARROW_PROPS))
ax.text(5.8, 5.3, 'resync() called', ha='center', va='center', fontsize=FONT_SMALL)

# RECOVERING -> CONNECTED
ax.add_patch(FancyArrowPatch((recov_cx - state_w/2, recov_cy + 0.2),
                              (conn_cx + 0.3, conn_cy - state_h/2),
                              connectionstyle="arc3,rad=0.2", **ARROW_PROPS))
ax.text(2.5, 5.3, 'Resync complete', ha='center', va='center', fontsize=FONT_SMALL)

# AUTONOMOUS self-loop (simplified - use arc instead of tight self-loop)
# Draw a curved arrow that loops back to the same state
loop_x = auto_cx + state_w/2 + 0.3
ax.add_patch(FancyArrowPatch((auto_cx + state_w/2, auto_cy + 0.4),
                              (auto_cx + state_w/2, auto_cy - 0.4),
                              connectionstyle="arc3,rad=-0.8", **ARROW_PROPS))
ax.text(auto_cx + 1.6, auto_cy + 0.8, 'Each step', ha='left', va='center', fontsize=FONT_SMALL)
ax.text(auto_cx + 1.6, auto_cy + 0.5, '(up to 10,000)', ha='left', va='center', fontsize=FONT_SMALL)

# Annotations
ax.text(auto_cx, auto_cy - 1.3, 'Snapshot every 50 steps', ha='center', va='center',
        fontsize=FONT_SMALL, style='italic')
ax.text(4.25, 2.5, 'Hard cap: 10,000 autonomous steps',
        ha='center', va='center', fontsize=FONT_SMALL, style='italic')

# Legend
ax.plot([1.5, 2.3], [1.5, 1.5], 'k-', lw=LINE_WIDTH)
ax.text(2.5, 1.5, 'Standard transition', va='center', fontsize=FONT_SMALL)
ax.plot([4.5, 5.3], [1.5, 1.5], 'k--', lw=LINE_WIDTH)
ax.text(5.5, 1.5, 'Direct reconnection', va='center', fontsize=FONT_SMALL)

plt.savefig(f'{OUT_DIR}/fig2.svg', format='svg')
plt.close()


# ═══════════════════════════════════════════════════════════════════════════
# FIG. 3 — Energy-Aware Modulation Curve
# ═══════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(PAPER_WIDTH, PAPER_HEIGHT), dpi=DPI)

# Sheet number
fig.text(0.5, 1.0 - 0.5 / PAPER_HEIGHT, f"3/{TOTAL_SHEETS}",
         ha='center', va='center', fontsize=FONT_BODY)
# Figure label
fig.text(LEFT_MARGIN / PAPER_WIDTH, (BOTTOM_MARGIN + 0.15) / PAPER_HEIGHT,
         "FIG. 3", ha='left', va='bottom', fontsize=FONT_TITLE)

# Title area
title_ax = fig.add_axes([0.15, 0.88, 0.7, 0.06])
title_ax.axis('off')
title_ax.text(0.5, 0.5, 'Energy-Aware Modulation Curve (120)',
              ha='center', va='center', fontsize=FONT_TITLE, weight='bold')

# Main graph
graph_ax = fig.add_axes([0.15, 0.35, 0.7, 0.48])
graph_ax.set_xlabel('System Energy Level (mWh)', fontsize=FONT_BODY)
graph_ax.set_ylabel('Autonomous Modulation Value', fontsize=FONT_BODY)
graph_ax.set_xlim(0, 100)
graph_ax.set_ylim(-0.5, 0.5)
graph_ax.set_xticks([0, 15, 30, 80, 100])
graph_ax.set_yticks([-0.4, -0.1, 0.0, 0.3])
graph_ax.grid(True, ls=':', alpha=0.5)

# Step function
energy = [0, 15, 15, 30, 30, 80, 80, 100]
mod = [-0.4, -0.4, -0.1, -0.1, 0.0, 0.0, 0.3, 0.3]
graph_ax.plot(energy, mod, 'k-', lw=LINE_WIDTH * 1.5)

# Threshold lines
for thresh in [15, 30, 80]:
    graph_ax.axvline(x=thresh, ls='--', color='black', lw=LINE_THIN)

# Region hatching
graph_ax.fill_between([0, 15], -0.5, 0.5, hatch='xxx', facecolor='none',
                       edgecolor='black', linewidth=0)
graph_ax.fill_between([15, 30], -0.5, 0.5, hatch='//', facecolor='none',
                       edgecolor='black', linewidth=0)
graph_ax.fill_between([80, 100], -0.5, 0.5, hatch='\\\\', facecolor='none',
                       edgecolor='black', linewidth=0)

# Region labels
graph_ax.text(7.5, 0.42, 'CRITICAL', ha='center', va='center', fontsize=FONT_SMALL, weight='bold')
graph_ax.text(7.5, 0.32, '-0.4', ha='center', va='center', fontsize=FONT_SMALL)
graph_ax.text(22.5, 0.42, 'LOW', ha='center', va='center', fontsize=FONT_SMALL, weight='bold')
graph_ax.text(22.5, 0.32, '-0.1', ha='center', va='center', fontsize=FONT_SMALL)
graph_ax.text(55, 0.42, 'NORMAL', ha='center', va='center', fontsize=FONT_SMALL, weight='bold')
graph_ax.text(55, 0.32, '0.0', ha='center', va='center', fontsize=FONT_SMALL)
graph_ax.text(90, 0.42, 'SURPLUS', ha='center', va='center', fontsize=FONT_SMALL, weight='bold')
graph_ax.text(90, 0.32, '+0.3', ha='center', va='center', fontsize=FONT_SMALL)

# Annotation area
annot_ax = fig.add_axes([0.15, 0.12, 0.7, 0.18])
annot_ax.axis('off')
annot_ax.text(0.5, 0.8, 'The system autonomously adjusts processing intensity based on energy',
              ha='center', va='center', fontsize=FONT_BODY)
annot_ax.text(0.5, 0.5, 'CRITICAL: Maximum conservation to prevent shutdown',
              ha='center', va='center', fontsize=FONT_SMALL)
annot_ax.text(0.5, 0.3, 'SURPLUS: Opportunistic exploration using excess energy',
              ha='center', va='center', fontsize=FONT_SMALL)
annot_ax.text(0.5, 0.1, 'Mimics biological metabolic regulation',
              ha='center', va='center', fontsize=FONT_SMALL, style='italic')

plt.savefig(f'{OUT_DIR}/fig3.svg', format='svg')
plt.close()


# ═══════════════════════════════════════════════════════════════════════════
# FIG. 4 — Autonomous Input Generator Output (118)
# ═══════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(PAPER_WIDTH, PAPER_HEIGHT), dpi=DPI)

# Sheet number and figure label
fig.text(0.5, 1.0 - 0.5 / PAPER_HEIGHT, f"4/{TOTAL_SHEETS}",
         ha='center', va='center', fontsize=FONT_BODY)
fig.text(LEFT_MARGIN / PAPER_WIDTH, (BOTTOM_MARGIN + 0.15) / PAPER_HEIGHT,
         "FIG. 4", ha='left', va='bottom', fontsize=FONT_TITLE)

# Title
title_ax = fig.add_axes([0.15, 0.88, 0.7, 0.06])
title_ax.axis('off')
title_ax.text(0.5, 0.5, 'Autonomous Input Generator Output (118)',
              ha='center', va='center', fontsize=FONT_TITLE, weight='bold')

# Main waveform graph
main_ax = fig.add_axes([0.15, 0.48, 0.7, 0.36])
main_ax.set_xlabel('Autonomous Step Number', fontsize=FONT_BODY)
main_ax.set_ylabel('Input Value', fontsize=FONT_BODY)
main_ax.set_xlim(0, 500)
main_ax.set_ylim(0, 1.05)

# Generate signals
np.random.seed(42)
steps = np.arange(501)
period = 100
base = 0.5 + 0.3 * np.sin(2 * np.pi * steps / period)

# Add bursts
composite = base.copy()
burst_mask = np.random.random(501) < 0.10
composite[burst_mask] = np.minimum(1.0, composite[burst_mask] + 0.2)

# Plot
main_ax.plot(steps, base, 'k--', lw=LINE_THIN, label='Circadian base')
main_ax.plot(steps, composite, 'k-', lw=LINE_WIDTH, label='Composite signal')

# Mark some bursts
burst_indices = np.where(burst_mask)[0][:5]
for idx in burst_indices:
    main_ax.plot([idx, idx], [base[idx], composite[idx]], 'k-', lw=LINE_WIDTH)
    main_ax.plot(idx, composite[idx], 'ko', markersize=4)

main_ax.legend(loc='upper right', fontsize=FONT_SMALL)
main_ax.text(400, 0.15, 'base = 0.5 + 0.3 sin(2\u03c0 step/100)', fontsize=FONT_SMALL)
main_ax.text(400, 0.05, '10% probability attention bursts', fontsize=FONT_SMALL)

# Energy tracking graph
energy_ax = fig.add_axes([0.15, 0.18, 0.7, 0.22])
energy_ax.set_xlabel('Autonomous Step Number', fontsize=FONT_BODY)
energy_ax.set_ylabel('Energy (mWh)', fontsize=FONT_BODY)
energy_ax.set_xlim(0, 500)
energy_ax.set_ylim(0, 100)

# Simulate energy
energy = 50 + np.cumsum(np.random.normal(0.02, 0.4, 501))
energy = np.clip(energy, 0, 100)
energy_ax.plot(steps, energy, 'k-', lw=LINE_WIDTH)

# Threshold lines
for thresh, label in [(15, '15'), (30, '30'), (80, '80')]:
    energy_ax.axhline(thresh, ls='--', color='black', lw=LINE_THIN)
    energy_ax.text(505, thresh, label, va='center', fontsize=FONT_SMALL)

# Annotation
annot_ax = fig.add_axes([0.15, 0.08, 0.7, 0.08])
annot_ax.axis('off')
annot_ax.text(0.5, 0.5, 'Circadian rhythm provides structured temporal variation',
              ha='center', va='center', fontsize=FONT_SMALL)
annot_ax.text(0.5, 0.1, 'Energy level determines modulation via curve in FIG. 3',
              ha='center', va='center', fontsize=FONT_SMALL, style='italic')

plt.savefig(f'{OUT_DIR}/fig4.svg', format='svg')
plt.close()


# ═══════════════════════════════════════════════════════════════════════════
# FIG. 5 — Resynchronization Payload Structure (122)
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(5)

ax.text(4.25, 9.8, 'Resynchronization Payload Structure (122)',
        ha='center', va='center', fontsize=FONT_TITLE, weight='bold')

# Main payload container
payload_x, payload_y, payload_w, payload_h = 1.8, 3.5, 5.0, 6.0
ax.add_patch(Rectangle((payload_x, payload_y), payload_w, payload_h,
                        fill=False, lw=LINE_WIDTH * 1.5))
ax.text(payload_x + payload_w/2, payload_y + payload_h - 0.3,
        'Resynchronization Payload', ha='center', va='center',
        fontsize=FONT_BODY, weight='bold')

# Section 1: Summary Statistics (always included)
sec1_x, sec1_y, sec1_w, sec1_h = 2.0, 7.2, 4.6, 2.0
ax.add_patch(Rectangle((sec1_x, sec1_y), sec1_w, sec1_h, fill=False, lw=LINE_WIDTH))
ax.text(sec1_x + sec1_w/2, sec1_y + sec1_h - 0.25, 'Summary Statistics',
        ha='center', va='center', fontsize=FONT_BODY, weight='bold')
ax.text(sec1_x + sec1_w/2, sec1_y + sec1_h - 0.5, '(ALWAYS included)',
        ha='center', va='center', fontsize=FONT_SMALL, style='italic')

summary_text = [
    'steps_autonomous: [integer]',
    'energy_delta: [float] mWh',
    'min/max/mean_energy: [float]',
    'total_spikes: [integer]',
    'mean_spikes_per_step: [float]'
]
for i, line in enumerate(summary_text):
    ax.text(sec1_x + 0.2, sec1_y + sec1_h - 0.85 - i * 0.28, line,
            ha='left', va='center', fontsize=FONT_SMALL, family='monospace')

ax.text(sec1_x + sec1_w + 0.2, sec1_y + sec1_h/2, '~200 bytes',
        ha='left', va='center', fontsize=FONT_SMALL)

# Section 2: Full Step Buffer (optional)
sec2_x, sec2_y, sec2_w, sec2_h = 2.0, 3.8, 4.6, 3.0
ax.add_patch(Rectangle((sec2_x, sec2_y), sec2_w, sec2_h, fill=False, lw=LINE_WIDTH, ls='dashed'))
ax.text(sec2_x + sec2_w/2, sec2_y + sec2_h - 0.25, 'Full Step Buffer',
        ha='center', va='center', fontsize=FONT_BODY, weight='bold')
ax.text(sec2_x + sec2_w/2, sec2_y + sec2_h - 0.5, '(OPTIONAL)',
        ha='center', va='center', fontsize=FONT_SMALL, style='italic')

buffer_text = [
    'Step 0: {input, mod, spikes, energy, temp}',
    'Step 1: {input, mod, spikes, energy, temp}',
    '...',
    'Step N: {input, mod, spikes, energy, temp}'
]
for i, line in enumerate(buffer_text):
    ax.text(sec2_x + 0.2, sec2_y + sec2_h - 0.9 - i * 0.35, line,
            ha='left', va='center', fontsize=FONT_SMALL, family='monospace')

ax.text(sec2_x + sec2_w + 0.2, sec2_y + sec2_h/2, '~100 bytes',
        ha='left', va='center', fontsize=FONT_SMALL)
ax.text(sec2_x + sec2_w + 0.2, sec2_y + sec2_h/2 - 0.3, 'per step',
        ha='left', va='center', fontsize=FONT_SMALL)

# Granularity indicators
ax.add_patch(FancyArrowPatch((payload_x, sec1_y + sec1_h/2), (payload_x - 0.5, sec1_y + sec1_h/2),
                              **ARROW_PROPS))
ax.text(payload_x - 0.6, sec1_y + sec1_h/2, 'Level 1:', ha='right', va='center',
        fontsize=FONT_SMALL, weight='bold')
ax.text(payload_x - 0.6, sec1_y + sec1_h/2 - 0.3, 'Summary only', ha='right', va='center',
        fontsize=FONT_SMALL)

ax.add_patch(FancyArrowPatch((payload_x, sec2_y + sec2_h/2), (payload_x - 0.5, sec2_y + sec2_h/2),
                              **ARROW_PROPS))
ax.text(payload_x - 0.6, sec2_y + sec2_h/2, 'Level 2:', ha='right', va='center',
        fontsize=FONT_SMALL, weight='bold')
ax.text(payload_x - 0.6, sec2_y + sec2_h/2 - 0.3, 'Full buffer', ha='right', va='center',
        fontsize=FONT_SMALL)

# Decision flow
diamond_cx, diamond_cy = 4.25, 2.5
ax.add_patch(Polygon([[diamond_cx, diamond_cy + 0.5],
                       [diamond_cx - 0.7, diamond_cy],
                       [diamond_cx, diamond_cy - 0.5],
                       [diamond_cx + 0.7, diamond_cy]],
                      closed=True, fill=False, lw=LINE_WIDTH))
ax.text(diamond_cx, diamond_cy, 'Full buffer\nrequested?', ha='center', va='center',
        fontsize=FONT_SMALL)

ax.add_patch(FancyArrowPatch((diamond_cx + 0.7, diamond_cy), (diamond_cx + 1.5, diamond_cy),
                              **ARROW_PROPS))
ax.text(diamond_cx + 1.6, diamond_cy, 'Yes: Level 2', ha='left', va='center', fontsize=FONT_SMALL)

ax.add_patch(FancyArrowPatch((diamond_cx - 0.7, diamond_cy), (diamond_cx - 1.5, diamond_cy),
                              **ARROW_PROPS))
ax.text(diamond_cx - 1.6, diamond_cy, 'No: Level 1', ha='right', va='center', fontsize=FONT_SMALL)

# Connection from payload to decision
ax.add_patch(FancyArrowPatch((payload_x + payload_w/2, payload_y), (diamond_cx, diamond_cy + 0.5),
                              **ARROW_PROPS))

plt.savefig(f'{OUT_DIR}/fig5.svg', format='svg')
plt.close()


# ═══════════════════════════════════════════════════════════════════════════
# FIG. 6 — Recovery Timeline Diagrams
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(6)

ax.text(4.25, 9.8, 'Recovery Timeline Diagrams',
        ha='center', va='center', fontsize=FONT_TITLE, weight='bold')

# Timeline dimensions
tl_left = 1.2
tl_right = 7.5
tl_len = tl_right - tl_left

def draw_timeline(ax, y, title, phases, annotation):
    """Draw a single timeline."""
    # Title
    ax.text(tl_left, y + 0.7, title, ha='left', va='center',
            fontsize=FONT_BODY, weight='bold')

    # Arrow axis
    ax.add_patch(FancyArrowPatch((tl_left, y), (tl_right, y), **ARROW_PROPS))
    ax.text(tl_right + 0.1, y, 'time', ha='left', va='center', fontsize=FONT_SMALL)

    # Phase markers
    n_phases = len(phases)
    for i, (label, sublabel) in enumerate(phases):
        x = tl_left + (i + 0.5) * tl_len / n_phases
        ax.plot([x - tl_len/(2*n_phases) + 0.1, x + tl_len/(2*n_phases) - 0.1],
                [y, y], 'k-', lw=LINE_WIDTH * 2)
        ax.text(x, y + 0.35, label, ha='center', va='center', fontsize=FONT_SMALL, weight='bold')
        ax.text(x, y + 0.15, sublabel, ha='center', va='center', fontsize=FONT_SMALL)

    # Annotation
    ax.text(4.25, y - 0.35, annotation, ha='center', va='center',
            fontsize=FONT_SMALL, style='italic')

# Timeline A: Normal Reconnection
phases_a = [
    ('CONNECTED', '[Claude active]'),
    ('TIMEOUT', '[Watchdog counting]'),
    ('AUTONOMOUS', '[Self-regulated]'),
    ('RESYNC', '[Buffer sent]'),
    ('CONNECTED', '[Restored]')
]
draw_timeline(ax, 8.0, 'Timeline A: Normal Reconnection', phases_a,
              'Seamless transition with full state capture')

# Timeline B: Crash Recovery
phases_b = [
    ('CONNECTED', '[Normal op.]'),
    ('CRASH', '[Server dies]'),
    ('RESTART', '[Relaunched]'),
    ('SNAPSHOT', '[Load JSON]'),
    ('CONNECTED', '[Restored]')
]
draw_timeline(ax, 5.8, 'Timeline B: Crash Recovery', phases_b,
              'Max state loss = 50 steps (snapshot interval)')

# Timeline C: Clean Shutdown
phases_c = [
    ('CONNECTED', '[Normal op.]'),
    ('AUTONOMOUS', '[Fallback]'),
    ('EOF', '[stdin closed]'),
    ('SHUTDOWN', '[Final snap]')
]
draw_timeline(ax, 3.6, 'Timeline C: Clean Shutdown', phases_c,
              'State preserved for next session - zero data loss')

# Legend
ax.text(4.25, 1.8, 'Legend:', ha='center', va='center', fontsize=FONT_BODY, weight='bold')
ax.plot([2.5, 3.3], [1.4, 1.4], 'k-', lw=LINE_WIDTH * 2)
ax.text(3.5, 1.4, 'System actively processing', va='center', fontsize=FONT_SMALL)
ax.text(4.25, 1.0, 'Bold markers indicate NO DATA LOSS at transitions',
        ha='center', va='center', fontsize=FONT_SMALL, weight='bold')

plt.savefig(f'{OUT_DIR}/fig6.svg', format='svg')
plt.close()


# ═══════════════════════════════════════════════════════════════════════════
# FIG. 7 — End-to-End Signal Flow: Connected vs. Autonomous Operation
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(7)

ax.text(4.25, 9.8, 'End-to-End Signal Flow',
        ha='center', va='center', fontsize=FONT_TITLE, weight='bold')

# Block dimensions
bw, bh = 1.2, 0.5

# ═══ TOP HALF: CONNECTED MODE ═══
ax.text(1.2, 9.3, 'CONNECTED MODE', ha='left', va='center',
        fontsize=FONT_BODY, weight='bold')

# External Cognitive Layer (100)
cloud_cx, cloud_cy = 4.25, 8.8
ax.add_patch(Ellipse((cloud_cx, cloud_cy), 2.5, 0.5, fill=False, lw=LINE_WIDTH))
ax.text(cloud_cx, cloud_cy, 'External Cognitive Layer (100)',
        ha='center', va='center', fontsize=FONT_SMALL)

# Arrow down from cloud
ax.add_patch(FancyArrowPatch((cloud_cx, cloud_cy - 0.25), (cloud_cx, 8.1),
                              ls='dashed', **ARROW_PROPS))
ax.text(cloud_cx + 1.0, 8.4, 'Cognitive', ha='left', va='center', fontsize=FONT_SMALL)
ax.text(cloud_cx + 1.0, 8.2, 'modulation', ha='left', va='center', fontsize=FONT_SMALL)

# Connected pipeline blocks
conn_y = 7.5
blocks_conn = [
    (1.5, 'Sensors'),
    (2.9, 'SNN (108)'),
    (4.3, 'Modulation'),
    (5.7, 'Motor'),
    (6.8, 'Harvester')
]

for bx, label in blocks_conn:
    ax.add_patch(Rectangle((bx, conn_y), bw, bh, fill=False, lw=LINE_WIDTH))
    ax.text(bx + bw/2, conn_y + bh/2, label, ha='center', va='center', fontsize=FONT_SMALL)

# Forward arrows
for i in range(len(blocks_conn) - 1):
    x1 = blocks_conn[i][0] + bw
    x2 = blocks_conn[i+1][0]
    ax.add_patch(FancyArrowPatch((x1, conn_y + bh/2), (x2, conn_y + bh/2), **ARROW_PROPS))

# Energy feedback (bold dashed)
ax.add_patch(FancyArrowPatch((6.8 + bw/2, conn_y), (2.9 + bw/2, conn_y - 0.3),
                              connectionstyle="arc3,rad=-0.3", ls='dashed',
                              lw=LINE_WIDTH * 1.5, arrowstyle='->', color='black'))
ax.text(4.8, conn_y - 0.5, 'Energy feedback', ha='center', va='center', fontsize=FONT_SMALL)

# Self-observation (dotted)
ax.add_patch(FancyArrowPatch((2.9 + bw, conn_y + bh), (2.9 + 0.3, conn_y + bh + 0.3),
                              connectionstyle="arc3,rad=0.3", ls='dotted',
                              lw=LINE_WIDTH * 1.5, arrowstyle='->', color='black'))
ax.text(3.2, conn_y + bh + 0.5, 'Self-obs.', ha='center', va='center', fontsize=FONT_SMALL)

ax.text(1.2, conn_y - 0.6, 'Heartbeat active (tool calls within 30s)',
        ha='left', va='center', fontsize=FONT_SMALL, style='italic')

# ═══ DIVIDING LINE ═══
div_y = 6.3
ax.plot([1.1, 7.7], [div_y, div_y], 'k--', lw=LINE_WIDTH)
ax.text(4.25, div_y + 0.15, 'DISCONNECTION EVENT (heartbeat timeout > 30s)',
        ha='center', va='bottom', fontsize=FONT_SMALL, weight='bold')
ax.text(4.25, div_y - 0.15, 'Seamless transition - core pipeline never stops',
        ha='center', va='top', fontsize=FONT_SMALL, style='italic')

# ═══ BOTTOM HALF: AUTONOMOUS MODE ═══
ax.text(1.2, 5.8, 'AUTONOMOUS MODE', ha='left', va='center',
        fontsize=FONT_BODY, weight='bold')

# Autonomous pipeline blocks
auto_y = 5.0
blocks_auto = [
    (1.3, 'Input Gen\n(118)'),
    (2.7, 'SNN (108)'),
    (4.1, 'Self-Mod\n(120)'),
    (5.5, 'Motor'),
    (6.7, 'Harvest')
]

for bx, label in blocks_auto:
    ax.add_patch(Rectangle((bx, auto_y), bw, bh + 0.1, fill=False, lw=LINE_WIDTH))
    ax.text(bx + bw/2, auto_y + (bh + 0.1)/2, label, ha='center', va='center', fontsize=FONT_SMALL)

# Forward arrows
for i in range(len(blocks_auto) - 1):
    x1 = blocks_auto[i][0] + bw
    x2 = blocks_auto[i+1][0]
    ax.add_patch(FancyArrowPatch((x1, auto_y + bh/2), (x2, auto_y + bh/2), **ARROW_PROPS))

# Energy feedback (bold dashed)
ax.add_patch(FancyArrowPatch((6.7 + bw/2, auto_y), (2.7 + bw/2, auto_y - 0.3),
                              connectionstyle="arc3,rad=-0.3", ls='dashed',
                              lw=LINE_WIDTH * 1.5, arrowstyle='->', color='black'))
ax.text(4.8, auto_y - 0.5, 'Energy feedback', ha='center', va='center', fontsize=FONT_SMALL)

# Self-observation (dotted)
ax.add_patch(FancyArrowPatch((2.7 + bw, auto_y + bh), (2.7 + 0.3, auto_y + bh + 0.3),
                              connectionstyle="arc3,rad=0.3", ls='dotted',
                              lw=LINE_WIDTH * 1.5, arrowstyle='->', color='black'))

# Input generator details
ax.text(1.3 + bw/2, auto_y - 0.25, 'Circadian + bursts', ha='center', va='center', fontsize=FONT_SMALL)

# Self-modulation details
ax.text(4.1 + bw/2, auto_y - 0.25, '<15:-0.4 | <30:-0.1', ha='center', va='center', fontsize=FONT_SMALL)
ax.text(4.1 + bw/2, auto_y - 0.45, '30-80:0.0 | >80:+0.3', ha='center', va='center', fontsize=FONT_SMALL)

# State Buffer (114) - cylinder
buf_cx, buf_cy = 1.8, 3.3
ax.add_patch(Ellipse((buf_cx, buf_cy + 0.3), 0.8, 0.2, fill=False, lw=LINE_WIDTH))
ax.add_patch(Rectangle((buf_cx - 0.4, buf_cy), 0.8, 0.3, fill=False, lw=LINE_WIDTH))
ax.add_patch(Ellipse((buf_cx, buf_cy), 0.8, 0.2, fill=False, lw=LINE_WIDTH))
ax.text(buf_cx, buf_cy + 0.15, 'Buffer', ha='center', va='center', fontsize=FONT_SMALL)
ax.text(buf_cx + 0.5, buf_cy + 0.15, '114', ha='left', va='center', fontsize=FONT_REF, weight='bold')
ax.add_patch(FancyArrowPatch((2.7 + bw/2, auto_y), (buf_cx, buf_cy + 0.4), **ARROW_PROPS))
ax.text(2.3, 4.1, 'Every step', ha='center', va='center', fontsize=FONT_SMALL)

# Snapshot (116) - disk
snap_cx, snap_cy = 1.8, 2.2
ax.add_patch(Rectangle((snap_cx - 0.4, snap_cy), 0.8, 0.4, fill=False, lw=LINE_WIDTH))
ax.text(snap_cx, snap_cy + 0.2, 'Snapshot', ha='center', va='center', fontsize=FONT_SMALL)
ax.text(snap_cx + 0.5, snap_cy + 0.2, '116', ha='left', va='center', fontsize=FONT_REF, weight='bold')
ax.add_patch(FancyArrowPatch((buf_cx, buf_cy - 0.1), (snap_cx, snap_cy + 0.4), **ARROW_PROPS))
ax.text(1.2, 2.75, 'Every 50', ha='center', va='center', fontsize=FONT_SMALL)

# Resync Payload (122) on the right
resync_x, resync_y, resync_w, resync_h = 5.8, 2.8, 1.6, 1.0
ax.add_patch(Rectangle((resync_x, resync_y), resync_w, resync_h, fill=False, lw=LINE_WIDTH, ls='dashed'))
ax.text(resync_x + resync_w/2, resync_y + resync_h - 0.2, 'Resync Payload',
        ha='center', va='center', fontsize=FONT_SMALL, weight='bold')
ax.text(resync_x + resync_w/2, resync_y + resync_h/2, '(122)',
        ha='center', va='center', fontsize=FONT_SMALL)
ax.text(resync_x + resync_w/2, resync_y + 0.2, 'summary + buffer',
        ha='center', va='center', fontsize=FONT_SMALL)

# Arrow from buffer to resync
ax.add_patch(FancyArrowPatch((buf_cx + 0.4, buf_cy + 0.15), (resync_x, resync_y + resync_h/2),
                              **ARROW_PROPS))

# Arrow from resync up (124)
ax.add_patch(FancyArrowPatch((resync_x + resync_w/2, resync_y + resync_h),
                              (resync_x + resync_w/2, div_y - 0.1),
                              ls='dashed', **ARROW_PROPS))
ax.text(resync_x + resync_w + 0.1, 4.8, 'resync()', ha='left', va='center', fontsize=FONT_SMALL)
ax.text(resync_x + resync_w + 0.1, 4.55, '(124)', ha='left', va='center', fontsize=FONT_SMALL)

# Key annotations
ax.text(4.25, 1.5, 'The fallback changes INPUT SOURCE and MODULATION SOURCE',
        ha='center', va='center', fontsize=FONT_BODY, weight='bold')
ax.text(4.25, 1.15, 'Core neural processing, motor actuation, and energy harvesting',
        ha='center', va='center', fontsize=FONT_SMALL)
ax.text(4.25, 0.85, 'continue WITHOUT INTERRUPTION through the transition',
        ha='center', va='center', fontsize=FONT_SMALL, weight='bold')

# Legend
ax.plot([1.2, 1.8], [0.5, 0.5], 'k-', lw=LINE_WIDTH)
ax.text(2.0, 0.5, 'Forward', va='center', fontsize=FONT_SMALL)
ax.plot([3.0, 3.6], [0.5, 0.5], 'k--', lw=LINE_WIDTH * 1.5)
ax.text(3.8, 0.5, 'Energy', va='center', fontsize=FONT_SMALL)
ax.plot([4.8, 5.4], [0.5, 0.5], 'k:', lw=LINE_WIDTH * 1.5)
ax.text(5.6, 0.5, 'Self-obs.', va='center', fontsize=FONT_SMALL)

plt.savefig(f'{OUT_DIR}/fig7.svg', format='svg')
plt.close()


print(f"All {TOTAL_SHEETS} Patent C figures generated in {OUT_DIR}/")
print("Reference numerals used consistently across all figures:")
print("  100 - External Cognitive Control Layer")
print("  102 - Heartbeat Watchdog")
print("  104 - Connected Mode Controller")
print("  106 - Autonomous Fallback Controller")
print("  108 - Spiking Neural Network + Energy Harvester")
print("  110 - Heartbeat Signal Path")
print("  112 - Modulation Command Path")
print("  114 - Step Buffer")
print("  116 - State Snapshots")
print("  118 - Autonomous Input Generator")
print("  120 - Energy-Aware Self-Modulation")
print("  122 - Resynchronization Payload")
print("  124 - Resync Signal Path")

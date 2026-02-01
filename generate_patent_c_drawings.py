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
    # Sheet number at top center (on fig, outside ax)
    fig.text(0.5, 1.0 - 0.5 / paper_height,
             f"{fig_num}/{TOTAL_SHEETS}", ha='center', va='center', fontsize=10)
    # Figure label at bottom left (on fig, outside ax)
    fig.text(left_margin / paper_width, (bottom_margin + 0.2) / paper_height,
             f"FIG. {fig_num}", ha='left', va='bottom', fontsize=font_size_label)
    return fig, ax


OUT_DIR = 'patent_drawings/patent_c'
os.makedirs(OUT_DIR, exist_ok=True)

# Leader line style for reference numerals (thin, per 37 CFR 1.84(q))
leader_props = dict(arrowstyle='->', lw=0.5, color='black')


# ════════════════════════════════════════════════════════════════════
# FIG. 1 — System Architecture with Fallback
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(1)

# Top section - Cognitive Control Layer (ref 100)
ax.add_patch(Ellipse((4.25, 9.5), 3, 1, fill=False, lw=line_width))
ax.text(4.25, 9.5, 'External Cognitive Control Layer (e.g., Claude)',
        ha='center', va='center', fontsize=10)
ax.text(4.25, 9.1, 'Provides intelligent cognitive decisions',
        ha='center', va='center', fontsize=8)
ax.add_patch(Ellipse((4.25, 9.5), 3, 1, fill=False, lw=line_width, ls='dashed'))
ax.text(5.8, 9.5, 'May disconnect', ha='left', va='center', fontsize=8)
ax.text(5.9, 9.8, '100', ha='left', fontsize=8)
ax.annotate('', xy=(5.75, 9.5), xytext=(5.9, 9.75), arrowprops=leader_props)

# Arrows downward
ax.add_patch(FancyArrowPatch((3, 8.5), (3, 8), **arrow_props))
ax.text(3.1, 8.25, 'Modulation commands (-1.0 to +1.0)',
        ha='left', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((5.5, 8.5), (5.5, 8), **arrow_props))
ax.text(5.1, 8.25, 'Heartbeat signal\n(implicit via tool calls)',
        ha='center', va='center', fontsize=8)

# Middle section - Transition Controller (ref 102)
ax.add_patch(Rectangle((3.5, 7), 2, 1, fill=False, lw=line_width))
ax.text(4.25, 7.75, 'Heartbeat Watchdog', ha='center', va='center', fontsize=10)
ax.text(4.25, 7.5, 'Monitors time since last cognitive input',
        ha='center', va='center', fontsize=8)
ax.text(4.25, 7.3, 'Timeout threshold: 30 seconds',
        ha='center', va='center', fontsize=8)
ax.text(4.25, 7.1, 'Check interval: 5 seconds',
        ha='center', va='center', fontsize=8)
ax.text(5.65, 7.5, '102', ha='left', fontsize=8)
ax.annotate('', xy=(5.5, 7.5), xytext=(5.65, 7.5), arrowprops=leader_props)

# Two output paths
# Pre-calculate autonomous box center for arrow target
auto_left = 5.0
auto_width = 2.3
auto_cx = auto_left + auto_width / 2
ax.add_patch(FancyArrowPatch((3.5, 6.5), (SAFE_LEFT + 1.0, 6), ls='solid', **arrow_props))
ax.text(2.5, 6.25, 'Heartbeat active -> Connected Mode',
        ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((5, 6.5), (auto_cx, 6), ls='dashed', **arrow_props))
ax.text(5.5, 6.25, 'Heartbeat timeout -> Autonomous Mode',
        ha='center', va='center', fontsize=8)

# Left path - Connected Mode (ref 104)
ax.add_patch(Rectangle((SAFE_LEFT, 5), 2, 1, fill=False, lw=line_width))
ax.text(SAFE_LEFT + 1.0, 5.75, 'Cognitive-Driven Operation',
        ha='center', va='center', fontsize=9)
ax.text(SAFE_LEFT + 1.0, 5.5, 'Input: Claude-controlled (0-1)',
        ha='center', va='center', fontsize=8)
ax.text(SAFE_LEFT + 1.0, 5.25, 'Mod: Claude-controlled (-1 to +1)',
        ha='center', va='center', fontsize=8)
ax.text(SAFE_LEFT + 2.15, 5.85, '104', ha='left', fontsize=8)
ax.annotate('', xy=(SAFE_LEFT + 2.0, 5.7), xytext=(SAFE_LEFT + 2.1, 5.8), arrowprops=leader_props)
ax.add_patch(FancyArrowPatch((SAFE_LEFT + 1.0, 4.5), (SAFE_LEFT + 1.0, 4), **arrow_props))

# Right path - Autonomous Mode (ref 106) — constrained within right margin
# auto_left, auto_width, auto_cx already defined above for arrow targeting
ax.add_patch(Rectangle((auto_left, 5), auto_width, 1, fill=False, lw=line_width))
ax.text(auto_cx, 5.75, 'Autonomous Fallback Controller',
        ha='center', va='center', fontsize=9)
ax.text(auto_cx, 5.5, 'Input: Self-generated (circadian)',
        ha='center', va='center', fontsize=8)
ax.text(auto_cx, 5.25, 'Modulation: Energy-aware (-0.4 to +0.3)',
        ha='center', va='center', fontsize=8)
ax.text(auto_left + auto_width + 0.1, 5.75, '106', ha='left', fontsize=8)
ax.annotate('', xy=(auto_left + auto_width, 5.6),
            xytext=(auto_left + auto_width + 0.1, 5.7), arrowprops=leader_props)
ax.add_patch(FancyArrowPatch((auto_cx, 4.5), (auto_cx, 4), **arrow_props))

# Additional outputs from Autonomous — constrained
buf_x = auto_left + auto_width - 0.3
ax.add_patch(FancyArrowPatch((buf_x, 5), (buf_x, 4.75), **arrow_props))
ax.add_patch(Rectangle((buf_x - 0.4, 4.25), 0.8, 0.5, fill=False, lw=line_width))
ax.text(buf_x, 4.5, 'Step\nBuffer', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((buf_x, 4.25), (buf_x, 3.85), **arrow_props))
ax.add_patch(Ellipse((buf_x, 3.6), 0.9, 0.4, fill=False, lw=line_width))
ax.text(buf_x, 3.6, 'Snapshots', ha='center', va='center', fontsize=8)

# Bottom section - Neural Processing (ref 108)
ax.add_patch(Rectangle((1.5, 2), 5, 1.5, fill=False, lw=line_width))
ax.text(4.25, 2.75, 'Spiking Neural Network + Energy Harvester',
        ha='center', va='center', fontsize=10)
ax.text(4.25, 2.5, 'Continuous operation regardless of control source',
        ha='center', va='center', fontsize=8)
ax.text(4.25, 2.25, 'THE SYSTEM NEVER STOPS',
        ha='center', va='center', fontsize=10)
ax.text(6.65, 2.75, '108', ha='left', fontsize=8)
ax.annotate('', xy=(6.5, 2.75), xytext=(6.65, 2.75), arrowprops=leader_props)

# Annotations
ax.text(4.25, 1.5, 'Seamless transition: SNN continues processing without interruption',
        ha='center', va='center', fontsize=8)
ax.text(4.25, 1.2, 'The control source changes; the computation continues',
        ha='center', va='center', fontsize=8)

plt.savefig(f'{OUT_DIR}/fig1.svg', format='svg')
plt.close()


# ════════════════════════════════════════════════════════════════════
# FIG. 2 — State Transition Diagram
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(2)

# Three states
# State 1 CONNECTED left
ax.add_patch(FancyBboxPatch((1.5, 6), 2, 2, boxstyle="round,pad=0.1",
                             fill=False, lw=line_width))
ax.text(2.5, 7.5, 'CONNECTED', ha='center', va='center', fontsize=10,
        weight='bold')
ax.text(2.5, 7.2, 'Cognitive layer active',
        ha='center', va='center', fontsize=8)
ax.text(2.5, 7, 'Input from cognitive layer',
        ha='center', va='center', fontsize=8)
ax.text(2.5, 6.8, 'Modulation from cognitive layer',
        ha='center', va='center', fontsize=8)

# State 2 AUTONOMOUS right
ax.add_patch(FancyBboxPatch((5, 6), 2, 2, boxstyle="round,pad=0.1",
                             fill=False, lw=line_width))
ax.text(6, 7.5, 'AUTONOMOUS', ha='center', va='center', fontsize=10)
ax.text(6, 7.2, 'Fallback active', ha='center', va='center', fontsize=8)
ax.text(6, 7, 'Self-generated input', ha='center', va='center', fontsize=8)
ax.text(6, 6.8, 'Energy-aware modulation',
        ha='center', va='center', fontsize=8)
ax.text(6, 6.6, 'State buffering active',
        ha='center', va='center', fontsize=8)

# State 3 RECOVERING bottom
ax.add_patch(FancyBboxPatch((3.75, 3), 2, 1.5, boxstyle="round,pad=0.1",
                             fill=False, lw=line_width))
ax.text(4.75, 4, 'RECOVERING', ha='center', va='center', fontsize=10)
ax.text(4.75, 3.8, 'Resynchronization', ha='center', va='center', fontsize=8)
ax.text(4.75, 3.6, 'Transmitting buffer', ha='center', va='center', fontsize=8)
ax.text(4.75, 3.4, 'Restoring cognitive control',
        ha='center', va='center', fontsize=8)

# Transitions
ax.add_patch(FancyArrowPatch((3.5, 7), (5, 7),
                              connectionstyle="arc3,rad=0.3", **arrow_props))
ax.text(4.25, 7.1, 'Heartbeat timeout (>30s no tool call)',
        ha='center', va='bottom', fontsize=8)

ax.add_patch(FancyArrowPatch((6, 6), (4.75, 4.5),
                              connectionstyle="arc3,rad=-0.3", **arrow_props))
ax.text(5.5, 5.25, 'Cognitive layer reconnects',
        ha='left', va='center', fontsize=8)

ax.add_patch(FancyArrowPatch((3.75, 4), (2.5, 6),
                              connectionstyle="arc3,rad=0.3", **arrow_props))
ax.text(3, 5, 'Resync complete', ha='right', va='center', fontsize=8)

# AUTONOMOUS self-loop
ax.add_patch(FancyArrowPatch((6.8, 7), (6.8, 7),
                              connectionstyle="arc3,rad=1", **arrow_props))
ax.text(6.2, 7.7, 'Each autonomous step\n(up to 10,000)',
        ha='center', va='center', fontsize=8)

# AUTONOMOUS -> CONNECTED direct dashed
ax.add_patch(FancyArrowPatch((5, 7), (3.5, 7), ls='dashed',
                              connectionstyle="arc3,rad=-0.3", **arrow_props))
ax.text(4.25, 6.5, 'Any tool call received\n(heartbeat reset)',
        ha='center', va='center', fontsize=8)

# Annotations
ax.text(2.5, 8.5, 'Initial state', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((2.5, 8.7), (2.5, 8.2), **arrow_props))
ax.text(6, 5.5, 'Snapshot every 50 steps', ha='center', va='center', fontsize=8)
ax.text(6.2, 6.1, 'Hard cap: 10,000 steps', ha='center', va='center', fontsize=8)

plt.savefig(f'{OUT_DIR}/fig2.svg', format='svg')
plt.close()


# ════════════════════════════════════════════════════════════════════
# FIG. 3 — Energy-Aware Modulation Curve
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(3)

# Graph area — inset with safe padding (+0.5" left for y-axis labels)
graph_ax = fig.add_axes([(SAFE_LEFT + 0.5) / paper_width,
                          (SAFE_BOTTOM + 1.0) / paper_height,
                          (SAFE_WIDTH - 0.5) / paper_width,
                          (SAFE_TOP - SAFE_BOTTOM - 2.0) / paper_height])
graph_ax.set_xlabel('System Energy Level (mWh)', fontsize=10)
graph_ax.set_ylabel('Autonomous Modulation Value', fontsize=10)
graph_ax.set_xticks([0, 1])
graph_ax.set_xticklabels(['0', '100+'])
graph_ax.set_yticks([0, 1])
graph_ax.set_yticklabels(['-0.5', '+0.5'])

# Step function
energy_norm = np.array([0, 0.15, 0.3, 0.8, 1.0])
mod_norm = np.array([0.1, 0.4, 0.5, 0.5, 0.8])
for i in range(4):
    graph_ax.plot([energy_norm[i], energy_norm[i+1]], [mod_norm[i], mod_norm[i]],
                  color='black', lw=line_width)
    if i < 3:
        graph_ax.plot([energy_norm[i+1], energy_norm[i+1]],
                      [mod_norm[i], mod_norm[i+1]], color='black', lw=line_width)

for thresh in [0.15, 0.3, 0.8]:
    graph_ax.axvline(x=thresh, ls='dashed', color='black', lw=line_width)

# Hatching
graph_ax.add_patch(Rectangle((0, 0), 0.15, 1, hatch='xxx', fill=False, lw=0))
graph_ax.add_patch(Rectangle((0.15, 0), 0.15, 1, hatch='/', fill=False, lw=0))
graph_ax.add_patch(Rectangle((0.8, 0), 0.2, 1, hatch='/', fill=False, lw=0))

# Labels
graph_ax.text(0.075, 0.95, 'CRITICAL\nMaximum conservation',
              ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)
graph_ax.text(0.225, 0.95, 'LOW\nCautious operation',
              ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)
graph_ax.text(0.55, 0.95, 'NORMAL\nNeutral operation',
              ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)
graph_ax.text(0.9, 0.95, 'SURPLUS\nExploration',
              ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)

ax.text(4.25, bottom_margin + 0.5,
        'System autonomously adjusts processing intensity based on energy — mimicking metabolic regulation',
        ha='center', fontsize=8)

plt.savefig(f'{OUT_DIR}/fig3.svg', format='svg')
plt.close()


# ════════════════════════════════════════════════════════════════════
# FIG. 4 — Autonomous Input Generator Output
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(4)

# Main graph — inset with safe padding (+0.5" left for y-axis labels)
main_ax = fig.add_axes([(SAFE_LEFT + 0.5) / paper_width,
                         (SAFE_BOTTOM + 3.0) / paper_height,
                         (SAFE_WIDTH - 0.5) / paper_width,
                         3.8 / paper_height])
main_ax.set_xlabel('Autonomous Step Number', fontsize=10)
main_ax.set_ylabel('Input Value', fontsize=10)
main_ax.set_title('Autonomous Input Generator Output', fontsize=10, weight='bold')

steps = np.linspace(0, 500, 501)
base = 0.5 + 0.3 * np.sin(2 * np.pi * steps / 500)
main_ax.plot(steps, base, ls='-', color='black', lw=1,
             label='Circadian base signal')

# Bursts
np.random.seed(42)
burst_indices = np.random.choice(range(501), int(501 * 0.1), replace=False)
composite = base.copy()
for idx in burst_indices:
    burst_val = np.random.uniform(0.3, 0.8)
    composite[idx] = min(1.0, base[idx] + 0.2)

main_ax.plot(steps, composite, color='black', lw=0.5, alpha=0.5)
# Mark a few representative bursts
for idx in sorted(burst_indices)[:8]:
    main_ax.plot([steps[idx], steps[idx]], [base[idx], composite[idx]],
                 color='black', lw=1.5)

main_ax.set_xlim(0, 500)
main_ax.set_ylim(0, 1.05)
main_ax.legend(fontsize=8)

main_ax.text(400, 0.95, 'base = 0.5 + 0.3×sin(2π×step/500)',
             fontsize=8, ha='right')
main_ax.text(400, 0.88, '10% probability attention bursts',
             fontsize=8, ha='right')

# Small energy graph — inset with safe padding (+0.5" left for y-axis labels)
small_ax = fig.add_axes([(SAFE_LEFT + 0.5) / paper_width,
                          (SAFE_BOTTOM + 1.0) / paper_height,
                          (SAFE_WIDTH - 0.5) / paper_width,
                          1.4 / paper_height])
small_ax.set_xlabel('Autonomous Step Number', fontsize=8)
small_ax.set_ylabel('Energy (mWh)', fontsize=8)
energy = 50 + np.cumsum(np.random.normal(0.01, 0.3, 501))
energy = np.clip(energy, 0, 100)
small_ax.plot(steps, energy, color='black', lw=1)
for thresh in [15, 30, 80]:
    small_ax.axhline(thresh, ls='dashed', color='black', lw=0.5)
    small_ax.text(500, thresh + 1, f'{thresh} mWh', fontsize=8, ha='right')
small_ax.set_xlim(0, 500)
small_ax.set_ylim(0, 100)

ax.text(4.25, bottom_margin + 0.5, 'Energy-aware modulation adjusts intensity',
        ha='center', fontsize=8)

plt.savefig(f'{OUT_DIR}/fig4.svg', format='svg')
plt.close()


# ════════════════════════════════════════════════════════════════════
# FIG. 5 — Resynchronization Payload Structure
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(5)

# Top-level
ax.add_patch(Rectangle((2, 7), 4, 3, fill=False, lw=line_width))
ax.text(4, 9.75, 'Resynchronization Payload',
        ha='center', va='center', fontsize=10)

# Section 1
ax.add_patch(Rectangle((2.5, 8.5), 3, 1, fill=False, lw=line_width))
ax.text(4, 9.25, 'Summary Statistics', ha='center', va='center', fontsize=10)
text_summary = ("steps_autonomous: [integer]\n"
                "energy_delta: [float] mWh\n"
                "min/max/mean_energy: [float] mWh\n"
                "total_spikes: [integer]\n"
                "mean_spikes_per_step: [float]")
ax.text(4, 8.8, text_summary, ha='center', va='center',
        fontsize=8, linespacing=1.5)
ax.text(4, 8.1, 'ALWAYS included (~200 bytes)',
        ha='center', va='center', fontsize=8)

# Section 2
ax.add_patch(Rectangle((2.5, 4), 3, 2, fill=False, lw=line_width))
ax.text(4, 5.75, 'Full Step Buffer (Optional)', ha='center', va='center',
        fontsize=10)
text_buffer = ("Step 0: {input, mod, spikes, energy, temp, pattern}\n"
               "Step 1: {input, mod, spikes, energy, temp, pattern}\n"
               "...\n"
               "Step N: {input, mod, spikes, energy, temp, pattern}")
ax.text(4, 5, text_buffer, ha='center', va='center',
        fontsize=8, linespacing=1.5)
ax.text(4, 4.25, 'OPTIONAL (~100 bytes × N steps)',
        ha='center', va='center', fontsize=8)

# Granularity labels — positioned inside safe area with left-aligned text
ax.add_patch(FancyArrowPatch((2, 8.75), (1.5, 8.75), **arrow_props))
ax.text(1.5, 9.0, 'Level 1:\nSummary only', ha='center', va='bottom', fontsize=8)
ax.add_patch(FancyArrowPatch((2, 5), (1.5, 5), **arrow_props))
ax.text(1.5, 5.25, 'Level 2:\nFull buffer', ha='center', va='bottom', fontsize=8)

# Decision diamond
ax.add_patch(Polygon([[4, 3], [3.5, 2.5], [4, 2], [4.5, 2.5]],
                      closed=True, fill=False, lw=line_width))
ax.text(4, 2.5, 'Full buffer\nrequested?', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((4.5, 2.5), (5.5, 2.5), **arrow_props))
ax.text(5.6, 2.5, 'Yes: Level 2', ha='left', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((3.5, 2.5), (2.5, 2.5), **arrow_props))
ax.text(2.4, 2.5, 'No: Level 1', ha='right', va='center', fontsize=8)

plt.savefig(f'{OUT_DIR}/fig5.svg', format='svg')
plt.close()


# ════════════════════════════════════════════════════════════════════
# FIG. 6 — Recovery Timeline Diagrams
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(6)

# Timeline A — compressed x positions to stay within right margin
ax.text(SAFE_LEFT, 9.2, 'Timeline A — Normal Reconnection:',
        ha='left', fontsize=10, weight='bold')
ax.add_patch(FancyArrowPatch((SAFE_LEFT, 8.5),
                              (SAFE_RIGHT, 8.5),
                              arrowstyle='->', lw=line_width))
phases_a = [
    (1.2, 'Connected', '[Claude active]'),
    (2.5, 'Timeout', '[Watchdog]'),
    (3.8, 'Autonomous', '[Self-regulated]'),
    (5.1, 'Resync', '[Buffer sent]'),
    (6.3, 'Connected', '[Restored]'),
]
for x, label, sub in phases_a:
    ax.text(x, 8.65, label, ha='left', va='bottom', fontsize=8, weight='bold')
    ax.text(x, 8.35, sub, ha='left', va='top', fontsize=7)

# Timeline B — compressed x positions
ax.text(SAFE_LEFT, 7.0, 'Timeline B — Crash Recovery:',
        ha='left', fontsize=10, weight='bold')
ax.add_patch(FancyArrowPatch((SAFE_LEFT, 6.3),
                              (SAFE_RIGHT, 6.3),
                              arrowstyle='->', lw=line_width))
phases_b = [
    (1.2, 'Connected', '[Normal op]'),
    (2.5, 'CRASH', '[Server dies]'),
    (3.8, 'Restart', '[Relaunched]'),
    (5.1, 'Snapshot', '[latest.json]'),
    (6.3, 'Connected', '[Restored]'),
]
for x, label, sub in phases_b:
    ax.text(x, 6.45, label, ha='left', va='bottom', fontsize=8, weight='bold')
    ax.text(x, 6.15, sub, ha='left', va='top', fontsize=7)
ax.text(4.25, 5.6, 'Max state loss = 50 steps (snapshot interval)',
        ha='center', fontsize=8)

# Timeline C — compressed x positions
ax.text(SAFE_LEFT, 4.5, 'Timeline C — Clean Shutdown:',
        ha='left', fontsize=10, weight='bold')
ax.add_patch(FancyArrowPatch((SAFE_LEFT, 3.8),
                              (SAFE_RIGHT - 1.0, 3.8),
                              arrowstyle='->', lw=line_width))
phases_c = [
    (1.2, 'Connected', '[Normal op]'),
    (2.8, 'Autonomous', '[Fallback]'),
    (4.4, 'EOF Signal', '[stdin closed]'),
    (5.8, 'Shutdown', '[Snapshot written]'),
]
for x, label, sub in phases_c:
    ax.text(x, 3.95, label, ha='left', va='bottom', fontsize=8, weight='bold')
    ax.text(x, 3.65, sub, ha='left', va='top', fontsize=7)
ax.text(4.25, 3.1, 'State preserved for next session — zero data loss',
        ha='center', fontsize=8)

# Common legend
ax.text(4.25, 2.0, 'Solid segments: System actively processing',
        ha='center', fontsize=8)
ax.text(4.25, 1.7, 'Dashed segments: System in transition',
        ha='center', fontsize=8)
ax.text(4.25, 1.4, 'Bold marker at each state change: No data loss at any transition',
        ha='center', fontsize=8, weight='bold')

plt.savefig(f'{OUT_DIR}/fig6.svg', format='svg')
plt.close()


# ════════════════════════════════════════════════════════════════════
# FIG. 7 — End-to-End Signal Flow: Connected vs. Autonomous Operation
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(7)

ax.text(SAFE_CX, SAFE_TOP - 0.15,
        'End-to-End Signal Flow: Connected vs. Autonomous Operation',
        ha='center', fontsize=font_body, weight='bold')

# ── TOP HALF: Connected Mode ──
ax.text(SAFE_LEFT, 9.8, 'CONNECTED MODE', fontsize=font_body, weight='bold')

# External Cognitive Layer (cloud)
ax.add_patch(Ellipse((4.25, 9.3), 2.5, 0.6, fill=False, lw=line_width))
ax.text(4.25, 9.3, 'External Cognitive Layer',
        ha='center', va='center', fontsize=font_small)

# Dashed arrow down from cloud
ax.add_patch(FancyArrowPatch((4.25, 9.0), (4.25, 8.65),
                              linestyle='dashed', **arrow_props))
ax.text(5.5, 8.8, 'Cognitive modulation\ncommands', fontsize=8)

# Connected mode pipeline — constrained within safe margins
pipe_y_top = 8.0
blocks_top = [
    (1.2, 'Sensors', 0.9),
    (2.35, 'SNN', 0.9),
    (3.5, 'Cognitive\nModulation', 1.2),
    (4.95, 'Motor\nActuator', 0.9),
    (6.1, 'Energy\nHarvester', 0.9),
]
bh = 0.55

for bx, label, bw in blocks_top:
    ax.add_patch(Rectangle((bx, pipe_y_top), bw, bh, fill=False, lw=line_width))
    ax.text(bx + bw / 2, pipe_y_top + bh / 2, label,
            ha='center', va='center', fontsize=8)

# Forward arrows in top pipeline
ax.add_patch(FancyArrowPatch((2.1, pipe_y_top + bh / 2),
                              (2.35, pipe_y_top + bh / 2), **arrow_props))
ax.add_patch(FancyArrowPatch((3.25, pipe_y_top + bh / 2),
                              (3.5, pipe_y_top + bh / 2), **arrow_props))
ax.add_patch(FancyArrowPatch((4.7, pipe_y_top + bh / 2),
                              (4.95, pipe_y_top + bh / 2), **arrow_props))
ax.add_patch(FancyArrowPatch((5.85, pipe_y_top + bh / 2),
                              (6.1, pipe_y_top + bh / 2), **arrow_props))

# Energy feedback (bold dashed) — right edge at 7.0, within safe bounds
ax.add_patch(FancyArrowPatch((7.0, pipe_y_top),
                              (3.0, pipe_y_top),
                              connectionstyle="arc3,rad=-0.3",
                              linestyle='dashed', lw=line_width * 1.5,
                              arrowstyle='->', color='black'))
ax.text(5.0, pipe_y_top - 0.3, 'Energy feedback',
        ha='center', fontsize=8)

# Self-observation (dotted)
ax.add_patch(FancyArrowPatch((2.9, pipe_y_top + bh),
                              (2.35, pipe_y_top + bh),
                              connectionstyle="arc3,rad=0.3",
                              linestyle='dotted', lw=line_width * 1.5,
                              arrowstyle='->', color='black'))
ax.text(2.5, pipe_y_top + bh + 0.2, 'Self-observation',
        ha='center', fontsize=8)

# Cognitive modulation arrow from cloud
ax.add_patch(FancyArrowPatch((4.25, 8.65), (4.1, pipe_y_top + bh),
                              linestyle='dashed', **arrow_props))

ax.text(SAFE_LEFT + 0.35, 7.4, 'Heartbeat active (tool calls within 30s)',
        fontsize=8, style='italic')

# ── DIVIDING LINE ──
div_y = 6.8
ax.plot([SAFE_LEFT, SAFE_RIGHT], [div_y, div_y],
        'k--', lw=line_width)
ax.text(4.25, div_y + 0.15,
        'DISCONNECTION EVENT (heartbeat timeout > 30s)',
        ha='center', fontsize=font_small, weight='bold')
ax.text(4.25, div_y - 0.15,
        'Seamless transition — no interruption to SNN or Harvester',
        ha='center', fontsize=8, style='italic')

# ── BOTTOM HALF: Autonomous Mode ──
ax.text(SAFE_LEFT, 6.4, 'AUTONOMOUS MODE', fontsize=font_body, weight='bold')

pipe_y_bot = 5.5

# Autonomous pipeline — constrained within safe margins (right edge < 7.725)
blocks_bot = [
    (1.2, 'Autonomous\nInput Gen', 1.2),
    (2.65, 'SNN', 0.9),
    (3.8, 'Energy-Aware\nSelf-Mod', 1.4),
    (5.45, 'Motor\nActuator', 0.85),
    (6.55, 'Energy\nHarvest', 0.85),
]

for bx, label, bw in blocks_bot:
    ax.add_patch(Rectangle((bx, pipe_y_bot), bw, bh, fill=False, lw=line_width))
    ax.text(bx + bw / 2, pipe_y_bot + bh / 2, label,
            ha='center', va='center', fontsize=7)

# Forward arrows
ax.add_patch(FancyArrowPatch((2.4, pipe_y_bot + bh / 2),
                              (2.65, pipe_y_bot + bh / 2), **arrow_props))
ax.add_patch(FancyArrowPatch((3.55, pipe_y_bot + bh / 2),
                              (3.8, pipe_y_bot + bh / 2), **arrow_props))
ax.add_patch(FancyArrowPatch((5.2, pipe_y_bot + bh / 2),
                              (5.45, pipe_y_bot + bh / 2), **arrow_props))
ax.add_patch(FancyArrowPatch((6.3, pipe_y_bot + bh / 2),
                              (6.55, pipe_y_bot + bh / 2), **arrow_props))

# Energy feedback (bold dashed) — right edge at 7.4, within safe bounds
ax.add_patch(FancyArrowPatch((7.4, pipe_y_bot),
                              (3.1, pipe_y_bot),
                              connectionstyle="arc3,rad=-0.3",
                              linestyle='dashed', lw=line_width * 1.5,
                              arrowstyle='->', color='black'))
ax.text(5.2, pipe_y_bot - 0.35, 'Energy feedback',
        ha='center', fontsize=8)

# Self-observation (dotted)
ax.add_patch(FancyArrowPatch((3.1, pipe_y_bot + bh),
                              (2.65, pipe_y_bot + bh),
                              connectionstyle="arc3,rad=0.3",
                              linestyle='dotted', lw=line_width * 1.5,
                              arrowstyle='->', color='black'))

# Input generator details
ax.text(1.75, pipe_y_bot - 0.2, 'Circadian base signal',
        ha='center', fontsize=8)
ax.text(1.75, pipe_y_bot - 0.4, '10% stochastic bursts',
        ha='center', fontsize=8)

# Self-modulation detail
ax.text(5.2, pipe_y_bot - 0.2,
        '<15:−0.4 | <30:−0.1 | 30-80:0.0 | >80:+0.3',
        ha='center', fontsize=8)

# State Buffer (cylinder) — left edge within safe bounds
buf_x, buf_y = SAFE_LEFT, 3.8
ax.add_patch(Ellipse((buf_x + 0.5, buf_y + 0.6), 1.0, 0.3,
                      fill=False, lw=line_width))
ax.add_patch(Rectangle((buf_x, buf_y), 1.0, 0.6, fill=False, lw=line_width))
ax.add_patch(Ellipse((buf_x + 0.5, buf_y), 1.0, 0.3,
                      fill=False, lw=line_width))
ax.text(buf_x + 0.5, buf_y + 0.3, 'State\nBuffer',
        ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((2.65, pipe_y_bot), (buf_x + 1.0, buf_y + 0.6),
                              **arrow_props))
ax.text(2.2, 4.6, 'Every step', fontsize=8)

# Snapshot Writer (disk) — left edge within safe bounds
snap_x, snap_y = SAFE_LEFT, 2.5
ax.add_patch(Rectangle((snap_x, snap_y), 1.0, 0.6, fill=False, lw=line_width))
ax.text(snap_x + 0.5, snap_y + 0.3, 'Snapshots\nlatest.json',
        ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((buf_x + 0.5, buf_y), (snap_x + 0.5, snap_y + 0.6),
                              **arrow_props))
ax.text(SAFE_LEFT + 0.5, 3.3, 'Every 50\nsteps', fontsize=8, ha='center')

# Right side — Reconnection — constrained within right margin
recon_x, recon_y = 5.7, 3.5
recon_w = 1.8
ax.add_patch(Rectangle((recon_x, recon_y), recon_w, 1.2, fill=False, lw=line_width,
                         ls='--'))
ax.text(recon_x + recon_w / 2, recon_y + 0.9, 'Resync Payload',
        ha='center', fontsize=font_small, weight='bold')
ax.text(recon_x + recon_w / 2, recon_y + 0.55, 'steps, energy_delta',
        ha='center', fontsize=8)
ax.text(recon_x + recon_w / 2, recon_y + 0.3, 'Optional: full buffer',
        ha='center', fontsize=8)

# Arrow from buffer to resync
ax.add_patch(FancyArrowPatch((buf_x + 1.0, buf_y + 0.3),
                              (recon_x, recon_y + 0.6), **arrow_props))

# Arrow from resync up to connected mode
ax.add_patch(FancyArrowPatch((recon_x + recon_w / 2, recon_y + 1.2),
                              (recon_x + recon_w / 2, div_y),
                              linestyle='dashed', **arrow_props))
ax.text(recon_x + recon_w / 2 + 0.2, 5.0, 'resync()',
        fontsize=8, ha='left')

# Key annotations
ax.text(SAFE_CX, 1.8,
        'Fallback changes INPUT SOURCE and MODULATION SOURCE',
        ha='center', fontsize=font_small, weight='bold')
ax.text(SAFE_CX, 1.4,
        'Core neural processing, motor actuation, energy harvesting',
        ha='center', fontsize=font_small)
ax.text(SAFE_CX, 1.1,
        'continue WITHOUT INTERRUPTION through the transition',
        ha='center', fontsize=font_small, weight='bold')

# Legend — within safe bounds
leg_y = SAFE_BOTTOM + 0.1
ax.plot([SAFE_LEFT + 0.1, SAFE_LEFT + 0.8], [leg_y, leg_y], 'k-', lw=line_width)
ax.text(SAFE_LEFT + 1.0, leg_y, 'Forward signal', va='center', fontsize=8)
ax.plot([3.2, 4.0], [leg_y, leg_y], 'k--', lw=line_width * 1.5)
ax.text(4.2, leg_y, 'Energy feedback', va='center', fontsize=8)
ax.plot([5.4, 6.2], [leg_y, leg_y], 'k:', lw=line_width * 1.5)
ax.text(6.4, leg_y, 'Self-observation', va='center', fontsize=8)

plt.savefig(f'{OUT_DIR}/fig7.svg', format='svg')
plt.close()


print(f"All {TOTAL_SHEETS} Patent C figures generated in {OUT_DIR}/")

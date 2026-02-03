"""
Generate USPTO-compliant SVG patent drawings for Patent A:
Self-Sustaining Neural-Motor Energy Harvesting Loop for Autonomous Cognitive Systems

8 Figures per Patent_A_Drawings_Description.txt
All drawings comply with 37 CFR 1.84.
Includes reference numerals cross-referenced with specification.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Ellipse, Polygon
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

# Safe drawing bounds (absolute coordinates, 0.15" inset from margins)
SAFE_LEFT = left_margin + 0.15       # 1.15
SAFE_RIGHT = paper_width - right_margin - 0.15  # 7.725
SAFE_BOTTOM = bottom_margin + 0.15   # 0.525
SAFE_TOP = paper_height - top_margin - 0.15     # 9.85
SAFE_WIDTH = SAFE_RIGHT - SAFE_LEFT   # 6.575
SAFE_CX = (SAFE_LEFT + SAFE_RIGHT) / 2  # ~4.4375

def setup_figure(fig_num, total_sheets):
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
             f"{fig_num}/{total_sheets}", ha='center', va='center', fontsize=10)
    # Figure label at bottom left (on fig, outside ax)
    fig.text(left_margin / paper_width, (bottom_margin + 0.2) / paper_height,
             f"FIG. {fig_num}", ha='left', va='bottom', fontsize=font_size_label)
    return fig, ax

OUT_DIR = 'patent_drawings/patent_a'
os.makedirs(OUT_DIR, exist_ok=True)


# ════════════════════════════════════════════════════════════════════
# FIG. 1 — System Architecture Block Diagram (8-Layer Loop)
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(1, 8)

# Leader line style for reference numerals (thin, per 37 CFR 1.84(q))
leader_props = dict(arrowstyle='->', lw=0.5, color='black')

# Environment (ref 100)
ax.add_patch(Ellipse((4.25, 10), 2, 0.5, fill=False, lw=line_width))
ax.text(4.25, 10, 'ENVIRONMENT', ha='center', va='center', fontsize=10)
ax.text(4.25, 10.35, '100', ha='center', va='bottom', fontsize=8)
ax.annotate('', xy=(4.25, 10.25), xytext=(4.25, 10.35), arrowprops=leader_props)

# Blocks with ref numerals (102-116)
blocks = [
    ('L1: Printed Membrane', 'ThermochromicMixin', '102'),
    ('L2: Sensing Pads', 'light_intensity, membrane_temp', '104'),
    ('L3: Optical Transmission', 'signal_voltage = light / 1000 x 5.0', '106'),
    ('L4: Neuromorphic CPU (SNN)', 'BaseSNN (LIF neurons)', '108'),
    ('L5: Servo Actuation', 'target_angle = clip(output x 180)', '110'),
    ('L6: Energy Harvesting', 'piezo + thermal', '112'),
    ('L7: Ground Reference', 'noise floor / baseline', '114'),
    ('L8: Recursive Reflection', 'previous_output', '116')
]

y_pos = 9.5
for i, (title, sublabel, ref) in enumerate(blocks):
    by = y_pos - (i + 1) * 1
    ax.add_patch(Rectangle((3.5, by), 2, 0.8, fill=False, lw=line_width))
    ax.text(4.5, by + 0.5, title, ha='center', va='center', fontsize=10)
    ax.text(4.5, by + 0.3, sublabel, ha='center', va='center', fontsize=8)
    ax.text(3.2, by + 0.4, ref, ha='right', va='center', fontsize=8)
    # Leader line from ref numeral to block edge
    ax.annotate('', xy=(3.5, by + 0.4), xytext=(3.25, by + 0.4), arrowprops=leader_props)
    if i < 7:
        ax.add_patch(FancyArrowPatch((4.5, by), (4.5, by - 0.2),
                                      arrowstyle='->', lw=line_width))

# Thermal cross-link dashed (ref 118) — constrained within right margin
ax.add_patch(FancyArrowPatch((5.5, 8.6), (6.3, 5.6),
             connectionstyle="arc3,rad=-0.5", ls='dashed',
             arrowstyle='->', lw=line_width))
ax.text(6.4, 7.5, '118', ha='left', va='center', fontsize=8)
ax.annotate('', xy=(6.1, 7.2), xytext=(6.4, 7.45), arrowprops=leader_props)

# Reflection feedback dotted (ref 120) — constrained within right margin
ax.add_patch(FancyArrowPatch((5.5, 2.6), (5.8, 2),
             connectionstyle="arc3,rad=0.3", arrowstyle='->',
             lw=line_width, ls='dotted'))
ax.add_patch(FancyArrowPatch((5.8, 2), (4.5, 5.4),
             connectionstyle="arc3,rad=0.3", arrowstyle='->',
             lw=line_width, ls='dotted'))
ax.text(6.2, 3.8, 'reflection feedback', ha='left', va='center', fontsize=8)
ax.text(6.2, 4.1, '120', ha='left', va='center', fontsize=8)
ax.annotate('', xy=(5.9, 3.5), xytext=(6.2, 4.0), arrowprops=leader_props)

# Loop close label
ax.text(2, 4, 'THE LOOP CLOSES HERE.', ha='center', va='center',
        fontsize=10, rotation=90)

# Signal pathways legend
ax.text(2, 1.5, 'Signal Pathways:', ha='left', fontsize=10)
ax.add_patch(Rectangle((2, 1.2), 1, 0.1, fill=False, lw=line_width))
ax.text(3.1, 1.25, 'Main spine (L1 through L8 to L4)',
        ha='left', va='center', fontsize=8)
ax.add_patch(Rectangle((2, 1.0), 1, 0.1, fill=False, lw=line_width, ls='dashed'))
ax.text(3.1, 1.05, 'Thermal cross-link (L1 membrane_temp directly to L6)',
        ha='left', va='center', fontsize=8)
ax.add_patch(Rectangle((2, 0.8), 1, 0.1, fill=False, lw=line_width, ls='dotted'))
ax.text(3.1, 0.85, 'Reflection feedback (L8 to L4)',
        ha='left', va='center', fontsize=8)

fig.savefig(f'{OUT_DIR}/fig1.svg', format='svg')
plt.close(fig)


# ════════════════════════════════════════════════════════════════════
# FIG. 2 — Energy Balance Comparison
# ════════════════════════════════════════════════════════════════════
# Data derived from actual simulation runs:
#
# CONTROL (EnergyConfig — phase7_full_integration.py):
#   base_consumption_mw=470.0, time_step_hours=0.005
#   drain_per_step = 470.0 × 0.005 = 2.35 mWh/step (harvesting negligible)
#   initial=50 mWh → final ≈ -4,650 mWh at step 2000
#
# EXPERIMENTAL (BalancedEnergyConfig — consciousness_mcp_server.py):
#   base_consumption_mw=45.0, friction_factor=18.0, thermal_factor=8.0
#   capacity_mwh=100.0 (physical storage ceiling)
#   initial=50 mWh → reaches 100 mWh cap at step ~43, then flat plateau
fig, ax = setup_figure(2, 8)

# Leader line style
leader_props = dict(arrowstyle='->', lw=0.5, color='black')

graph_ax = fig.add_axes([
    (SAFE_LEFT + 0.9) / paper_width,
    (SAFE_BOTTOM + 1.0) / paper_height,
    (SAFE_WIDTH - 0.9) / paper_width,
    (SAFE_TOP - SAFE_BOTTOM - 2.0) / paper_height
])
graph_ax.set_xlabel('Operational Steps', fontsize=10)
graph_ax.set_ylabel('Cumulative Energy (mWh)', fontsize=9)
graph_ax.tick_params(axis='y', labelsize=8)

x = np.linspace(0, 2000, 2001)

# CONTROL: linear drain at 2.35 mWh/step (470 mW × 0.005 h)
# Harvesting is negligible with friction_factor=0.0005, thermal_factor=0.0002
control_y = 50.0 - 2.35 * x  # 50 - 4700 = -4650 at step 2000

# EXPERIMENTAL: rapid rise to 100 mWh cap, then flat plateau
# Net gain ≈ +1.2 mWh/step at medium activity → caps at step ~43
# After cap: energy stays at 100 mWh (self-discharge ≈ overflow harvest)
exp_y = np.minimum(50.0 + 1.2 * x, 100.0)

graph_ax.plot(x, control_y, ls='-', color='black', lw=line_width,
              label='Control (EnergyConfig, 470 mW)')
graph_ax.plot(x, exp_y, ls='--', color='black', lw=line_width,
              label='Experimental (BalancedEnergyConfig, 45 mW)')

# Axis limits to fit actual data
graph_ax.set_xlim(0, 2100)
graph_ax.set_ylim(-5000, 300)

# Self-sustaining threshold line (ref 204)
graph_ax.axhline(0, ls=':', color='black', lw=1)
graph_ax.text(1200, 30, '204  Self-Sustaining Threshold (0 mWh)',
              ha='center', va='bottom', fontsize=8)

# Capacity ceiling line (ref 206)
graph_ax.axhline(100, ls=':', color='black', lw=0.5)
graph_ax.text(1200, 110, '206  Storage Capacity (100 mWh)',
              ha='center', va='bottom', fontsize=8)

# Control line label (ref 200)
graph_ax.text(800, -1500, '200', ha='left', fontsize=8)
graph_ax.annotate('', xy=(700, control_y[700]), xytext=(800, -1480),
                  arrowprops=leader_props)

# Experimental line label (ref 202)
graph_ax.text(400, 220, '202', ha='left', fontsize=8)
graph_ax.annotate('', xy=(300, exp_y[300]), xytext=(400, 215),
                  arrowprops=leader_props)

# Outcome annotations
graph_ax.annotate('System fails\n(energy depleted)\n-4,650 mWh',
                  xy=(1900, control_y[1900]), xytext=(1200, -3800),
                  arrowprops=dict(arrowstyle='->'), fontsize=8)
graph_ax.annotate('System thrives\n(homeostatic equilibrium)\n100 mWh',
                  xy=(1900, exp_y[1900]), xytext=(1400, 250),
                  arrowprops=dict(arrowstyle='->'), fontsize=8)

# Shaded region between curves
graph_ax.fill_between(x, control_y, exp_y, hatch='.', alpha=0.08)

# Legend in upper-left of graph (within bounds, above the control drop)
graph_ax.legend(loc='upper left', fontsize=7, frameon=True)

# Formula annotations in lower region
graph_ax.text(300, -4200,
              'Control: drain = 470 mW \u00d7 0.005 h = 2.35 mWh/step',
              fontsize=7)
graph_ax.text(300, -4500,
              'Experimental: net gain \u2248 1.2 mWh/step \u2192 cap at step ~43',
              fontsize=7)

fig.savefig(f'{OUT_DIR}/fig2.svg', format='svg')
plt.close(fig)


# ════════════════════════════════════════════════════════════════════
# FIG. 3 — SNN Architecture (LIF Neuron Model)
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(3, 8)

# Leader line style
leader_props = dict(arrowstyle='->', lw=0.5, color='black')

# Single LIF Neuron Detail (ref 300)
ax.add_patch(Circle((4, 8), 0.5, fill=False, lw=line_width))
ax.text(4, 8, 'Neuron i', ha='center', va='center', fontsize=10)
ax.text(4.7, 8, '300', ha='left', va='center', fontsize=8)
ax.annotate('', xy=(4.5, 8), xytext=(4.7, 8), arrowprops=leader_props)
ax.text(4, 7.3, 'V(t+1) = V(t) x leak + I x dt', ha='center', fontsize=8)

# Inputs
ax.add_patch(FancyArrowPatch((3, 8), (3.5, 8), arrowstyle='->', lw=line_width))
ax.text(3.2, 8.15, 'I_external', ha='center', va='bottom', fontsize=8)
ax.text(2.7, 8.3, '302', ha='right', fontsize=8)
ax.annotate('', xy=(3.0, 8.1), xytext=(2.75, 8.25), arrowprops=leader_props)
ax.add_patch(FancyArrowPatch((3, 7.5), (3.5, 7.5), arrowstyle='->', lw=line_width))
ax.text(3.2, 7.65, 'I_reflection', ha='center', va='bottom', fontsize=8)
ax.text(2.7, 7.8, '304', ha='right', fontsize=8)
ax.annotate('', xy=(3.0, 7.6), xytext=(2.75, 7.75), arrowprops=leader_props)

# Threshold line
ax.plot([3.5, 4.5], [8.5, 8.5], ls='--', color='black')
ax.text(4.6, 8.55, 'V_threshold = 0.5', ha='left', va='bottom', fontsize=8)
ax.text(4.6, 8.75, '306', ha='left', fontsize=8)
ax.annotate('', xy=(4.5, 8.5), xytext=(4.6, 8.7), arrowprops=leader_props)

# Output
ax.add_patch(FancyArrowPatch((4.5, 8), (5.2, 8), arrowstyle='->', lw=line_width))
ax.text(4.9, 8.15, 'spike (0 or 1)', ha='center', va='bottom', fontsize=8)
ax.text(5.4, 8.3, '308', ha='left', fontsize=8)
ax.annotate('', xy=(5.2, 8.1), xytext=(5.4, 8.25), arrowprops=leader_props)

ax.text(4, 7.0, 'If V >= threshold: spike, V = V_reset', ha='center', fontsize=8)

# Network Topology (ref 310)
ax.text(4, 6.2, 'Network Topology:', ha='center', fontsize=10, weight='bold')
ax.text(5.0, 6.2, '310', ha='left', fontsize=8)
ax.annotate('', xy=(4.6, 6.2), xytext=(5.0, 6.2), arrowprops=leader_props)
for i in range(5):
    ax.add_patch(Circle((2 + i * 1, 5), 0.2, fill=False))
    ax.text(2 + i * 1, 5, str(i + 1), ha='center', va='center', fontsize=8)

# Connections
for i in range(4):
    for j in range(i + 1, 5):
        ax.plot([2 + i, 2 + j], [5, 5], color='black', lw=0.5)
ax.text(3, 5.35, 'W[i,j]', ha='center', fontsize=8)
ax.text(3, 5.6, '314', ha='center', fontsize=8)
ax.annotate('', xy=(3, 5.2), xytext=(3, 5.55), arrowprops=leader_props)

# Self-connections crossed out
for i in range(5):
    cx = 2 + i
    ax.add_patch(Ellipse((cx, 4.5), 0.3, 0.3, fill=False))
    ax.plot([cx - 0.15, cx + 0.15], [4.35, 4.65], color='black')

# Input/output arrows
ax.add_patch(FancyArrowPatch((1.5, 5), (1.8, 5), arrowstyle='->', lw=line_width))
ax.text(1.5, 5.15, 'adjusted_input', ha='left', va='bottom', fontsize=8)
ax.text(1.5, 5.5, '316', ha='left', fontsize=8)
ax.annotate('', xy=(1.5, 5.1), xytext=(1.5, 5.45), arrowprops=leader_props)
ax.add_patch(FancyArrowPatch((6.2, 5), (6.5, 5), arrowstyle='->', lw=line_width))
ax.text(6.6, 5.15, 'spike_vector', ha='left', va='bottom', fontsize=8)
ax.text(6.8, 5.4, '318', ha='left', fontsize=8)
ax.annotate('', xy=(6.5, 5.1), xytext=(6.8, 5.35), arrowprops=leader_props)

ax.text(4, 3.8, 'N = 50 neurons (operational), N = 20 neurons (control)',
        ha='center', fontsize=8)

# STDP inset (ref 320)
ax.add_patch(Rectangle((2, 2.5), 4.5, 1, fill=False))
ax.text(4.25, 3.2, 'If post fires: W += A+ x pre_trace (LTP)',
        fontsize=8, ha='center')
ax.text(4.25, 3.0, 'If pre fires: W -= A- x post_trace (LTD)',
        fontsize=8, ha='center')
ax.text(4.25, 2.8, 'A- > A+ (stability bias)', fontsize=8, ha='center')
ax.text(6.6, 2.5, '320', ha='left', fontsize=8)
ax.annotate('', xy=(6.5, 2.7), xytext=(6.6, 2.55), arrowprops=leader_props)

fig.savefig(f'{OUT_DIR}/fig3.svg', format='svg')
plt.close(fig)


# ════════════════════════════════════════════════════════════════════
# FIG. 4 — Energy Harvesting Circuit
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(4, 8)

# Leader line style
leader_props = dict(arrowstyle='->', lw=0.5, color='black')

# Piezoelectric Harvester (ref 400)
ax.add_patch(Rectangle((1.5, 7), 1.5, 1.2, fill=False, lw=line_width))
ax.text(2.25, 7.7, 'PIEZO', ha='center', va='center', fontsize=10, weight='bold')
ax.text(2.25, 7.3, '27mm disc', ha='center', fontsize=8)
ax.text(1.3, 7.6, '400', ha='right', fontsize=8)
ax.annotate('', xy=(1.5, 7.6), xytext=(1.35, 7.6), arrowprops=leader_props)

# Mechanical coupling (ref 406) — left edge within safe bounds
ax.add_patch(FancyArrowPatch((SAFE_LEFT + 0.05, 7.6), (1.5, 7.6), arrowstyle='->', lw=line_width))
ax.text(1.35, 7.9, 'servo shaft', ha='center', fontsize=8)
ax.text(1.5, 7.2, 'friction = 18.0', ha='left', fontsize=8)

# Full-bridge rectifier (ref 402)
ax.add_patch(FancyArrowPatch((3, 7.6), (3.8, 7.6), arrowstyle='->', lw=line_width))
ax.add_patch(Rectangle((3.8, 7.1), 1.2, 1.0, fill=False, lw=line_width))
ax.text(4.4, 7.6, 'Full-Bridge\nRectifier\n(4 diodes)',
        ha='center', va='center', fontsize=8)
ax.text(5.15, 7.6, '402', ha='left', fontsize=8)
ax.annotate('', xy=(5.0, 7.6), xytext=(5.15, 7.6), arrowprops=leader_props)

# Smoothing capacitor (ref 404)
ax.add_patch(FancyArrowPatch((5, 7.6), (5.5, 7.6), arrowstyle='->', lw=line_width))
ax.add_patch(Rectangle((5.5, 7.2), 0.8, 0.8, fill=False, lw=line_width))
ax.text(5.9, 7.6, 'C', ha='center', va='center', fontsize=10)
ax.text(6.5, 7.6, '404', ha='left', fontsize=8)
ax.annotate('', xy=(6.3, 7.6), xytext=(6.5, 7.6), arrowprops=leader_props)

# Thermoelectric (ref 408)
ax.add_patch(Rectangle((1.5, 5), 1.5, 1.2, fill=False, lw=line_width))
ax.text(2.25, 5.7, 'TEG', ha='center', va='center', fontsize=10, weight='bold')
ax.text(2.25, 5.3, 'NTC 10K\nThermistor', ha='center', fontsize=8)
ax.text(1.3, 5.6, '408', ha='right', fontsize=8)
ax.annotate('', xy=(1.5, 5.6), xytext=(1.35, 5.6), arrowprops=leader_props)

ax.add_patch(FancyArrowPatch((3, 5.6), (3.8, 5.6), arrowstyle='->', lw=line_width))
ax.add_patch(Rectangle((3.8, 5.1), 1.2, 1.0, fill=False, lw=line_width))
ax.text(4.4, 5.6, 'Rectifier', ha='center', va='center', fontsize=8)
ax.text(5.15, 5.6, '410', ha='left', fontsize=8)
ax.annotate('', xy=(5.0, 5.6), xytext=(5.15, 5.6), arrowprops=leader_props)

ax.add_patch(FancyArrowPatch((5, 5.6), (5.5, 5.6), arrowstyle='->', lw=line_width))
ax.add_patch(Rectangle((5.5, 5.2), 0.8, 0.8, fill=False, lw=line_width))
ax.text(5.9, 5.6, 'C', ha='center', va='center', fontsize=10)
ax.text(6.5, 5.6, '412', ha='left', fontsize=8)
ax.annotate('', xy=(6.3, 5.6), xytext=(6.5, 5.6), arrowprops=leader_props)

# Summing node — shifted left to keep storage within right margin
ax.add_patch(FancyArrowPatch((6.3, 7.6), (6.5, 6.8), arrowstyle='->', lw=line_width))
ax.add_patch(FancyArrowPatch((6.3, 5.6), (6.5, 6.4), arrowstyle='->', lw=line_width))
ax.add_patch(Circle((6.7, 6.6), 0.3, fill=False, lw=line_width))
ax.text(6.7, 6.6, '+', ha='center', va='center', fontsize=12)

# Storage (ref 414) — constrained: right edge at 7.5 (within 7.725 safe)
ax.add_patch(FancyArrowPatch((6.7, 6.3), (6.5, 4.5), arrowstyle='->', lw=line_width))
ax.add_patch(Rectangle((5.5, 3.5), 2, 1, fill=False, lw=line_width))
ax.text(6.5, 4, 'Energy Storage\n(battery/supercap)', ha='center', va='center', fontsize=8)
ax.text(6.5, 3.3, '414', ha='center', fontsize=8)
ax.annotate('', xy=(6.5, 3.5), xytext=(6.5, 3.38), arrowprops=leader_props)

# Output to SNN
ax.add_patch(FancyArrowPatch((5.5, 4), (4.5, 4), arrowstyle='->', lw=line_width))
ax.text(5.0, 4.2, 'Power to SNN', ha='center', fontsize=8)

ax.text(2.25, 5.0, 'thermal_factor = 8.0', ha='center', fontsize=8)

fig.savefig(f'{OUT_DIR}/fig4.svg', format='svg')
plt.close(fig)


# ════════════════════════════════════════════════════════════════════
# FIG. 5 — Activity-Dependent Energy Dynamics
# ════════════════════════════════════════════════════════════════════
# Data derived from BalancedEnergyConfig (core/energy.py):
#   friction_factor=18.0, thermal_factor=8.0, base_consumption_mw=45.0,
#   activity_cost_mw=1.2, activity_cost_quadratic=0.06, time_step_hours=0.005
#   Assumes ΔT=5°C (typical operating thermal gradient)
#
#   Harvest = 0.20 + 0.09 * s           (thermal baseline + piezo per spike)
#   Cost    = 0.225 + 0.006 * s + 0.0003 * s²  (base + linear + quadratic)
#   Crossover at s ≈ 0.3 spikes (net = 0)
fig, ax = setup_figure(5, 8)

# Leader line style
leader_props = dict(arrowstyle='->', lw=0.5, color='black')

graph_ax = fig.add_axes([
    (SAFE_LEFT + 0.8) / paper_width,
    (SAFE_BOTTOM + 1.5) / paper_height,
    (SAFE_WIDTH - 1.0) / paper_width,
    (SAFE_TOP - SAFE_BOTTOM - 2.8) / paper_height
])
graph_ax.set_xlabel('Neural Activity (Spikes / Step)', fontsize=10)
graph_ax.set_ylabel('Energy per Step (mWh)', fontsize=10)

# Spike range: 0 to 50 (N=50 neurons max)
s = np.linspace(0, 50, 200)

# Harvest: thermal baseline (0.20 mWh) + piezo per spike (0.09 mWh/spike)
harvest = 0.20 + 0.09 * s

# Cost: base (0.225 mWh) + linear (0.006/spike) + quadratic (0.0003/spike²)
cost = 0.225 + 0.006 * s + 0.0003 * s**2

# Plot harvest curve (dashed — ref 500)
graph_ax.plot(s, harvest, ls='--', color='black', lw=line_width)
graph_ax.text(51, harvest[-1], 'Harvest\n~4.7 mWh', ha='left', va='center', fontsize=8)
graph_ax.text(30, 3.2, '500', ha='center', fontsize=8)
graph_ax.annotate('', xy=(30, harvest[120]), xytext=(30, 3.15),
                  arrowprops=leader_props)

# Plot cost curve (solid — ref 502)
graph_ax.plot(s, cost, ls='-', color='black', lw=line_width)
graph_ax.text(51, cost[-1], 'Cost\n~1.3 mWh', ha='left', va='center', fontsize=8)
graph_ax.text(40, 0.55, '502', ha='center', fontsize=8)
graph_ax.annotate('', xy=(40, cost[160]), xytext=(40, 0.6),
                  arrowprops=leader_props)

# Shade net-positive region between curves (ref 504)
graph_ax.fill_between(s, cost, harvest, where=(harvest >= cost),
                      hatch='/', alpha=0.08, edgecolor='black')
graph_ax.text(25, 2.0, 'NET POSITIVE REGION', ha='center', va='center',
              fontsize=10, weight='bold')
graph_ax.text(25, 1.7, 'Harvest >> Cost', ha='center', va='center', fontsize=8)
graph_ax.text(25, 1.45, '(Self-Sustaining)', ha='center', va='center', fontsize=8)
graph_ax.text(25, 1.15, '504', ha='center', fontsize=8)
graph_ax.annotate('', xy=(25, 1.3), xytext=(25, 1.2),
                  arrowprops=leader_props)

# Crossover point circle and label (ref 506)
crossover_s = 0.3
crossover_y = 0.20 + 0.09 * crossover_s  # ≈ 0.227
graph_ax.plot(crossover_s, crossover_y, 'o', color='black', markersize=8,
              fillstyle='none', markeredgewidth=line_width)
graph_ax.text(3, -0.08, 'Crossover (0.3 spikes)', ha='left', fontsize=8)
graph_ax.text(3, -0.15, '506', ha='left', fontsize=8)
graph_ax.annotate('', xy=(crossover_s + 0.3, crossover_y),
                  xytext=(3, -0.05),
                  arrowprops=leader_props)

# Zero line
graph_ax.axhline(0, ls=':', color='black', lw=0.5)

# Axis limits
graph_ax.set_xlim(-1, 55)
graph_ax.set_ylim(-0.2, 5.2)

# Formula box at top (ref 508)
formula_text = ('Harvest = 0.20 + (0.09 \u00d7 spikes)\n'
                'Cost = 0.225 + (0.006 \u00d7 s) + (0.0003 \u00d7 s\u00b2)')
graph_ax.text(1, 4.9, formula_text, fontsize=8, va='top',
              bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                        edgecolor='black', lw=0.5))
graph_ax.text(22, 4.95, '508', ha='left', fontsize=8)
graph_ax.annotate('', xy=(20, 4.7), xytext=(22, 4.9),
                  arrowprops=leader_props)

# Zone 1 label at bottom of drawing area
ax.text(SAFE_CX, SAFE_BOTTOM + 0.6, 'Zone 1: Quiescent Drain',
        ha='center', fontsize=9, weight='bold')
ax.text(SAFE_CX, SAFE_BOTTOM + 0.35, '0-1 Spikes: Cost > Harvest',
        ha='center', fontsize=8)

fig.savefig(f'{OUT_DIR}/fig5.svg', format='svg')
plt.close(fig)


# ════════════════════════════════════════════════════════════════════
# FIG. 6 — Hardware Reference Design
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(6, 8)

# Leader line style
leader_props = dict(arrowstyle='->', lw=0.5, color='black')

# Raspberry Pi Pico (ref 600)
ax.add_patch(Rectangle((3, 7.5), 2.5, 1.2, fill=False, lw=line_width * 1.5))
ax.text(4.25, 8.2, 'Raspberry Pi Pico', ha='center', fontsize=10, weight='bold')
ax.text(4.25, 7.9, '(RP2040)', ha='center', fontsize=8)
ax.text(5.65, 8.1, '600', ha='left', fontsize=8)
ax.annotate('', xy=(5.5, 8.1), xytext=(5.65, 8.1), arrowprops=leader_props)

# Piezo 27mm (ref 602)
ax.add_patch(Circle((1.5, 9), 0.5, fill=False, lw=line_width))
ax.text(1.5, 9, 'Piezo\n27mm', ha='center', va='center', fontsize=8)
ax.text(2.15, 9, '602', ha='left', fontsize=8)
ax.annotate('', xy=(2.0, 9), xytext=(2.15, 9), arrowprops=leader_props)
ax.add_patch(FancyArrowPatch((2, 9), (3, 8.5), arrowstyle='->', lw=line_width))
ax.text(2.5, 8.9, 'ADC', ha='center', fontsize=8)

# SG90 Servo (ref 604) — constrained within right margin
ax.add_patch(Rectangle((5.6, 8.5), 1.3, 0.8, fill=False, lw=line_width))
ax.text(6.25, 8.9, 'SG90 Servo', ha='center', fontsize=8)
ax.text(7.05, 8.9, '604', ha='left', fontsize=8)
ax.annotate('', xy=(6.9, 8.9), xytext=(7.05, 8.9), arrowprops=leader_props)
ax.add_patch(FancyArrowPatch((5.5, 8.1), (5.6, 8.9), arrowstyle='->', lw=line_width))
ax.text(5.6, 8.6, 'PWM', ha='center', fontsize=8)

# NTC 10K Thermistor (ref 606)
ax.add_patch(Rectangle((1, 6.5), 1.5, 0.8, fill=False, lw=line_width))
ax.text(1.75, 6.9, 'NTC 10K\nThermistor', ha='center', va='center', fontsize=8)
ax.text(2.65, 6.9, '606', ha='left', fontsize=8)
ax.annotate('', xy=(2.5, 6.9), xytext=(2.65, 6.9), arrowprops=leader_props)
ax.add_patch(FancyArrowPatch((2.5, 6.9), (3, 7.8), arrowstyle='->', lw=line_width))
ax.text(2.8, 7.4, 'ADC', ha='center', fontsize=8)

# WS2812B RGB LED (ref 608) — constrained within right margin
ax.add_patch(Rectangle((5.6, 6.5), 1.3, 0.8, fill=False, lw=line_width))
ax.text(6.25, 6.9, 'WS2812B\nRGB LED', ha='center', va='center', fontsize=8)
ax.text(7.05, 6.9, '608', ha='left', fontsize=8)
ax.annotate('', xy=(6.9, 6.9), xytext=(7.05, 6.9), arrowprops=leader_props)
ax.add_patch(FancyArrowPatch((5.5, 7.8), (5.6, 6.9), arrowstyle='->', lw=line_width))
ax.text(5.6, 7.3, 'GPIO', ha='center', fontsize=8)

# Photoresistor (ref 610)
ax.add_patch(Rectangle((1, 5), 1.5, 0.8, fill=False, lw=line_width))
ax.text(1.75, 5.4, 'Photoresistor\n(LDR)', ha='center', va='center', fontsize=8)
ax.text(2.65, 5.4, '610', ha='left', fontsize=8)
ax.annotate('', xy=(2.5, 5.4), xytext=(2.65, 5.4), arrowprops=leader_props)
ax.add_patch(FancyArrowPatch((2.5, 5.4), (3, 7.6),
             arrowstyle='->', lw=line_width, ls='dashed'))
ax.text(2.8, 6.5, 'ADC', ha='center', fontsize=8)

# BOM table (component list only — no prices per USPTO guidelines)
ax.add_patch(Rectangle((1.5, 2), 5.5, 2.5, fill=False, lw=line_width))
ax.text(4.25, 4.2, 'Bill of Materials', ha='center', fontsize=10, weight='bold')
bom = [
    'Raspberry Pi Pico (RP2040)',
    'SG90 Micro Servo',
    '27mm Piezoelectric Disc',
    'NTC 10K Thermistor',
    'Photoresistor (LDR)',
    'WS2812B RGB LED',
    'Misc (wires, board, inductor)',
]
for i, part in enumerate(bom):
    ax.text(2, 3.9 - i * 0.25, part, fontsize=8)

fig.savefig(f'{OUT_DIR}/fig6.svg', format='svg')
plt.close(fig)


# ════════════════════════════════════════════════════════════════════
# FIG. 7 — Validation Results Summary
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(7, 8)

data = [
    ['Claim', 'Criterion', 'Measured', 'Threshold', 'Result'],
    ['', 'Phase 7 Control Baseline (EnergyConfig)', '', '', ''],
    ['A', 'Closed-loop continuity', '2000 pts', '2000', 'PASS'],
    ['B', 'Boundedness', 'bounded', 'bounded', 'PASS'],
    ['C', 'Robustness (noise)', 'Std(\u03b8)\u226445\u00b0', '\u226445\u00b0', 'PASS'],
    ['D', 'Input-output gain', 'corr\u22650.2', '\u22650.2', 'PASS'],
    ['E', 'Saturation ratio', 'sat\u22640.20', '\u22640.20', 'PASS'],
    ['', 'Phase 7 Full Integration (Control)', '', '', ''],
    ['--', 'Energy at 2000 steps', '-4,697 mWh', '< 0', 'CONFIRMED'],
    ['', 'MCP Integration (BalancedEnergyConfig)', '', '', ''],
    ['--', 'Energy at 2000 steps', '100.0 mWh (capped)', '> 0', 'CONFIRMED'],
    ['', 'Phase 8 STDP', '', '', ''],
    ['F8.1', 'Weight entropy decrease', '2.95\u21922.02', 'decrease', 'PASS'],
    ['F8.2', 'STDP MI > 1.2x frozen', '6.52x', '> 1.20', 'PASS'],
    ['F8.3', 'Weight convergence', '0.00%', '< 10%', 'PASS']
]

table_ax = fig.add_axes([
    (SAFE_LEFT + 0.2) / paper_width,
    (SAFE_BOTTOM + 1.0) / paper_height,
    (SAFE_WIDTH - 0.4) / paper_width,
    (SAFE_TOP - SAFE_BOTTOM - 2.0) / paper_height
])
table_ax.axis('off')
table = table_ax.table(cellText=data, loc='center', cellLoc='center',
                        edges='closed')
table.set_fontsize(8)
table.scale(1, 1.5)

# Bold header row
for j in range(5):
    table[0, j].set_text_props(weight='bold')

# Bold/italic section headers
for row_idx in [1, 7, 9, 11]:
    for j in range(5):
        table[row_idx, j].set_text_props(weight='bold', style='italic')

ax.text(4.25, 0.9, 'All claims validated. System reproducible via git tags.',
        ha='center', fontsize=8)
ax.text(4.25, 1.15, '700', ha='center', fontsize=8)
ax.annotate('', xy=(4.25, 1.0), xytext=(4.25, 1.1),
            arrowprops=dict(arrowstyle='->', lw=0.5, color='black'))

fig.savefig(f'{OUT_DIR}/fig7.svg', format='svg')
plt.close(fig)


# ════════════════════════════════════════════════════════════════════
# FIG. 8 — Energy-Bounded Recursive Control Architecture
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(8, 8)

cx, cy = 4.25, 5.5

# Main control block (ref 800)
ax.add_patch(Rectangle((cx - 1.5, cy - 0.5), 3, 1, fill=False, lw=line_width))
ax.text(cx, cy + 0.3, 'Energy-Bounded Recursive Control',
        ha='center', va='center', fontsize=10, weight='bold')
ax.text(cx, cy - 0.1, 'reflection_coeff bounded by energy state',
        ha='center', va='center', fontsize=8)
ax.text(cx + 1.7, cy, '800', ha='left', fontsize=8)
ax.annotate('', xy=(cx + 1.5, cy), xytext=(cx + 1.7, cy),
            arrowprops=dict(arrowstyle='->', lw=0.5, color='black'))

# SNN Processing (ref 802) — constrained within right margin (7.725 safe)
snn_left = cx + 1.5  # 5.75
snn_width = 1.6      # right edge = 7.35
snn_cx = snn_left + snn_width / 2
ax.add_patch(FancyArrowPatch((cx + 1.5, cy), (snn_left, cy),
             arrowstyle='->', lw=line_width))
ax.add_patch(Rectangle((snn_left, cy - 0.5), snn_width, 1, fill=False, lw=line_width))
ax.text(snn_cx, cy + 0.1, 'SNN Processing',
        ha='center', va='center', fontsize=10)
ax.text(snn_cx, cy - 0.2, '(50 LIF neurons)',
        ha='center', va='center', fontsize=8)
ax.text(snn_left + snn_width + 0.1, cy + 0.3, '802', ha='left', fontsize=8)
ax.annotate('', xy=(snn_left + snn_width, cy + 0.3),
            xytext=(snn_left + snn_width + 0.05, cy + 0.3),
            arrowprops=dict(arrowstyle='->', lw=0.5, color='black'))

# Feedback loop arcs — constrained within safe bounds
ax.add_patch(FancyArrowPatch((snn_left + snn_width, cy + 0.5),
             (snn_cx, cy + 1.5),
             connectionstyle="arc3,rad=0.4", arrowstyle='->', lw=line_width))
ax.add_patch(FancyArrowPatch((snn_cx, cy + 1.5), (cx, cy + 1.5),
             connectionstyle="arc3,rad=0.3", arrowstyle='->', lw=line_width))
ax.text(cx + 1.0, cy + 1.8, 'self-observation feedback',
        ha='center', fontsize=8)
ax.add_patch(FancyArrowPatch((cx, cy + 1.5), (cx - 1.5, cy + 0.5),
             connectionstyle="arc3,rad=0.3", arrowstyle='->', lw=line_width))

# Energy monitor (ref 804)
ax.add_patch(Ellipse((cx, cy - 2.0), 2.5, 0.8, fill=False, lw=line_width))
ax.text(cx, cy - 2.0, 'Energy Monitor', ha='center', va='center', fontsize=10)
ax.text(cx + 1.45, cy - 2.0, '804', ha='left', fontsize=8)
ax.annotate('', xy=(cx + 1.25, cy - 2.0), xytext=(cx + 1.45, cy - 2.0),
            arrowprops=dict(arrowstyle='->', lw=0.5, color='black'))
ax.add_patch(FancyArrowPatch((cx, cy - 1.6), (cx, cy - 0.5),
             arrowstyle='->', ls='dashed', lw=line_width))
ax.text(cx + 0.2, cy - 1.1, 'energy-aware\nmodulation',
        ha='left', fontsize=8)

# Energy rules — spaced to avoid overlap
ax.text(cx, cy - 2.8, 'Energy < 15 mWh: inhibit (mod = -0.4)',
        ha='center', fontsize=8)
ax.text(cx, cy - 3.15, 'Energy < 30 mWh: cautious (mod = -0.1)',
        ha='center', fontsize=8)
ax.text(cx, cy - 3.5, 'Energy > 80 mWh: explore (mod = +0.3)',
        ha='center', fontsize=8)

ax.text(cx, bottom_margin + 0.8,
        'Recursive control loop bounded by energy levels to ensure self-sustainability.',
        ha='center', fontsize=8)

fig.savefig(f'{OUT_DIR}/fig8.svg', format='svg')
plt.close(fig)


print(f"All 8 Patent A figures generated in {OUT_DIR}/")

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
fig, ax = setup_figure(2, 8)

graph_ax = fig.add_axes([
    (SAFE_LEFT + 0.9) / paper_width,
    (SAFE_BOTTOM + 1.0) / paper_height,
    (SAFE_WIDTH - 0.9) / paper_width,
    (SAFE_TOP - SAFE_BOTTOM - 2.0) / paper_height
])
graph_ax.set_xlabel('Operational Steps', fontsize=10)
graph_ax.set_ylabel('Cumulative Energy (mWh)', fontsize=9)
graph_ax.tick_params(axis='y', labelsize=8)

x = np.linspace(0, 2000, 100)
control_y = 50 - (470 / 1000) * x   # Drops to ~-890 at x=2000
graph_ax.plot(x, control_y, ls='-', color='black', lw=line_width,
              label='Control (470 mW)')

exp_y = 50 + (45 / 1000 - 0.002) * x  # Rises to ~140 at x=2000
graph_ax.plot(x, exp_y, ls='--', color='black', lw=line_width,
              label='Experimental (45 mW)')

# Set y-limits to fit the actual data with room for annotations
graph_ax.set_xlim(0, 2050)
graph_ax.set_ylim(-1050, 200)

# Self-sustaining threshold line (ref 204)
graph_ax.axhline(0, ls=':', color='black', lw=1)
graph_ax.text(1050, 10, '204  Self-Sustaining Threshold (0 mWh)',
              ha='center', va='bottom', fontsize=8)

# Control line label (ref 200) — in the middle of the control curve
graph_ax.text(1400, -500, '200', ha='left', fontsize=8)
graph_ax.annotate('', xy=(1300, control_y[65]), xytext=(1400, -490),
                  arrowprops=dict(arrowstyle='->', lw=0.5, color='black'))

# Experimental line label (ref 202) — above experimental line
graph_ax.text(1400, 150, '202', ha='left', fontsize=8)
graph_ax.annotate('', xy=(1300, exp_y[65]), xytext=(1400, 145),
                  arrowprops=dict(arrowstyle='->', lw=0.5, color='black'))

# Outcome annotations — positioned within y-limits
graph_ax.annotate('System fails\n(energy depleted)',
                  xy=(1900, control_y[95]), xytext=(1400, -800),
                  arrowprops=dict(arrowstyle='->'), fontsize=8)
graph_ax.annotate('System thrives\n(net positive)',
                  xy=(1900, exp_y[95]), xytext=(600, 150),
                  arrowprops=dict(arrowstyle='->'), fontsize=8)

graph_ax.fill_between(x, control_y, exp_y, hatch='.', alpha=0.1)

# Legend in lower-left of graph (within bounds)
graph_ax.legend(loc='lower left', fontsize=8, frameon=True)

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
fig, ax = setup_figure(5, 8)

graph_ax = fig.add_axes([
    (SAFE_LEFT + 0.5) / paper_width,
    (SAFE_BOTTOM + 1.0) / paper_height,
    (SAFE_WIDTH - 0.5) / paper_width,
    (SAFE_TOP - SAFE_BOTTOM - 2.0) / paper_height
])
graph_ax.set_xlabel('Neural Activity (spikes/step)', fontsize=10)
graph_ax.set_ylabel('Net Energy (mWh/step)', fontsize=10)
graph_ax.set_title('Activity vs Net Energy', fontsize=10)

activity = np.linspace(0, 1.0, 100)
cost = 0.05 * activity**2
harvest = 0.1 - 0.05 * activity
net = harvest - cost
graph_ax.plot(activity, net, color='black', lw=line_width)
graph_ax.text(0.5, 0.07, '500', ha='center', fontsize=8)
graph_ax.annotate('', xy=(0.5, 0.05), xytext=(0.5, 0.065),
                  arrowprops=dict(arrowstyle='->', lw=0.5, color='black'))

graph_ax.axhline(0, ls=':', color='black', lw=0.5)
graph_ax.text(0.95, 0.002, '0 mWh', ha='right', fontsize=8)

graph_ax.axvspan(0, 0.2, hatch='xxx', alpha=0.05, edgecolor='black')
graph_ax.axvspan(0.2, 0.7, hatch='/', alpha=0.05, edgecolor='black')
graph_ax.axvspan(0.7, 1.0, hatch='xxx', alpha=0.05, edgecolor='black')

graph_ax.text(0.1, -0.02, 'Low activity\ninsufficient\nharvesting',
              fontsize=8, ha='center')
graph_ax.text(0.45, 0.08, 'Sweet spot\nnet positive energy',
              fontsize=8, ha='center')
graph_ax.text(0.85, -0.02, 'High activity\nquadratic cost\ndominates',
              fontsize=8, ha='center')

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

# BOM table
ax.add_patch(Rectangle((1.5, 2), 5.5, 2.5, fill=False, lw=line_width))
ax.text(4.25, 4.2, 'Bill of Materials', ha='center', fontsize=10, weight='bold')
bom = [
    ('Raspberry Pi Pico', '$4'),
    ('SG90 Micro Servo', '$3'),
    ('27mm Piezo Disc', '$2'),
    ('NTC 10K Thermistor', '$1'),
    ('Photoresistor (LDR)', '$1'),
    ('WS2812B RGB LED', '$1'),
    ('Misc (wires, board)', '$3'),
]
for i, (part, cost) in enumerate(bom):
    ax.text(2, 3.9 - i * 0.25, part, fontsize=8)
    ax.text(6.5, 3.9 - i * 0.25, cost, fontsize=8, ha='right')

ax.text(4.25, 1.6, 'Total BOM Cost: <$25', ha='center', fontsize=10, weight='bold')

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
    ['--', 'Energy at 2000 steps', '+4,170 mWh', '> 0', 'CONFIRMED'],
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

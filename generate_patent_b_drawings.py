import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arrow, Circle, FancyArrowPatch, Ellipse, Polygon, PathPatch, FancyBboxPatch
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

os.makedirs('patent_drawings/patent_b', exist_ok=True)

# Leader line style for reference numerals (thin, per 37 CFR 1.84(q))
leader_props = dict(arrowstyle='->', lw=0.5, color='black')

# ════════════════════════════════════════════════════════════════════
# FIG. 1 — Self-Observation Feedback Loop
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(1, 6)

# Layout: use center-relative coordinates
cx = SAFE_CX  # ~4.44
top_y = SAFE_TOP - 0.5  # ~9.35

# Left side: External Input (ref 100)
ax.add_patch(FancyArrowPatch((SAFE_LEFT + 0.2, top_y - 1.5), (SAFE_LEFT + 1.2, top_y - 1.5),
             arrowstyle='->', lw=line_width))
ax.text(SAFE_LEFT + 0.7, top_y - 1.3, 'External Input I_ext(t)',
        ha='center', va='bottom', fontsize=8)
ax.text(SAFE_LEFT + 0.1, top_y - 1.1, '100', ha='center', fontsize=8)
ax.annotate('', xy=(SAFE_LEFT + 0.4, top_y - 1.4),
            xytext=(SAFE_LEFT + 0.15, top_y - 1.15), arrowprops=leader_props)

# Summing junction (ref 102)
sum_x = SAFE_LEFT + 1.6
ax.add_patch(Circle((sum_x, top_y - 1.5), 0.25, fill=False, lw=line_width))
ax.text(sum_x, top_y - 1.5, '+', ha='center', va='center', fontsize=font_size_label)
ax.text(sum_x, top_y - 1.0, '102', ha='center', fontsize=8)
ax.annotate('', xy=(sum_x, top_y - 1.25),
            xytext=(sum_x, top_y - 1.05), arrowprops=leader_props)

# Center: SNN (ref 104) — keep within bounds
snn_left = SAFE_LEFT + 2.0
snn_width = 3.0
snn_right = snn_left + snn_width
snn_cx = snn_left + snn_width / 2
ax.add_patch(Rectangle((snn_left, top_y - 2.5), snn_width, 1.8, fill=False, lw=line_width))
ax.text(snn_cx, top_y - 2.0, 'Spiking Neural Network (N LIF neurons)',
        ha='center', va='center', fontsize=9)
ax.text(snn_cx, top_y - 2.3, 'V_i(t+1) = V_i(t) x leak + I_adjusted x dt',
        ha='center', va='center', fontsize=8)
ax.text(snn_right + 0.15, top_y - 0.8, '104', ha='left', fontsize=8)
ax.annotate('', xy=(snn_right, top_y - 0.7),
            xytext=(snn_right + 0.15, top_y - 0.8), arrowprops=leader_props)

# Small circles for neurons
for i in range(5):
    ax.add_patch(Circle((snn_left + 0.5 + i * 0.4, top_y - 1.7), 0.1, fill=False))

# Right side: Spike Output (ref 106)
spike_x = snn_right + 0.3
ax.add_patch(FancyArrowPatch((snn_right, top_y - 1.5), (spike_x + 0.8, top_y - 1.5),
             arrowstyle='->', lw=line_width))
ax.text(spike_x + 0.4, top_y - 1.3, 'Spike Output S(t)',
        ha='center', va='bottom', fontsize=8)
ax.text(spike_x + 1.0, top_y - 1.1, '106', ha='left', fontsize=8)
ax.annotate('', xy=(spike_x + 0.8, top_y - 1.4),
            xytext=(spike_x + 1.0, top_y - 1.15), arrowprops=leader_props)

# Bottom path: Aggregate Output (ref 108)
agg_cx = snn_cx + 0.5
agg_width = 2.8
agg_left = agg_cx - agg_width / 2
ax.add_patch(FancyArrowPatch((agg_cx, top_y - 2.0), (agg_cx, top_y - 3.5),
             arrowstyle='->', lw=line_width))
ax.add_patch(Rectangle((agg_left, top_y - 4.0), agg_width, 1.0, fill=False, lw=line_width))
ax.text(agg_cx, top_y - 3.5, 'Aggregate Output Computation',
        ha='center', va='center', fontsize=9)
ax.text(agg_cx, top_y - 3.7, 'O(t) = mean(V_1, V_2, ..., V_N)',
        ha='center', va='center', fontsize=8)
ax.text(agg_cx, top_y - 4.2, 'Mean membrane potential across all neurons',
        ha='center', va='center', fontsize=8)
ax.text(agg_left + agg_width + 0.2, top_y - 3.3, '108', ha='left', fontsize=8)
ax.annotate('', xy=(agg_left + agg_width, top_y - 3.2),
            xytext=(agg_left + agg_width + 0.15, top_y - 3.3), arrowprops=leader_props)

# Reflection Scaling (ref 110)
refl_cx = SAFE_LEFT + 1.5
refl_width = 2.0
refl_left = refl_cx - refl_width / 2
ax.add_patch(FancyArrowPatch((agg_left, top_y - 3.5), (refl_left + refl_width, top_y - 3.5),
             arrowstyle='->', lw=line_width))
ax.add_patch(Rectangle((refl_left, top_y - 4.0), refl_width, 1.0, fill=False, lw=line_width))
ax.text(refl_cx, top_y - 3.5, 'Reflection Scaling',
        ha='center', va='center', fontsize=9)
ax.text(refl_cx, top_y - 3.7, 'I_refl = O(t) x refl_coeff',
        ha='center', va='center', fontsize=8)
ax.text(refl_left - 0.2, top_y - 3.3, '110', ha='right', fontsize=8)
ax.annotate('', xy=(refl_left, top_y - 3.4),
            xytext=(refl_left - 0.15, top_y - 3.35), arrowprops=leader_props)

# Feedback to summing (ref 112 — the self-observation feedback path)
delay_x = sum_x + 0.2
ax.add_patch(FancyArrowPatch((refl_cx, top_y - 3.0), (refl_cx, top_y - 1.75),
             arrowstyle='->', lw=line_width * 2))  # bold
# Delay element (ref 114)
ax.add_patch(Rectangle((delay_x - 0.25, top_y - 2.5), 0.5, 0.5, fill=False, lw=line_width))
ax.text(delay_x, top_y - 2.25, 'z^{-1}', ha='center', va='center', fontsize=8)
ax.text(delay_x - 0.7, top_y - 2.25, '112', ha='right', fontsize=8)
ax.annotate('', xy=(delay_x - 0.25, top_y - 2.25),
            xytext=(delay_x - 0.65, top_y - 2.25), arrowprops=leader_props)
ax.text(delay_x + 0.45, top_y - 2.25, '114', ha='left', fontsize=8)
ax.annotate('', xy=(delay_x + 0.25, top_y - 2.25),
            xytext=(delay_x + 0.4, top_y - 2.25), arrowprops=leader_props)

# Key label
ax.text(cx, SAFE_BOTTOM + 1.0, 'Self-observation: the network observes its own prior aggregate state',
        ha='center', va='center', fontsize=8)
ax.text(cx, SAFE_BOTTOM + 0.6, 'I_adjusted(t+1) = I_ext(t+1) + I_reflection(t)',
        ha='center', va='center', fontsize=8)

plt.savefig('patent_drawings/patent_b/fig1.svg', format='svg')
plt.close()

# ════════════════════════════════════════════════════════════════════
# FIG. 2 — Reflection Coefficient Spectrum
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(2, 6)

# Horizontal bar — constrained within safe area
bar_x = SAFE_LEFT + 0.3
bar_width = SAFE_WIDTH - 0.6
bar_y = SAFE_TOP - 1.5
bar_height = 0.5
ax.add_patch(Rectangle((bar_x, bar_y), bar_width, bar_height, fill=False, lw=line_width))

# Ends
ax.text(bar_x - 0.15, bar_y + bar_height / 2, '0.0', ha='right', va='center', fontsize=10)
ax.text(bar_x + bar_width + 0.15, bar_y + bar_height / 2, '1.0', ha='left', va='center', fontsize=10)

# Operational range bracket
op_start = bar_x + 0.1 * bar_width
op_end = bar_x + 0.3 * bar_width
ax.plot([op_start, op_end], [bar_y - 0.1, bar_y - 0.1], color='black', lw=line_width)
ax.text((op_start + op_end) / 2, bar_y - 0.25, '0.1 to 0.3 (typical)', ha='center', fontsize=8)

# Regions with hatching
regions = [
    (0.0, 0.2, '//'),
    (0.2, 0.4, ''),
    (0.4, 0.7, '//'),
    (0.7, 1.0, 'xxx')
]

for start, end, hatch in regions:
    reg_start = bar_x + start * bar_width
    reg_width = (end - start) * bar_width
    if hatch:
        ax.add_patch(Rectangle((reg_start, bar_y), reg_width, bar_height,
                     hatch=hatch, fill=False, edgecolor='black', lw=0))

# Region labels — STACKED VERTICALLY below bar to avoid overlap
# Each region gets its own vertical column with proper spacing
region_data = [
    (0.0, 0.2, 'Minimal\nself-awareness', 'Slight influence\nof prior state', 'Primarily\nexternally driven'),
    (0.2, 0.4, 'Balanced\nself-observation', 'External + meaningful\nself-reference', 'OPERATIONAL\nRANGE'),
    (0.4, 0.7, 'Self-dominated\nprocessing', 'Internal state\ndominates', 'Echo chamber\nrisk'),
    (0.7, 1.0, 'Self-\nabsorption', 'External input\noverwhelmed', 'Locks onto\nown state')
]

label_y_start = bar_y - 0.6
for start, end, title, desc, behavior in region_data:
    reg_start = bar_x + start * bar_width
    reg_width = (end - start) * bar_width
    reg_cx = reg_start + reg_width / 2
    ax.text(reg_cx, label_y_start, f'{start}-{end}',
            ha='center', va='top', fontsize=8, weight='bold')
    ax.text(reg_cx, label_y_start - 0.4, title,
            ha='center', va='top', fontsize=8)
    ax.text(reg_cx, label_y_start - 1.0, desc,
            ha='center', va='top', fontsize=8)
    ax.text(reg_cx, label_y_start - 1.6, behavior,
            ha='center', va='top', fontsize=8, style='italic')

# Arrow increasing
arrow_y = bar_y - 3.5
ax.add_patch(FancyArrowPatch((bar_x, arrow_y), (bar_x + bar_width, arrow_y),
             arrowstyle='->', lw=line_width))
ax.text(bar_x + bar_width / 2, arrow_y - 0.15,
        'Increasing self-referential processing', ha='center', fontsize=8)

# Note
ax.text(bar_x + bar_width / 2, arrow_y - 0.6,
        'The reflection coefficient is the system\'s self-awareness dial',
        ha='center', fontsize=8)

plt.savefig('patent_drawings/patent_b/fig2.svg', format='svg')
plt.close()

# ════════════════════════════════════════════════════════════════════
# FIG. 3 — Dynamic Modulation Sources
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(3, 6)

cx = SAFE_CX

# Center: Reflection Coefficient Computation
comp_left = SAFE_LEFT + 0.8
comp_width = 4.0
comp_cx = comp_left + comp_width / 2
ax.add_patch(Rectangle((comp_left, 5.5), comp_width, 1.2, fill=False, lw=line_width * 1.5))
ax.text(comp_cx, 6.3, 'Reflection Coefficient Computation',
        ha='center', va='center', fontsize=10, weight='bold')
ax.text(comp_cx, 6.0, 'refl_coeff = base_coeff + modulation x sensitivity',
        ha='center', va='center', fontsize=8)
ax.text(comp_cx, 5.75, 'Default values: base_coeff = 0.2, sensitivity = 0.1',
        ha='center', va='center', fontsize=8)

# Top pathway: External Modulation
ax.add_patch(Ellipse((comp_cx, 8.5), 3, 0.8, fill=False, lw=line_width))
ax.text(comp_cx, 8.5, 'External Cognitive Control Layer',
        ha='center', va='center', fontsize=10, weight='bold')
ax.add_patch(FancyArrowPatch((comp_cx, 8.1), (comp_cx, 6.7),
             arrowstyle='->', lw=line_width))
ax.text(comp_cx + 0.1, 7.4, 'modulation value (-1.0 to +1.0)',
        ha='left', va='center', fontsize=8)

# Callout boxes — repositioned within bounds
callouts_ext = [
    ('mod = -0.5: Reduce\nself-observation', 9.2),
    ('mod = 0.0: Neutral\n(base coefficient)', 8.9),
    ('mod = +0.8: Increase\nself-observation', 8.6),
]
callout_left = SAFE_RIGHT - 1.8
for text, y in callouts_ext:
    ax.add_patch(Rectangle((callout_left, y - 0.15), 1.7, 0.3, fill=False, lw=0.5))
    ax.text(callout_left + 0.85, y, text, ha='center', va='center', fontsize=8)

# Bottom pathway: Internal Modulation
ax.add_patch(Rectangle((comp_left, 2.5), comp_width, 2.0, fill=False, lw=line_width))
ax.text(comp_cx, 4.2, 'Energy State Monitor',
        ha='center', va='center', fontsize=10, weight='bold')

# Energy rules inside the box
rules = [
    'energy < 15 mWh:  mod = -0.4  (conserve)',
    'energy < 30 mWh:  mod = -0.1  (cautious)',
    'energy > 80 mWh:  mod = +0.3  (explore)',
    'otherwise:        mod =  0.0  (neutral)',
]
for i, rule in enumerate(rules):
    ax.text(comp_left + 0.2, 3.8 - i * 0.3, rule, fontsize=8, family='monospace')

ax.add_patch(FancyArrowPatch((comp_cx, 4.5), (comp_cx, 5.5),
             arrowstyle='->', lw=line_width))
ax.text(comp_cx + 0.1, 5.0, 'energy-aware modulation',
        ha='left', va='center', fontsize=8)

# Right output — kept within bounds
out_arrow_end = min(comp_left + comp_width + 1.0, SAFE_RIGHT - 0.5)
ax.add_patch(FancyArrowPatch((comp_left + comp_width, 6.1), (out_arrow_end, 6.1),
             arrowstyle='->', lw=line_width))
ax.text(out_arrow_end + 0.05, 6.3, 'reflection_coeff',
        ha='left', va='center', fontsize=8, weight='bold')
ax.text(out_arrow_end + 0.05, 6.1, '(applied at next',
        ha='left', va='center', fontsize=8)
ax.text(out_arrow_end + 0.05, 5.95, 'SNN step)',
        ha='left', va='center', fontsize=8)

# Selector switch triangle
ax.add_patch(Polygon([[comp_cx, 5.3], [comp_cx - 0.5, 4.7], [comp_cx + 0.5, 4.7]],
             closed=True, fill=False, lw=line_width))

# Priority note at bottom
ax.text(cx, 1.8, 'Source priority: External overrides Internal\nwhen cognitive layer active',
        ha='center', va='center', fontsize=8, weight='bold',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='black', lw=0.8))

# Resulting range note
ax.text(cx, 1.1, 'Resulting range: 0.1 to 0.3 (typical operation)',
        ha='center', va='center', fontsize=8)

plt.savefig('patent_drawings/patent_b/fig3.svg', format='svg')
plt.close()

# ════════════════════════════════════════════════════════════════════
# FIG. 4 — Self-Referential Learning Loop (STDP + Self-Observation)
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(4, 6)

cx = SAFE_CX

# Main loop — all boxes repositioned to stay within bounds
# Top: SNN Processing Step t
snn_w = 2.5
snn_left = cx - snn_w / 2
ax.add_patch(Rectangle((snn_left, 8.2), snn_w, 0.8, fill=False, lw=line_width))
ax.text(cx, 8.6, 'SNN Processing Step t', ha='center', va='center', fontsize=10)

# Arrow right from SNN to STDP label
ax.add_patch(FancyArrowPatch((snn_left + snn_w, 8.6), (snn_left + snn_w + 0.6, 8.6),
             arrowstyle='->', lw=line_width))
ax.text(snn_left + snn_w + 0.3, 8.8, 'Spike output S(t)',
        ha='center', va='bottom', fontsize=8)

# Arrow down from SNN
ax.add_patch(FancyArrowPatch((cx, 8.2), (cx, 7.6), arrowstyle='->', lw=line_width))
ax.text(cx + 0.1, 7.9, 'Weight update signal', ha='left', va='center', fontsize=8)

# Right: STDP Weight Update — repositioned to stay within right margin
stdp_w = 2.5
stdp_left = SAFE_RIGHT - stdp_w - 0.1
stdp_cx = stdp_left + stdp_w / 2
ax.add_patch(Rectangle((stdp_left, 6.0), stdp_w, 1.4, fill=False, lw=line_width))
ax.text(stdp_cx, 7.1, 'STDP Weight Update', ha='center', va='center', fontsize=10)
ax.text(stdp_cx, 6.8, 'Post fires: W[i,j] += A+ x pre_trace[i]',
        fontsize=8, ha='center')
ax.text(stdp_cx, 6.55, 'Pre fires: W[i,j] -= A- x post_trace[j]',
        fontsize=8, ha='center')
ax.text(stdp_cx, 6.3, 'Temporal correlation learning',
        fontsize=8, ha='center')
ax.add_patch(FancyArrowPatch((stdp_cx, 6.0), (stdp_cx, 5.5),
             arrowstyle='->', lw=line_width))

# Bottom: Updated Weight Matrix
mat_w = 2.8
mat_left = cx - mat_w / 2
ax.add_patch(Rectangle((mat_left, 4.5), mat_w, 0.8, fill=False, lw=line_width))
ax.text(cx, 4.9, 'Updated Weight Matrix W(t+1)',
        ha='center', va='center', fontsize=10)
ax.add_patch(FancyArrowPatch((mat_left, 4.9), (mat_left - 0.5, 4.9),
             arrowstyle='->', lw=line_width))

# Left: Self-Observation
obs_w = 2.2
obs_left = SAFE_LEFT + 0.1
obs_cx = obs_left + obs_w / 2
ax.add_patch(Rectangle((obs_left, 6.2), obs_w, 0.8, fill=False, lw=line_width))
ax.text(obs_cx, 6.6, 'Self-Observation O(t)',
        ha='center', va='center', fontsize=10)
ax.add_patch(FancyArrowPatch((obs_cx, 7.0), (obs_cx, 8.2),
             arrowstyle='->', lw=line_width * 2))  # bold feedback

# Center annotation
ax.text(cx, 5.8, 'The network learns which temporal spike\npatterns correlate with self-observation',
        ha='center', fontsize=8)

# Key insight box
insight_w = 4.5
insight_left = cx - insight_w / 2
ax.add_patch(Rectangle((insight_left, 3.0), insight_w, 1.2, fill=False))
ax.text(cx, 3.6, 'STDP strengthens connections between neurons\n'
        'that fire in causal sequence. Self-observation provides\n'
        'an input correlating with the network\'s own behavior.\n'
        'Result: internal representations of own processing.',
        ha='center', fontsize=8, linespacing=1.4)

# Timeline
ax.text(cx, 2.2, 'Timeline:\n'
        '- Step t: Process input + self-observation\n'
        '- Step t: Fire spikes, update STDP traces\n'
        '- Step t: Compute new self-observation O(t)\n'
        '- Step t+1: Apply updated weights + new self-observation',
        ha='center', fontsize=8, linespacing=1.4)

plt.savefig('patent_drawings/patent_b/fig4.svg', format='svg')
plt.close()

# ════════════════════════════════════════════════════════════════════
# FIG. 5 — Energy-Aware Self-Observation Regulation
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(5, 6)

# Top: Energy Level bar
bar_x = SAFE_LEFT + 0.2
bar_width = SAFE_WIDTH - 0.4
bar_y = SAFE_TOP - 1.0
bar_height = 0.5
ax.add_patch(Rectangle((bar_x, bar_y), bar_width, bar_height, fill=False, lw=line_width))
ax.text(bar_x + bar_width / 2, bar_y + 0.65, 'Energy Level (mWh)',
        ha='center', va='center', fontsize=10)

# Regions
regions_energy = [
    (0, 15, 'CRITICAL', 'xxx'),
    (15, 30, 'LOW', '/'),
    (30, 80, 'NORMAL', ''),
    (80, 100, 'SURPLUS', '/')
]
for start, end, label, hatch in regions_energy:
    reg_start = bar_x + (start / 100) * bar_width
    reg_width = ((end - start) / 100) * bar_width
    if hatch:
        ax.add_patch(Rectangle((reg_start, bar_y), reg_width, bar_height,
                     hatch=hatch, fill=False, edgecolor='black', lw=0))
    ax.text(reg_start + reg_width / 2, bar_y + bar_height / 2, label,
            ha='center', va='center', fontsize=9)

# Middle: Modulation Mapping
ax.text(bar_x + bar_width / 2, bar_y - 0.8, 'Modulation Mapping',
        ha='center', fontsize=10)
for i, mod in enumerate([-0.4, -0.1, 0.0, 0.3]):
    reg_mid = bar_x + ((regions_energy[i][0] + regions_energy[i][1]) / 2 / 100) * bar_width
    ax.add_patch(FancyArrowPatch((reg_mid, bar_y - 0.1), (reg_mid, bar_y - 1.0),
                 arrowstyle='->', lw=line_width))
    ax.text(reg_mid, bar_y - 1.2, f'mod = {mod}', ha='center', fontsize=8)

# Bottom: Effect on Reflection Coefficient — SPREAD OUT markers
ax.text(bar_x + bar_width / 2, bar_y - 2.2, 'Effect on Reflection Coefficient',
        ha='center', fontsize=10)
num_line_start = SAFE_LEFT + 0.5
num_line_end = SAFE_RIGHT - 0.5
num_line_y = bar_y - 3.0
ax.plot([num_line_start, num_line_end], [num_line_y, num_line_y],
        color='black', lw=line_width)
ax.text(num_line_start - 0.15, num_line_y, '0.0', ha='right', va='center', fontsize=8)
ax.text(num_line_end + 0.15, num_line_y, '0.5', ha='left', va='center', fontsize=8)

# Spread markers across the full number line width for legibility
markers = [0.16, 0.19, 0.20, 0.23]
ann_labels = ['CRITICAL', 'LOW', 'NORMAL', 'SURPLUS']
ann_short = ['Reduced\nself-obs.', 'Slightly\nreduced', 'Baseline\nnormal', 'Enhanced\nself-obs.']
# Evenly space the 4 markers across the visual line
num_line_len = num_line_end - num_line_start
for i, mark in enumerate(markers):
    # Use evenly spaced positions for visual clarity
    pos = num_line_start + (i + 0.5) / 4 * num_line_len
    ax.plot(pos, num_line_y, 'ko', markersize=6)
    ax.text(pos, num_line_y + 0.3, f'{ann_labels[i]}\n{mark}',
            ha='center', fontsize=8, weight='bold')
    ax.text(pos, num_line_y - 0.4, ann_short[i],
            ha='center', fontsize=8, style='italic')

# Bottom note
ax.text(bar_x + bar_width / 2, SAFE_BOTTOM + 0.8,
        'Energy-aware regulation ensures the system reduces\n'
        'cognitive overhead when energy is scarce and explores\n'
        'deeper self-reference when energy is abundant',
        ha='center', fontsize=8, linespacing=1.5)

plt.savefig('patent_drawings/patent_b/fig5.svg', format='svg')
plt.close()

# ════════════════════════════════════════════════════════════════════
# FIG. 6 — End-to-End Signal Flow with Self-Observation Integration
# ════════════════════════════════════════════════════════════════════
fig, ax = setup_figure(6, 6)

cx = SAFE_CX

ax.text(cx, SAFE_TOP - 0.15,
        'End-to-End Signal Flow with Self-Observation Integration',
        ha='center', fontsize=10, weight='bold')

# ── Left: Environmental Sensors ──
sens_x, sens_y = SAFE_LEFT + 0.1, 7.0
sens_w, sens_h = 1.2, 1.0
ax.add_patch(Rectangle((sens_x, sens_y), sens_w, sens_h, fill=False, lw=line_width))
ax.text(sens_x + sens_w / 2, sens_y + sens_h - 0.2,
        'Environmental', ha='center', fontsize=8, weight='bold')
ax.text(sens_x + sens_w / 2, sens_y + 0.4,
        'Sensors', ha='center', fontsize=8, weight='bold')
ax.text(sens_x + sens_w / 2, sens_y + 0.15,
        'Light, Temp', ha='center', fontsize=8)

# ── Center: SNN (large, prominent) ──
snn_x, snn_y = 2.5, 5.8
snn_w, snn_h = 2.2, 3.0
ax.add_patch(Rectangle((snn_x, snn_y), snn_w, snn_h, fill=False, lw=line_width * 2))
ax.text(snn_x + snn_w / 2, snn_y + snn_h - 0.25,
        'Spiking Neural Network', ha='center', fontsize=10, weight='bold')

# Neuron circles inside SNN
for i in range(4):
    for j in range(3):
        nx = snn_x + 0.4 + i * 0.45
        ny = snn_y + 0.7 + j * 0.55
        ax.add_patch(Circle((nx, ny), 0.1, fill=False, lw=0.5))

ax.text(snn_x + snn_w / 2, snn_y + 0.25,
        'output = mean(V_1...V_N)', ha='center', fontsize=8)

# ── Sensors → SNN (external input) ──
ax.add_patch(FancyArrowPatch((sens_x + sens_w, sens_y + sens_h / 2),
                              (snn_x, snn_y + snn_h * 0.7),
                              arrowstyle='->', lw=line_width, color='black'))
ax.text(2.0, 8.2, 'External Input\nI_ext(t)', ha='center', fontsize=8)

# ── Self-observation feedback (DOTTED BOLD) ──
ax.add_patch(FancyArrowPatch((snn_x + snn_w / 2, snn_y),
                              (1.8, 4.7),
                              connectionstyle="arc3,rad=0.3",
                              linestyle='dotted', lw=line_width * 2,
                              arrowstyle='->', color='black'))
ax.add_patch(FancyArrowPatch((1.8, 4.5), (snn_x, snn_y + 0.5),
                              linestyle='dotted', lw=line_width * 2,
                              arrowstyle='->', color='black'))
ax.text(SAFE_LEFT + 0.2, 5.0, 'SELF-OBSERVATION\nprevious_output x\nreflection_coeff',
        ha='center', fontsize=8, weight='bold')

# ── Cognitive Modulation (above SNN) ──
cog_x, cog_y = 2.8, 9.3
cog_w, cog_h = 2.5, 0.6
ax.add_patch(Rectangle((cog_x, cog_y), cog_w, cog_h, fill=False, lw=line_width))
ax.text(cog_x + cog_w / 2, cog_y + cog_h / 2,
        'Cognitive Modulation', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((cog_x + cog_w / 2, cog_y),
                              (snn_x + snn_w / 2, snn_y + snn_h),
                              linestyle='dashed', arrowstyle='->', lw=line_width, color='black'))
ax.text(cog_x + cog_w + 0.1, 9.1, 'refl_coeff =\nbase + mod x sens',
        ha='left', fontsize=8)

# ── SNN output → Motor Actuator ──
ax.add_patch(FancyArrowPatch((snn_x + snn_w, snn_y + snn_h / 2),
                              (5.2, snn_y + snn_h / 2),
                              arrowstyle='->', lw=line_width, color='black'))
ax.text(5.0, snn_y + snn_h / 2 + 0.2, 'Spike Pattern +\nAggregate Output',
        ha='center', fontsize=8)

# ── Motor Actuator ──
mot_x, mot_y = 5.2, 6.5
mot_w, mot_h = 1.1, 1.4
ax.add_patch(Rectangle((mot_x, mot_y), mot_w, mot_h, fill=False, lw=line_width))
ax.text(mot_x + mot_w / 2, mot_y + mot_h - 0.25,
        'Motor', ha='center', fontsize=8, weight='bold')
ax.text(mot_x + mot_w / 2, mot_y + 0.5,
        'Actuator', ha='center', fontsize=8, weight='bold')

# ── Energy Harvester ──
harv_x, harv_y = 5.2, 4.5
harv_w, harv_h = 1.1, 1.2
ax.add_patch(Rectangle((harv_x, harv_y), harv_w, harv_h, fill=False, lw=line_width))
ax.text(harv_x + harv_w / 2, harv_y + harv_h - 0.25,
        'Energy', ha='center', fontsize=8, weight='bold')
ax.text(harv_x + harv_w / 2, harv_y + 0.5,
        'Harvester', ha='center', fontsize=8, weight='bold')

# Motor → Harvester
ax.add_patch(FancyArrowPatch((mot_x + mot_w / 2, mot_y),
                              (harv_x + harv_w / 2, harv_y + harv_h),
                              arrowstyle='->', lw=line_width, color='black'))
ax.text(mot_x + mot_w + 0.05, 5.8, 'Mechanical\nenergy', fontsize=8)

# ── Energy feedback (DASHED — Patent A pathway) ──
ax.add_patch(FancyArrowPatch((harv_x, harv_y + harv_h / 2),
                              (snn_x + snn_w, snn_y + 0.5),
                              connectionstyle="arc3,rad=-0.3",
                              linestyle='dashed', arrowstyle='->', lw=line_width * 1.5, color='black'))
ax.text(cx, 4.3, 'ENERGY FEEDBACK\n(Patent A pathway)', ha='center', fontsize=8)

# ── Legend ──
leg_y = 1.5
leg_x = SAFE_LEFT + 0.2
leg_w = SAFE_WIDTH - 0.4
ax.add_patch(Rectangle((leg_x, leg_y), leg_w, 2.0, fill=False, lw=line_width, ls='--'))
ax.text(leg_x + leg_w / 2, leg_y + 1.7, 'Legend',
        ha='center', fontsize=10, weight='bold')

ax.plot([leg_x + 0.2, leg_x + 1.0], [leg_y + 1.3, leg_y + 1.3], 'k:', lw=line_width * 2)
ax.text(leg_x + 1.2, leg_y + 1.3,
        'Self-Observation pathway (this patent)', va='center', fontsize=8, weight='bold')

ax.plot([leg_x + 0.2, leg_x + 1.0], [leg_y + 0.9, leg_y + 0.9], 'k--', lw=line_width * 1.5)
ax.text(leg_x + 1.2, leg_y + 0.9,
        'Energy feedback pathway (co-pending Patent A)', va='center', fontsize=8)

ax.plot([leg_x + 0.2, leg_x + 1.0], [leg_y + 0.5, leg_y + 0.5], 'k-', lw=0.5)
ax.text(leg_x + 1.2, leg_y + 0.5,
        'Synaptic computation (internal to SNN)', va='center', fontsize=8)

ax.text(leg_x + leg_w / 2, leg_y + 0.1,
        'The self-observation pathway is architecturally distinct from\nboth energy feedback and synaptic computation',
        ha='center', fontsize=8, style='italic')

plt.savefig('patent_drawings/patent_b/fig6.svg', format='svg')
plt.close()

print("All 6 Patent B figures generated in patent_drawings/patent_b/")

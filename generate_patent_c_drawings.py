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

# Function to setup figure
def setup_figure(fig_num, total_sheets):
    fig = plt.figure(figsize=(paper_width, paper_height), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, paper_width)
    ax.set_ylim(0, paper_height)
    ax.axis('off')
    # Sheet number at top center
    ax.text(paper_width / 2, paper_height - 0.5, f"{fig_num}/{total_sheets}", ha='center', va='center', fontsize=10)
    # Figure label
    ax.text(left_margin, bottom_margin + 0.2, f"FIG. {fig_num}", ha='left', va='bottom', fontsize=font_size_label)
    return fig, ax

os.makedirs('patent_drawings/patent_c', exist_ok=True)

# FIG. 1 - System Architecture with Fallback
fig, ax = setup_figure(1, 6)

# Top section - Cognitive Control Layer
ax.add_patch(Ellipse((4.25, 9.5), 3, 1, fill=False, lw=line_width))
ax.text(4.25, 9.5, 'External Cognitive Control Layer (e.g., Claude)', ha='center', va='center', fontsize=10)
ax.text(4.25, 9.1, 'Provides intelligent cognitive decisions', ha='center', va='center', fontsize=8)
# Dashed outline for may become unavailable
ax.add_patch(Ellipse((4.25, 9.5), 3, 1, fill=False, lw=line_width, ls='dashed'))
ax.text(6, 9.5, 'May become unavailable', ha='left', va='center', fontsize=8)

# Arrows downward
arrow_props = {'arrowstyle':'->', 'lw':line_width}
ax.add_patch(FancyArrowPatch((3, 8.5), (3, 8), **arrow_props))
ax.text(3.1, 8.25, 'Modulation commands (-1.0 to +1.0)', ha='left', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((5.5, 8.5), (5.5, 8), **arrow_props))
ax.text(5.6, 8.25, 'Heartbeat signal (implicit via tool calls)', ha='left', va='center', fontsize=8)

# Middle section - Transition Controller
ax.add_patch(Rectangle((3.5, 7), 2, 1, fill=False, lw=line_width))
ax.text(4.25, 7.75, 'Heartbeat Watchdog', ha='center', va='center', fontsize=10)
ax.text(4.25, 7.5, 'Monitors time since last cognitive input', ha='center', va='center', fontsize=8)
ax.text(4.25, 7.3, 'Timeout threshold: 30 seconds', ha='center', va='center', fontsize=8)
ax.text(4.25, 7.1, 'Check interval: 5 seconds', ha='center', va='center', fontsize=8)

# Two output paths
ax.add_patch(FancyArrowPatch((3.5, 6.5), (2, 6), ls='solid', **arrow_props))
ax.text(2.5, 6.25, 'Heartbeat active -> Connected Mode', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((5, 6.5), (6.5, 6), ls='dashed', **arrow_props))
ax.text(5.75, 6.25, 'Heartbeat timeout -> Autonomous Mode', ha='center', va='center', fontsize=8)

# Left path - Connected Mode
ax.add_patch(Rectangle((1, 5), 2, 1, fill=False, lw=line_width))
ax.text(2, 5.75, 'Cognitive-Driven Operation', ha='center', va='center', fontsize=10)
ax.text(2, 5.5, 'Input: Claude-controlled (0-1)', ha='center', va='center', fontsize=8)
ax.text(2, 5.25, 'Modulation: Claude-controlled (-1 to +1)', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((2, 4.5), (2, 4), **arrow_props))

# Right path - Autonomous Mode
ax.add_patch(Rectangle((5.5, 5), 2, 1, fill=False, lw=line_width))
ax.text(6.5, 5.75, 'Autonomous Fallback Controller', ha='center', va='center', fontsize=10)
ax.text(6.5, 5.5, 'Input: Self-generated (circadian + bursts)', ha='center', va='center', fontsize=8)
ax.text(6.5, 5.25, 'Modulation: Energy-aware (-0.4 to +0.3)', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((6.5, 4.5), (6.5, 4), **arrow_props))

# Additional outputs from Autonomous
ax.add_patch(FancyArrowPatch((7.5, 5.5), (7.5, 5), **arrow_props))
ax.add_patch(Rectangle((7.25, 4.75), 0.5, 0.5, fill=False, lw=line_width))
ax.text(7.5, 5, 'Step Buffer', ha='center', va='center', fontsize=8)

ax.add_patch(FancyArrowPatch((7.5, 5), (7.5, 4.5), **arrow_props))
ax.add_patch(Ellipse((7.5, 4), 0.5, 0.3, fill=False, lw=line_width))  # cylinder shape
ax.text(7.5, 4, 'State Snapshots', ha='center', va='center', fontsize=8)

# Bottom section - Neural Processing
ax.add_patch(Rectangle((1.5, 2), 5, 1.5, fill=False, lw=line_width))
ax.text(4.25, 2.75, 'Spiking Neural Network + Energy Harvester', ha='center', va='center', fontsize=10)
ax.text(4.25, 2.5, 'Continuous operation regardless of control source', ha='center', va='center', fontsize=8)
ax.text(4.25, 2.25, 'THE SYSTEM NEVER STOPS', ha='center', va='center', fontsize=10)

# Annotations
ax.text(4.25, 1.5, 'Seamless transition: SNN continues processing without interruption', ha='center', va='center', fontsize=8)
ax.text(4.25, 1.2, 'The control source changes; the computation continues', ha='center', va='center', fontsize=8)

plt.savefig('patent_drawings/patent_c/fig1.svg', format='svg')
plt.close()

# FIG. 2 - State Transition Diagram
fig, ax = setup_figure(2, 6)

# Three states
# State 1 CONNECTED left
ax.add_patch(FancyBboxPatch((1.5, 6), 2, 2, boxstyle="round,pad=0.1", fill=False, lw=line_width))
ax.text(2.5, 7.5, 'CONNECTED', ha='center', va='center', fontsize=10, weight='bold')
ax.text(2.5, 7.2, 'Cognitive layer active', ha='center', va='center', fontsize=8)
ax.text(2.5, 7, 'Input from cognitive layer', ha='center', va='center', fontsize=8)
ax.text(2.5, 6.8, 'Modulation from cognitive layer', ha='center', va='center', fontsize=8)

# State 2 AUTONOMOUS right
ax.add_patch(FancyBboxPatch((5, 6), 2, 2, boxstyle="round,pad=0.1", fill=False, lw=line_width))
ax.text(6, 7.5, 'AUTONOMOUS', ha='center', va='center', fontsize=10)
ax.text(6, 7.2, 'Fallback active', ha='center', va='center', fontsize=8)
ax.text(6, 7, 'Self-generated input', ha='center', va='center', fontsize=8)
ax.text(6, 6.8, 'Energy-aware modulation', ha='center', va='center', fontsize=8)
ax.text(6, 6.6, 'State buffering active', ha='center', va='center', fontsize=8)

# State 3 RECOVERING bottom
ax.add_patch(FancyBboxPatch((3.75, 3), 2, 1.5, boxstyle="round,pad=0.1", fill=False, lw=line_width))
ax.text(4.75, 4, 'RECOVERING', ha='center', va='center', fontsize=10)
ax.text(4.75, 3.8, 'Resynchronization', ha='center', va='center', fontsize=8)
ax.text(4.75, 3.6, 'Transmitting buffer', ha='center', va='center', fontsize=8)
ax.text(4.75, 3.4, 'Restoring cognitive control', ha='center', va='center', fontsize=8)

# Transitions
# CONNECTED -> AUTONOMOUS
ax.add_patch(FancyArrowPatch((3.5, 7), (5, 7), connectionstyle="arc3,rad=0.3", **arrow_props))
ax.text(4.25, 7.1, 'Heartbeat timeout (>30s no tool call)', ha='center', va='bottom', fontsize=8)
ax.text(4.25, 6.9, 'last_tool_call_time > 30s', ha='center', va='top', fontsize=8)

# AUTONOMOUS -> RECOVERING
ax.add_patch(FancyArrowPatch((6, 6), (4.75, 4.5), connectionstyle="arc3,rad=-0.3", **arrow_props))
ax.text(5.5, 5.25, 'Cognitive layer reconnects (resync called)', ha='left', va='center', fontsize=8)
ax.text(5.5, 5, 'resync() tool invoked', ha='left', va='center', fontsize=8)

# RECOVERING -> CONNECTED
ax.add_patch(FancyArrowPatch((3.75, 4), (2.5, 6), connectionstyle="arc3,rad=0.3", **arrow_props))
ax.text(3, 5, 'Resync complete, buffer transmitted', ha='right', va='center', fontsize=8)
ax.text(3, 4.75, 'Cognitive layer acknowledges state', ha='right', va='center', fontsize=8)

# AUTONOMOUS self-loop
ax.add_patch(FancyArrowPatch((7, 7), (7, 7), connectionstyle="arc3,rad=1", **arrow_props))
ax.text(7.1, 7, 'Each autonomous step (up to 10,000)', ha='left', va='center', fontsize=8)
ax.text(7.1, 6.75, 'autonomous_steps < hard_cap', ha='left', va='center', fontsize=8)

# AUTONOMOUS -> CONNECTED direct dashed
ax.add_patch(FancyArrowPatch((5, 7), (3.5, 7), ls='dashed', connectionstyle="arc3,rad=-0.3", **arrow_props))
ax.text(4.25, 6.5, 'Any tool call received (heartbeat reset)', ha='center', va='center', fontsize=8)
ax.text(4.25, 6.3, 'Direct reconnection without explicit resync', ha='center', va='center', fontsize=8)

# Additional annotations
ax.text(2.5, 8.5, 'Initial state', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((2.5, 8.7), (2.5, 8.2), **arrow_props))
ax.text(6, 5.5, 'Snapshot every 50 steps', ha='center', va='center', fontsize=8)
ax.text(7.1, 6.5, 'Hard cap: 10,000 steps', ha='left', va='center', fontsize=8)

plt.savefig('patent_drawings/patent_c/fig2.svg', format='svg')
plt.close()

# FIG. 3 - Energy-Aware Modulation Curve
fig = plt.figure(figsize=(paper_width, paper_height), dpi=dpi)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, paper_width)
ax.set_ylim(0, paper_height)
ax.axis('off')
ax.text(paper_width / 2, paper_height - 0.5, "3/6", ha='center', va='center', fontsize=10)
ax.text(left_margin, bottom_margin + 0.2, "FIG. 3", ha='left', va='bottom', fontsize=font_size_label)

# Graph area
graph_ax = fig.add_axes([left_margin / paper_width, (bottom_margin + 1) / paper_height, (paper_width - left_margin - right_margin) / paper_width, (paper_height - top_margin - bottom_margin - 2) / paper_height])
graph_ax.set_xlabel('System Energy Level (mWh)', fontsize=10)
graph_ax.set_ylabel('Autonomous Modulation Value', fontsize=10)
graph_ax.set_xticks([0, 1])
graph_ax.set_xticklabels(['0', '100+'])
graph_ax.set_yticks([0, 1])
graph_ax.set_yticklabels(['-0.5', '+0.5'])

# Step function
energy_norm = np.array([0, 0.15, 0.3, 0.8, 1.0])
mod_norm = np.array([0.1, 0.4, 0.5, 0.5, 0.8])  # normalized (mod +0.5)/1
for i in range(4):
    graph_ax.plot([energy_norm[i], energy_norm[i+1]], [mod_norm[i], mod_norm[i]], color='black', lw=line_width)
    if i < 3:
        graph_ax.plot([energy_norm[i+1], energy_norm[i+1]], [mod_norm[i], mod_norm[i+1]], color='black', lw=line_width)

# Vertical dashed lines
for thresh in [0.15, 0.3, 0.8]:
    graph_ax.axvline(x=thresh, ls='dashed', color='black', lw=line_width)
    graph_ax.text(thresh, -0.05, str(int(thresh*100)), ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)

# Hatching
graph_ax.add_patch(Rectangle((0, 0), 0.15, 1, hatch='xxx', fill=False, lw=0))
graph_ax.add_patch(Rectangle((0.15, 0), 0.15, 1, hatch='/', fill=False, lw=0))
graph_ax.add_patch(Rectangle((0.8, 0), 0.2, 1, hatch='/', fill=False, lw=0))

# Labels
graph_ax.text(0.075, 0.95, 'CRITICAL — Maximum conservation', ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)
graph_ax.text(0.075, 0.9, 'Inhibit neural activity to preserve energy', ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)

graph_ax.text(0.225, 0.95, 'LOW — Cautious operation', ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)
graph_ax.text(0.225, 0.9, 'Slightly reduce activity', ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)

graph_ax.text(0.55, 0.95, 'NORMAL — Neutral operation', ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)
graph_ax.text(0.55, 0.9, 'Standard autonomous processing', ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)

graph_ax.text(0.9, 0.95, 'SURPLUS — Opportunistic exploration', ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)
graph_ax.text(0.9, 0.9, 'Increase activity to utilize excess energy', ha='center', va='top', fontsize=8, transform=graph_ax.transAxes)

# Annotation
ax.text(4.25, bottom_margin + 0.5, 'The system autonomously adjusts its processing intensity based on available energy — mimicking biological metabolic regulation', ha='center', fontsize=8)

plt.savefig('patent_drawings/patent_c/fig3.svg', format='svg')
plt.close()

# FIG. 4 - Autonomous Input Generator Output
fig = plt.figure(figsize=(paper_width, paper_height), dpi=dpi)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, paper_width)
ax.set_ylim(0, paper_height)
ax.axis('off')
ax.text(paper_width / 2, paper_height - 0.5, "4/6", ha='center', va='center', fontsize=10)
ax.text(left_margin, bottom_margin + 0.2, "FIG. 4", ha='left', va='bottom', fontsize=font_size_label)

# Main graph
main_ax = fig.add_axes([left_margin / paper_width, (bottom_margin + 3) / paper_height, (paper_width - left_margin - right_margin) / paper_width, 4 / paper_height])
main_ax.set_xlabel('Autonomous Step Number', fontsize=10)
main_ax.set_ylabel('Input Value', fontsize=10)
main_ax.set_xticks([0, 1])
main_ax.set_xticklabels(['0', '500 (representative)'])
main_ax.set_yticks([0, 1])
main_ax.set_yticklabels(['0.0', '1.0'])

steps = np.linspace(0, 1, 501)
period = 100 / 500  # normalized
base = 0.5 + 0.3 * np.sin(2 * np.pi * steps / period)
main_ax.plot(steps, base, ls='-', color='black', lw=1)
main_ax.text(0.95, 0.95, 'base = 0.5 + 0.3 x sin(2 x pi x step / period)', ha='right', va='top', fontsize=8, transform=main_ax.transAxes)
main_ax.text(0.95, 0.9, 'period = 100 steps', ha='right', va='top', fontsize=8, transform=main_ax.transAxes)
main_ax.text(0.95, 0.85, 'Amplitude range: 0.2 to 0.8', ha='right', va='top', fontsize=8, transform=main_ax.transAxes)

# Bursts
np.random.seed(42)  # for reproducibility
burst_indices = np.random.choice(range(501), int(501*0.1), replace=False)
bursts = np.zeros(501)
bursts[burst_indices] = 0.2
composite = base + bursts
for idx in burst_indices:
    main_ax.plot([steps[idx], steps[idx]], [base[idx], composite[idx]], color='black', lw=2)
    main_ax.text(steps[idx], composite[idx], '10% probability burst', ha='left', va='bottom', fontsize=8, rotation=90, transform=main_ax.transData)

main_ax.plot(steps, composite, color='black', lw=2)
main_ax.text(0.05, 0.95, 'Composite autonomous input', ha='left', va='top', fontsize=8, transform=main_ax.transAxes)

# Small graph
small_ax = fig.add_axes([left_margin / paper_width, (bottom_margin + 1) / paper_height, (paper_width - left_margin - right_margin) / paper_width, 1.5 / paper_height])
small_ax.set_xlabel('Autonomous Step Number', fontsize=8)
small_ax.set_ylabel('Energy Level', fontsize=8)
energy = 50 + np.cumsum(np.random.normal(0, 0.1, 501))
small_ax.plot(steps, energy / 100, color='black', lw=1)  # normalized for plot
for thresh in [0.15, 0.3, 0.8]:
    small_ax.axhline(thresh, ls='dashed', color='black')
    small_ax.text(1, thresh + 0.01, str(int(thresh*100)), ha='right', va='bottom', fontsize=8, transform=small_ax.transAxes)
small_ax.text(0.5, 0.05, 'Energy-aware modulation applied to composite input', ha='center', fontsize=8, transform=small_ax.transAxes)

# Annotations
ax.text(4.25, bottom_margin + 0.5, 'Circadian rhythm provides structured temporal variation', ha='center', fontsize=8)
ax.text(4.25, bottom_margin + 0.3, 'Random bursts prevent the system from settling into trivial attractors', ha='center', fontsize=8)
ax.text(4.25, bottom_margin + 0.1, 'Energy-aware modulation adjusts overall intensity', ha='center', fontsize=8)

plt.savefig('patent_drawings/patent_c/fig4.svg', format='svg')
plt.close()

# FIG. 5 - Resynchronization Payload Structure
fig, ax = setup_figure(5, 6)

# Top-level
ax.add_patch(Rectangle((2, 7), 4, 3, fill=False, lw=line_width))
ax.text(4, 9.75, 'Resynchronization Payload', ha='center', va='center', fontsize=10)

# Section 1
ax.add_patch(Rectangle((2.5, 8.5), 3, 1, fill=False, lw=line_width))
ax.text(4, 9.25, 'Summary Statistics', ha='center', va='center', fontsize=10)
text_summary = "steps_autonomous: [integer]\nenergy_delta: [float] mWh\nmin_energy: [float] mWh\nmax_energy: [float] mWh\nmean_energy: [float] mWh\ntotal_spikes: [integer]\nmean_spikes_per_step: [float]"
ax.text(4, 8.75, text_summary, ha='center', va='center', fontsize=8, linespacing=1.5)
ax.text(4, 8, 'ALWAYS included (compact summary)', ha='center', va='center', fontsize=8)
ax.text(4, 7.75, '~200 bytes', ha='center', va='center', fontsize=8)

# Section 2
ax.add_patch(Rectangle((2.5, 6.5), 3, 0.5, fill=False, lw=line_width))
ax.text(4, 6.75, 'Energy Delta Detail', ha='center', va='center', fontsize=10)
text_energy = "energy_start: [float] mWh\nenergy_end: [float] mWh\nenergy_delta: [float] mWh"
ax.text(4, 6.5, text_energy, ha='center', va='center', fontsize=8, linespacing=1.5)
ax.add_patch(FancyArrowPatch((5.5, 6.5), (6, 6.5), **arrow_props))
ax.text(6.1, 6.5, 'Positive = system gained energy during autonomy', ha='left', va='center', fontsize=8)

# Section 3
ax.add_patch(Rectangle((2.5, 4), 3, 2, fill=False, lw=line_width))
ax.text(4, 5.75, 'Full Step Buffer (Optional)', ha='center', va='center', fontsize=10)
text_buffer = "Step 0: {input, modulation, spikes, energy, temp, pattern}\nStep 1: {input, modulation, spikes, energy, temp, pattern}\n...\nStep N: {input, modulation, spikes, energy, temp, pattern}"
ax.text(4, 5, text_buffer, ha='center', va='center', fontsize=8, linespacing=1.5)
ax.text(4, 4.25, 'OPTIONAL — Full operational history', ha='center', va='center', fontsize=8)
ax.text(4, 4, '~100 bytes x N steps', ha='center', va='center', fontsize=8)

# Granularity
ax.add_patch(FancyArrowPatch((2, 8.75), (1.5, 8.75), **arrow_props))
ax.text(1.4, 8.75, 'Level 1: Summary only (fast resync)', ha='right', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((2, 5), (1.5, 5), **arrow_props))
ax.text(1.4, 5, 'Level 2: Full buffer (complete reconstruction)', ha='right', va='center', fontsize=8)

# Decision
ax.add_patch(Polygon([[4, 3], [3.5, 2.5], [4, 2], [4.5, 2.5]], closed=True, fill=False, lw=line_width))
ax.text(4, 2.5, 'Cognitive layer requests full buffer?', ha='center', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((4.5, 2.5), (5, 2.5), **arrow_props))
ax.text(5.1, 2.5, 'Yes: Transmit Level 2 (summary + full buffer)', ha='left', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((3.5, 2.5), (3, 2.5), **arrow_props))
ax.text(2.9, 2.5, 'No: Transmit Level 1 (summary only)', ha='right', va='center', fontsize=8)

plt.savefig('patent_drawings/patent_c/fig5.svg', format='svg')
plt.close()

# FIG. 6 - Recovery Timeline Diagrams
fig, ax = setup_figure(6, 6)

# Timeline A
ax.text(left_margin, 8, 'Timeline A — Normal Reconnection:', ha='left', fontsize=10)
ax.add_patch(FancyArrowPatch((left_margin, 7.5), (left_margin + paper_width - left_margin - right_margin, 7.5), arrowstyle='->', lw=line_width))
positions = np.linspace(left_margin, paper_width - right_margin, 6)
labels = ['-- Connected --', '-- Timeout (30s) --', '-- Autonomous --', '-- Resync --', '-- Connected -->']
for i, label in enumerate(labels):
    ax.text(positions[i], 7.6, label, ha='left', va='bottom', fontsize=8)
sublabels = ['[Claude active]', '[Watchdog counting]', '[Self-generated input + energy modulation]', '[Buffer transmitted]', '[Cognitive control restored]']
for i, sub in enumerate(sublabels):
    ax.text(positions[i], 7.4, sub, ha='left', va='top', fontsize=8)
trans_labels = ["Claude goes silent", "Fallback engages", "resync() called", "Seamless resumption"]
for i, trans in enumerate(trans_labels):
    ax.text(positions[i+1], 7.2, trans, ha='left', fontsize=8)
ax.text((positions[2] + positions[3])/2, 7, '[N steps buffered]', ha='center', fontsize=8)

# Timeline B
ax.text(left_margin, 6, 'Timeline B — Crash Recovery:', ha='left', fontsize=10)
ax.add_patch(FancyArrowPatch((left_margin, 5.5), (left_margin + paper_width - left_margin - right_margin, 5.5), arrowstyle='->', lw=line_width))
positions_b = np.linspace(left_margin, paper_width - right_margin, 5)
labels_b = ['-- Connected --', '-- CRASH --', '-- Server Restart --', '-- Snapshot Load --', '-- Connected -->']
for i, label in enumerate(labels_b):
    ax.text(positions_b[i], 5.6, label, ha='left', va='bottom', fontsize=8)
sublabels_b = ['[Normal operation]', '[MCP server terminates]', '[Process restarts]', '[Reads latest.json]', '[State restored]']
for i, sub in enumerate(sublabels_b):
    ax.text(positions_b[i], 5.4, sub, ha='left', va='top', fontsize=8)
trans_labels_b = ["Server process dies", "Process relaunched", "initialize_consciousness loads snapshot"]
for i, trans in enumerate(trans_labels_b):
    ax.text(positions_b[i+1], 5.2, trans, ha='left', fontsize=8)
ax.text(4.25, 4.8, 'State restored from last snapshot (max 50 steps lost)', ha='center', fontsize=8)
ax.text((positions_b[3] + positions_b[4])/2, 5, '[latest.json (serialized every 50 steps)]', ha='center', fontsize=8)

# Timeline C
ax.text(left_margin, 4, 'Timeline C — Clean Shutdown:', ha='left', fontsize=10)
ax.add_patch(FancyArrowPatch((left_margin, 3.5), (left_margin + paper_width - left_margin - right_margin - 1, 3.5), arrowstyle='->', lw=line_width))
positions_c = np.linspace(left_margin, paper_width - right_margin - 1, 4)
labels_c = ['-- Connected --', '-- Autonomous --', '-- EOF Signal --', '-- Shutdown']
for i, label in enumerate(labels_c):
    ax.text(positions_c[i], 3.6, label, ha='left', va='bottom', fontsize=8)
sublabels_c = ['[Normal operation]', '[Fallback operation]', '[stdin closed]', '[Final snapshot written to disk]']
for i, sub in enumerate(sublabels_c):
    ax.text(positions_c[i], 3.4, sub, ha='left', va='top', fontsize=8)
trans_labels_c = ["Claude disconnects", "Process receives EOF", "finally block writes snapshot"]
for i, trans in enumerate(trans_labels_c):
    ax.text(positions_c[i+1], 3.2, trans, ha='left', fontsize=8)
ax.text(4.25, 2.8, 'State preserved for next session', ha='center', fontsize=8)

# Common
ax.text(4.25, 1.5, 'Solid line segments: "System actively processing"', ha='center', fontsize=8)
ax.text(4.25, 1.3, 'Dashed line segments: "System in transition"', ha='center', fontsize=8)
ax.text(4.25, 1.1, 'Bold marker at each state change: "No data loss at any transition"', ha='center', fontsize=8)

plt.savefig('patent_drawings/patent_c/fig6.svg', format='svg')
plt.close()

print("All 6 Patent C figures generated successfully in patent_drawings/patent_c/")

#!/usr/bin/env python3
"""
Patent Diagram Generator — Graphviz-based patent figure generation.

Uses the LobeHub patent-diagram-generator skill pattern to create
patent-style technical diagrams for all three patents (A, B, C)
in the Consciousness_Env project.

Generates DOT source files and renders SVG/PNG/PDF when Graphviz
system binary (dot) is available.

Usage:
    python tools/generate_patent_diagrams.py [--format svg|png|pdf] [--patent a|b|c|all]
"""

import argparse
import os
import sys

import graphviz


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'patent_drawings', 'graphviz')


def patent_style_attrs():
    """Return common Graphviz attributes for patent-style diagrams."""
    return {
        'graph': {
            'fontname': 'Arial',
            'fontsize': '14',
            'bgcolor': 'white',
            'pad': '0.5',
            'nodesep': '0.6',
            'ranksep': '0.8',
        },
        'node': {
            'fontname': 'Arial',
            'fontsize': '12',
            'shape': 'box',
            'style': 'rounded',
            'penwidth': '1.5',
            'color': 'black',
            'fontcolor': 'black',
        },
        'edge': {
            'fontname': 'Arial',
            'fontsize': '10',
            'color': 'black',
            'penwidth': '1.2',
        },
    }


# ---------------------------------------------------------------------------
# Patent A: Self-Sustaining Neural-Motor Energy Harvesting Loop
# ---------------------------------------------------------------------------

def patent_a_fig1_system_overview():
    """FIG. 1 — 8-Layer Consciousness Loop Overview."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentA_Fig1', comment='8-Layer Consciousness Loop')
    dot.attr(rankdir='TB', label='FIG. 1', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    dot.node('env', 'ENVIRONMENT\n(100)', shape='ellipse')
    dot.node('l1', 'L1: Printed Membrane\nThermochromicMixin\n(102)')
    dot.node('l2', 'L2: Sensing Pads\nlight_intensity, temp\n(104)')
    dot.node('l3', 'L3: Optical Transmission\nsignal_voltage\n(106)')
    dot.node('l4', 'L4: Neuromorphic CPU\nBaseSNN + L8 input\n(108)')
    dot.node('l5', 'L5: Servo Actuation\ntarget_angle\n(110)')
    dot.node('l6', 'L6: Energy Harvesting\npiezo + thermal\n(112)')
    dot.node('l7', 'L7: Ground Reference\nnoise floor\n(114)')
    dot.node('l8', 'L8: Recursive Reflection\nprevious_output\n(116)')

    dot.edge('env', 'l1', label='light, heat')
    dot.edge('l1', 'l2', label='membrane signal')
    dot.edge('l2', 'l3', label='light intensity')
    dot.edge('l3', 'l4', label='signal voltage')
    dot.edge('l4', 'l5', label='SNN output')
    dot.edge('l5', 'l6', label='movement\n(friction)')
    dot.edge('l6', 'l7', label='harvested energy')
    dot.edge('l7', 'l8', label='baseline ref')
    dot.edge('l8', 'l4', label='reflection\ncoeff', style='dashed')

    # Thermal cross-link
    dot.edge('l1', 'l6', label='thermal\ncross-link', style='dotted', constraint='false')

    return dot


def patent_a_fig2_energy_loop():
    """FIG. 2 — Energy Harvesting Closed Loop."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentA_Fig2', comment='Energy Harvesting Loop')
    dot.attr(rankdir='LR', label='FIG. 2', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    dot.node('snn', 'Spiking Neural\nNetwork\n(10)')
    dot.node('motor', 'Motor\nActuator\n(20)')
    dot.node('piezo', 'Piezoelectric\nHarvester\n(30)')
    dot.node('thermo', 'Thermoelectric\nHarvester\n(32)')
    dot.node('power', 'Power\nFeedback\n(40)')

    dot.edge('snn', 'motor', label='neural output')
    dot.edge('motor', 'piezo', label='mechanical\nfriction')
    dot.edge('motor', 'thermo', label='heat\ndifferential', style='dotted')
    dot.edge('piezo', 'power', label='electrical\nenergy')
    dot.edge('thermo', 'power', label='electrical\nenergy')
    dot.edge('power', 'snn', label='sustaining\npower')

    return dot


def patent_a_fig3_method_flowchart():
    """FIG. 3 — Method flowchart for self-sustaining operation."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentA_Fig3', comment='Self-Sustaining Method')
    dot.attr(rankdir='TB', label='FIG. 3', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    dot.node('s1', 'S1: Receive\nSensor Input\n(200)', shape='box')
    dot.node('s2', 'S2: Process via\nSNN\n(210)', shape='box')
    dot.node('s3', 'S3: Generate\nMotor Output\n(220)', shape='box')
    dot.node('s4', 'S4: Harvest\nEnergy\n(230)', shape='box')
    dot.node('d1', 'Net-positive\nenergy?\n(240)', shape='diamond')
    dot.node('s5', 'S5: Continue\nOperation\n(250)', shape='box')
    dot.node('s6', 'S6: Enter\nConservation\n(260)', shape='box')

    dot.edge('s1', 's2')
    dot.edge('s2', 's3')
    dot.edge('s3', 's4')
    dot.edge('s4', 'd1')
    dot.edge('d1', 's5', label='Yes')
    dot.edge('d1', 's6', label='No')
    dot.edge('s5', 's1', style='dashed', label='loop')
    dot.edge('s6', 's1', style='dashed', label='loop')

    return dot


# ---------------------------------------------------------------------------
# Patent B: Configurable Recursive Self-Observation
# ---------------------------------------------------------------------------

def patent_b_fig1_reflection():
    """FIG. 1 — Recursive Self-Observation Architecture."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentB_Fig1', comment='Recursive Self-Observation')
    dot.attr(rankdir='TB', label='FIG. 1', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    dot.node('input', 'External\nInput\n(10)', shape='parallelogram')
    dot.node('snn', 'Spiking Neural\nNetwork\n(20)')
    dot.node('output', 'Aggregate\nOutput\n(30)')
    dot.node('record', 'Record Output\nat timestep t\n(40)')
    dot.node('scale', 'Scale by\nReflection Coeff\n(50)')
    dot.node('modulate', 'Cognitive\nModulation\n(60)', shape='ellipse')

    dot.edge('input', 'snn')
    dot.edge('snn', 'output')
    dot.edge('output', 'record')
    dot.edge('record', 'scale', label='t → t+1')
    dot.edge('scale', 'snn', label='feedback', style='dashed')
    dot.edge('modulate', 'scale', label='adjust\ngain', style='dotted')

    return dot


def patent_b_fig2_spectrum():
    """FIG. 2 — Self-Awareness Spectrum."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentB_Fig2', comment='Self-Awareness Spectrum')
    dot.attr(rankdir='LR', label='FIG. 2', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    dot.node('zero', 'Coeff = 0.0\nNo Self-Observation\n(70)')
    dot.node('low', 'Coeff = 0.2\nSubtle Feedback\n(72)')
    dot.node('mid', 'Coeff = 0.5\nBalanced\n(74)')
    dot.node('high', 'Coeff = 1.0\nSelf-Dominated\n(76)')

    dot.edge('zero', 'low', label='increasing')
    dot.edge('low', 'mid', label='self-awareness')
    dot.edge('mid', 'high', label='spectrum')

    return dot


def patent_b_fig3_stdp():
    """FIG. 3 — STDP Learning with Self-Observation."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentB_Fig3', comment='STDP + Self-Observation')
    dot.attr(rankdir='TB', label='FIG. 3', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    dot.node('pre', 'Pre-synaptic\nNeuron i\n(80)')
    dot.node('post', 'Post-synaptic\nNeuron j\n(82)')
    dot.node('ltp', 'LTP:\nw += A+ × trace_i\n(84)')
    dot.node('ltd', 'LTD:\nw -= A- × trace_j\n(86)')
    dot.node('reflect', 'L8 Reflection\nFeedback\n(88)', shape='ellipse')

    dot.edge('pre', 'post', label='synapse w[i,j]')
    dot.edge('post', 'ltp', label='post fires')
    dot.edge('pre', 'ltd', label='pre fires')
    dot.edge('reflect', 'pre', style='dashed', label='modulates\nfiring')
    dot.edge('reflect', 'post', style='dashed', label='modulates\nfiring')

    return dot


# ---------------------------------------------------------------------------
# Patent C: Cognitive Fallback with Autonomous Self-Regulation
# ---------------------------------------------------------------------------

def patent_c_fig1_architecture():
    """FIG. 1 — System Architecture: Seamless Mode Transition."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentC_Fig1', comment='System Architecture - Mode Transition')
    dot.attr(rankdir='TB', label='FIG. 1', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    # External cognitive control (Claude)
    dot.node('cognitive', 'External Cognitive\nControl (Claude)\n(100)', shape='ellipse', style='dashed')

    # Heartbeat watchdog
    dot.node('watchdog', 'Heartbeat Watchdog\nTimeout: 30s | Check: 5s\n(102)')

    # Two operational modes
    dot.node('connected', 'CONNECTED\nCognitive-Driven\nOperation\n(104)')
    dot.node('autonomous', 'AUTONOMOUS\nFallback Controller\n(106)', penwidth='2.5')

    # State persistence
    dot.node('buffer', 'Step Buffer\n(108)', shape='cylinder')
    dot.node('snapshot', 'Snapshot Store\n(.snapshots/latest.json)\n(110)', shape='cylinder')

    # Core processing
    dot.node('snn', 'SNN + Energy Harvester\n(112)')
    dot.node('harvester', 'Energy Harvester\n(114)', shape='hexagon')

    # Flows
    dot.edge('cognitive', 'watchdog', label='tool calls')
    dot.edge('watchdog', 'connected', label='active\n(heartbeat OK)')
    dot.edge('watchdog', 'autonomous', label='timeout\n(>30s silent)', style='dashed')
    dot.edge('connected', 'snn', label='Claude input\n+ modulation')
    dot.edge('autonomous', 'snn', label='self-regulated\ninput + modulation')
    dot.edge('snn', 'buffer', label='step data')
    dot.edge('autonomous', 'snapshot', label='every 50 steps')
    dot.edge('snn', 'harvester', constraint='false')

    return dot


def patent_c_fig2_state_machine():
    """FIG. 2 — State Machine: CONNECTED / AUTONOMOUS / RECOVERING."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentC_Fig2', comment='State Machine')
    dot.attr(rankdir='LR', label='FIG. 2', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    # States (circles)
    dot.node('connected', 'CONNECTED\n(200)', shape='doublecircle', width='1.3')
    dot.node('autonomous', 'AUTONOMOUS\n(202)', shape='circle', width='1.3')
    dot.node('recovering', 'RECOVERING\n(204)', shape='circle', width='1.3')

    # Start arrow
    dot.node('start', '', shape='point', width='0.1')
    dot.edge('start', 'connected', label='START')

    # Transitions
    dot.edge('connected', 'autonomous', label='Heartbeat timeout\n>30s no tool call\n(206)')
    dot.edge('autonomous', 'recovering', label='resync() called\n(208)')
    dot.edge('recovering', 'connected', label='Resync complete\n(210)')

    # Direct reconnection shortcut
    dot.edge('autonomous', 'connected', label='Any tool call\n(direct reconnect)\n(212)',
             style='dashed', constraint='false')

    # Self-loop on autonomous
    dot.edge('autonomous', 'autonomous', label='Each step\n(max 10K)\n(214)')

    # Legend
    dot.node('legend',
             '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">'
             '<TR><TD COLSPAN="2"><B>State Legend (216)</B></TD></TR>'
             '<TR><TD>Double circle</TD><TD>Initial state</TD></TR>'
             '<TR><TD>Solid arrow</TD><TD>Primary transition</TD></TR>'
             '<TR><TD>Dashed arrow</TD><TD>Direct reconnect</TD></TR>'
             '</TABLE>>',
             shape='plaintext')

    return dot


def patent_c_fig3_energy_modulation():
    """FIG. 3 — Energy-Aware Modulation Strategy (4-zone step function)."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentC_Fig3', comment='Energy-Aware Modulation')
    dot.attr(rankdir='LR', label='FIG. 3', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    # Y-axis label
    dot.node('yaxis', 'Modulation\nValue\n(300)', shape='plaintext')

    # Four energy zones as boxes
    dot.node('critical', 'CRITICAL\n0-15 mWh\nMod = -0.4\n(308)',
             style='rounded,bold', color='black')
    dot.node('low', 'LOW\n15-30 mWh\nMod = -0.1\n(310)',
             style='rounded')
    dot.node('normal', 'NORMAL\n30-80 mWh\nMod = 0.0\n(312)',
             style='rounded')
    dot.node('surplus', 'SURPLUS\n>80 mWh\nMod = +0.3\n(314)',
             style='rounded')

    # X-axis label
    dot.node('xaxis', 'Energy (mWh)\n(304)', shape='plaintext')

    # Flow left to right (increasing energy)
    dot.edge('yaxis', 'critical', style='invis')
    dot.edge('critical', 'low', label='15 mWh')
    dot.edge('low', 'normal', label='30 mWh')
    dot.edge('normal', 'surplus', label='80 mWh')
    dot.edge('surplus', 'xaxis', style='invis')

    # Behavioral effects table
    dot.node('effects',
             '<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">'
             '<TR><TD COLSPAN="2"><B>Behavioral Effects (302)</B></TD></TR>'
             '<TR><TD>-0.4</TD><TD>Max conservation, inhibit activity</TD></TR>'
             '<TR><TD>-0.1</TD><TD>Cautious, slight reduction</TD></TR>'
             '<TR><TD>0.0</TD><TD>Standard autonomous processing</TD></TR>'
             '<TR><TD>+0.3</TD><TD>Opportunistic exploration</TD></TR>'
             '</TABLE>>',
             shape='plaintext')

    return dot


def patent_c_fig4_input_generator():
    """FIG. 4 — Autonomous Input Generator and Energy Recovery."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentC_Fig4', comment='Input Generator & Energy Recovery')
    dot.attr(rankdir='LR', label='FIG. 4', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    # Input signal pipeline
    dot.node('osc', 'Circadian\nOscillator\nperiod=500\n(400)')
    dot.node('burst', 'Attention Burst\nInjector\np=10%, amp=0.2\n(402)')
    dot.node('sum', 'Signal\nSummation', shape='circle', width='0.6')
    dot.node('output', 'Autonomous\nInput Signal\n[0, 1]')

    dot.edge('osc', 'sum', label='0.5 + 0.3*sin(2*pi*t/500)')
    dot.edge('burst', 'sum', label='random burst')
    dot.edge('sum', 'output')

    # Formula box
    dot.node('formula',
             '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">'
             '<TR><TD><B>Input Formula (404)</B></TD></TR>'
             '<TR><TD>input = 0.5 + 0.3 * sin(2*pi*step/period) + burst</TD></TR>'
             '<TR><TD>burst: 10% chance, amplitude +0.2</TD></TR>'
             '</TABLE>>',
             shape='plaintext')

    # Energy recovery annotation
    dot.node('recovery',
             '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">'
             '<TR><TD><B>Energy Recovery (406)</B></TD></TR>'
             '<TR><TD>~10 mWh -> 100 mWh in ~500 steps</TD></TR>'
             '<TR><TD>Traverses: CRITICAL -> LOW -> NORMAL -> SURPLUS</TD></TR>'
             '</TABLE>>',
             shape='plaintext')

    return dot


def patent_c_fig5_resync_payload():
    """FIG. 5 — Resynchronization Payload Structure."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentC_Fig5', comment='Resync Payload Structure')
    dot.attr(rankdir='TB', label='FIG. 5', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    # Outer payload container
    with dot.subgraph(name='cluster_payload') as s:
        s.attr(label='Resynchronization Payload (500)', style='rounded', penwidth='2')

        # Summary statistics (always included)
        s.node('summary',
               '<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">'
               '<TR><TD COLSPAN="2"><B>Summary Statistics (502)</B></TD></TR>'
               '<TR><TD>steps_autonomous</TD><TD>int</TD></TR>'
               '<TR><TD>energy_delta</TD><TD>float mWh</TD></TR>'
               '<TR><TD>min/max/mean energy</TD><TD>float mWh</TD></TR>'
               '<TR><TD>total_spikes</TD><TD>int</TD></TR>'
               '<TR><TD>mean_spikes_per_step</TD><TD>float</TD></TR>'
               '</TABLE>>',
               shape='plaintext')

        # Energy delta detail
        s.node('delta', 'Energy Delta\nnet change (mWh)\n(504)')

    # Decision: full buffer?
    dot.node('decision', 'Full buffer\nrequested?\n(508)', shape='diamond')

    # Full step buffer (optional)
    dot.node('full_buffer',
             '<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">'
             '<TR><TD COLSPAN="2"><B>Full Step Buffer (506)</B></TD></TR>'
             '<TR><TD>input</TD><TD>float per step</TD></TR>'
             '<TR><TD>modulation</TD><TD>float per step</TD></TR>'
             '<TR><TD>spikes</TD><TD>int per step</TD></TR>'
             '<TR><TD>energy</TD><TD>float per step</TD></TR>'
             '<TR><TD>temperature</TD><TD>float per step</TD></TR>'
             '<TR><TD>pattern</TD><TD>str per step</TD></TR>'
             '</TABLE>>',
             shape='plaintext')

    # Cognitive layer receives payload
    dot.node('cognitive', 'Cognitive Layer\n(Claude)', shape='ellipse')

    dot.edge('summary', 'decision')
    dot.edge('decision', 'full_buffer', label='Yes')
    dot.edge('decision', 'cognitive', label='No\n(summary only)')
    dot.edge('full_buffer', 'cognitive', label='transmit')
    dot.edge('delta', 'decision')

    return dot


def patent_c_fig6_recovery_timelines():
    """FIG. 6 — Recovery Timelines: 3 Scenarios."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentC_Fig6', comment='Recovery Timelines')
    graph_attrs = {**attrs['graph'], 'ranksep': '0.5', 'nodesep': '0.4'}
    dot.attr(rankdir='LR', label='FIG. 6', labelloc='t', **graph_attrs)
    dot.attr('node', **attrs['node'], width='1.2')
    dot.attr('edge', **attrs['edge'])

    # Scenario 1: Normal Reconnection (600)
    with dot.subgraph(name='cluster_normal') as s:
        s.attr(label='Normal Reconnection (600)', style='rounded')
        s.node('n1', 'CONNECTED')
        s.node('n2', 'Claude silent\n(30s timeout)')
        s.node('n3', 'AUTONOMOUS\n(N steps)')
        s.node('n4', 'resync()')
        s.node('n5', 'CONNECTED')
        s.edge('n1', 'n2')
        s.edge('n2', 'n3')
        s.edge('n3', 'n4')
        s.edge('n4', 'n5')

    # Scenario 2: Crash Recovery (602)
    with dot.subgraph(name='cluster_crash') as s:
        s.attr(label='Crash Recovery (602)', style='rounded')
        s.node('c1', 'CONNECTED')
        s.node('c2', 'CRASH', shape='box', style='bold')
        s.node('c3', 'RESTART\n(process relaunch)')
        s.node('c4', 'SNAPSHOT\n(load latest.json)')
        s.node('c5', 'CONNECTED')
        s.edge('c1', 'c2')
        s.edge('c2', 'c3')
        s.edge('c3', 'c4', label='max 50\nsteps lost')
        s.edge('c4', 'c5')

    # Scenario 3: Clean Shutdown (604)
    with dot.subgraph(name='cluster_shutdown') as s:
        s.attr(label='Clean Shutdown (604)', style='rounded')
        s.node('s1', 'CONNECTED')
        s.node('s2', 'AUTONOMOUS')
        s.node('s3', 'EOF\n(stdin closed)')
        s.node('s4', 'SHUTDOWN\n(final snapshot)')
        s.node('s5', 'State\npreserved')
        s.edge('s1', 's2')
        s.edge('s2', 's3')
        s.edge('s3', 's4')
        s.edge('s4', 's5')

    # Recovery guarantees legend
    dot.node('legend',
             '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">'
             '<TR><TD COLSPAN="2"><B>Recovery Guarantees (606)</B></TD></TR>'
             '<TR><TD>Solid line</TD><TD>System actively processing</TD></TR>'
             '<TR><TD>Bold marker</TD><TD>No data loss at transition</TD></TR>'
             '<TR><TD>Snapshots</TD><TD>Every 50 autonomous steps</TD></TR>'
             '</TABLE>>',
             shape='plaintext')

    return dot


def patent_c_fig7_signal_flow():
    """FIG. 7 — End-to-End Signal Flow: Connected vs Autonomous Mode."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentC_Fig7', comment='End-to-End Signal Flow')
    dot.attr(rankdir='LR', label='FIG. 7', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    # Connected mode components
    with dot.subgraph(name='cluster_connected') as s:
        s.attr(label='CONNECTED MODE', style='rounded')
        s.node('claude', 'Cognitive Layer\n(Claude)\n(700)', shape='ellipse', style='dashed')
        s.node('claude_input', 'INPUT\n(from Claude)\n(702)')

    # Core processing (shared)
    dot.node('input_switch', 'Input\nSwitch\n(716)', shape='triangle')
    dot.node('snn_core', 'SNN CORE\n(704)', penwidth='2.5')
    dot.node('mod_switch', 'Modulation\nSwitch\n(718)', shape='triangle')
    dot.node('motor', 'Motor Output\n(706)')
    dot.node('actuator', 'Actuator\n(708)', shape='box', style='rounded,bold')

    # Mode boundary
    dot.node('boundary', 'MODE BOUNDARY (710)', shape='plaintext', fontsize='10')

    # Autonomous mode components
    with dot.subgraph(name='cluster_autonomous') as s:
        s.attr(label='AUTONOMOUS MODE', style='rounded,dashed')
        s.node('input_gen', 'Input\nGenerator\n(712)')
        s.node('energy_mod', 'Energy\nModulation\n(4-zone)\n(714)')

    # Resync feedback
    dot.node('resync', 'Resync\nFeedback\n(720)', shape='parallelogram')

    # Connected path
    dot.edge('claude', 'claude_input')
    dot.edge('claude_input', 'input_switch')
    dot.edge('claude', 'mod_switch', style='dashed', label='cognitive\nmodulation')

    # Autonomous path
    dot.edge('input_gen', 'input_switch', style='dashed')
    dot.edge('energy_mod', 'mod_switch', style='dashed')

    # Core data path
    dot.edge('input_switch', 'snn_core', label='selected\ninput')
    dot.edge('mod_switch', 'snn_core', label='selected\nmodulation')
    dot.edge('snn_core', 'motor', label='neural\noutput')
    dot.edge('motor', 'actuator')

    # Resync feedback
    dot.edge('snn_core', 'resync', label='state data', style='dotted')
    dot.edge('resync', 'claude', label='resync()\npayload', style='dotted', constraint='false')

    return dot


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

ALL_DIAGRAMS = {
    'a': [
        ('fig1_system_overview', patent_a_fig1_system_overview),
        ('fig2_energy_loop', patent_a_fig2_energy_loop),
        ('fig3_method_flowchart', patent_a_fig3_method_flowchart),
    ],
    'b': [
        ('fig1_reflection', patent_b_fig1_reflection),
        ('fig1_reflection', patent_b_fig1_reflection),
        ('fig2_spectrum', patent_b_fig2_spectrum),
        ('fig3_stdp', patent_b_fig3_stdp),
    ],
    'c': [
        ('fig1_architecture', patent_c_fig1_architecture),
        ('fig2_state_machine', patent_c_fig2_state_machine),
        ('fig3_energy_modulation', patent_c_fig3_energy_modulation),
        ('fig4_input_generator', patent_c_fig4_input_generator),
        ('fig5_resync_payload', patent_c_fig5_resync_payload),
        ('fig6_recovery_timelines', patent_c_fig6_recovery_timelines),
        ('fig7_signal_flow', patent_c_fig7_signal_flow),
    ],
}
# Fix duplicate in patent_b
ALL_DIAGRAMS['b'] = [
    ('fig1_reflection', patent_b_fig1_reflection),
    ('fig2_spectrum', patent_b_fig2_spectrum),
    ('fig3_stdp', patent_b_fig3_stdp),
]


def generate(patents, fmt):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for patent_key in patents:
        patent_dir = os.path.join(OUTPUT_DIR, f'patent_{patent_key}')
        os.makedirs(patent_dir, exist_ok=True)

        diagrams = ALL_DIAGRAMS[patent_key]
        for name, fn in diagrams:
            dot = fn()
            filepath = os.path.join(patent_dir, name)

            # Always save DOT source
            dot_path = filepath + '.dot'
            with open(dot_path, 'w') as f:
                f.write(dot.source)
            print(f'  DOT source: {dot_path}')

            # Try to render if Graphviz binary is available
            try:
                dot.render(filepath, format=fmt, cleanup=True)
                print(f'  Rendered:   {filepath}.{fmt}')
            except graphviz.backend.execute.ExecutableNotFound:
                print(f'  [skip render] Graphviz "dot" binary not found — DOT source saved')

    print(f'\nReference Numbers:')
    print(f'  Patent A: 10-40 (energy loop), 100-116 (8-layer system), 200-260 (method)')
    print(f'  Patent B: 10-60 (reflection arch), 70-76 (spectrum), 80-88 (STDP)')
    print(f'  Patent C: 100-114 (architecture), 200-216 (state machine), 300-314 (energy mod),')
    print(f'            400-406 (input gen), 500-508 (resync payload), 600-606 (recovery), 700-720 (signal flow)')


def main():
    parser = argparse.ArgumentParser(description='Generate patent diagrams using Graphviz')
    parser.add_argument('--format', '-f', default='svg', choices=['svg', 'png', 'pdf'],
                        help='Output format (default: svg)')
    parser.add_argument('--patent', '-p', default='all', choices=['a', 'b', 'c', 'all'],
                        help='Which patent to generate (default: all)')
    args = parser.parse_args()

    patents = ['a', 'b', 'c'] if args.patent == 'all' else [args.patent]

    print(f'Generating patent diagrams (format={args.format})...\n')
    generate(patents, args.format)
    print('\nDone.')


if __name__ == '__main__':
    main()

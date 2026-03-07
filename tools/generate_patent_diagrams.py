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

def patent_c_fig1_fallback():
    """FIG. 1 — Fallback System Architecture."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentC_Fig1', comment='Cognitive Fallback Architecture')
    dot.attr(rankdir='TB', label='FIG. 1', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    dot.node('claude', 'Cognitive\nControl Layer\n(10)', shape='ellipse')
    dot.node('heartbeat', 'Heartbeat\nMonitor\n(20)')
    dot.node('snn', 'SNN +\nPhysics Loop\n(30)')
    dot.node('auto', 'Autonomous\nRunner\n(40)')
    dot.node('buffer', 'State\nBuffer\n(50)', shape='cylinder')
    dot.node('snapshot', 'Persistent\nSnapshot\n(60)', shape='cylinder')

    dot.edge('claude', 'heartbeat', label='tool calls\n(every <30s)')
    dot.edge('heartbeat', 'snn', label='active mode')
    dot.edge('heartbeat', 'auto', label='timeout\n>30s', style='dashed')
    dot.edge('auto', 'snn', label='self-regulated\ninput')
    dot.edge('snn', 'buffer', label='step data')
    dot.edge('auto', 'snapshot', label='every 50\nsteps')

    return dot


def patent_c_fig2_method():
    """FIG. 2 — Fallback Method Flowchart."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentC_Fig2', comment='Fallback Method')
    dot.attr(rankdir='TB', label='FIG. 2', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    dot.node('start', 'Start\n(300)', shape='ellipse')
    dot.node('s1', 'S1: Monitor\nHeartbeat\n(310)')
    dot.node('d1', 'Timeout\n>30s?\n(320)', shape='diamond')
    dot.node('s2', 'S2: Engage\nAutonomous Runner\n(330)')
    dot.node('s3', 'S3: Generate\nSelf-Regulating Input\n(340)')
    dot.node('d2', 'Energy\nLevel?\n(350)', shape='diamond')
    dot.node('s4a', 'Modulation\n-0.4 (conserve)\n(352)')
    dot.node('s4b', 'Modulation\n0.0 (neutral)\n(354)')
    dot.node('s4c', 'Modulation\n+0.3 (spend)\n(356)')
    dot.node('s5', 'S5: Buffer\nStep Data\n(360)')
    dot.node('d3', 'Reconnected?\n(370)', shape='diamond')
    dot.node('s6', 'S6: Resync\nPayload\n(380)')
    dot.node('end', 'Resume\nCognitive Control\n(390)', shape='ellipse')

    dot.edge('start', 's1')
    dot.edge('s1', 'd1')
    dot.edge('d1', 's1', label='No')
    dot.edge('d1', 's2', label='Yes')
    dot.edge('s2', 's3')
    dot.edge('s3', 'd2')
    dot.edge('d2', 's4a', label='<15 mWh')
    dot.edge('d2', 's4b', label='15-80 mWh')
    dot.edge('d2', 's4c', label='>80 mWh')
    dot.edge('s4a', 's5')
    dot.edge('s4b', 's5')
    dot.edge('s4c', 's5')
    dot.edge('s5', 'd3')
    dot.edge('d3', 's3', label='No', style='dashed')
    dot.edge('d3', 's6', label='Yes')
    dot.edge('s6', 'end')

    return dot


def patent_c_fig3_resync():
    """FIG. 3 — Resynchronization Protocol."""
    attrs = patent_style_attrs()
    dot = graphviz.Digraph('PatentC_Fig3', comment='Resync Protocol')
    dot.attr(rankdir='LR', label='FIG. 3', labelloc='t', **attrs['graph'])
    dot.attr('node', **attrs['node'])
    dot.attr('edge', **attrs['edge'])

    dot.node('buffer', 'Autonomy\nBuffer\n(50)', shape='cylinder')
    dot.node('summary', 'Summary\nStatistics\n(52)')
    dot.node('delta', 'Energy\nDelta\n(54)')
    dot.node('payload', 'Resync\nPayload\n(56)')
    dot.node('cognitive', 'Cognitive\nLayer\n(10)', shape='ellipse')

    dot.edge('buffer', 'summary', label='compute')
    dot.edge('buffer', 'delta', label='compute')
    dot.edge('summary', 'payload')
    dot.edge('delta', 'payload')
    dot.edge('payload', 'cognitive', label='transmit')

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
        ('fig1_fallback', patent_c_fig1_fallback),
        ('fig2_method', patent_c_fig2_method),
        ('fig3_resync', patent_c_fig3_resync),
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
    print(f'  Patent C: 10-60 (fallback arch), 300-390 (method), 50-56 (resync)')


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

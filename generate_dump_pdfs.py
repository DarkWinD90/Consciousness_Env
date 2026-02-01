#!/usr/bin/env python3
"""
Generate three PDF dump files for Consciousness_Env:
  1. Repository_Dump.pdf    — Complete source code listing
  2. Falsifiable_Claims.pdf — All validated claims (Phases 7-10)
  3. Patent_Figures_All.pdf — All 21 patent SVG figures in one PDF
"""

import os
import sys
import glob
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Preformatted, KeepTogether, HRFlowable, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register DejaVu Mono for code
pdfmetrics.registerFont(TTFont('DejaVuMono', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuMono-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

ROOT = os.path.dirname(os.path.abspath(__file__))

# ════════════════════════════════════════════════════════════════════
# Styles
# ════════════════════════════════════════════════════════════════════

styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    'DumpTitle', parent=styles['Title'],
    fontName='DejaVuSans-Bold', fontSize=18, spaceAfter=6,
)
SUBTITLE_STYLE = ParagraphStyle(
    'DumpSubtitle', parent=styles['Normal'],
    fontName='DejaVuSans', fontSize=10, textColor=HexColor('#555555'),
    spaceAfter=20, alignment=TA_CENTER,
)
HEADING_STYLE = ParagraphStyle(
    'DumpHeading', parent=styles['Heading2'],
    fontName='DejaVuSans-Bold', fontSize=12, spaceBefore=16, spaceAfter=8,
    textColor=HexColor('#1a1a1a'),
)
SUBHEADING_STYLE = ParagraphStyle(
    'DumpSubheading', parent=styles['Heading3'],
    fontName='DejaVuSans-Bold', fontSize=10, spaceBefore=12, spaceAfter=4,
    textColor=HexColor('#333333'),
)
CODE_STYLE = ParagraphStyle(
    'DumpCode', parent=styles['Code'],
    fontName='DejaVuMono', fontSize=6.5, leading=8.5,
    leftIndent=0, rightIndent=0,
    textColor=black, backColor=HexColor('#f5f5f5'),
    borderPadding=4,
)
BODY_STYLE = ParagraphStyle(
    'DumpBody', parent=styles['Normal'],
    fontName='DejaVuSans', fontSize=9, leading=12,
    spaceAfter=6,
)
TABLE_HEADER_STYLE = ParagraphStyle(
    'TableHeader', parent=styles['Normal'],
    fontName='DejaVuSans-Bold', fontSize=8, leading=10,
    textColor=white,
)
TABLE_CELL_STYLE = ParagraphStyle(
    'TableCell', parent=styles['Normal'],
    fontName='DejaVuSans', fontSize=8, leading=10,
)
PASS_STYLE = ParagraphStyle(
    'PassCell', parent=styles['Normal'],
    fontName='DejaVuSans-Bold', fontSize=8, leading=10,
    textColor=HexColor('#006600'),
)
FILENAME_STYLE = ParagraphStyle(
    'FileName', parent=styles['Normal'],
    fontName='DejaVuMono-Bold', fontSize=9, leading=12,
    textColor=HexColor('#0055aa'), spaceBefore=14, spaceAfter=4,
)


def safe_text(text):
    """Escape XML special characters for reportlab Paragraphs."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


# ════════════════════════════════════════════════════════════════════
# 1. REPOSITORY DUMP PDF
# ════════════════════════════════════════════════════════════════════

def generate_repo_dump():
    """Generate complete repository source code listing."""
    outpath = os.path.join(ROOT, 'Repository_Dump.pdf')
    doc = SimpleDocTemplate(
        outpath, pagesize=letter,
        leftMargin=0.6*inch, rightMargin=0.6*inch,
        topMargin=0.7*inch, bottomMargin=0.7*inch,
    )
    story = []

    # Title page
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph('Consciousness_Env', TITLE_STYLE))
    story.append(Paragraph('Complete Repository Source Code Dump', SUBTITLE_STYLE))
    story.append(Spacer(1, 0.3*inch))

    # File inventory
    file_groups = [
        ('Core Modules', 'core/', [
            '__init__.py', 'base_snn.py', 'energy.py', 'thermochromic.py',
            'history.py', 'predictive.py', 'multimodal.py',
            'claude_interface.py', 'neural_router.py',
            'consciousness_enhancer.py', 'enhanced_consciousness.py',
        ]),
        ('Phase Validation Scripts', 'phases/', [
            '__init__.py',
            'phase1_optical_sensing.py', 'phase2_neuromorphic_processing.py',
            'phase3_closed_loop_feedback.py', 'phase4_energy_harvesting.py',
            'phase5_adaptive_membrane.py', 'phase6_recursive_reflection.py',
            'phase7_control_baseline.py', 'phase7_full_integration.py',
            'phase8_stdp.py', 'phase9_predictive_processing.py',
            'phase10_multimodal.py',
        ]),
        ('MCP Servers', 'mcp/', [
            '__init__.py', 'consciousness_mcp_server.py', 'consciousness_server.py',
        ]),
        ('Appendices', 'appendices/', [
            '__init__.py', 'appendix_a_base_simulation.py',
            'appendix_b_system_graph.py', 'appendix_c_recursive_reflection.py',
        ]),
        ('Tests', 'tests/', [
            '__init__.py', 'run_200_step_test.py',
            'test_code_simplifier.py', 'test_phase7_metrics.py',
        ]),
        ('Tools', 'tools/', ['__init__.py', 'code_simplifier.py']),
        ('Root Scripts', '', [
            'consciousness_cli.py', 'setup.py',
            'generate_patent_a_drawings.py', 'generate_patent_b_drawings.py',
            'generate_patent_c_drawings.py', 'export_drawings_pdf.py',
        ]),
        ('Configuration', '', [
            'CLAUDE.md', 'requirements.txt', 'MANIFEST.in',
            '.gitignore', '.mcp.json', 'environment.yml',
        ]),
    ]

    # Table of contents
    story.append(Paragraph('Table of Contents', HEADING_STYLE))
    toc_lines = []
    file_count = 0
    for group_name, prefix, files in file_groups:
        toc_lines.append(f'<b>{safe_text(group_name)}</b>')
        for f in files:
            filepath = os.path.join(prefix, f) if prefix else f
            toc_lines.append(f'  {safe_text(filepath)}')
            file_count += 1
    story.append(Preformatted('\n'.join(toc_lines), CODE_STYLE))
    story.append(Paragraph(f'<b>{file_count} files total</b>', BODY_STYLE))
    story.append(PageBreak())

    # Dump each file
    for group_name, prefix, files in file_groups:
        story.append(Paragraph(group_name, HEADING_STYLE))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))

        for fname in files:
            filepath = os.path.join(prefix, fname) if prefix else fname
            fullpath = os.path.join(ROOT, filepath)

            story.append(Paragraph(safe_text(filepath), FILENAME_STYLE))

            if os.path.exists(fullpath):
                try:
                    with open(fullpath, 'r', encoding='utf-8', errors='replace') as fh:
                        content = fh.read()
                    if len(content) == 0:
                        content = '(empty file)'

                    # Add line numbers
                    lines = content.split('\n')
                    numbered = []
                    for i, line in enumerate(lines, 1):
                        num = f'{i:4d}'
                        numbered.append(f'{num}  {safe_text(line)}')
                    numbered_text = '\n'.join(numbered)

                    story.append(Preformatted(numbered_text, CODE_STYLE))
                except Exception as e:
                    story.append(Paragraph(f'Error reading file: {e}', BODY_STYLE))
            else:
                story.append(Paragraph(f'(file not found: {filepath})', BODY_STYLE))

            story.append(Spacer(1, 8))

        story.append(PageBreak())

    doc.build(story)
    print(f'[1/3] Repository dump: {outpath}')
    return outpath


# ════════════════════════════════════════════════════════════════════
# 2. FALSIFIABLE CLAIMS PDF
# ════════════════════════════════════════════════════════════════════

def generate_claims_dump():
    """Generate falsifiable claims reference document."""
    outpath = os.path.join(ROOT, 'Falsifiable_Claims.pdf')
    doc = SimpleDocTemplate(
        outpath, pagesize=letter,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch,
    )
    story = []

    # Title
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph('Consciousness_Env', TITLE_STYLE))
    story.append(Paragraph('Falsifiable Claims Registry', SUBTITLE_STYLE))
    story.append(Paragraph(
        'All validated claims across Phases 7-10 with thresholds, '
        'measured values, and control conditions.',
        BODY_STYLE
    ))
    story.append(Spacer(1, 0.3*inch))

    # Summary table
    story.append(Paragraph('Summary', HEADING_STYLE))
    summary_data = [
        [Paragraph('<b>Phase</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Claims</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Total</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Status</b>', TABLE_HEADER_STYLE)],
        [Paragraph('Phase 7: Control Baseline', TABLE_CELL_STYLE),
         Paragraph('A, B, C, D, E', TABLE_CELL_STYLE),
         Paragraph('5', TABLE_CELL_STYLE),
         Paragraph('ALL PASS', PASS_STYLE)],
        [Paragraph('Phase 8: STDP', TABLE_CELL_STYLE),
         Paragraph('F8.1, F8.2, F8.3', TABLE_CELL_STYLE),
         Paragraph('3', TABLE_CELL_STYLE),
         Paragraph('ALL PASS', PASS_STYLE)],
        [Paragraph('Phase 9: Predictive Processing', TABLE_CELL_STYLE),
         Paragraph('F9.1, F9.2, F9.3', TABLE_CELL_STYLE),
         Paragraph('3', TABLE_CELL_STYLE),
         Paragraph('ALL PASS', PASS_STYLE)],
        [Paragraph('Phase 10: Multi-Modal Integration', TABLE_CELL_STYLE),
         Paragraph('F10.1, F10.2, F10.3', TABLE_CELL_STYLE),
         Paragraph('3', TABLE_CELL_STYLE),
         Paragraph('ALL PASS', PASS_STYLE)],
    ]
    t = Table(summary_data, colWidths=[2.5*inch, 1.8*inch, 0.6*inch, 1.0*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f9f9f9')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))
    story.append(Paragraph('<b>Total: 14 claims, 14 PASS, 0 FAIL</b>', BODY_STYLE))
    story.append(PageBreak())

    # ── Phase 7 ──
    story.append(Paragraph('Phase 7: Control Baseline', HEADING_STYLE))
    story.append(Paragraph(
        'Validation script: <font face="DejaVuMono">phases/phase7_control_baseline.py</font><br/>'
        'Tag: <font face="DejaVuMono">v0.5.0-phase7-baseline</font> (7c369d8)',
        BODY_STYLE
    ))
    story.append(Paragraph(
        'The control baseline establishes 5 fundamental claims about the classical '
        'servo control loop. These claims must continue to PASS for all future phases.',
        BODY_STYLE
    ))

    p7_data = [
        [Paragraph('<b>Claim</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Criterion</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Threshold</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Measured</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Result</b>', TABLE_HEADER_STYLE)],
        [Paragraph('A', TABLE_CELL_STYLE),
         Paragraph('Closed-loop continuity', TABLE_CELL_STYLE),
         Paragraph('All channels 2000 pts', TABLE_CELL_STYLE),
         Paragraph('True', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
        [Paragraph('B', TABLE_CELL_STYLE),
         Paragraph('Boundedness', TABLE_CELL_STYLE),
         Paragraph('All states bounded', TABLE_CELL_STYLE),
         Paragraph('True', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
        [Paragraph('C', TABLE_CELL_STYLE),
         Paragraph('Robustness under noise', TABLE_CELL_STYLE),
         Paragraph('Std(theta) &lt;= 45 deg', TABLE_CELL_STYLE),
         Paragraph('9.89 deg', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
        [Paragraph('D', TABLE_CELL_STYLE),
         Paragraph('Input-output gain', TABLE_CELL_STYLE),
         Paragraph('corr(L, theta) &gt;= 0.2', TABLE_CELL_STYLE),
         Paragraph('0.993', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
        [Paragraph('E', TABLE_CELL_STYLE),
         Paragraph('Saturation ratio', TABLE_CELL_STYLE),
         Paragraph('sat_theta &lt;= 0.20', TABLE_CELL_STYLE),
         Paragraph('0.000', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
    ]
    t = Table(p7_data, colWidths=[0.5*inch, 1.6*inch, 1.6*inch, 1.0*inch, 0.6*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f9f9f9')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        '<b>Parameters:</b> N=2000 steps, period=200, sigma_L=50, '
        'Kp=0.3, Kd=0.4, m=1.0, c=0.5, k=1.0',
        BODY_STYLE
    ))
    story.append(PageBreak())

    # ── Phase 8 ──
    story.append(Paragraph('Phase 8: Spike-Timing Dependent Plasticity (STDP)', HEADING_STYLE))
    story.append(Paragraph(
        'Validation script: <font face="DejaVuMono">phases/phase8_stdp.py</font><br/>'
        'Tag: <font face="DejaVuMono">v1.0.0-phase8-stdp</font> (80cf3e5)',
        BODY_STYLE
    ))
    story.append(Paragraph(
        'STDP enables the SNN to learn temporal correlations. Control: frozen weights '
        'with identical input and seed.',
        BODY_STYLE
    ))

    p8_data = [
        [Paragraph('<b>Claim</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Criterion</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Threshold</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Measured</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Result</b>', TABLE_HEADER_STYLE)],
        [Paragraph('F8.1', TABLE_CELL_STYLE),
         Paragraph('Weight entropy decreases', TABLE_CELL_STYLE),
         Paragraph('H_final &lt; H_initial', TABLE_CELL_STYLE),
         Paragraph('2.95 to 2.02 bits', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
        [Paragraph('F8.2', TABLE_CELL_STYLE),
         Paragraph('STDP MI &gt; frozen MI', TABLE_CELL_STYLE),
         Paragraph('ratio &gt; 1.20x', TABLE_CELL_STYLE),
         Paragraph('6.50x', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
        [Paragraph('F8.3', TABLE_CELL_STYLE),
         Paragraph('Weight convergence', TABLE_CELL_STYLE),
         Paragraph('late/early &lt; 0.10', TABLE_CELL_STYLE),
         Paragraph('0.0000', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
    ]
    t = Table(p8_data, colWidths=[0.5*inch, 1.6*inch, 1.4*inch, 1.2*inch, 0.6*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f9f9f9')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        '<b>Parameters:</b> N=1000, neurons=10, threshold=0.3, weight_scale=0.2, '
        'A+=0.005, A-=0.006, tau=20, seed=42',
        BODY_STYLE
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        '<b>Control:</b> Same network with stdp_enabled=False (frozen weights), '
        'same input sequence, same random seed.',
        BODY_STYLE
    ))
    story.append(PageBreak())

    # ── Phase 9 ──
    story.append(Paragraph('Phase 9: Predictive Processing', HEADING_STYLE))
    story.append(Paragraph(
        'Validation script: <font face="DejaVuMono">phases/phase9_predictive_processing.py</font><br/>'
        'Tag: <font face="DejaVuMono">v2.0.0-phase9-predictive</font> (4baa21f)',
        BODY_STYLE
    ))
    story.append(Paragraph(
        'Dual-pathway system predicts the next input signal. Prediction error is the '
        'learning signal. Control: frozen readout weights, STDP disabled.',
        BODY_STYLE
    ))

    p9_data = [
        [Paragraph('<b>Claim</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Criterion</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Threshold</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Measured</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Result</b>', TABLE_HEADER_STYLE)],
        [Paragraph('F9.1', TABLE_CELL_STYLE),
         Paragraph('Error reduction (periodic)', TABLE_CELL_STYLE),
         Paragraph('&gt;50% cycle 1 to 10', TABLE_CELL_STYLE),
         Paragraph('63.9%', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
        [Paragraph('F9.2', TABLE_CELL_STYLE),
         Paragraph('No learning on random', TABLE_CELL_STYLE),
         Paragraph('p &gt; 0.05', TABLE_CELL_STYLE),
         Paragraph('p = 0.6919', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
        [Paragraph('F9.3', TABLE_CELL_STYLE),
         Paragraph('Spike + recovery on switch', TABLE_CELL_STYLE),
         Paragraph('peak &gt; 1.3x pre', TABLE_CELL_STYLE),
         Paragraph('1.51x, recovered', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
    ]
    t = Table(p9_data, colWidths=[0.5*inch, 1.6*inch, 1.4*inch, 1.2*inch, 0.6*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f9f9f9')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        '<b>Parameters:</b> N=2000, neurons=10, threshold=0.5, weight_scale=0.1, '
        'buffer=100, readout_lr=0.05, decay=0.999, seed=42',
        BODY_STYLE
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        '<b>Control:</b> learning_enabled=False (frozen readout weights, STDP disabled). '
        'Prediction stays at initial bias (0.5).',
        BODY_STYLE
    ))
    story.append(PageBreak())

    # ── Phase 10 ──
    story.append(Paragraph('Phase 10: Multi-Modal Sensory Integration', HEADING_STYLE))
    story.append(Paragraph(
        'Validation script: <font face="DejaVuMono">phases/phase10_multimodal.py</font><br/>'
        'Tag: <font face="DejaVuMono">v3.0.0-phase10-multimodal</font> (9e2c333)',
        BODY_STYLE
    ))
    story.append(Paragraph(
        'Three independent SNN populations (light, sound, pressure) connected by cross-modal '
        'weight matrices with STDP. Broadcast input injection for input-driven spike timing.',
        BODY_STYLE
    ))

    p10_data = [
        [Paragraph('<b>Claim</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Criterion</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Threshold</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Measured</b>', TABLE_HEADER_STYLE),
         Paragraph('<b>Result</b>', TABLE_HEADER_STYLE)],
        [Paragraph('F10.1', TABLE_CELL_STYLE),
         Paragraph('Sync: simultaneous &gt; offset', TABLE_CELL_STYLE),
         Paragraph('difference &gt; 0.20', TABLE_CELL_STYLE),
         Paragraph('0.6974', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
        [Paragraph('F10.2', TABLE_CELL_STYLE),
         Paragraph('Weight entropy decreases', TABLE_CELL_STYLE),
         Paragraph('H_final &lt; H_initial', TABLE_CELL_STYLE),
         Paragraph('2.31 to 0.00 bits', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
        [Paragraph('F10.3', TABLE_CELL_STYLE),
         Paragraph('Weight convergence', TABLE_CELL_STYLE),
         Paragraph('late/early &lt; 0.20', TABLE_CELL_STYLE),
         Paragraph('0.1775', TABLE_CELL_STYLE),
         Paragraph('PASS', PASS_STYLE)],
    ]
    t = Table(p10_data, colWidths=[0.5*inch, 1.7*inch, 1.3*inch, 1.2*inch, 0.6*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f9f9f9')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        '<b>Parameters:</b> N=2000, neurons=10, threshold=0.8, weight_scale=0.05, '
        'input_scale=0.5 (broadcast), cross_a+=0.001, cross_a-=0.0012, cross_w_max=0.2, seed=42',
        BODY_STYLE
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        '<b>Control (F10.1):</b> Same inputs with 50-step phase offsets between modalities. '
        'Offset produces negative inter-population correlation (-0.15).',
        BODY_STYLE
    ))
    story.append(Paragraph(
        '<b>Control (F10.2):</b> cross_stdp_enabled=False. Frozen weights stay at random '
        'initialization (entropy 2.31 bits, unchanged).',
        BODY_STYLE
    ))
    story.append(PageBreak())

    # ── Reproducibility ──
    story.append(Paragraph('Reproducibility', HEADING_STYLE))
    story.append(Paragraph(
        'Every validated state is pinned by an annotated git tag. '
        'To reproduce any phase exactly:',
        BODY_STYLE
    ))
    repro_code = (
        'git fetch origin --tags\n'
        'git checkout v0.5.0-phase7-baseline    # Phase 7\n'
        'git checkout v1.0.0-phase8-stdp        # Phase 8\n'
        'git checkout v2.0.0-phase9-predictive  # Phase 9\n'
        'git checkout v3.0.0-phase10-multimodal # Phase 10\n'
        '\n'
        '# Run all validations:\n'
        'python phases/phase7_control_baseline.py\n'
        'python phases/phase8_stdp.py\n'
        'python phases/phase9_predictive_processing.py\n'
        'python phases/phase10_multimodal.py'
    )
    story.append(Preformatted(repro_code, CODE_STYLE))

    doc.build(story)
    print(f'[2/3] Falsifiable claims: {outpath}')
    return outpath


# ════════════════════════════════════════════════════════════════════
# 3. ALL PATENT FIGURES PDF
# ════════════════════════════════════════════════════════════════════

def generate_figures_pdf():
    """Generate all 21 patent figures in one clean PDF."""
    outpath = os.path.join(ROOT, 'Patent_Figures_All.pdf')

    # Check for cairosvg
    try:
        import cairosvg
    except ImportError:
        print('[3/3] SKIPPED: cairosvg not available for SVG rendering')
        return None

    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Image, Spacer, PageBreak, Paragraph
    import tempfile

    doc = SimpleDocTemplate(
        outpath, pagesize=letter,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch,
    )
    story = []

    # Title page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph('Consciousness_Env', TITLE_STYLE))
    story.append(Paragraph('Patent Drawings — All Figures', SUBTITLE_STYLE))
    story.append(Paragraph(
        'Patent A: Self-Sustaining Neural-Motor Energy Harvesting Loop (8 figures)<br/>'
        'Patent B: Configurable Recursive Self-Observation (6 figures)<br/>'
        'Patent C: Cognitive Fallback with Autonomous Self-Regulation (7 figures)',
        BODY_STYLE
    ))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph('<b>21 figures total — USPTO 37 CFR 1.84 compliant</b>', BODY_STYLE))
    story.append(PageBreak())

    patents = [
        ('Patent A: Self-Sustaining Neural-Motor Energy Harvesting Loop',
         'patent_a', 8),
        ('Patent B: Configurable Recursive Self-Observation',
         'patent_b', 6),
        ('Patent C: Cognitive Fallback with Autonomous Self-Regulation',
         'patent_c', 7),
    ]

    tmpdir = tempfile.mkdtemp()

    for patent_title, subdir, num_figs in patents:
        story.append(Paragraph(patent_title, HEADING_STYLE))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        story.append(Spacer(1, 0.2*inch))

        for fig_num in range(1, num_figs + 1):
            svg_path = os.path.join(ROOT, 'patent_drawings', subdir, f'fig{fig_num}.svg')
            if not os.path.exists(svg_path):
                story.append(Paragraph(f'Missing: {svg_path}', BODY_STYLE))
                continue

            # Convert SVG to PNG
            png_path = os.path.join(tmpdir, f'{subdir}_fig{fig_num}.png')
            try:
                cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=200)
            except Exception as e:
                story.append(Paragraph(f'Error rendering {subdir}/fig{fig_num}.svg: {e}', BODY_STYLE))
                continue

            # Figure label
            story.append(Paragraph(
                f'<b>FIG. {fig_num}</b>',
                ParagraphStyle('FigLabel', parent=BODY_STYLE, alignment=TA_CENTER,
                               fontName='DejaVuSans-Bold', fontSize=10)
            ))

            # Add image, sized to fit page
            page_w = letter[0] - 1.5*inch
            page_h = letter[1] - 2.5*inch  # leave room for label + margins

            img = Image(png_path)
            iw, ih = img.drawWidth, img.drawHeight
            scale = min(page_w / iw, page_h / ih, 1.0)
            img.drawWidth = iw * scale
            img.drawHeight = ih * scale
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(PageBreak())

    doc.build(story)

    # Cleanup temp files
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)

    print(f'[3/3] Patent figures: {outpath}')
    return outpath


# ════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('Generating PDF dump files...')
    print()
    repo_pdf = generate_repo_dump()
    claims_pdf = generate_claims_dump()
    figures_pdf = generate_figures_pdf()
    print()
    print('=' * 60)
    print('DONE — Generated files:')
    if repo_pdf:
        size = os.path.getsize(repo_pdf) / 1024
        print(f'  {os.path.basename(repo_pdf):30s} ({size:.0f} KB)')
    if claims_pdf:
        size = os.path.getsize(claims_pdf) / 1024
        print(f'  {os.path.basename(claims_pdf):30s} ({size:.0f} KB)')
    if figures_pdf:
        size = os.path.getsize(figures_pdf) / 1024
        print(f'  {os.path.basename(figures_pdf):30s} ({size:.0f} KB)')
    print('=' * 60)

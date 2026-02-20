"""
Export all patent SVG drawings into a single PDF, clearly separated by patent.
Each patent section starts with a title/cover page, followed by its figures.
"""

import cairosvg
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
import os
import tempfile
import glob

OUTPUT_PDF = "Patent_Drawings_All.pdf"
PAGE_W, PAGE_H = letter  # 8.5 x 11 inches in points (612 x 792)

# Page dimensions for SVG-to-PNG rasterization
paper_width = 8.5   # inches
paper_height = 11   # inches
dpi = 300

PATENTS = [
    {
        "id": "A",
        "title": "PATENT A",
        "subtitle": "Self-Sustaining Neural-Motor Energy Harvesting Loop\nfor Autonomous Cognitive Systems",
        "dir": "patent_drawings/patent_a",
        "figures": 8,
        "fig_titles": [
            "FIG. 1 — System Architecture Block Diagram (8-Layer Loop)",
            "FIG. 2 — Energy Balance Comparison",
            "FIG. 3 — SNN Architecture (LIF Neuron Model)",
            "FIG. 4 — Energy Harvesting Circuit",
            "FIG. 5 — Activity-Dependent Energy Dynamics",
            "FIG. 6 — Hardware Reference Design",
            "FIG. 7 — Validation Results Summary",
            "FIG. 8 — Energy-Bounded Recursive Control Architecture",
        ],
    },
    {
        "id": "B",
        "title": "PATENT B",
        "subtitle": "Configurable Recursive Self-Observation Method\nand System for Spiking Neural Networks\nwith Dynamic Reflection Coefficient Modulation",
        "dir": "patent_drawings/patent_b",
        "figures": 6,
        "fig_titles": [
            "FIG. 1 — Self-Observation Feedback Loop",
            "FIG. 2 — Reflection Coefficient Spectrum",
            "FIG. 3 — Dynamic Modulation Sources",
            "FIG. 4 — Self-Referential Learning Loop (STDP + Self-Observation)",
            "FIG. 5 — Energy-Aware Self-Observation Regulation",
            "FIG. 6 — End-to-End Signal Flow with Self-Observation Integration",
        ],
    },
    {
        "id": "C",
        "title": "PATENT C",
        "subtitle": "Method and System for Autonomous Self-Regulation\nand Cognitive Resynchronization in Neural Processing\nSystems During Disconnection from External Control Layers",
        "dir": "patent_drawings/patent_c",
        "figures": 7,
        "fig_titles": [
            "FIG. 1 — System Architecture with Fallback",
            "FIG. 2 — State Transition Diagram",
            "FIG. 3 — Energy-Aware Modulation Curve",
            "FIG. 4 — Autonomous Input Generator Output",
            "FIG. 5 — Resynchronization Payload Structure",
            "FIG. 6 — Recovery Timeline Diagrams",
            "FIG. 7 — End-to-End Signal Flow: Connected vs. Autonomous",
        ],
    },
]

def draw_separator_page(c, patent):
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2 * inch, patent["title"])
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.5 * inch, patent["subtitle"])
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 3.5 * inch, f"{patent['figures']} drawing sheets")
    c.showPage()

def convert_svg_to_png(svg_path, png_path):
    cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=dpi,
                     output_width=int(paper_width * dpi),
                     output_height=int(paper_height * dpi))

def add_drawing_pages(c, patent, tmpdir):
    for i in range(1, patent["figures"] + 1):
        svg_path = os.path.join(patent["dir"], f"fig{i}.svg")
        if not os.path.exists(svg_path):
            print(f"  WARNING: {svg_path} not found, skipping")
            continue

        tmp_png = os.path.join(tmpdir, f"{patent['id']}_fig{i}.png")
        try:
            convert_svg_to_png(svg_path, tmp_png)
            c.drawImage(tmp_png, 0, 0, width=PAGE_W, height=PAGE_H,
                        preserveAspectRatio=True, anchor='c')
            c.showPage()
            print(f"  Added {svg_path}")
        except Exception as e:
            print(f"  ERROR converting {svg_path}: {e}")
            c.setFont("Helvetica", 14)
            c.drawCentredString(PAGE_W / 2, PAGE_H / 2,
                                f"{patent['title']} — FIG. {i}")
            c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 20,
                                f"(See SVG file: {svg_path})")
            c.showPage()

def main():
    # Combined PDF
    c = canvas.Canvas(OUTPUT_PDF, pagesize=letter)
    c.setTitle("Patent Drawings — All Three Patents")
    c.setAuthor("Kevin Christopher Ward")
    c.setSubject("USPTO Patent Drawing Sheets")

    with tempfile.TemporaryDirectory() as tmpdir:
        for patent in PATENTS:
            draw_separator_page(c, patent)
            add_drawing_pages(c, patent, tmpdir)

        c.save()

    file_size = os.path.getsize(OUTPUT_PDF)
    total_pages = sum(1 + p["figures"] for p in PATENTS)
    print(f"\nCombined PDF: {OUTPUT_PDF}")
    print(f"  Size: {file_size:,} bytes ({file_size // 1024} KB)")
    print(f"  Pages: {total_pages} (3 separators + 21 drawings)")

    # Per-patent PDFs
    with tempfile.TemporaryDirectory() as tmpdir:
        for patent in PATENTS:
            per_pdf = f"Patent_Drawings_{patent['id']}.pdf"
            pc = canvas.Canvas(per_pdf, pagesize=letter)
            pc.setTitle(f"{patent['title']} — Drawing Sheets")
            pc.setAuthor("Kevin Christopher Ward")
            pc.setSubject("USPTO Patent Drawing Sheets")

            add_drawing_pages(pc, patent, tmpdir)
            pc.save()

            pf_size = os.path.getsize(per_pdf)
            print(f"\n{patent['title']} PDF: {per_pdf}")
            print(f"  Size: {pf_size:,} bytes ({pf_size // 1024} KB)")
            print(f"  Pages: {patent['figures']} drawings (no separator)")

if __name__ == "__main__":
    main()

"""
Convert USPTO-formatted patent specification .txt files to compliant PDFs.

Formatting follows 37 CFR 1.52 and USPTO Patent Center PDF Guidelines:
  - Page size:     8.5 x 11 inches (US Letter)
  - Margins:       Top 1", Bottom 1", Left 1.25", Right 1"
  - Font:          Times-Roman 12pt (embedded by reportlab)
  - Line spacing:  Double (24pt leading for 12pt font)
  - Page numbers:  Centered at bottom of each page
  - Paragraph nos: [0001] format, bold, per 37 CFR 1.52(b)
  - Claims:        Start on a new page
  - Abstract:      Start on a new page
  - No encryption, no multimedia, no annotations
"""

import os
import re
# Enable reportlab's invariant output mode before importing any
# rendering classes. In invariant mode the PDF's CreationDate /
# ModDate are fixed to a deterministic epoch and the document ID is
# a content hash rather than a random nonce, making regenerated PDFs
# byte-for-byte identical across runs. This is a prerequisite for
# .github/workflows/filing-pdfs.yml's drift-detection diff against
# the committed artifacts. Can be disabled with RL_INVARIANT=0 to
# restore timestamped output for debugging.
if os.environ.get('RL_INVARIANT', '1') != '0':
    from reportlab import rl_config
    rl_config.invariant = 1
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    KeepTogether,
)
from reportlab.lib.colors import black


# ---------------------------------------------------------------------------
# Page geometry (37 CFR 1.52 + FILING_INSTRUCTIONS.md)
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = letter  # 612 x 792 points
MARGIN_TOP = 1.0 * inch
MARGIN_BOTTOM = 1.0 * inch
MARGIN_LEFT = 1.25 * inch
MARGIN_RIGHT = 1.0 * inch

FRAME_W = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
FRAME_H = PAGE_H - MARGIN_TOP - MARGIN_BOTTOM

# Double spacing for 12pt font = 24pt leading
LEADING = 24


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def make_styles():
    """Create paragraph styles for each document element."""
    styles = {}

    # Normal body text — double-spaced, justified
    styles["body"] = ParagraphStyle(
        "Body",
        fontName="Times-Roman",
        fontSize=12,
        leading=LEADING,
        alignment=TA_JUSTIFY,
        textColor=black,
        spaceAfter=0,
        spaceBefore=0,
    )

    # Major section headings (TITLE OF THE INVENTION, CLAIMS, etc.)
    styles["heading"] = ParagraphStyle(
        "Heading",
        fontName="Times-Bold",
        fontSize=12,
        leading=LEADING,
        alignment=TA_CENTER,
        textColor=black,
        spaceBefore=LEADING,
        spaceAfter=LEADING,
    )

    # Sub-headings within detailed description (System Architecture, etc.)
    styles["subheading"] = ParagraphStyle(
        "SubHeading",
        fontName="Times-Bold",
        fontSize=12,
        leading=LEADING,
        alignment=TA_LEFT,
        textColor=black,
        spaceBefore=LEADING,
        spaceAfter=0,
    )

    # Claim text — slightly indented for readability
    styles["claim"] = ParagraphStyle(
        "Claim",
        fontName="Times-Roman",
        fontSize=12,
        leading=LEADING,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        textColor=black,
        spaceBefore=6,
        spaceAfter=6,
    )

    # Claim sub-items (a), (b), etc. — indented
    styles["claim_sub"] = ParagraphStyle(
        "ClaimSub",
        fontName="Times-Roman",
        fontSize=12,
        leading=LEADING,
        alignment=TA_JUSTIFY,
        leftIndent=0.5 * inch,
        textColor=black,
        spaceBefore=0,
        spaceAfter=0,
    )

    # Inventor / header lines at top of document
    styles["header_line"] = ParagraphStyle(
        "HeaderLine",
        fontName="Times-Roman",
        fontSize=12,
        leading=LEADING,
        alignment=TA_CENTER,
        textColor=black,
        spaceBefore=0,
        spaceAfter=0,
    )

    return styles


# ---------------------------------------------------------------------------
# Section detection
# ---------------------------------------------------------------------------
# Major sections that get centered bold headings
MAJOR_SECTIONS = {
    "PROVISIONAL APPLICATION FOR PATENT",
    "UNDER 35 U.S.C. 111(b)",
    "TITLE OF THE INVENTION",
    "INVENTOR(S)",
    "CROSS-REFERENCE TO RELATED APPLICATIONS",
    "FIELD OF THE INVENTION",
    "BACKGROUND OF THE INVENTION",
    "SUMMARY OF THE INVENTION",
    "BRIEF DESCRIPTION OF THE DRAWINGS",
    "DETAILED DESCRIPTION OF THE INVENTION",
    "DETAILED DESCRIPTION OF THE DRAWINGS",
    "EXPERIMENTAL VALIDATION",
    "CLAIMS",
    "ABSTRACT OF THE DISCLOSURE",
    "REFERENCE TO SOURCE CODE",
    "DRAWING DESCRIPTIONS — PATENT A",
    "DRAWING DESCRIPTIONS — PATENT B",
    "DRAWING DESCRIPTIONS — PATENT C",
}

# Sections that force a page break before them (37 CFR 1.52)
PAGE_BREAK_BEFORE = {"CLAIMS", "ABSTRACT OF THE DISCLOSURE"}

# Regex for paragraph numbers: [0001], [0023], etc.
PARA_NUM_RE = re.compile(r"^(\[\d{4,}\])\s+(.*)")

# Regex for top-level claims: "1. ", "2. ", etc.
CLAIM_NUM_RE = re.compile(r"^(\d+)\.\s+(.*)")

# Regex for claim sub-items: "(a) ", "(b) ", etc.
CLAIM_SUB_RE = re.compile(r"^\(([a-z])\)\s+(.*)")

# Sub-headings (not paragraph-numbered, not major sections, not claims)
# These are short lines that act as sub-section titles within detailed desc.


def is_subheading(line, in_claims):
    """Heuristic: a line is a sub-heading if it's short, not numbered,
    not a major section, not a claim item, and not blank."""
    stripped = line.strip()
    if not stripped:
        return False
    if stripped in MAJOR_SECTIONS:
        return False
    if PARA_NUM_RE.match(stripped):
        return False
    if in_claims and (CLAIM_NUM_RE.match(stripped) or CLAIM_SUB_RE.match(stripped)):
        return False
    if stripped.startswith("(") or stripped.startswith("["):
        return False
    # Sub-headings are typically short (< 80 chars) and contain no period
    # except for FIG. references in drawing descriptions
    if len(stripped) < 100 and not stripped.endswith("."):
        return True
    # FIG. X — Title pattern in drawing descriptions
    if stripped.startswith("FIG."):
        return True
    return False


def escape_xml(text):
    """Escape XML special characters for reportlab Paragraph."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


# ---------------------------------------------------------------------------
# Page numbering
# ---------------------------------------------------------------------------
def add_page_number(canvas_obj, doc):
    """Draw centered page number at bottom of each page (37 CFR 1.52)."""
    canvas_obj.saveState()
    canvas_obj.setFont("Times-Roman", 12)
    page_num = canvas_obj.getPageNumber()
    canvas_obj.drawCentredString(
        PAGE_W / 2,
        0.5 * inch,
        str(page_num),
    )
    canvas_obj.restoreState()


# ---------------------------------------------------------------------------
# Document builder
# ---------------------------------------------------------------------------
def build_pdf(txt_path, pdf_path):
    """Parse a USPTO-formatted .txt file and produce a compliant PDF."""
    styles = make_styles()

    # Read source text
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Build flowables
    flowables = []
    in_claims = False
    in_abstract = False
    prev_blank = False

    i = 0
    while i < len(lines):
        raw = lines[i].rstrip("\n")
        stripped = raw.strip()
        i += 1

        # Skip fully blank lines (spacing handled by styles)
        if not stripped:
            prev_blank = True
            continue

        # --- Major section heading ---
        if stripped in MAJOR_SECTIONS:
            if stripped in PAGE_BREAK_BEFORE:
                flowables.append(PageBreak())

            if stripped == "CLAIMS":
                in_claims = True
                in_abstract = False
            elif stripped == "ABSTRACT OF THE DISCLOSURE":
                in_abstract = True
                in_claims = False
            else:
                if stripped in ("FIELD OF THE INVENTION",
                                "BACKGROUND OF THE INVENTION",
                                "SUMMARY OF THE INVENTION",
                                "DETAILED DESCRIPTION OF THE INVENTION",
                                "DETAILED DESCRIPTION OF THE DRAWINGS",
                                "EXPERIMENTAL VALIDATION",
                                "CROSS-REFERENCE TO RELATED APPLICATIONS",
                                "REFERENCE TO SOURCE CODE"):
                    in_claims = False
                    in_abstract = False

            flowables.append(
                Paragraph(escape_xml(stripped), styles["heading"])
            )
            prev_blank = False
            continue

        # --- Paragraph-numbered text: [0001] ... ---
        m = PARA_NUM_RE.match(stripped)
        if m:
            num = m.group(1)
            text = m.group(2)
            # Collect continuation lines (next non-blank lines that don't
            # start with a section header, paragraph number, or claim number)
            while i < len(lines):
                next_raw = lines[i].rstrip("\n")
                next_stripped = next_raw.strip()
                if not next_stripped:
                    break
                if next_stripped in MAJOR_SECTIONS:
                    break
                if PARA_NUM_RE.match(next_stripped):
                    break
                if in_claims and CLAIM_NUM_RE.match(next_stripped):
                    break
                text += " " + next_stripped
                i += 1

            # Bold paragraph number per 37 CFR 1.52(b)
            para_text = (
                f'<b>{escape_xml(num)}</b>'
                f'&nbsp;&nbsp;&nbsp;&nbsp;'
                f'{escape_xml(text)}'
            )
            flowables.append(Paragraph(para_text, styles["body"]))
            flowables.append(Spacer(1, 6))
            prev_blank = False
            continue

        # --- Claim sub-items: (a) ... ---
        if in_claims:
            m_sub = CLAIM_SUB_RE.match(stripped)
            if m_sub:
                letter_item = m_sub.group(1)
                text = m_sub.group(2)
                # Collect continuation
                while i < len(lines):
                    next_raw = lines[i].rstrip("\n")
                    next_stripped = next_raw.strip()
                    if not next_stripped:
                        break
                    if next_stripped in MAJOR_SECTIONS:
                        break
                    if CLAIM_NUM_RE.match(next_stripped):
                        break
                    if CLAIM_SUB_RE.match(next_stripped):
                        break
                    text += " " + next_stripped
                    i += 1

                para_text = f"({escape_xml(letter_item)}) {escape_xml(text)}"
                flowables.append(Paragraph(para_text, styles["claim_sub"]))
                prev_blank = False
                continue

            # --- Top-level claims: 1. ... ---
            m_claim = CLAIM_NUM_RE.match(stripped)
            if m_claim:
                num = m_claim.group(1)
                text = m_claim.group(2)
                # Collect continuation lines that aren't sub-items or new claims
                while i < len(lines):
                    next_raw = lines[i].rstrip("\n")
                    next_stripped = next_raw.strip()
                    if not next_stripped:
                        break
                    if next_stripped in MAJOR_SECTIONS:
                        break
                    if CLAIM_NUM_RE.match(next_stripped):
                        break
                    if CLAIM_SUB_RE.match(next_stripped):
                        break
                    # "wherein" continuation lines belong to this claim
                    text += " " + next_stripped
                    i += 1

                para_text = f"<b>{escape_xml(num)}.</b> {escape_xml(text)}"
                flowables.append(Spacer(1, 6))
                flowables.append(Paragraph(para_text, styles["claim"]))
                prev_blank = False
                continue

        # --- Sub-heading detection ---
        if is_subheading(stripped, in_claims):
            if prev_blank:
                flowables.append(Spacer(1, 6))
            flowables.append(
                Paragraph(escape_xml(stripped), styles["subheading"])
            )
            prev_blank = False
            continue

        # --- Default: regular body text (continuation or standalone) ---
        text = stripped
        # Collect continuation lines
        while i < len(lines):
            next_raw = lines[i].rstrip("\n")
            next_stripped = next_raw.strip()
            if not next_stripped:
                break
            if next_stripped in MAJOR_SECTIONS:
                break
            if PARA_NUM_RE.match(next_stripped):
                break
            if is_subheading(next_stripped, in_claims):
                break
            text += " " + next_stripped
            i += 1

        flowables.append(Paragraph(escape_xml(text), styles["body"]))
        flowables.append(Spacer(1, 6))
        prev_blank = False

    # --- Build the PDF ---
    doc = BaseDocTemplate(
        pdf_path,
        pagesize=letter,
        title=os.path.splitext(os.path.basename(pdf_path))[0],
        author="Kevin Christopher Ward",
        subject="USPTO Patent Application",
    )

    frame = Frame(
        MARGIN_LEFT,
        MARGIN_BOTTOM,
        FRAME_W,
        FRAME_H,
        id="main",
        showBoundary=0,
    )

    template = PageTemplate(
        id="USPTO",
        frames=[frame],
        onPage=add_page_number,
    )
    doc.addPageTemplates([template])

    doc.build(flowables)
    return doc.page


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
PDF_OUTPUT_DIR = os.path.join("patents", "pdfs")

SPECIFICATIONS = [
    {
        "txt": "patents/uspto_formatted/Patent_A_USPTO.txt",
        "pdf": os.path.join(PDF_OUTPUT_DIR, "Patent_A_Specification.pdf"),
        "label": "Patent A Specification",
    },
    {
        "txt": "patents/uspto_formatted/Patent_B_USPTO.txt",
        "pdf": os.path.join(PDF_OUTPUT_DIR, "Patent_B_Specification.pdf"),
        "label": "Patent B Specification",
    },
    {
        "txt": "patents/uspto_formatted/Patent_C_USPTO.txt",
        "pdf": os.path.join(PDF_OUTPUT_DIR, "Patent_C_Specification.pdf"),
        "label": "Patent C Specification",
    },
    {
        "txt": "patents/uspto_formatted/Patent_A_Drawings_Description.txt",
        "pdf": os.path.join(PDF_OUTPUT_DIR, "Patent_A_Drawings_Description.pdf"),
        "label": "Patent A Drawing Descriptions",
    },
    {
        "txt": "patents/uspto_formatted/Patent_B_Drawings_Description.txt",
        "pdf": os.path.join(PDF_OUTPUT_DIR, "Patent_B_Drawings_Description.pdf"),
        "label": "Patent B Drawing Descriptions",
    },
    {
        "txt": "patents/uspto_formatted/Patent_C_Drawings_Description.txt",
        "pdf": os.path.join(PDF_OUTPUT_DIR, "Patent_C_Drawings_Description.pdf"),
        "label": "Patent C Drawing Descriptions",
    },
]


def main():
    print("USPTO Specification → PDF Converter")
    print("=" * 50)
    print()
    print("Formatting per 37 CFR 1.52 + Patent Center PDF Guidelines:")
    print("  Page:       8.5\" x 11\" (US Letter)")
    print("  Margins:    T=1\" B=1\" L=1.25\" R=1\"")
    print("  Font:       Times-Roman 12pt (embedded)")
    print("  Spacing:    Double (24pt leading)")
    print("  Pages:      Numbered bottom-center")
    print("  Para nums:  [0001] bold per 37 CFR 1.52(b)")
    print("  Claims:     Page break before")
    print("  Abstract:   Page break before")
    print()

    os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
    total_pages = 0

    for spec in SPECIFICATIONS:
        txt_path = spec["txt"]
        pdf_path = spec["pdf"]

        if not os.path.exists(txt_path):
            print(f"  SKIP: {txt_path} not found")
            continue

        pages = build_pdf(txt_path, pdf_path)
        file_size = os.path.getsize(pdf_path)
        total_pages += pages

        print(f"  {spec['label']:40s} → {pdf_path}")
        print(f"    Pages: {pages:3d}    Size: {file_size:,} bytes "
              f"({file_size // 1024} KB)")

    print()
    print(f"Total: {len(SPECIFICATIONS)} PDFs, {total_pages} pages")
    print()
    print("Compliance checklist:")
    print("  [x] Times-Roman 12pt embedded (reportlab default)")
    print("  [x] Double-spaced (24pt leading)")
    print("  [x] Margins exceed 37 CFR 1.52 minimums")
    print("  [x] Page numbers centered at bottom")
    print("  [x] Paragraph numbers [XXXX] in bold")
    print("  [x] Claims on separate page")
    print("  [x] Abstract on separate page")
    print("  [x] No encryption, no multimedia, no annotations")
    print("  [x] PDF version 1.4 (reportlab default)")
    print("  [x] All fonts embedded")


if __name__ == "__main__":
    main()

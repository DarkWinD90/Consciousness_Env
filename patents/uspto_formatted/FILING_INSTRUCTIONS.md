# USPTO Filing Instructions — Step by Step

## Before You Start

### Determine Your Entity Status

**Micro Entity** ($65/application = $195 total) — You likely qualify if:
- [ ] You have NOT been named as inventor on more than 4 prior US patent applications
- [ ] Your gross income does not exceed $251,190
- [ ] You have NOT assigned/licensed the invention to a non-micro entity

**Small Entity** ($130/application = $390 total) — You qualify if:
- [ ] You are an individual OR a company with fewer than 500 employees
- [ ] You have NOT assigned/licensed to a large entity

If unsure, file as **small entity** to be safe.

---

## Step 1: Create a USPTO Account

1. Go to: https://patentcenter.uspto.gov
2. Click "Create Account"
3. Complete identity verification (required as of Sept 2025)
4. You will receive a Customer Number — save this

---

## Step 2: Convert Text Files to Properly Formatted PDFs

### For Each Patent (A, B, C):

Open the corresponding `Patent_X_USPTO.txt` file in **Microsoft Word**, **Google Docs**, or **LibreOffice Writer**.

Apply these settings:

**Page Setup:**
- Paper size: 8.5 x 11 inches (US Letter)
- Orientation: Portrait
- Top margin: 1 inch (2.54 cm)
- Bottom margin: 1 inch (2.54 cm)
- Left margin: 1.25 inches (3.18 cm)
- Right margin: 1 inch (2.54 cm)

**Font & Spacing:**
- Font: Times New Roman, 12 point
- Line spacing: Double (2.0)
- Paragraph spacing: 0 pt before, 0 pt after
- Color: Black text only

**Page Numbers:**
- Position: Bottom center
- Starting from page 1

**Section Breaks:**
- Abstract MUST start on a new page
- Claims MUST start on a new page

**Save/Export as PDF**

Name the files:
- `Patent_A_Specification.pdf`
- `Patent_B_Specification.pdf`
- `Patent_C_Specification.pdf`

---

## Step 3: Fill Out Cover Sheets (PTO/SB/16)

Download the form: https://www.uspto.gov/sites/default/files/documents/sb0016.pdf

Fill out ONE cover sheet per patent application. You will submit 3 total.

### Fields to Complete:

**Box 1 — DOCKET NUMBER:** (optional, for your tracking)
- Patent A: `CONSCIOUSNESS-2026-001`
- Patent B: `CONSCIOUSNESS-2026-002`
- Patent C: `CONSCIOUSNESS-2026-003`

**Box 2 — TITLE OF INVENTION:**
- Patent A: `Self-Sustaining Neural-Motor Energy Harvesting Loop for Autonomous Cognitive Systems`
- Patent B: `Configurable Recursive Self-Observation Method and System for Spiking Neural Networks with Dynamic Reflection Coefficient Modulation`
- Patent C: `Method and System for Autonomous Self-Regulation and Cognitive Resynchronization in Neural Processing Systems During Disconnection from External Control Layers`

**Box 3 — INVENTOR(S):**
- Given Name: [YOUR FIRST NAME]
- Family Name: [YOUR LAST NAME]
- City: [YOUR CITY]
- State: [YOUR STATE]
- Country: US
- (Add additional inventors if applicable)

**Box 4 — CORRESPONDENCE ADDRESS:**
- [YOUR FULL MAILING ADDRESS]
- Telephone: [YOUR PHONE]
- Email: [YOUR EMAIL]

**Box 5 — APPLICATION FILED BY:**
- Check: "Applicant is the inventor"

**Box 6 — ENTITY STATUS:**
- Check: "Micro Entity" or "Small Entity" (whichever applies)

**Box 7 — METHOD OF PAYMENT:**
- Will be handled during online submission

**Box 8 — RELATED APPLICATIONS:**
- Leave blank for first filing (cross-references are in the specification)

Save each completed cover sheet as PDF:
- `Patent_A_CoverSheet_SB16.pdf`
- `Patent_B_CoverSheet_SB16.pdf`
- `Patent_C_CoverSheet_SB16.pdf`

> **Note**: Pre-filled cover sheets already exist in the repository root. Review and verify they are correct before filing.

---

## Step 4: Prepare Drawing Sheets (Optional but Recommended)

Create simple black and white line drawings for each patent. You can use:
- **draw.io** (free, web-based) — https://app.diagrams.net
- **Microsoft PowerPoint** (export to PDF)
- **LibreOffice Draw** (free)
- **Any drawing tool** that exports to black & white PDF

### Drawing Format Requirements:
- Paper: 8.5 x 11 inches
- Top margin: 1 inch
- Left margin: 1 inch
- Right margin: 5/8 inch
- Bottom margin: 3/8 inch
- Black lines on white background only
- Label each figure: "FIG. 1", "FIG. 2", etc.
- Sheet numbers at top center: "1/7", "2/7", etc.
- NO frames or borders around drawing area

### Patent A Drawings (8 figures):
- FIG. 1: System Architecture Block Diagram (8-layer loop)
- FIG. 2: Energy Balance Comparison (control vs. experimental)
- FIG. 3: SNN Architecture (LIF neuron model)
- FIG. 4: Energy Harvesting Circuit (piezo + inductor + rectifier)
- FIG. 5: Activity-Dependent Energy Dynamics (sweet spot curve)
- FIG. 6: Hardware Reference Design (component layout)
- FIG. 7: Validation Results Summary (claims table)
- FIG. 8: Energy-Bounded Recursive Control Architecture

### Patent B Drawings (6 figures):
- FIG. 1: Self-Observation Feedback Loop
- FIG. 2: Reflection Coefficient Spectrum
- FIG. 3: Dynamic Modulation Sources
- FIG. 4: Self-Referential Learning Loop (STDP + self-observation)
- FIG. 5: Energy-Aware Self-Observation Regulation
- FIG. 6: End-to-End Signal Flow with Self-Observation Integration

### Patent C Drawings (7 figures):
- FIG. 1: System Architecture with Fallback
- FIG. 2: State Transition Diagram
- FIG. 3: Energy-Aware Modulation Curve
- FIG. 4: Autonomous Input Generator Output
- FIG. 5: Resynchronization Payload Structure
- FIG. 6: Recovery Timeline Diagrams
- FIG. 7: End-to-End Signal Flow (Connected vs. Autonomous)

The hand-illustrated SVG source files are in `patent_drawings/patent_a/`, `patent_drawings/patent_b/`, and `patent_drawings/patent_c/`. Before filing, export these SVGs to per-patent drawings PDFs (e.g. `Patent_A_Drawings.pdf`, `Patent_B_Drawings.pdf`, `Patent_C_Drawings.pdf`) using any SVG→PDF tool (Inkscape, CairoSVG, or browser print).

---

## Step 5: File Online via Patent Center

### For EACH of the 3 patents, repeat this process:

1. Go to: https://patentcenter.uspto.gov
2. Log in with your USPTO account
3. Click **"New Submission"** → **"Provisional Application"**
4. Upload your **Cover Sheet PDF** (PTO/SB/16) — e.g. `Patent_A_CoverSheet_SB16.pdf`
5. Upload your **Specification PDF** (the main patent document) — e.g. `Patent_A_Specification.pdf`
6. Upload your **Drawings Description PDF** — e.g. `Patent_A_Drawings_Description.pdf`
7. Upload your **Drawings PDF** — e.g. `Patent_A_Drawings.pdf` (exported from SVGs)
8. Select your **Entity Status** (Micro or Small)
9. If Micro Entity: you must also submit **Form PTO/SB/15A** — e.g. `Patent_A_MicroEntity_SB15A.pdf`
   - Pre-filled forms already exist in the repository root
   - Blank form: https://www.uspto.gov/sites/default/files/documents/sb0015a.pdf
10. Pay the filing fee:
    - Micro Entity: **$65**
    - Small Entity: **$130**
11. Review all documents for accuracy
12. Click **Submit**
13. **SAVE YOUR FILING RECEIPT** — it contains your Application Number

### Repeat for all 3 patents

---

## Step 6: After Filing

### Immediately:
- [ ] Save all 3 filing receipts
- [ ] Record application numbers
- [ ] Record confirmation numbers
- [ ] Save the filing date (should be February 2, 2026 if filing today)

### Update This Repository:
- [ ] Add application numbers to `CLAUDE.md` Section 10.2
- [ ] Commit updated CLAUDE.md with filing numbers
- [ ] Push to main

### Within 30 Days:
- [ ] Verify all 3 applications appear in Patent Center under "My Applications"
- [ ] Confirm entity status is correct
- [ ] Check for any USPTO notices or deficiency letters

### Within 12 Months (by February 2, 2027):
- [ ] Convert all 3 provisionals to non-provisional utility patents
- [ ] File PCT international application by January 15, 2027
- [ ] Build hardware prototype (Phase 11) for evidence
- [ ] Engage patent attorney for non-provisional preparation

---

## Cost Summary

### Option 1: Micro Entity
| Item | Cost |
|------|------|
| Patent A filing fee | $65 |
| Patent B filing fee | $65 |
| Patent C filing fee | $65 |
| **Total** | **$195** |

### Option 2: Small Entity
| Item | Cost |
|------|------|
| Patent A filing fee | $130 |
| Patent B filing fee | $130 |
| Patent C filing fee | $130 |
| **Total** | **$390** |

### Payment Methods Accepted:
- Credit/Debit Card
- Electronic Funds Transfer (EFT)
- USPTO Deposit Account (if you have one)

---

## File Checklist (Per Patent)

### Documents to Upload (per patent):
- [ ] PTO/SB/16 Cover Sheet — `Patent_X_CoverSheet_SB16.pdf`
- [ ] PTO/SB/15A Micro Entity Certification (if micro entity) — `Patent_X_MicroEntity_SB15A.pdf`
- [ ] Specification Document — `Patent_X_Specification.pdf`
- [ ] Drawings Description — `Patent_X_Drawings_Description.pdf`
- [ ] Drawing Sheets — `Patent_X_Drawings.pdf` (exported from SVGs in `patent_drawings/patent_x/`)

### Information You Need:
- [ ] Your full legal name
- [ ] Your city, state, country of residence
- [ ] Your mailing address
- [ ] Your phone number
- [ ] Your email address
- [ ] Credit card or payment information
- [ ] Docket numbers (optional, for your tracking)

---

## Troubleshooting

**Q: Patent Center won't let me log in?**
A: Identity verification is required as of September 2025. Call the Patent Electronic Business Center at 866-217-9197 (toll-free).

**Q: My PDF gets rejected?**
A: Check that it's text-based (not a scanned image), margins meet requirements, and font is a standard approved font.

**Q: The cover sheet won't load?**
A: Use the fillable PDF version from USPTO, not a third-party form. Open in Adobe Reader, not a browser.

**Q: I'm not sure about entity status?**
A: File as Small Entity ($130 each) — it's the safest option. You can claim Micro Entity later if you confirm eligibility.

**Q: Can I add information after filing?**
A: No. Provisional applications cannot be amended. Any new information must go in the non-provisional filing within 12 months.

**Q: What happens after filing?**
A: Nothing immediately. Provisionals are not examined. You get a filing receipt, application number, and 12-month priority window. You can use "Patent Pending" immediately after filing.

---

## Support

- **USPTO Patent Center**: https://patentcenter.uspto.gov
- **Phone**: 866-217-9197 (toll-free) or 571-272-4100
- **Hours**: 6 AM - 12 AM ET, Monday-Friday
- **Email**: ebc@uspto.gov

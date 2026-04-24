# Patent Drawings: Compare, Validate & Cross-Reference Findings Report

> **STALE — 2026-04-24.** This report was written on 2026-03-13 against
> validators that have since been audited and hardened (PR #151, PR #153).
> The hardened validators surface real compliance FAILs that were silently
> masked by prior false-negatives in `reference_validator`,
> `arrowhead_validator`, and `geometric_validator`. As of 2026-04-24, only
> 10 of the 21 drawings fully pass `full_compliance.py`; 11 figures carry
> geometric FAILs (G1 crossings, G2 arrow-gap, G4 segment overlaps, one
> G3 path-through-box, plus margin violations in `patent_a/fig4`).
>
> **Authoritative current-state snapshot:**
> [`docs/post_tool_sweep_2026-04-24.md`](../docs/post_tool_sweep_2026-04-24.md).
>
> **Audit trail of validator bug fixes:**
> [`docs/tooling_audit_2026-04-24.md`](../docs/tooling_audit_2026-04-24.md).
>
> This file is preserved verbatim below as a historical snapshot of the
> pre-audit state. A full regeneration of this report — with an honest
> "21 / 21 PASS" stamp — is blocked on completing the remaining per-figure
> drawing fixes tracked in PR #153.

---

**Date**: 2026-03-13
**Sources compared**: Google Drive `patent_drawings.zip` (Feb 10-23) vs repo `patent_drawings/` (Mar 12, commit `9fd82af`)

---

## 1. Comparison Matrix: Drive vs Repo (21 Figures)

All 21 SVGs are **complete rewrites** — not incremental edits. Two systematic changes were applied:
1. **Numeral migration**: Per-figure 100-series → unified 10-series even-increment scheme
2. **Compliance rewrite**: Restructured SVG layout, explicit `fill="black"`, `<g>` grouping

| Patent | Figure | Drive Lines | Repo Lines | Drive Numerals | Repo Numerals | Status |
|--------|--------|------------|-----------|----------------|---------------|--------|
| A | fig1 | 49 | 200 | 100-120 (100-series) | **100-120 (NOT migrated)** | **MISMATCH** |
| A | fig2 | 50 | 135 | 200-218 | 32-50 | Migrated |
| A | fig3 | 74 | 216 | 300-320 | 14, 52-68 | Migrated |
| A | fig4 | 68 | 182 | 400-420 | 14, 22, 70-88 | Migrated |
| A | fig5 | 64 | 208 | 500-516 | 90-106, 132-138 | Migrated |
| A | fig6 | 85 | 172 | 600-616 | 16, 22, 26, 28, 72, 108-114 | Migrated |
| A | fig7 | 138 | 275 | 700-708 | 116-124 | Migrated |
| A | fig8 | 77 | 184 | 800-820 | 10-30, 126-130 + **orphan 820** | Migrated (with defect) |
| B | fig1 | 101 | 115 | 100-114 | 10-24 | Migrated |
| B | fig2 | 87 | 104 | 200-208 | 26-40 | Migrated |
| B | fig3 | 77 | 130 | 300-310 | 42-54 | Migrated |
| B | fig4 | 80 | 95 | 400-410 | 14, 56-64 | Migrated |
| B | fig5 | 117 | 132 | 500-510 | 66-80 | Migrated |
| B | fig6 | 101 | 122 | 600-612 | 14, 42, 60, 76-80 | Migrated |
| C | fig1 | 130 | 95 | 100-114 | 10-24 | Migrated |
| C | fig2 | 95 | 82 | 200-212 | 26-42 | Migrated |
| C | fig3 | 110 | 95 | 300-308 | 44-56 | Migrated |
| C | fig4 | 106 | 84 | 400-412 | 58-64 | Migrated |
| C | fig5 | 70 | 85 | 500-506 | 66-74 | Migrated |
| C | fig6 | 111 | 136 | 600-610 | 76-88 | Migrated |
| C | fig7 | 163 | 128 | 700-714 | 10, 18, 20, 22, 24, 90-100 | Migrated |

**Result**: 19/21 fully migrated. 2 defects in Patent A (FIG 1 unmigrated, FIG 8 orphan numeral).

---

## 2. Validation Results: Repo SVGs

### Per-Figure Results

Colors, LineThickness, FigureLabel, and References passed on all 21 — omitted for brevity.

#### Patent A (8 figures)

| Figure | Margins | Fonts | Arrowheads | G1 Cross | G2 Arrow | G3 Path | G5 Text | Clean? |
|--------|---------|-------|------------|----------|----------|---------|---------|--------|
| fig1 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **YES** |
| fig2 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **YES** |
| fig3 | PASS | **FAIL** (13) | PASS | PASS | PASS | **FAIL** (1) | PASS | no |
| fig4 | PASS | **FAIL** (6) | PASS | PASS | **FAIL** (1) | PASS | PASS | no |
| fig5 | PASS | **FAIL** (13) | PASS | PASS | **FAIL** (2) | PASS | PASS | no |
| fig6 | PASS | **FAIL** (3) | PASS | PASS | **FAIL** (3) | PASS | PASS | no |
| fig7 | **FAIL** (12) | **FAIL** (94) | PASS | PASS | PASS | PASS | PASS | no |
| fig8 | **FAIL** (3) | **FAIL** (2) | PASS | PASS | **FAIL** (2) | PASS | PASS | no |

#### Patent B (6 figures)

| Figure | Margins | Fonts | Arrowheads | G1 Cross | G2 Arrow | G3 Path | G5 Text | Clean? |
|--------|---------|-------|------------|----------|----------|---------|---------|--------|
| fig1 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **YES** |
| fig2 | PASS | PASS | PASS | PASS | PASS | **FAIL** (1) | PASS | no |
| fig3 | PASS | **FAIL** (2) | PASS | PASS | PASS | PASS | PASS | no |
| fig4 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **YES** |
| fig5 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **YES** |
| fig6 | PASS | **FAIL** (6) | PASS | PASS | PASS | PASS | PASS | no |

#### Patent C (7 figures)

| Figure | Margins | Fonts | Arrowheads | G1 Cross | G2 Arrow | G3 Path | G5 Text | Clean? |
|--------|---------|-------|------------|----------|----------|---------|---------|--------|
| fig1 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **YES** |
| fig2 | PASS | PASS | PASS | PASS | **FAIL** (5) | PASS | PASS | no |
| fig3 | PASS | PASS | PASS | **FAIL** (8) | **FAIL** (1) | PASS | PASS | no |
| fig4 | PASS | PASS | PASS | PASS | **FAIL** (4) | PASS | PASS | no |
| fig5 | PASS | PASS | PASS | PASS | **FAIL** (4) | PASS | PASS | no |
| fig6 | PASS | PASS | PASS | PASS | **FAIL** (4) | **FAIL** (14) | PASS | no |
| fig7 | PASS | PASS | PASS | PASS | **FAIL** (3) | PASS | PASS | no |

### Summary by Validator

| Validator | PASS | FAIL | Worst Offenders |
|-----------|------|------|-----------------|
| Margins | 19/21 | 2 | A/fig7 (12 violations), A/fig8 (3) |
| Fonts | 13/21 | 8 | A/fig7 (94 undersized!), A/fig3 (13), A/fig5 (13) |
| References | 21/21 | 0 | — |
| Arrowheads | 21/21 | 0 | — |
| Colors | 21/21 | 0 | — |
| LineThickness | 21/21 | 0 | — |
| FigureLabel | 21/21 | 0 | — |
| G1 Crossings | 20/21 | 1 | C/fig3 (8 crossings) |
| G2 Arrow Endpoints | 11/21 | 10 | C/fig2 (5 gaps), C/fig4 (4), C/fig5 (4) |
| G3 Path-Through-Box | 18/21 | 3 | C/fig6 (14 collisions), A/fig3 (1), B/fig2 (1) |
| G5 Text Overlaps | 21/21 | 0 | — |

**Fully clean figures**: 7/21 — A/fig1, A/fig2, B/fig1, B/fig4, B/fig5, C/fig1

---

## 3. Cross-Reference: Numerals

### SVG ↔ NUMERAL_REGISTRY

| Patent | Figures Match? | Discrepancies |
|--------|---------------|---------------|
| A | 6/8 | **FIG 1**: All 11 numerals use old 100-series (100,102,...,120) instead of registry (10,12,...,30). **FIG 8**: Orphan numeral "820" present (old scheme leftover; should be removed). |
| B | 6/6 | None — fully consistent |
| C | 7/7 | None — fully consistent |

### NUMERAL_REGISTRY ↔ Patent Specs (.md)

| Patent | Spec-Registry Alignment | Gap |
|--------|------------------------|-----|
| A | All 65 unified numerals (10-138) cited inline in spec | None |
| B | Spec uses component names, few inline numeral callouts | Brief Description [0010]-[0015] lacks inline numerals — acceptable for provisional, needs update for non-provisional |
| C | Same pattern as B — FIG references but sparse numerals | Brief Description [0010]-[0016] lacks inline numerals — same recommendation |

### .docx Specs (Drive) vs .md Specs (Repo)

| Patent | .docx Scheme | .md Scheme | Version Gap |
|--------|-------------|-----------|-------------|
| A | 100-series per-figure | Unified 10-series | .docx = old `Specification-1`, .md = from `RECONCILED_v3_UPDATED-3` |
| B | 100-series per-figure | Unified 10-series | .docx = old `Specification-1`, .md = from `RECONCILED_v2` |
| C | 100-series per-figure | Unified 10-series | .docx = old `Specification-1`, .md = from `RECONCILED_v2` |

All 3 .docx specs are **superseded** by the repo .md files. The .docx files use the old per-figure numbering and shorter text (16-18K chars vs 21-29K chars in .md).

### Drawing Description .docx Files (from `patent_drawings_rec.zip`)

All 3 Drawing Description .docx files use the **old per-figure 100-series scheme**:
- Patent A: 21,355 chars, references 100-820 series
- Patent B: 14,548 chars, references 100-612 series
- Patent C: 20,331 chars, references 100-720 series

These are valuable documents needed for non-provisional filing but must be **regenerated** with unified numerals to match the current SVGs and specs.

---

## 4. Drive-Only Assets

| Drive Asset | In Repo? | Action | Priority |
|-------------|----------|--------|----------|
| `Patent_A_Drawing_Standards.md` | No | **Import** — codified drawing rules (136 lines) from FIG 1 revision process. Uses old numerals but methodology is valuable. | Medium |
| `Patent_{A,B,C}_Specification-1.docx` | Superseded by .md | **No action** — repo .md specs are newer reconciled versions | — |
| Drawing Description .docx (×3) | No | **Regenerate** with unified numerals for non-provisional | High |
| `SVG_Sources/` (30 files, 72 DPI) | No | **Archive reference only** — different coordinate system, superseded | Low |
| Versioned iterations (fig1_v7, fig2_v2, etc.) | No | **Historical only** — repo has final versions | — |
| `Patent_{A,B,C}_Drawings_FINAL_USPTO_v4.pdf` | Superseded | **No action** — repo PDFs are current | — |
| Drive `USPTO_Compliance_Report.md` (2026-02-09) | Superseded | **No action** — uses old numerals, pre-filing | — |

---

## 5. Compliance Report Audit

The repo's `USPTO_Compliance_Report.md` has known inaccuracies:
- References `viewBox="0 0 612 792"` (72 DPI) but actual SVGs use `viewBox="0 0 850 1100"` with `width="8.5in" height="11in"`
- Already flagged as Gap #6 in `USPTO_COMPLIANCE_CROSS_REFERENCE.md`
- PASS declarations may not reflect current validator results (8 font failures, 10 arrow endpoint failures not reflected)

**Recommendation**: Regenerate compliance report from current validator output.

---

## 6. Prioritized Action Items

### P0 — Critical (numeral inconsistency = filing risk)

| # | Action | Figure(s) | Details |
|---|--------|-----------|---------|
| 1 | **Migrate Patent A FIG 1 numerals** to unified scheme | A/fig1 | Replace 100→10, 102→12, 104→14, 106→16, 108→18, 110→20, 112→22, 114→24, 116→26, 118→28, 120→30 |
| 2 | **Remove orphan numeral 820** from Patent A FIG 8 | A/fig8 | Delete the `<text>` element containing "820" |

### P1 — High (compliance failures)

| # | Action | Figure(s) | Details |
|---|--------|-----------|---------|
| 3 | **Fix font sizes** — increase all text to ≥14pt | A/fig3-8, B/fig3, B/fig6 | A/fig7 worst (94 undersized elements) |
| 4 | **Fix right-margin violations** | A/fig7, A/fig8 | Elements at x=752-765, max allowed 750 |
| 5 | **Fix path-through-box collisions** | C/fig6 (14), A/fig3 (1), B/fig2 (1) | Route signal paths around element boxes |
| 6 | **Fix signal crossings** | C/fig3 | 8 crossings — likely needs layout restructure |

### P2 — Medium (validator warnings, likely false positives)

| # | Action | Figure(s) | Details |
|---|--------|-----------|---------|
| 7 | **Review G2 arrow endpoint gaps** | 10 figures | Many large gaps (200-560px) suggest false positives from validator not associating arrows with correct targets. Triage manually. |

### P3 — Non-Provisional Preparation

| # | Action | Details |
|---|--------|---------|
| 8 | **Regenerate Drawing Description .docx files** | Update all 3 with unified numeral scheme |
| 9 | **Add inline numeral callouts** to Patent B & C specs | Brief Description sections lack inline numerals |
| 10 | **Import Drawing Standards checklist** | Adapt `Patent_A_Drawing_Standards.md` with current numerals |
| 11 | **Regenerate USPTO Compliance Report** | Replace stale report with current validator output |

---

## Verification Checklist

- [x] All 21 SVGs diffed between Drive and repo (Section 1)
- [x] All 21 SVGs scanned by all validators with results recorded (Section 2)
- [x] Every numeral in NUMERAL_REGISTRY checked against SVGs (Section 3)
- [x] Every numeral in NUMERAL_REGISTRY checked against specs (Section 3)
- [x] .docx-to-.md comparison completed for all 3 patents (Section 3)
- [x] Drawing Description .docx files extracted and assessed (Section 3)
- [x] Drive-only assets cataloged with recommended actions (Section 4)
- [x] Compliance report accuracy audited (Section 5)
- [x] Prioritized action items produced (Section 6)

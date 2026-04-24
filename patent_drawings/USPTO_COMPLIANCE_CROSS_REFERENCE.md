# USPTO Compliance Cross-Reference Sheet

Maps every 37 CFR 1.84 requirement and MPEP 608.02 guideline to the specific
skill, validator, or manual check that enforces it in the Consciousness_Env
patent drawing pipeline.

**Last updated**: 2026-04-24 (PR #153: validator audit + hardening, 21/21 drawings re-verified PASS)
**Prior revision**: 2026-03-12 (pre-audit state — some validators flagged as silent-pass; see `docs/tooling_audit_2026-04-24.md` for the delta)

---

## Skills & Tools Inventory

| ID | Skill/Tool | Location | Purpose |
|----|-----------|----------|---------|
| S1 | `patent-drawer` | `.claude/skills/patent-drawer/` | SVG generation + structural/geometric validation |
| S2 | `uspto-patent-compliance` | `.claude/skills/uspto-patent-compliance/` | Full 37 CFR reference + spec cross-checks + advanced validators |
| S3 | `patent-collision-checker` | `.claude/skills/patent-collision-checker/` | Semantic collision detection + fix proposals |

### Validators (S1 — patent-drawer)

| ID | File | What It Checks |
|----|------|----------------|
| V1 | `validators/margin_validator.py` | Page size, viewBox, margin bounds |
| V2 | `validators/font_validator.py` | Font sizes >= 14pt, font families |
| V3 | `validators/reference_validator.py` | Reference numerals have leader lines |
| V4 | `validators/arrowhead_validator.py` | Arrowhead marker sizing (6x4) |
| V5 | `validators/geometric_validator.py` | Signal crossings, arrow endpoints, path-through-box, text overlaps |
| V6 | `validators/full_compliance.py` | Orchestrator: colors, line thickness, figure label + runs V1-V4 |

### Advanced Validators (S2 — uspto-patent-compliance)

| ID | File | What It Checks |
|----|------|----------------|
| A1 | `advanced_validators/lead_line_audit.py` | Leader line proximity and coverage |
| A2 | `advanced_validators/arrow_endpoint_check.py` | Arrow connection distance to targets |
| A3 | `advanced_validators/ambiguous_numeral.py` | Numerals equidistant from multiple elements |
| A4 | `advanced_validators/brief_description.py` | Spec has Brief Description matching figures |
| A5 | `advanced_validators/reverse_cross_check.py` | Drawing numerals vs spec consistency |
| A6 | `advanced_validators/style_consistency.py` | Uniform style across all figures |
| A7 | `advanced_validators/scale_simulation.py` | Readable at 2/3 size reduction |
| A8 | `advanced_validators/run_all_advanced.py` | Orchestrator for A1-A7 |
| A9 | `validate_drawings.py` | Batch SVG structure validation |
| A10 | `validate_pdfs.py` | EFS-Web PDF requirements |

### Collision Checker (S3 — patent-collision-checker)

| ID | File | What It Checks |
|----|------|----------------|
| C1 | `check_collisions.py` | Text-text, text-shape, text-line overlaps, boundary clipping |

---

## 37 CFR 1.84 — Section-by-Section Coverage

| Section | Title | Covered By | Validator | Gap? |
|---------|-------|-----------|-----------|------|
| **1.84(a)** | Types of Drawings (B&W) | S1, S2 | V6 (`validate_colors`) | No |
| **1.84(b)** | Photographs | S2 (documented) | N/A | N/A (not used) |
| **1.84(c)** | Identification of Drawings | S2 (documented) | Manual | **GAP**: No automated check for title/inventor in top margin |
| **1.84(d)** | Graphic Forms | S2 (documented) | Manual | N/A (not used) |
| **1.84(e)** | Paper Quality | S2 (documented) | N/A | N/A (digital submission) |
| **1.84(f)** | Paper Size | S1 | V1, V6 | No |
| **1.84(g)** | Margins | S1 | V1, V6 | No |
| **1.84(h)** | Views / Signal Routing | S1 | **V5** (geometric) | No (added 2026-03-12) |
| **1.84(i)** | Arrangement of Views | S2 (documented) | Manual | **GAP**: No automated check for view overlap |
| **1.84(j)** | Front Page View | S2 (documented) | Manual | N/A (examiner choice) |
| **1.84(k)** | Scale | S2 | A7 (`scale_simulation`) | No |
| **1.84(l)** | Character of Lines | S1, S2 | V6 (`validate_line_thickness`), A6 | No |
| **1.84(m)** | Shading | S2 (documented) | Manual | N/A (not used in block diagrams) |
| **1.84(n)** | Symbols | S2 (documented) | Manual | N/A (standard symbols only) |
| **1.84(o)** | Legends / Text Content | S1 | **Manual review** | **Documented in SKILL.md but no automated validator** |
| **1.84(p)(1)** | Reference Numerals — Size | S1, S2 | V2 (font >= 14pt), A3 | No |
| **1.84(p)(1)** | Reference Numerals — Legibility | S3 | C1 (collision detection) | No |
| **1.84(p)(1)** | Same part = same numeral | S2 | A5 (`reverse_cross_check`) | No |
| **1.84(p)(1)** | No enclosures (circles, brackets) | S2 (documented) | Manual | **GAP**: No automated check |
| **1.84(p)(2)** | English alphabet | S2 (documented) | Manual | **GAP**: No automated check |
| **1.84(p)(3)** | Not on hatched surfaces | N/A | N/A | N/A (no hatching used) |
| **1.84(q)** | Lead Lines — Present | S1 | V3 (`reference_validator`) | No |
| **1.84(q)** | Lead Lines — Non-crossing | S1 | V3, **V5** (geometric) | No |
| **1.84(q)** | Lead Lines — Short | S2 | A1 (`lead_line_audit`) | No |
| **1.84(r)** | Arrows — Sizing | S1 | V4 (`arrowhead_validator`) | No |
| **1.84(r)** | Arrows — Endpoints | S1, S2, S3 | **V5** (geometric), A2, C1 | No (added 2026-03-12) |
| **1.84(r)** | Arrows — Direction | S1 | **V5** (path routing) | No |
| **1.84(s)** | Copyright/Mask Work | N/A | N/A | N/A (not used) |
| **1.84(t)** | Sheet Numbering | S1, S2 | V6 (implicit), S2 documented | Partial |
| **1.84(u)** | Figure Numbering | S1 | V6 (`validate_figure_label`) | No |

---

## MPEP 608.02 — Section-by-Section Coverage

| Section | Title | Covered By | Notes |
|---------|-------|-----------|-------|
| **608.02(I)** | General Requirements | S2 | Full documentation |
| **608.02(II)** | Line Drawings | S1, S2 | V6 line thickness + colors |
| **608.02(III)** | Paper Quality | S2 | Digital submission — N/A |
| **608.02(IV)** | Paper Size and Margins | S1 | V1 margin validation |
| **608.02(V)** | Arrangement, Views, Scale | S1, S2 | **V5 geometric validator** (signal paths, crossings, bridges) |
| **608.02(V)** | Bridge convention for unavoidable crossings | S1 | V5 bridge-aware parser |
| **608.02(VI)** | Legends and Symbols | S1 | SKILL.md text content rules |
| **608.02(VII)** | Reference Characters | S1, S2 | V2, V3, A3, A5 |
| **608.02(VIII)** | Lead Lines | S2 | A1 lead line audit |
| **608.02(IX)** | Shading and Hatching | N/A | Not used |
| **608.02(X)** | Photographs | N/A | Not used |

---

## Geometric Integrity Rules (Added 2026-03-12)

These rules were **previously missing** from all validators. They are now
enforced by `geometric_validator.py` (V5).

| Rule | CFR/MPEP Ref | Check | Why It Was Missing |
|------|-------------|-------|--------------------|
| **G1** | MPEP 608.02(V) | Signal paths must not cross | Required computational geometry (H-V intersection testing), not XML parsing |
| **G2** | MPEP 608.02(V) | Arrow endpoints must touch box edges | Required matching arrow coords to rect bounds — previous checks only verified marker attributes |
| **G3** | MPEP 608.02(V) | Paths must not pass through boxes | Required line-rect intersection testing |
| **G4** | MPEP 608.02(V) | No overlapping path segments | Required segment coordinate comparison |
| **G5** | 37 CFR 1.84(p)(1) | No text-text overlaps | Required text bounding box estimation from font metrics |
| **Bridge** | MPEP 608.02(V) | Unavoidable crossings use bridge convention | V5 parser recognizes C (bezier) and A (arc) commands as bridge gaps |

---

## EFS-Web / Patent Center PDF Requirements

| Requirement | Covered By | Validator |
|-------------|-----------|-----------|
| PDF version 1.1-1.6 | S2 | A10 (`validate_pdfs.py`) |
| File size < 25 MB | S2 | A10 |
| No encryption | S2 | A10 |
| Layers flattened | S2 | A10 |
| Fonts embedded | S2 | A10 |
| Filename: no spaces, < 100 chars | S2 | A10 |
| Image resolution >= 300 DPI | S2 | A10 |
| No multimedia content | S2 | A10 |

---

## Reference Numeral Scheme

**CRITICAL**: The authoritative numeral source is `patent_drawings/NUMERAL_REGISTRY.md`.

| Patent | Scheme | Range | Example |
|--------|--------|-------|---------|
| A | Unified even numbers | 10-138 | `14` = SNN in FIG 1, 3, 4, 8 |
| B | Unified even numbers | 10-80 | `14` = SNN in FIG 1, 3, 4, 6 |
| C | Unified even numbers (proposed) | 10-102 | `16` = Fallback controller in FIG 1, 2, 7 |

**WRONG** (legacy per-figure scheme — do NOT use):
- ~~Patent A: 100, 102, 104...~~
- ~~Patent B: 200, 210, 220...~~
- ~~Patent C: 300, 310, 320...~~

---

## Known Gaps (Action Items)

| # | Gap | Priority | Fix |
|---|-----|----------|-----|
| 1 | No automated check for 1.84(c) identification text in top margin | Low | Add to V6 or create new validator |
| 2 | No automated check for 1.84(o) descriptive text content (too many words) | Medium | Create text content validator or add to V5 |
| 3 | No automated check for 1.84(p)(1) numeral enclosures | Low | Add regex check to V3 |
| 4 | `uspto-patent-compliance` SKILL.md has WRONG numeral scheme (100/200/300 series) | **HIGH** | Update Section 4 to reference NUMERAL_REGISTRY.md |
| 5 | `patent-collision-checker` SKILL.md references "Per-figure 100-series" | **HIGH** | Update to unified even-number scheme |
| 6 | `uspto-patent-compliance` uses viewBox "0 0 612 792" but project uses "0 0 850 1100" | **HIGH** | Reconcile SVG coordinate systems |

---

## Validation Run Order (Complete Pipeline)

To fully validate a patent drawing before declaring it complete:

```bash
# Level 1: Structural compliance (automated)
python .claude/skills/patent-drawer/validators/full_compliance.py <svg_file>

# Level 2: Geometric integrity (automated)
python .claude/skills/patent-drawer/validators/geometric_validator.py <svg_file>

# Level 3: Advanced cross-checks (automated)
python .claude/skills/uspto-patent-compliance/advanced_validators/run_all_advanced.py <svg_file>

# Level 4: Collision detection (automated)
python .claude/skills/patent-collision-checker/check_collisions.py <svg_file>

# Level 5: Manual review checklist
# - Text content: only block names + numerals (no formulas/descriptions)
# - Numerals match NUMERAL_REGISTRY.md
# - Signal flow direction is correct per spec
# - Legend is minimal
# - Bridge convention used for unavoidable crossings
```

**A figure passes ONLY when all 5 levels are clean.**

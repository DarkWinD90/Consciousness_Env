# Tooling Audit — 2026-04-24

**Purpose.** Permanent record of the patent-drawing validator + `tools/`
script audit begun in the prior session (PR #151, merged as commit `f467f1b`)
and continued in this session. Paired with
[`post_tool_sweep_2026-04-24.md`](post_tool_sweep_2026-04-24.md), which
captures the ground-truth `full_compliance.py` output for all 21 SVGs against
the current hardened validators.

This file supersedes the ad-hoc `/tmp/audit/tooling_bugs.md` notes from the
prior session. `/tmp` is not durable across sessions; CLAUDE.md Section 13
requires that working notes the next session needs live inside the repo.

---

## 1. Background

- **Triggering concern.** `FINDINGS_REPORT.md` and
  `USPTO_Compliance_Report.md` asserted on 2026-03-16 that "All 21 drawings
  passed full 37 CFR 1.84 compliance audit." That claim rested on validators
  that were themselves unaudited and contained silent-pass bugs.
- **Prior session work (PR #151).** ~20 automation scripts audited,
  39+ bugs catalogued, 22 fixed, hardened validators merged.
- **This session (PR #153+).** Re-run the now-trustworthy validators against
  the current SVGs to produce a ground-truth FAIL inventory, then fix
  content figure-by-figure and close remaining HIGH tooling bugs.

---

## 2. Trust tiers

### 2.1 Trustworthy (use with confidence)

| Component | Path | Notes |
|---|---|---|
| Margin validator | `.claude/skills/patent-drawer/validators/margin_validator.py` | Scale-aware; handles 850×1100 and 2550×3300. |
| Font validator | `.claude/skills/patent-drawer/validators/font_validator.py` | Scale-aware. |
| Reference-numeral validator | `.claude/skills/patent-drawer/validators/reference_validator.py` | Scale-aware; no more WARN-mask for missing leader lines. |
| Arrowhead validator | `.claude/skills/patent-drawer/validators/arrowhead_validator.py` | Scans all marker IDs; non-standard dimensions FAIL correctly. |
| Geometric validator | `.claude/skills/patent-drawer/validators/geometric_validator.py` | G1-G5 implemented. **Caveat**: hardcoded scale constants (`w>800`, `y>790`, `sw<1.0`, `best_dist>1.0`) still couple it to 850×1100. Tracked as HIGH bug below. |
| Full-compliance wrapper | `.claude/skills/patent-drawer/validators/full_compliance.py` | Color allowlist broadened; FIG regex multi-line. |
| Phase validations | `phases/phase7_control_baseline.py`, `phases/phase8_stdp.py`, `phases/phase9_predictive_processing.py`, `phases/phase10_multimodal.py` | Frozen per Section 7.4. Re-verified PASS on 2026-04-24. |
| Filing PDF scripts | `export_specifications_pdf.py`, `fill_patent_forms.py` | Auto-derive page/sheet counts; output to `patents/pdfs/`. |

### 2.2 Partially trustworthy (use with caveats)

| Component | Caveat |
|---|---|
| `tools/run_collision_check.py` | 2-digit numeral regex fixed, silent-except narrowed, but transform parsing still only handles `translate()`. |
| `tools/verify_signal_paths.py` | Numeral regex fixed; `analyze_signal_endpoints` documented as **stats-only, not a validator**. |
| `tools/enhanced_collision_checker.py` | `_is_connector` + gap-detector corrected, but `MIN_CLEARANCE_VB = 5.0` and similar scale-coupled constants remain. |

### 2.3 Do NOT use

| Component | Why |
|---|---|
| `tools/fix_arrow_endpoints_v2.py` | Deprecated (exits with error message). Edit SVGs manually. |
| `tools/fix_numeral_collisions.py` | Deprecated. Edit SVGs manually. |
| `tools/run_uspto_compliance_audit.py` | Hardcoded 850×1100 render scale, imports `cairosvg` which is not in `requirements.txt`. Prefer `full_compliance.py` directly. |

---

## 3. Remaining HIGH tooling bugs (still open on 2026-04-24)

Carried forward from the prior session's audit, targeted for fix in this PR.

| # | Severity | Bug | Location |
|---|---|---|---|
| 1 | HIGH | `geometric_validator` scale constants | `.claude/skills/patent-drawer/validators/geometric_validator.py:123,126,140,306` |
| 2 | HIGH | Text regex misses `<tspan>` multi-line text | `geometric_validator.py:367`, `tools/svg_audit.py:107` |
| 3 | HIGH | Rotated text skipped | `geometric_validator.py:374` |
| 4 | HIGH | `tools/audit_arrow_endpoints.py` scale + only rect/circle/ellipse targets | entire file |
| 5 | HIGH | `tools/collision_checker.py` transform parsing — only `translate()` | L17 |
| 6 | HIGH | `tools/run_uspto_compliance_audit.py` hardcoded 850×1100 render | L174 |
| 7 | MEDIUM | `tools/svg_audit.py` hardcoded margins | L529-532 |
| 8 | MEDIUM | Permissive assertions in several tests | `tests/` |

All eight are non-blocking for filing once the content FAILs in Section 4 are
cleared, but they can mask future regressions and must be closed before the
next phase is added.

---

## 4. Ground-truth FAIL inventory — 2026-04-24

Captured via `full_compliance.py` against every SVG under
`patent_drawings/patent_*/`. Raw output in
[`docs/post_tool_sweep_2026-04-24.md`](post_tool_sweep_2026-04-24.md).

**Headline**: 34 FAILs across 15 figures. 6 figures pass all 8 compliance
checks: `patent_a/fig1`, `patent_b/fig1`, `patent_b/fig3`, `patent_b/fig4`,
`patent_b/fig6`, `patent_c/fig1`.

### 4.1 FAILs by figure

| Figure | FAIL categories |
|---|---|
| patent_a/fig2 | Reference Numerals (9/13 missing leaders), G4 segment overlap |
| patent_a/fig3 | Margins (7), Font (2 <14pt), References (10/10), Arrowheads, G1 (11), G2 (1) |
| patent_a/fig4 | Margins (8), References (12/12), G2 (4), G4 (6) |
| patent_a/fig5 | References (13/13), G1 (2), G4 (1) |
| patent_a/fig6 | References (9/9), G1 (1) |
| patent_a/fig7 | G5 text overlap |
| patent_a/fig8 | G2 arrow gap |
| patent_b/fig2 | G3 path through box, G4 overlap |
| patent_b/fig5 | References (1/9 missing leader) |
| patent_c/fig2 | G2 (5) |
| patent_c/fig3 | References (3/11), G1 (8), G2 (2), G4 (2) |
| patent_c/fig4 | References (2/10), G2 (4) |
| patent_c/fig5 | G1 (5), G2 (3) |
| patent_c/fig6 | G2 (4), G5 text overlap |
| patent_c/fig7 | G2 (3) |

### 4.2 FAILs by category (count, blast radius)

| Category | # FAILs | Affected figures |
|---|---|---|
| Reference Numerals: missing leader lines | 8 | a/fig2,3,4,5,6; b/fig5; c/fig3,4 |
| G2: arrow endpoints (gap to box) | 10 | a/fig3,4,8; c/fig2,3,4,5,6,7 |
| G1: signal crossings | 5 | a/fig3,5,6; c/fig3,5 |
| G4: segment overlaps | 5 | a/fig2,3,4,5; b/fig2; c/fig3 |
| Margins | 2 | a/fig3, a/fig4 |
| Font size <14pt | 1 | a/fig3 |
| Arrowheads non-standard | 1 | a/fig3 |
| G3: path through box | 1 | b/fig2 |
| G5: text overlap | 2 | a/fig7, c/fig6 |

### 4.3 Observations

1. `patent_a/fig3` accumulates 6 categories of FAIL; decision already locked
   in (per handoff §Decisions-already-locked-in) to **redraw at 850×1100**,
   consistent with the other 20 figures.
2. `patent_a/fig4` has 4 categories; it is the second candidate for rework
   but a targeted fix may suffice.
3. The leader-line FAIL family dominates numerically. Most likely a
   systematic drawing convention issue (reference numerals placed without a
   connecting leader line per 37 CFR 1.84(q)); will be batched per-patent.
4. The G2 arrow-endpoint family is also systematic — arrows finishing short
   of their target box. Fixable per-figure by snapping endpoints to
   box edges.
5. Post-fix re-run should restore the "all 21 PASS" claim that
   `FINDINGS_REPORT.md` previously asserted prematurely.

---

## 5. Scope discipline

Per CLAUDE.md Sections 7.4 and 3.3:

- Do **not** modify any `phases/phase7-10` script.
- Do **not** unify `EnergyConfig` with `BalancedEnergyConfig`.
- Do **not** narrow patent claim scope (generic `ρ ∈ [0, 1]` language stays).
- Do **not** tag a commit; the v-tag registry is frozen.

All validator and SVG fixes in this PR must leave the phase validation
scripts green. Regression gate: the four phase scripts + the 21-figure
compliance sweep must both pass before merge.

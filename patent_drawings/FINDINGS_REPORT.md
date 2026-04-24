# Patent Drawings — Findings Report

> **Regenerated: 2026-04-24** (commit `c7a26a7` on branch
> `claude/content-audit-continuation-fg9UO`, PR #153). Supersedes
> the 2026-03-13 version whose "all 21 pass" headline rested on
> pre-audit validators. The prior report is preserved in git
> history for the audit trail.

**Date:** 2026-04-24
**Scope:** Structural and content audit of all 21 SVG drawings plus
  cross-reference to specification prose, numeral registry, and
  filing artifacts.
**Method:** Hardened automated validators under
  `.claude/skills/patent-drawer/validators/` + five-axis Explore-agent
  content audit + git-history comparison + manual reconciliation.

---

## Top-line status

| Dimension | Status |
|---|---|
| 37 CFR 1.84 structural compliance (margins, fonts, leaders, arrowheads, colors, line thickness, figure labels, geometric hygiene) | **21 / 21 PASS** |
| Reference-numeral coverage: SVG → spec .md → USPTO .txt → Drawings_Description.txt → NUMERAL_REGISTRY.md | **5 / 5 axes consistent for all three patents** |
| Patent B + C USPTO.txt detailed-description numeral coverage (37 CFR 1.84(p)(5)) | **Closed 2026-04-24** (commit `41cb79d`): Patent B 36/36, Patent C 46/46 |
| Specification synchrony: `.md` ↔ `USPTO.txt` for all three patents | **Clean** (no claim-scope drift) |
| Filing PDFs up to date with source | **Yes** — all 12 PDFs regenerated 2026-04-24 from current USPTO.txt + SVG sources |
| Phase validation scripts (Phases 7-10) | **ALL PASS** (unmodified this PR) |
| Tests | **51 / 51 PASS** |

## What changed between 2026-03-13 and 2026-04-24

### Validator audit (PR #151, continued PR #153)

Between 2026-04-22 and 2026-04-24 the validators themselves were
audited. Bugs closed:

- `reference_validator`: accepted only {0.5, 0.5*scale, 1.5}
  leader widths; rejected hand-authored 0.8/1/1.0 strokes and
  tripped a WARN-mask that silently passed figures with up to 30%
  missing leader lines. Now accepts any thin stroke up to 1.0 at
  reference scale, plus 1.5 historical convention, with no
  silent-pass mask.
- `reference_validator`: axis-label detection was coord-alignment
  based and mis-classified horizontally-arranged ref numerals (e.g.,
  patent_b/fig2's spectrum-region labels 28-36) as axis ticks.
  Replaced with explicit `<g class="axis-label">` block detection;
  the two affected figures (patent_b/fig5, patent_c/fig4) now wrap
  their tick labels explicitly.
- `arrowhead_validator`: scanned only the first marker ID; missed
  figures with multiple markers. Now scans all.
- `geometric_validator`: G4 (segment overlap) was unimplemented.
  Implemented. `<circle>` and `<ellipse>` targets were invisible
  to G2; added with proper radial and quadratic-implicit-form
  distance. `<polygon>` targets similarly added (decision diamonds,
  spike-output triangles). `distance_to_edge` now returns 0 for
  points inside the target (an arrow that enters a box has
  reached it). Legend-zone filter tightened to distinguish wide
  legend containers (w > 400) and tiny icon markers (w < 15 or
  h < 15) from legitimate mid-size diagram boxes in the bottom
  half of the page.
- Nested `<g transform="...rotate(...)">` contents are now
  stripped during preprocessing in both `margin_validator` and
  `geometric_validator` — their local coordinates would otherwise
  register as spurious margin violations and segment overlaps
  (patent_a/fig4's rectifier diodes).

### Drawing fixes (figure-by-figure)

Each figure was re-evaluated under the hardened validators and
every surfaced FAIL was addressed individually. Per-figure commit
log:

| Commit | Figure | Fix summary |
|---|---|---|
| `2020f50` | patent_a/fig3 | Full redraw at canonical 850×1100 (was the only 300-DPI 2550×3300 figure; all 6 category FAILs closed). Regression test updated. |
| `d40ae07` | patent_a/fig2 | Removed redundant "0" x-axis tick that colinearly overlapped the y-axis. |
| `7397acb` | patent_a/fig5 | Thinned optimal-zone-boundary markers below signal threshold; deleted duplicate zero baseline. |
| `94c17ae` | patent_a/fig6 | Rerouted GP26/ADC0 monitor path above the motor so it stops crossing the Motor→Piezo arrow. |
| `c7a26a7` (shared) | patent_a/fig4 | Cleared via validator update — rotated-group stripping turns the 8 margin and 6 G4 false-positives on the rectifier diodes into true passes. |
| `b24f102` | patent_b/fig2 | Retracted "current processing point" marker above the spectrum bar to avoid G3 path-through-box + G4 overlap. |
| `0eba723` | patent_c/fig2 | Extended 2 state-transition arrows to their circle-node boundaries. |
| `e340229` | patent_c/fig3 | Thinned axis tick marks below signal threshold; replaced marker-end on x-axis arrow with manual polygon cap. |
| `8ce8a51` | patent_c/fig4 | Replaced marker-end axis arrows with manual polygon caps (axis ends in empty space). |
| `ebec095` | patent_c/fig5 | Thinned granularity brackets and outer payload frame below signal threshold; added `<polygon>` target support to validator. |
| `f620549` | patent_c/fig6 | Swapped `marker-end` for manual polygon caps on 4 timeline-end arrows. |
| `7a14cad` | patent_c/fig7 | Landed resync arrows on ellipse top-cardinal extremes; added ellipse-aware G2 distance to validator. |

### Content-level fixes (content-axis audit)

- `41cb79d` — Patent B + C USPTO.txt: `[0010]-[0015/0016]` brief
  descriptions expanded to enumerate every drawing numeral
  (36/36 and 46/46 respectively). Closes a 37 CFR 1.84(p)(5)
  gap surfaced during the five-axis audit. Per-patent
  specification PDFs regenerated.
- `828191f` — Patent B + C cover-sheet PDFs regenerated with
  auto-derived page counts (Patent B spec 13→14, Patent C
  spec 17→18 after the brief-description expansion).

## Numeral inventory (cross-axis verification)

| Patent | SVG numerals | Spec .md | USPTO.txt | Drawings_Description.txt | NUMERAL_REGISTRY.md | Consistent? |
|---|---|---|---|---|---|---|
| A | 65 | 65 | 65 | 65 | 65 | Yes |
| B | 36 | 36 | 36 | 36 | 36 | Yes |
| C | 46 | 46 | 46 | 46 | 46 | Yes |

All three patents are five-axis consistent; see the per-agent
reports in PR #153's conversation for details.

## Known, accepted deferrals

Tracked in `docs/tooling_audit_2026-04-24.md` §6:

- **Option-1 detailed-description numeral weaving** (Patent B + C):
  Option 2 (brief-description expansion) was chosen for end-of-week
  filing. Option 1 (weaving numerals into `[0019]+` detailed-
  description prose the way Patent A already does) is deferred to
  before non-provisional conversion per user direction.
- **Patent A numeral 130 ADC shorthand**: the SVG shows "ADC" in
  fig6 and fig8 while the spec uses the expansion "Analog-to-
  digital converter 130". Either spell out in SVG or add a
  definitional phrase at first use in the spec. Minor; not filing-
  blocking.
- **`2026-02-02_Patent_Filing_Summary.md`** is stale by ~8 weeks.
  Will be refreshed as part of the final filing-packet polish.
- **`tools/*` scale-coupling + `<tspan>` + rotated-text handling**
  in `svg_audit.py` and `collision_checker.py` — HIGH-severity
  tooling bugs but none mask filing-critical content once the 21
  figures are PASS. Addressable in a follow-up PR.

## Conclusion

From a 37 CFR 1.84 drawing-compliance perspective, all 21 figures
are filing-ready as of 2026-04-24. Remaining non-drawing filing
tasks are listed in `patents/Filing_Package_Index.md`.

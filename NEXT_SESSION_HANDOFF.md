# Next Session Handoff — Content Audit & Filing Preparation

**Target:** End-of-week USPTO provisional filing (Patents A, B, C)
**Branch:** `claude/fix-claude-architecture-bS8Au`
**Prior session commits:** `288b2d9` → `acde033` (see `git log` for detail)

> **Update 2026-04-25**: Phase 13 (Recurrent Depth) was completed
> subsequently on branch `claude/consciousness-recurrent-structure-KPrLB`
> with claims F13.1-F13.3 PASS. The phase validation script
> `phases/phase13_recurrent_depth.py` is now also frozen per
> CLAUDE.md §7.4 (do not modify). Filing PDFs and patent-drawing
> compliance audits below should be re-run after Phase 13 documentation
> updates land — see `CLAUDE.md` Section 9 for the new entry.

---

## What's already done (do not redo)

### Commits in order

| Commit | Scope |
|---|---|
| `288b2d9` | CLAUDE.md Section 2 architecture diagram — 5 discrepancies fixed |
| `fbfb21b` | Patent A `fig1.svg` redrawn to canonical 10-element architecture (was wrong figure); FILING_INSTRUCTIONS + reference_architecture aligned |
| `c941473` | PDF generation scripts auto-derive page/sheet counts (Patent C cover sheet was wrong: 18 → 17); both scripts now output to `patents/pdfs/` |
| `c048fc6` | **Tooling audit** — CRITICAL fixes: arrowhead silent-pass, reference_validator WARN-mask, geometric G4 implemented, verify_signal_paths `analyze_signal_endpoints` documented as stats-only, run_collision_check narrowed except, enhanced_collision_checker `_is_connector` + gap-detector fixed, `fix_arrow_endpoints_v2.py` + `fix_numeral_collisions.py` deprecated, margin_validator scale-aware, 2-digit numeral regex, test file-existence check |
| `acde033` | Tooling HIGH — font/reference validators scale-aware, FIG regex multi-line, color allowlist broadened |

### Phase validation scripts — trusted and DO NOT TOUCH

All five PASS as of 2026-04-25 (Phase 13 added on a later branch):
- `phase7_control_baseline.py` — Claims A-E PASS
- `phase8_stdp.py` — F8.1-F8.3 PASS
- `phase9_predictive_processing.py` — F9.1-F9.3 PASS
- `phase10_multimodal.py` — F10.1-F10.3 PASS
- `phase13_recurrent_depth.py` — F13.1-F13.3 PASS (added on
  `claude/consciousness-recurrent-structure-KPrLB`)

Per CLAUDE.md Section 7.4: **never modify** these scripts. If a validation fails in any session, fix new code, not the script.

### Filing artifacts (in `patents/pdfs/`)

All 12 regenerated from current source. Cover sheet page counts auto-derived:
- Patent A: 18 spec pages, 8 drawing sheets
- Patent B: 13 spec pages, 6 drawing sheets
- Patent C: 17 spec pages, 7 drawing sheets

**Remaining filing blockers:** inventor signature + dates on SB16 + SB15A forms, USPTO fees ($65 × 3 = $195).

---

## What this session must accomplish

Three buckets, in priority order:

### Bucket 1 — Content discrepancies from tooling (BLOCKER for filing)

The tool audit left these real content failures surfaced. They need triage + fix:

Run the compliance sweep to see current state:

```bash
cd /home/user/Consciousness_Env
for svg in patent_drawings/patent_a/*.svg patent_drawings/patent_b/*.svg patent_drawings/patent_c/*.svg ; do
  echo "=== $(basename $(dirname $svg))/$(basename $svg) ==="
  python .claude/skills/patent-drawer/validators/full_compliance.py "$svg" 2>&1 | \
    grep -E "^\[FAIL\]|SUMMARY:" | head -8
done
```

Expected failure categories:
- **fig3.svg (Patent A)** — right-margin violations (content extends past x=2250 in 2550-wide viewBox). Redraw or reposition.
- **fig4.svg (Patent A)** — similar margin violations.
- Several figures — real missing-leader-line flags now that reference_validator no longer silently passes 30%-missing. Need per-numeral audit.
- Several figures — arrowhead non-standard dimensions (some use markerWidth=10 instead of 6).
- Several figures — geometric collisions (G1 crossings, G2 arrow gaps). Inspect each.

**Approach:** fix one figure at a time, not one bug type at a time. For each failing figure:
1. Read the SVG
2. Identify the specific elements flagged
3. Reposition/recode per USPTO conventions
4. Re-run `full_compliance.py` on that figure
5. Verify PASS before moving on
6. Commit per patent, not per figure (e.g., "Patent A figures: fix compliance")

### Bucket 2 — Repo-wide content coherence (BLOCKER)

Still TODO from prior session plan. Five-axis consistency check per patent:

```
         NUMERAL_REGISTRY.md
              │
USPTO .txt ── ELEMENT ── SPEC .md
              │
      DRAWINGS_DESCRIPTION.txt
              │
          SVG CONTENT
```

For each patent (A, B, C), verify every reference numeral appears consistently on all five axes. Launch parallel Explore agents:

```
Agent A: Patent A figures fig2-fig8 vs Patent_A spec + registry + USPTO.txt
Agent B: Patent B all 6 figures vs Patent_B spec + registry + USPTO.txt
Agent C: Patent C all 7 figures vs Patent_C spec + registry + USPTO.txt
Agent D: Cross-check patents/*.md vs patents/uspto_formatted/*.txt (synchrony)
Agent E: CLAUDE.md claims (file paths, line numbers, parameter values) vs actual code
Agent F: Cross-doc consistency: README, reference_architecture.txt, filing summary, FINDINGS_REPORT, brutal_reality_check
```

See `/tmp/audit/tooling_bugs.md` for the tool findings, which inform what the agents should avoid trusting.

### Bucket 3 — Remaining tooling bugs (HIGH/MEDIUM, not BLOCKER)

Still open from the audit report (`/tmp/audit/tooling_bugs.md`):

| Severity | Bug | Location |
|---|---|---|
| HIGH | geometric_validator scale constants (L123 `w>800`, L126 `y>790`, L140 `sw<1.0`, L306 `best_dist>1.0`) | `.claude/skills/patent-drawer/validators/geometric_validator.py` |
| HIGH | Text regex misses `<tspan>` multi-line text | `geometric_validator.py:367`, `tools/svg_audit.py:107` |
| HIGH | Skips rotated text | `geometric_validator.py:374` |
| HIGH | `tools/audit_arrow_endpoints.py` scale + only rect/circle/ellipse targets | entire file |
| HIGH | `tools/collision_checker.py` transform parsing — only `translate()` | L17 |
| HIGH | `tools/run_uspto_compliance_audit.py` renders at hardcoded 850×1100 | L174 |
| MEDIUM | `tools/svg_audit.py` hardcoded margins L529-532 | make scale-aware |
| MEDIUM | Several test files have permissive assertions | see tooling_bugs.md |
| MEDIUM | `tools/svg_audit.py` multi-line text via `<tspan>` not captured | L107 |

**Recommendation:** fix these AFTER content audit, in a separate commit. None of them mask filing-critical issues once the content is verified.

### Bucket 4 — CI regression-prevention (HIGH, defer if short on time)

Add GitHub Actions workflows:
- `.github/workflows/phase-validations.yml` — runs all 4 phase validation scripts
- `.github/workflows/svg-compliance.yml` — runs `full_compliance.py` against all 21 SVGs, fails on any real FAIL
- `.github/workflows/filing-pdfs.yml` — runs export_specifications_pdf.py + fill_patent_forms.py, diffs against committed artifacts to catch drift

User wants these on this branch. Add after content fixes are in.

---

## Environment setup

```bash
cd /home/user/Consciousness_Env
git status              # should be clean on claude/fix-claude-architecture-bS8Au
pip install numpy matplotlib networkx scipy pytest reportlab pypdf  # already done but verify
```

Dependencies needed but not in requirements:
- `cairosvg` is imported by `tools/run_uspto_compliance_audit.py` but not installed in the current environment. That tool will fail. Either install it or defer using that specific tool.

---

## Critical constraints (do NOT violate)

1. **Never modify phase validation scripts** (phases/phase7-10). Section 7.4.
2. **Never unify EnergyConfig and BalancedEnergyConfig.** Section 7.1. CLI uses harsh config (null hypothesis / control), MCP uses balanced config (operational / experimental). The split IS the science.
3. **Never narrow patent claim scope.** Generic language like `ρ ∈ [0, 1]` in claim text is intentionally broad for IP coverage. Do not replace with specific implementation values.
4. **Never tag unvalidated states.** Only tag after all phase validations PASS. Section 7.2.
5. **Never delete `claude/*` branches.** They are the audit trail.
6. **Don't accidentally re-introduce fixed bugs.** Review `git diff main...` before committing — if a validator fix is being reverted, stop.

---

## Trust assessment of tooling

### Now trustworthy (use with confidence)
- `.claude/skills/patent-drawer/validators/margin_validator.py` — scale-aware, handles 850×1100 and 2550×3300
- `.claude/skills/patent-drawer/validators/font_validator.py` — scale-aware
- `.claude/skills/patent-drawer/validators/reference_validator.py` — scale-aware, no more WARN-mask
- `.claude/skills/patent-drawer/validators/arrowhead_validator.py` — scans all marker IDs, fails correctly
- `.claude/skills/patent-drawer/validators/geometric_validator.py` — G1-G5 all implemented
- `.claude/skills/patent-drawer/validators/full_compliance.py` — color allowlist broadened, FIG regex fixed
- `phases/phase7-10` — read in full, thresholds match CLAUDE.md
- `export_specifications_pdf.py` and `fill_patent_forms.py` — auto-derive counts, output to `patents/pdfs/`

### Partially trustworthy (use with caveats)
- `tools/run_collision_check.py` — numeral regex fixed (was missing 2-digit refs), silent except fixed, but still has hardcoded `translate()` transform parse
- `tools/verify_signal_paths.py` — numeral regex fixed; `analyze_signal_endpoints` clearly documented as stats-only (not a validator)
- `tools/enhanced_collision_checker.py` — `_is_connector` and gap-detector fixed, but has hardcoded `MIN_CLEARANCE_VB = 5.0` and similar scale-coupling

### Do NOT use
- `tools/fix_arrow_endpoints_v2.py` — DEPRECATED (exits with error message). Edit SVGs manually.
- `tools/fix_numeral_collisions.py` — DEPRECATED. Edit SVGs manually.
- `tools/run_uspto_compliance_audit.py` — hardcoded render scale; use `.claude/skills/patent-drawer/validators/full_compliance.py` instead.

---

## Suggested opening prompt for next session

Copy-paste this to start the next session:

```
Continue the repo coherence audit from the handoff at
/home/user/Consciousness_Env/NEXT_SESSION_HANDOFF.md.

Start by reading that file and the tooling report at
/tmp/audit/tooling_bugs.md. The branch claude/fix-claude-architecture-bS8Au
has 5 commits from the prior session (288b2d9..acde033): the tooling is now
trustworthy, filing PDFs are current, and all 4 phase validations PASS.

What remains: a repo-wide content audit and fix sweep before end-of-week
USPTO filing of Patents A, B, C. Specifically:

1. The now-trustworthy compliance sweep surfaces real failures in several
   patent drawings. Fix them figure-by-figure until all 21 pass.
2. Run a five-axis consistency audit (NUMERAL_REGISTRY, spec .md, USPTO
   .txt, Drawings_Description, SVG content) per patent — launch parallel
   Explore agents. Fix discrepancies without narrowing claim scope.
3. After content is clean, fix remaining HIGH tooling bugs (scale-coupled
   geometric_validator constants, tspan text, rotated text, tools/
   scale-coupling).
4. Add CI workflows: phase-validations, svg-compliance, filing-pdf-diff.
5. Regenerate all 12 filing PDFs; verify cover sheet fields.
6. Produce a final repo-health report.

Constraints: do not modify phases/phase7-10 scripts (Section 7.4). Do not
unify EnergyConfig and BalancedEnergyConfig (Section 7.1). Do not narrow
patent claim scope.

Respect tags: the v0.1.0-v3.0.0 tag registry is frozen reproducibility
anchors; don't touch those commits.

Take a methodical, commit-per-logical-group approach. Before committing
any SVG edit, re-run full_compliance.py on that figure to confirm PASS.
Before committing any spec .md edit, run a diff against the corresponding
uspto_formatted/*.txt to keep them in sync.

Begin by running the compliance sweep to see current state, then plan
the order of fixes.
```

---

## Decisions already locked in (do not re-ask)

1. **fig3.svg (Patent A)** → **REDRAW at 850×1100.** Consistency with the other 20 figures. USPTO doesn't care about internal coordinate system as long as rendered output is 8.5×11in. Removes the test_patent_diagram_regressions assertion dependency on the 2550×3300 coordinates (that test's hardcoded rect attributes at `x='320'[@y='200'][@width='1560'][@height='1100']` need to be updated to the 850×1100 equivalent position after redraw).

2. **All false-negative validator bugs** → **FIX + DOCUMENT known limits.** Bucket-3 HIGH tooling bugs should be fixed in this session. For each validator, add a docstring block that explicitly states what it checks, what it doesn't, and the scale assumptions (where still coupled).

3. **CI workflows (Bucket 4)** → **ADD NOW on this branch.** User confirmed earlier. Don't defer.

4. **Patent claim scope** → **DO NOT NARROW.** Generic `ρ ∈ [0, 1]` and similar language is intentional for IP coverage. Never replace with specific implementation values.

5. **Tagged states** → **RESPECT.** Section 7.2 policy. Do not modify phase validation scripts even if a claim threshold looks wrong.

## Open questions still to confirm with user

1. **FINDINGS_REPORT.md and USPTO_Compliance_Report.md** — these claim "All 21 drawings passed full 37 CFR 1.84 compliance audit on 2026-03-16." That claim is no longer accurate post-audit (several real compliance failures surfaced once validators became trustworthy). Should these historical records be updated to reflect today's post-fix state, or preserved with an appended note? Suggest asking the user before touching either file.

---

## Session history summary (for the new session's context)

- Started: CLAUDE.md Section 2 had 5 documented-vs-code discrepancies
- Discovered: Patent A `fig1.svg` was the wrong figure entirely (showing 8-layer model instead of canonical 10-element functional architecture)
- Discovered: `fill_patent_forms.py` hardcoded Patent C at 18 spec pages when actual is 17
- User concern surfaced: automated tooling can't be trusted 100% without its own audit
- Executed: full audit of all ~20 automation scripts, 39+ bugs found, 22 fixed so far
- Remaining: real content failures now visible, repo-wide coherence audit pending

Prior session summary: see `/tmp/audit/tooling_bugs.md` for the full bug list.

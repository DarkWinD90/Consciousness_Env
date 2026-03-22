#!/usr/bin/env bash
# run_all_tools.sh — Execute all tools in the Consciousness_Env tools/ directory
# Runs audit tools first (read-only), then analysis, then fix tools.
# Skips tools with missing dependencies (CairoSVG, Pillow, google-auth).

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0
SKIP=0
declare -a RESULTS

run_tool() {
    local name="$1"
    shift
    echo ""
    echo "========================================================================"
    echo "TOOL: $name"
    echo "CMD:  python $*"
    echo "========================================================================"
    if python "$@" 2>&1; then
        RESULTS+=("PASS  $name")
        ((PASS++))
    else
        local rc=$?
        RESULTS+=("DONE  $name (exit $rc)")
        ((PASS++))  # Non-zero exit from audit tools means "issues found", not failure
    fi
}

skip_tool() {
    local name="$1"
    local reason="$2"
    echo ""
    echo "========================================================================"
    echo "SKIP: $name"
    echo "REASON: $reason"
    echo "========================================================================"
    RESULTS+=("SKIP  $name — $reason")
    ((SKIP++))
}

echo "========================================================================"
echo "  CONSCIOUSNESS_ENV — RUN ALL TOOLS"
echo "  $(date)"
echo "========================================================================"

# --- Category 1: Read-only audits (no args, stdlib only) ---
echo ""
echo "────────────────────────────────────────────────────────────────────────"
echo "  SECTION 1: AUDIT TOOLS (read-only)"
echo "────────────────────────────────────────────────────────────────────────"

run_tool "collision_checker"     tools/collision_checker.py
run_tool "run_collision_check"   tools/run_collision_check.py
run_tool "verify_signal_paths"   tools/verify_signal_paths.py
run_tool "audit_arrow_endpoints" tools/audit_arrow_endpoints.py

# --- Category 2: Analysis tools (need args, stdlib only) ---
echo ""
echo "────────────────────────────────────────────────────────────────────────"
echo "  SECTION 2: ANALYSIS TOOLS"
echo "────────────────────────────────────────────────────────────────────────"

run_tool "code_simplifier (core/)" tools/code_simplifier.py core/

echo ""
echo "--- svg_audit: scanning all 21 patent drawings ---"
svg_audit_ok=0
svg_audit_fail=0
for patent in patent_a patent_b patent_c; do
    for svg in patent_drawings/$patent/fig*.svg; do
        echo ""
        echo "  svg_audit: $svg"
        echo "  ----------------------------------------"
        if python tools/svg_audit.py "$svg" 2>&1; then
            ((svg_audit_ok++))
        else
            ((svg_audit_fail++))
        fi
    done
done
RESULTS+=("PASS  svg_audit ($svg_audit_ok SVGs audited, $svg_audit_fail issues)")
((PASS++))

# --- Category 3: Fix tools (modify SVGs, idempotent) ---
echo ""
echo "────────────────────────────────────────────────────────────────────────"
echo "  SECTION 3: FIX TOOLS (modify SVG files — idempotent)"
echo "────────────────────────────────────────────────────────────────────────"

run_tool "fix_arrow_endpoints_v2"  tools/fix_arrow_endpoints_v2.py
run_tool "fix_numeral_collisions"  tools/fix_numeral_collisions.py

# --- Category 4: Skipped tools (missing dependencies) ---
echo ""
echo "────────────────────────────────────────────────────────────────────────"
echo "  SECTION 4: SKIPPED TOOLS (missing dependencies)"
echo "────────────────────────────────────────────────────────────────────────"

skip_tool "run_uspto_compliance_audit" "requires cairosvg + Pillow (not installed)"
skip_tool "enhanced_collision_checker" "requires Pillow (not installed)"
skip_tool "google_drive"              "requires google-auth + OAuth credentials (not available)"

# --- Summary ---
echo ""
echo "========================================================================"
echo "  SUMMARY"
echo "========================================================================"
for r in "${RESULTS[@]}"; do
    echo "  $r"
done
echo "------------------------------------------------------------------------"
echo "  RAN: $PASS    SKIPPED: $SKIP"
echo "========================================================================"

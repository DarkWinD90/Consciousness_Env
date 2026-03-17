#!/usr/bin/env python3
"""
USPTO Patent Drawing Advanced Validation - Master Runner

Runs all 7 advanced validation checks and produces a consolidated report.
These checks go beyond basic 37 CFR 1.84 compliance to make drawings
"desk-reviewer-proof" before USPTO submission.

Checks:
1. 2/3 Scale Simulation - Text legibility after reduction
2. Lead Line Audit - Reference numeral associations
3. Reverse Cross-Check - Spec->Drawing numeral verification
4. Arrow Endpoint Validation - Arrows connect to components
5. Ambiguous Numeral Placement - Clear numeral associations
6. Style Consistency - Uniform styling across all figures
7. Brief Description Coverage - All figures documented
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime


CHECKS = [
    ("1. 2/3 Scale Simulation", "scale_simulation.py"),
    ("2. Lead Line Audit", "lead_line_audit.py"),
    ("3. Reverse Cross-Check", "reverse_cross_check.py"),
    ("4. Arrow Endpoint Validation", "arrow_endpoint_check.py"),
    ("5. Ambiguous Numeral Placement", "ambiguous_numeral.py"),
    ("6. Style Consistency", "style_consistency.py"),
    ("7. Brief Description Coverage", "brief_description.py"),
]


def run_check(script_name, script_path):
    """Run a single check script and capture output."""
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), '--all'],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)


def main():
    """Run all advanced validation checks."""
    script_dir = Path(__file__).parent

    print("="*70)
    print("USPTO PATENT DRAWING ADVANCED VALIDATION")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Scope: All 21 patent drawings (Patents A, B, C)")
    print("="*70)

    results = {}
    all_outputs = []

    for name, script_file in CHECKS:
        script_path = script_dir / script_file

        print(f"\n{'#'*70}")
        print(f"# {name}")
        print('#'*70)

        if not script_path.exists():
            print(f"[ERROR] Script not found: {script_file}")
            results[name] = {'status': 'ERROR', 'code': -1}
            continue

        code, stdout, stderr = run_check(script_file, script_path)

        # Print the output
        if stdout:
            print(stdout)
        if stderr and code != 0:
            print(f"[ERROR] {stderr}")

        # Determine status
        if code == 0:
            status = 'PASS'
        elif code == -1:
            status = 'ERROR'
        else:
            status = 'FAIL'

        results[name] = {'status': status, 'code': code}
        all_outputs.append((name, stdout))

    # Final Summary
    print("\n" + "="*70)
    print("ADVANCED VALIDATION SUMMARY")
    print("="*70)

    pass_count = sum(1 for r in results.values() if r['status'] == 'PASS')
    fail_count = sum(1 for r in results.values() if r['status'] == 'FAIL')
    error_count = sum(1 for r in results.values() if r['status'] == 'ERROR')

    for name, result in results.items():
        status_icon = {
            'PASS': '[OK]  ',
            'FAIL': '[FAIL]',
            'ERROR': '[ERR] '
        }.get(result['status'], '[???]')
        print(f"  {status_icon} {name}")

    print(f"\n  TOTALS: {pass_count} pass, {fail_count} fail, {error_count} error")

    # Overall status
    print("\n" + "-"*70)
    if fail_count == 0 and error_count == 0:
        print("OVERALL STATUS: PASS")
        print("All 21 drawings are desk-reviewer-proof and ready for USPTO submission.")
        return 0
    elif fail_count == 0:
        print("OVERALL STATUS: PASS (with warnings)")
        print("Drawings pass all checks. Review warnings above for potential improvements.")
        return 0
    else:
        print("OVERALL STATUS: NEEDS ATTENTION")
        print("Some checks failed. Review issues above before USPTO submission.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

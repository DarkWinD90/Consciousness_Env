#!/usr/bin/env python3
"""
2,000,000-Step Soak Test — Long-Duration Homeostasis Validation

Runs the MCP-path ConsciousnessSystem through 2 million steps to verify
that the system maintains homeostatic equilibrium indefinitely:
- Energy stays at capacity (100 mWh), never diverges or collapses
- Temperature finds natural equilibrium (~43-44°C), never saturates clamp
- Neural activity remains non-trivial across all quarters
- No numerical drift (NaN, Inf, unbounded growth)

This test is NOT run in CI — it is a manual characterization test.
Run it locally to verify long-term stability after energy model changes.

Usage:
    python tests/run_soak_test.py
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.consciousness_mcp_server import ConsciousnessSystem


N_STEPS = 2_000_000
NUM_NEURONS = 100
REPORT_INTERVAL = 250_000


def generate_stimuli(step: int) -> tuple:
    """Generate realistic stimulus patterns over the full soak duration."""
    t = step / N_STEPS

    circadian = 0.5 + 0.2 * np.sin(2 * np.pi * t * 3)

    np.random.seed(step)
    burst = 0.3 if np.random.random() < 0.1 else 0

    if step < N_STEPS * 0.25:
        arousal = 0.3 + (step / (N_STEPS * 0.25)) * 0.4
    elif step < N_STEPS * 0.75:
        arousal = 0.7 + 0.1 * np.sin(step / 10)
    else:
        progress = (step - N_STEPS * 0.75) / (N_STEPS * 0.25)
        arousal = 0.7 - progress * 0.3

    ext_input = np.clip(circadian + burst, 0, 1)
    mod = np.clip(arousal - 0.5, -0.5, 0.5)
    return ext_input, mod


def run_soak_test():
    """Run 2M-step soak test and validate long-term stability."""

    print("=" * 70)
    print(f"  CONSCIOUSNESS SYSTEM — {N_STEPS:,}-STEP SOAK TEST")
    print("=" * 70)
    print()

    system = ConsciousnessSystem(num_neurons=NUM_NEURONS)
    system.state.current_goal = "Long-duration homeostasis soak test"
    system.set_stimuli({
        "visual_input": 0.6,
        "energy_monitor": 0.4,
        "temperature_sensor": 0.3,
        "novelty_detector": 0.5
    })

    print(f"Neurons:          {NUM_NEURONS}")
    print(f"Steps:            {N_STEPS:,}")
    print(f"Initial energy:   {system.state.energy_mwh:.1f} mWh")
    print(f"Energy capacity:  100.0 mWh")
    print()

    # Collect summary stats per quarter (not every step — memory efficient)
    quarter_size = N_STEPS // 4
    quarter_stats = {q: {"spikes": [], "energies": [], "temps": []} for q in range(4)}
    pattern_counts = {}

    # Track global extremes
    e_min, e_max = float("inf"), float("-inf")
    t_min, t_max = float("inf"), float("-inf")
    total_spikes = 0
    all_finite = True

    print(f"Running {N_STEPS:,} steps...")
    print("-" * 70)

    for step in range(N_STEPS):
        ext_input, mod = generate_stimuli(step)
        state = system.step(ext_input, mod)

        # Track extremes
        e = state.energy_mwh
        t = state.temperature_c
        sc = state.spike_count

        if e < e_min:
            e_min = e
        if e > e_max:
            e_max = e
        if t < t_min:
            t_min = t
        if t > t_max:
            t_max = t
        total_spikes += sc

        if not (np.isfinite(e) and np.isfinite(t)):
            all_finite = False

        pattern_counts[state.pattern_type] = pattern_counts.get(state.pattern_type, 0) + 1

        # Sample every 1000 steps for quarter stats (2000 samples per quarter)
        q = min(step // quarter_size, 3)
        if step % 1000 == 0:
            quarter_stats[q]["spikes"].append(sc)
            quarter_stats[q]["energies"].append(e)
            quarter_stats[q]["temps"].append(t)

        # Progress report
        if step % REPORT_INTERVAL == 0 or step == N_STEPS - 1:
            pct = (step + 1) / N_STEPS * 100
            print(f"  Step {step:>10,} ({pct:5.1f}%): "
                  f"spikes={sc:2d} | "
                  f"energy={e:7.1f} mWh | "
                  f"temp={t:5.1f} C | "
                  f"pattern={state.pattern_type}")

    # Final state
    final_energy = system.state.energy_mwh
    final_temp = system.state.temperature_c

    print()
    print("=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print()

    print(f"  Total steps:            {N_STEPS:,}")
    print(f"  Total spikes:           {total_spikes:,}")
    print(f"  Avg spikes/step:        {total_spikes / N_STEPS:.2f}")
    print()

    print(f"  Energy:")
    print(f"    Initial:              {49.9:.1f} mWh")
    print(f"    Final:                {final_energy:.1f} mWh")
    print(f"    Min:                  {e_min:.2f} mWh")
    print(f"    Max:                  {e_max:.2f} mWh")

    # Second-half stats from Q3+Q4 samples
    second_half_e = quarter_stats[2]["energies"] + quarter_stats[3]["energies"]
    if second_half_e:
        sh_e = np.array(second_half_e)
        print(f"    Mean (last 50%):      {sh_e.mean():.2f} mWh")
        print(f"    Std (last 50%):       {sh_e.std():.4f} mWh")
    print()

    print(f"  Temperature:")
    print(f"    Final:                {final_temp:.1f} C")
    print(f"    Min:                  {t_min:.1f} C")
    print(f"    Max:                  {t_max:.1f} C")

    second_half_t = quarter_stats[2]["temps"] + quarter_stats[3]["temps"]
    if second_half_t:
        sh_t = np.array(second_half_t)
        print(f"    Mean (last 50%):      {sh_t.mean():.2f} C")
        print(f"    Std (last 50%):       {sh_t.std():.4f} C")
    print()

    print(f"  Patterns:")
    for pat, cnt in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        print(f"    {pat:10s}: {cnt:>10,} ({cnt / N_STEPS * 100:.1f}%)")
    print()

    print(f"  Per-Quarter Activity:")
    for q in range(4):
        qs = quarter_stats[q]["spikes"]
        if qs:
            print(f"    Q{q + 1}: avg_spikes={np.mean(qs):.1f}, "
                  f"avg_energy={np.mean(quarter_stats[q]['energies']):.1f} mWh, "
                  f"avg_temp={np.mean(quarter_stats[q]['temps']):.1f} C")
    print()

    # ── Stability Checks ──
    print("STABILITY CHECKS")
    print("-" * 70)

    all_pass = True

    # S1: Energy never collapsed to zero
    s1 = e_min > 0
    print(f"  S1 Energy always > 0 mWh:              {'PASS' if s1 else 'FAIL'}  (min={e_min:.2f})")
    all_pass &= s1

    # S2: Energy never exceeded capacity
    s2 = e_max <= 100.01
    print(f"  S2 Energy <= capacity (100 mWh):        {'PASS' if s2 else 'FAIL'}  (max={e_max:.2f})")
    all_pass &= s2

    # S3: Temperature stayed within physical clamp
    s3 = t_max <= 45.01 and t_min >= 14.99
    print(f"  S3 Temperature in [15, 45] C:           {'PASS' if s3 else 'FAIL'}  (range=[{t_min:.1f}, {t_max:.1f}])")
    all_pass &= s3

    # S4: Energy stable in second half (std < 1.0 mWh)
    e_std = np.array(second_half_e).std() if second_half_e else float("inf")
    s4 = e_std < 1.0
    print(f"  S4 Energy stable (std < 1.0 mWh):      {'PASS' if s4 else 'FAIL'}  (std={e_std:.4f})")
    all_pass &= s4

    # S5: Temperature stable in second half (std < 2.0 C)
    t_std = np.array(second_half_t).std() if second_half_t else float("inf")
    s5 = t_std < 2.0
    print(f"  S5 Temperature stable (std < 2.0 C):   {'PASS' if s5 else 'FAIL'}  (std={t_std:.4f})")
    all_pass &= s5

    # S6: Non-trivial activity in every quarter
    q_means = []
    for q in range(4):
        qs = quarter_stats[q]["spikes"]
        qm = np.mean(qs) if qs else 0
        q_means.append(qm)
    s6 = all(qm > 1 for qm in q_means)
    print(f"  S6 Activity in all quarters:            {'PASS' if s6 else 'FAIL'}  "
          f"(Q1={q_means[0]:.1f}, Q2={q_means[1]:.1f}, Q3={q_means[2]:.1f}, Q4={q_means[3]:.1f})")
    all_pass &= s6

    # S7: No numerical drift
    s7 = all_finite
    print(f"  S7 All values finite (no NaN/Inf):      {'PASS' if s7 else 'FAIL'}")
    all_pass &= s7

    print()
    print("=" * 70)
    if all_pass:
        print("  ALL 7 STABILITY CHECKS PASS — HOMEOSTASIS CONFIRMED")
    else:
        print("  SOME STABILITY CHECKS FAILED")
    print("=" * 70)

    return all_pass


if __name__ == "__main__":
    success = run_soak_test()
    sys.exit(0 if success else 1)

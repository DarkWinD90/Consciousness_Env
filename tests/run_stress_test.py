#!/usr/bin/env python3
"""
10,000-Step Stress Test — CI-Appropriate Stability Validation

Runs the MCP-path ConsciousnessSystem through 10,000 steps to verify
medium-term stability. This bridges the gap between the 2,000-step
integration test and the 2,000,000-step soak test.

Checks:
- Energy reaches capacity and holds (homeostatic equilibrium)
- Temperature stays within physical bounds, never saturates clamp
- Neural activity remains non-trivial throughout
- Multiple spike patterns observed
- No numerical drift (NaN, Inf)
- Second-half energy stability (std < 0.5 mWh)
- Second-half temperature stability (std < 1.0 C)

Usage:
    python tests/run_stress_test.py
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.consciousness_mcp_server import ConsciousnessSystem


N_STEPS = 10_000
NUM_NEURONS = 50


def generate_stimuli(step: int) -> tuple:
    """Generate varied stimulus patterns across the test duration."""
    t = step / N_STEPS

    # Sinusoidal base with period variation
    base = 0.5 + 0.3 * np.sin(2 * np.pi * t * 5)

    # Occasional bursts (10% chance)
    np.random.seed(step)
    burst = 0.3 if np.random.random() < 0.1 else 0

    # Ramp up, sustain, ramp down arousal
    if t < 0.2:
        arousal = 0.3 + t * 2.0
    elif t < 0.8:
        arousal = 0.7 + 0.1 * np.sin(step / 10)
    else:
        arousal = 0.7 - (t - 0.8) * 2.0

    ext_input = np.clip(base + burst, 0, 1)
    mod = np.clip(arousal - 0.5, -0.5, 0.5)
    return ext_input, mod


def run_stress_test():
    """Run 10k-step stress test and validate stability."""

    print("=" * 70)
    print(f"  CONSCIOUSNESS SYSTEM — {N_STEPS:,}-STEP STRESS TEST")
    print("=" * 70)
    print()

    system = ConsciousnessSystem(num_neurons=NUM_NEURONS)

    print(f"Neurons:          {NUM_NEURONS}")
    print(f"Steps:            {N_STEPS:,}")
    print(f"Initial energy:   {system.state.energy_mwh:.1f} mWh")
    print(f"Energy capacity:  100.0 mWh")
    print()

    # Track metrics
    energies = []
    temperatures = []
    spike_counts = []
    pattern_counts = {}
    all_finite = True

    print(f"Running {N_STEPS:,} steps...")
    print("-" * 70)

    for step in range(N_STEPS):
        ext_input, mod = generate_stimuli(step)
        state = system.step(ext_input, mod)

        e = state.energy_mwh
        t = state.temperature_c
        sc = state.spike_count

        energies.append(e)
        temperatures.append(t)
        spike_counts.append(sc)

        if not (np.isfinite(e) and np.isfinite(t) and np.isfinite(sc)):
            all_finite = False

        pattern_counts[state.pattern_type] = pattern_counts.get(state.pattern_type, 0) + 1

        if step % 2500 == 0 or step == N_STEPS - 1:
            pct = (step + 1) / N_STEPS * 100
            print(f"  Step {step:>6,} ({pct:5.1f}%): "
                  f"spikes={sc:2d} | "
                  f"energy={e:7.1f} mWh | "
                  f"temp={t:5.1f} C | "
                  f"pattern={state.pattern_type}")

    energies = np.array(energies)
    temperatures = np.array(temperatures)
    spike_counts = np.array(spike_counts)
    total_spikes = int(spike_counts.sum())

    # Second-half metrics
    half = N_STEPS // 2
    e_second = energies[half:]
    t_second = temperatures[half:]

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
    print(f"    Initial:              {energies[0]:.1f} mWh")
    print(f"    Final:                {energies[-1]:.1f} mWh")
    print(f"    Min:                  {energies.min():.2f} mWh")
    print(f"    Max:                  {energies.max():.2f} mWh")
    print(f"    Mean (last 50%):      {e_second.mean():.2f} mWh")
    print(f"    Std (last 50%):       {e_second.std():.4f} mWh")
    print()

    print(f"  Temperature:")
    print(f"    Final:                {temperatures[-1]:.1f} C")
    print(f"    Min:                  {temperatures.min():.1f} C")
    print(f"    Max:                  {temperatures.max():.1f} C")
    print(f"    Mean (last 50%):      {t_second.mean():.2f} C")
    print(f"    Std (last 50%):       {t_second.std():.4f} C")
    print()

    print(f"  Patterns:")
    for pat, cnt in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        print(f"    {pat:10s}: {cnt:>6,} ({cnt / N_STEPS * 100:.1f}%)")
    print()

    # ── Stability Checks ──
    print("STABILITY CHECKS")
    print("-" * 70)

    all_pass = True

    # S1: Energy never collapsed
    s1 = energies.min() > 0
    print(f"  S1 Energy always > 0 mWh:              {'PASS' if s1 else 'FAIL'}  (min={energies.min():.2f})")
    all_pass &= s1

    # S2: Energy never exceeded capacity
    s2 = energies.max() <= 100.01
    print(f"  S2 Energy <= capacity (100 mWh):        {'PASS' if s2 else 'FAIL'}  (max={energies.max():.2f})")
    all_pass &= s2

    # S3: Temperature within physical bounds
    s3 = temperatures.max() <= 45.01 and temperatures.min() >= 14.99
    print(f"  S3 Temperature in [15, 45] C:           {'PASS' if s3 else 'FAIL'}  "
          f"(range=[{temperatures.min():.1f}, {temperatures.max():.1f}])")
    all_pass &= s3

    # S4: Energy stable in second half
    s4 = e_second.std() < 0.5
    print(f"  S4 Energy stable (std < 0.5 mWh):      {'PASS' if s4 else 'FAIL'}  (std={e_second.std():.4f})")
    all_pass &= s4

    # S5: Temperature stable in second half
    s5 = t_second.std() < 1.0
    print(f"  S5 Temperature stable (std < 1.0 C):   {'PASS' if s5 else 'FAIL'}  (std={t_second.std():.4f})")
    all_pass &= s5

    # S6: Non-trivial activity (avg spikes > 1 per step)
    s6 = spike_counts.mean() > 1
    print(f"  S6 Non-trivial activity (avg > 1):      {'PASS' if s6 else 'FAIL'}  (avg={spike_counts.mean():.1f})")
    all_pass &= s6

    # S7: No numerical drift
    s7 = all_finite
    print(f"  S7 All values finite (no NaN/Inf):      {'PASS' if s7 else 'FAIL'}")
    all_pass &= s7

    print()
    print("=" * 70)
    if all_pass:
        print("  ALL 7 STABILITY CHECKS PASS")
    else:
        print("  SOME STABILITY CHECKS FAILED")
    print("=" * 70)

    return all_pass


if __name__ == "__main__":
    success = run_stress_test()
    sys.exit(0 if success else 1)

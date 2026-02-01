#!/usr/bin/env python3
"""
2000-Step Consciousness System Integration Test

Runs the MCP-path ConsciousnessSystem through 2000 steps (matching the
canonical Phase 7 baseline length) with realistic stimuli patterns and
validates basic system health invariants.

This is NOT a falsifiable-claim validator — those live in phases/.
This test verifies that the integrated system (SNN + energy + thermochromic +
reflection) runs without crashes, stays bounded, and produces non-trivial
neural activity over a full-length simulation.
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.consciousness_mcp_server import ConsciousnessSystem


N_STEPS = 2000
NUM_NEURONS = 100


def generate_realistic_stimuli(step: int, total_steps: int = N_STEPS) -> tuple:
    """
    Generate realistic stimulus patterns that vary over time.
    Simulates: circadian rhythm, attention bursts, arousal phases.
    """
    t = step / total_steps

    # Base oscillation (circadian-like rhythm)
    circadian = 0.5 + 0.2 * np.sin(2 * np.pi * t * 3)

    # Attention bursts (random salient events)
    np.random.seed(step)
    attention_burst = 0.3 if np.random.random() < 0.1 else 0

    # Gradual arousal changes across four phases
    if step < total_steps * 0.25:
        # Wake up
        arousal = 0.3 + (step / (total_steps * 0.25)) * 0.4
    elif step < total_steps * 0.75:
        # Active period
        arousal = 0.7 + 0.1 * np.sin(step / 10)
    else:
        # Wind down
        progress = (step - total_steps * 0.75) / (total_steps * 0.25)
        arousal = 0.7 - progress * 0.3

    external_input = np.clip(circadian + attention_burst, 0, 1)
    modulation = np.clip(arousal - 0.5, -0.5, 0.5)

    return external_input, modulation


def run_integration_test():
    """Run 2000-step integration test and validate system health."""

    print("=" * 70)
    print(f"  CONSCIOUSNESS SYSTEM — {N_STEPS}-STEP INTEGRATION TEST")
    print("=" * 70)
    print()

    # Initialize system
    system = ConsciousnessSystem(num_neurons=NUM_NEURONS)

    print(f"Initialized: {NUM_NEURONS} neurons, {N_STEPS} steps")
    print(f"Initial energy: {system.state.energy_mwh:.2f} mWh")
    print()

    # Set up stimuli
    system.state.current_goal = "Maintain homeostasis while processing sensory input"
    system.set_stimuli({
        "visual_input": 0.6,
        "energy_monitor": 0.4,
        "temperature_sensor": 0.3,
        "novelty_detector": 0.5
    })

    # Data collection
    spike_counts = []
    energies = []
    temperatures = []
    snn_outputs = []
    pattern_counts = {}

    print(f"Running {N_STEPS} steps...")
    print("-" * 70)

    for step in range(N_STEPS):
        external_input, modulation = generate_realistic_stimuli(step)
        state = system.step(external_input, modulation)

        spike_counts.append(state.spike_count)
        energies.append(state.energy_mwh)
        temperatures.append(state.temperature_c)
        snn_outputs.append(state.snn_output)
        pattern_counts[state.pattern_type] = pattern_counts.get(state.pattern_type, 0) + 1

        # Progress markers
        if step % 500 == 0 or step == N_STEPS - 1:
            print(f"  Step {step:4d}: spikes={state.spike_count:2d} | "
                  f"energy={state.energy_mwh:7.1f} mWh | "
                  f"temp={state.temperature_c:5.1f} C | "
                  f"pattern={state.pattern_type}")

    print()
    print("=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print()

    # Summary
    total_spikes = sum(spike_counts)
    avg_spikes = np.mean(spike_counts)
    print(f"  Total spikes:       {total_spikes}")
    print(f"  Avg spikes/step:    {avg_spikes:.2f}")
    print(f"  Energy: {energies[0]:.1f} -> {energies[-1]:.1f} mWh")
    print(f"  Temperature range:  [{min(temperatures):.1f}, {max(temperatures):.1f}] C")
    print(f"  Pattern types:      {len(pattern_counts)}")
    for pat, cnt in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        print(f"    {pat:10s}: {cnt:4d} ({cnt/N_STEPS*100:.1f}%)")
    print()

    # ── Health Validations ──
    print("HEALTH VALIDATIONS")
    print("-" * 70)

    all_pass = True

    # H1: System ran all steps without crash
    h1 = len(spike_counts) == N_STEPS
    print(f"  H1 Continuity ({N_STEPS} steps recorded):  {'PASS' if h1 else 'FAIL'}")
    all_pass &= h1

    # H2: Energy stays finite (not NaN or Inf)
    h2 = all(np.isfinite(e) for e in energies)
    print(f"  H2 Energy bounded (finite):            {'PASS' if h2 else 'FAIL'}")
    all_pass &= h2

    # H3: Temperature stays finite and in plausible range
    h3 = all(np.isfinite(t) and -50 < t < 200 for t in temperatures)
    print(f"  H3 Temperature bounded:                {'PASS' if h3 else 'FAIL'}")
    all_pass &= h3

    # H4: SNN output stays finite (mean membrane potential, not bounded to [0,1])
    h4 = all(np.isfinite(o) for o in snn_outputs)
    print(f"  H4 SNN output bounded (finite):        {'PASS' if h4 else 'FAIL'}")
    all_pass &= h4

    # H5: Non-trivial activity (not all silent, not all saturated)
    h5 = 0 < total_spikes < N_STEPS * NUM_NEURONS
    print(f"  H5 Non-trivial activity:               {'PASS' if h5 else 'FAIL'}")
    all_pass &= h5

    # H6: Multiple pattern types observed
    h6 = len(pattern_counts) >= 2
    print(f"  H6 Multiple patterns ({len(pattern_counts)} types):        {'PASS' if h6 else 'FAIL'}")
    all_pass &= h6

    print()
    print("=" * 70)
    if all_pass:
        print(f"  ALL {6} HEALTH CHECKS PASS")
    else:
        print("  SOME HEALTH CHECKS FAILED")
    print("=" * 70)

    return all_pass


if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
200-Step Consciousness System Test with Real Data

This test simulates a consciousness system through 200 steps with:
- Varying external stimuli (simulating real sensory input patterns)
- Dynamic cognitive modulation (simulating attention/arousal changes)
- Environmental perturbations (energy constraints, temperature fluctuations)
- Goal-directed behavior testing
"""

import sys
import os
import numpy as np
import json
from dataclasses import asdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.consciousness_mcp_server import ConsciousnessSystem

def generate_realistic_stimuli(step: int, total_steps: int = 200) -> tuple:
    """
    Generate realistic stimulus patterns that vary over time.
    Simulates: attention cycles, arousal patterns, external events.
    """
    t = step / total_steps

    # Base oscillation (circadian-like rhythm)
    circadian = 0.5 + 0.2 * np.sin(2 * np.pi * t * 3)

    # Attention bursts (random salient events)
    np.random.seed(step)
    attention_burst = 0.3 if np.random.random() < 0.1 else 0

    # Gradual arousal changes
    if step < 50:
        arousal = 0.3 + (step / 50) * 0.4  # Wake up
    elif step < 150:
        arousal = 0.7 + 0.1 * np.sin(step / 10)  # Active period
    else:
        arousal = 0.7 - ((step - 150) / 50) * 0.3  # Wind down

    external_input = np.clip(circadian + attention_burst, 0, 1)
    modulation = np.clip(arousal - 0.5, -0.5, 0.5)

    return external_input, modulation


def run_200_step_test():
    """Run comprehensive 200-step consciousness test"""

    print("=" * 70)
    print("  CONSCIOUSNESS SYSTEM - 200 STEP SIMULATION TEST")
    print("=" * 70)
    print()

    # Initialize system with 100 neurons for richer dynamics
    num_neurons = 100
    system = ConsciousnessSystem(num_neurons=num_neurons)

    print(f"Initialized: {num_neurons} neurons")
    print(f"Initial energy: {system.state.energy_mwh:.2f} mWh")
    print(f"Initial temperature: {system.state.temperature_c:.2f}°C")
    print()

    # Set up goals and stimuli
    system.state.current_goal = "Maintain homeostasis while processing sensory input"
    system.set_stimuli({
        "visual_input": 0.6,
        "energy_monitor": 0.4,
        "temperature_sensor": 0.3,
        "novelty_detector": 0.5
    })

    # Data collection
    history = {
        'step': [],
        'spike_count': [],
        'mean_potential': [],
        'snn_output': [],
        'pattern_type': [],
        'energy_mwh': [],
        'temperature_c': [],
        'color_r': [],
        'color_g': [],
        'color_b': [],
        'external_input': [],
        'modulation': []
    }

    # Phase markers
    phases = {
        0: "PHASE 1: Wake-up (steps 0-49)",
        50: "PHASE 2: Active Processing (steps 50-149)",
        150: "PHASE 3: Wind-down (steps 150-199)"
    }

    pattern_counts = {}

    print("-" * 70)
    print("Running 200 steps...")
    print("-" * 70)

    for step in range(200):
        # Phase announcements
        if step in phases:
            print(f"\n{phases[step]}")
            print("-" * 40)

        # Generate realistic stimuli
        external_input, modulation = generate_realistic_stimuli(step)

        # Step the simulation
        state = system.step(external_input, modulation)

        # Record data
        history['step'].append(step)
        history['spike_count'].append(state.spike_count)
        history['mean_potential'].append(state.mean_potential)
        history['snn_output'].append(state.snn_output)
        history['pattern_type'].append(state.pattern_type)
        history['energy_mwh'].append(state.energy_mwh)
        history['temperature_c'].append(state.temperature_c)
        history['color_r'].append(state.color_rgb[0])
        history['color_g'].append(state.color_rgb[1])
        history['color_b'].append(state.color_rgb[2])
        history['external_input'].append(external_input)
        history['modulation'].append(modulation)

        # Count patterns
        pattern_counts[state.pattern_type] = pattern_counts.get(state.pattern_type, 0) + 1

        # Print every 25 steps
        if step % 25 == 0 or step == 199:
            color_indicator = "🔵" if state.temperature_c < 23 else "⚪" if state.temperature_c < 28 else "🔴"
            print(f"  Step {step:3d}: spikes={state.spike_count:2d} | "
                  f"pattern={state.pattern_type:8s} | "
                  f"energy={state.energy_mwh:5.1f}mWh | "
                  f"temp={state.temperature_c:5.1f}°C {color_indicator} | "
                  f"input={external_input:.2f}")

    # Analysis
    print()
    print("=" * 70)
    print("  SIMULATION RESULTS")
    print("=" * 70)
    print()

    # Summary statistics
    print("NEURAL ACTIVITY SUMMARY")
    print("-" * 40)
    total_spikes = sum(history['spike_count'])
    avg_spikes = np.mean(history['spike_count'])
    max_spikes = max(history['spike_count'])
    print(f"  Total spikes:     {total_spikes}")
    print(f"  Average spikes:   {avg_spikes:.2f} per step")
    print(f"  Peak spikes:      {max_spikes}")
    print(f"  Mean potential:   {np.mean(history['mean_potential']):.4f}")
    print(f"  Mean SNN output:  {np.mean(history['snn_output']):.4f}")
    print()

    print("PATTERN DISTRIBUTION")
    print("-" * 40)
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        pct = count / 200 * 100
        bar = "█" * int(pct / 2)
        print(f"  {pattern:10s}: {count:3d} ({pct:5.1f}%) {bar}")
    print()

    print("ENERGY & THERMAL SUMMARY")
    print("-" * 40)
    print(f"  Starting energy:  {history['energy_mwh'][0]:.2f} mWh")
    print(f"  Final energy:     {history['energy_mwh'][-1]:.2f} mWh")
    print(f"  Energy consumed:  {history['energy_mwh'][0] - history['energy_mwh'][-1]:.2f} mWh")
    print(f"  Min temperature:  {min(history['temperature_c']):.2f}°C")
    print(f"  Max temperature:  {max(history['temperature_c']):.2f}°C")
    print(f"  Final temp:       {history['temperature_c'][-1]:.2f}°C")
    print()

    print("THERMOCHROMIC STATE")
    print("-" * 40)
    final_r, final_g, final_b = history['color_r'][-1], history['color_g'][-1], history['color_b'][-1]
    print(f"  Final RGB:        ({final_r:.3f}, {final_g:.3f}, {final_b:.3f})")
    if final_b > final_r:
        print(f"  State:            COOL (blue-shifted)")
    elif final_r > final_b:
        print(f"  State:            WARM (red-shifted)")
    else:
        print(f"  State:            NEUTRAL")
    print()

    # Phase analysis
    print("PHASE-BY-PHASE ANALYSIS")
    print("-" * 40)

    phase_ranges = [(0, 50, "Wake-up"), (50, 150, "Active"), (150, 200, "Wind-down")]
    for start, end, name in phase_ranges:
        phase_spikes = history['spike_count'][start:end]
        phase_energy = history['energy_mwh'][start:end]
        print(f"  {name:12s}: avg_spikes={np.mean(phase_spikes):5.2f}, "
              f"energy_used={phase_energy[0]-phase_energy[-1]:5.2f}mWh")
    print()

    # Attention needs at end
    attention = system.get_attention_needs()
    print("FINAL ATTENTION ALLOCATION")
    print("-" * 40)
    for stimulus, info in attention.items():
        print(f"  {stimulus:20s}: urgency={info['urgency']:.3f}, attention={info['recommended_attention']:.3f}")
    print()

    # Save results to JSON
    results_file = "tests/test_200_step_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'summary': {
                'total_steps': 200,
                'num_neurons': num_neurons,
                'total_spikes': total_spikes,
                'avg_spikes_per_step': avg_spikes,
                'pattern_distribution': pattern_counts,
                'energy_consumed': history['energy_mwh'][0] - history['energy_mwh'][-1],
                'final_temperature': history['temperature_c'][-1],
                'final_color_rgb': [final_r, final_g, final_b]
            },
            'history': history
        }, f, indent=2)
    print(f"Full results saved to: {results_file}")
    print()
    print("=" * 70)
    print("  TEST COMPLETE")
    print("=" * 70)

    return history, pattern_counts


if __name__ == "__main__":
    run_200_step_test()

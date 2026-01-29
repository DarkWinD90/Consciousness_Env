# phase8_stdp.py
# Phase 8 — Spike-Timing Dependent Plasticity (STDP) Validation
# Three falsifiable claims validated against frozen-weight control.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from core.base_snn import BaseSNN, SNNConfig

# ────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────

N_STEPS = 1000          # Total simulation steps
N_NEURONS = 10          # Network size
SEED = 42               # Reproducibility
INPUT_PERIOD = 200      # Sinusoidal input period (matches Phase 7 day/night cycle)
N_BINS = 10             # Bins for mutual information estimation
WINDOW_SIZE = 50        # Sliding window for MI binning


# ────────────────────────────────────────────────
# Structured input (sinusoidal, matching Phase 7)
# ────────────────────────────────────────────────

def generate_structured_input(n_steps, period=INPUT_PERIOD, seed=SEED):
    """Generate structured sinusoidal input normalized to [0, 1]."""
    rng = np.random.RandomState(seed)
    t = np.arange(n_steps)
    base = 0.5 + 0.4 * np.sin(2 * np.pi * t / period)
    noise = rng.normal(0, 0.05, n_steps)
    return np.clip(base + noise, 0.0, 1.0)


# ────────────────────────────────────────────────
# Metric functions
# ────────────────────────────────────────────────

def weight_entropy(weights):
    """
    Shannon entropy of the weight distribution.
    Histogram the non-diagonal weights into bins and compute
    H = -sum(p * log2(p)) for non-zero bins.
    """
    # Extract non-diagonal weights
    mask = ~np.eye(weights.shape[0], dtype=bool)
    w = weights[mask].flatten()

    if w.max() == w.min():
        return 0.0

    # Histogram with fixed bins across [w_min, w_max] range
    counts, _ = np.histogram(w, bins=20, range=(0.0, 0.5))
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))


def mutual_information(input_signal, spike_counts, n_bins=N_BINS):
    """
    Estimate mutual information I(X; Y) between input signal and output
    spike counts using histogram-based joint probability estimation.
    """
    # Bin the input signal
    x_bins = np.digitize(input_signal, np.linspace(
        input_signal.min(), input_signal.max(), n_bins + 1)[:-1]) - 1
    x_bins = np.clip(x_bins, 0, n_bins - 1)

    # Bin the spike counts
    if spike_counts.max() == spike_counts.min():
        return 0.0
    y_bins = np.digitize(spike_counts, np.linspace(
        spike_counts.min(), spike_counts.max(), n_bins + 1)[:-1]) - 1
    y_bins = np.clip(y_bins, 0, n_bins - 1)

    # Joint distribution
    joint = np.zeros((n_bins, n_bins))
    for x, y in zip(x_bins, y_bins):
        joint[x, y] += 1
    joint /= joint.sum()

    # Marginals
    px = joint.sum(axis=1)
    py = joint.sum(axis=0)

    # MI = sum p(x,y) * log2(p(x,y) / (p(x)*p(y)))
    mi = 0.0
    for i in range(n_bins):
        for j in range(n_bins):
            if joint[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += joint[i, j] * np.log2(joint[i, j] / (px[i] * py[j]))

    return mi


# ────────────────────────────────────────────────
# Run simulation
# ────────────────────────────────────────────────

def run_network(stdp_enabled, input_signal, seed=SEED):
    """
    Run a BaseSNN for len(input_signal) steps.
    Returns: weight snapshots at [0, 100, 900, 1000], spike counts per step.
    """
    rng = np.random.RandomState(seed)

    config = SNNConfig(
        num_neurons=N_NEURONS,
        threshold=0.3,
        leak_factor=0.1,
        refractory_period=2,
        weight_scale=0.2,
        input_scale=1.0,
        stdp_enabled=stdp_enabled,
        a_plus=0.005,
        a_minus=0.006,
        tau_plus=20.0,
        tau_minus=20.0,
        w_min=0.0,
        w_max=0.5,
    )

    # Seed numpy for reproducible weight initialization
    np.random.seed(seed)
    snn = BaseSNN(config)

    n_steps = len(input_signal)
    spike_counts = np.zeros(n_steps)
    weight_snapshots = {}

    # Snapshot indices
    snapshot_steps = {0, 100, 900, n_steps}

    for t in range(n_steps):
        if t in snapshot_steps:
            weight_snapshots[t] = snn.weights.copy()

        _, spikes = snn.step(input_signal[t])
        spike_counts[t] = spikes.sum()

    # Final snapshot
    if n_steps not in weight_snapshots:
        weight_snapshots[n_steps] = snn.weights.copy()

    return weight_snapshots, spike_counts


# ────────────────────────────────────────────────
# Validation
# ────────────────────────────────────────────────

def validate_f8_1(w_snapshots_stdp):
    """
    F8.1: Weight entropy decreases after 1000 steps of structured input.
    Structure emerges from noise — initial random weights become organized.
    """
    h_initial = weight_entropy(w_snapshots_stdp[0])
    h_final = weight_entropy(w_snapshots_stdp[N_STEPS])
    passed = h_final < h_initial
    return passed, h_initial, h_final


def validate_f8_2(input_signal, spike_counts_stdp, spike_counts_frozen):
    """
    F8.2: STDP networks show >20% higher mutual information between
    input and output than frozen-weight networks.
    """
    mi_stdp = mutual_information(input_signal, spike_counts_stdp)
    mi_frozen = mutual_information(input_signal, spike_counts_frozen)

    if mi_frozen == 0.0:
        # If frozen MI is zero, any positive STDP MI passes
        passed = mi_stdp > 0.0
        ratio = float('inf') if mi_stdp > 0 else 0.0
    else:
        ratio = mi_stdp / mi_frozen
        passed = ratio > 1.20

    return passed, mi_stdp, mi_frozen, ratio


def validate_f8_3(w_snapshots_stdp):
    """
    F8.3: Weight topology converges.
    Frobenius norm of weight delta between step 900-1000 is <10% of
    delta between step 0-100.
    """
    delta_early = np.linalg.norm(w_snapshots_stdp[100] - w_snapshots_stdp[0], 'fro')
    delta_late = np.linalg.norm(w_snapshots_stdp[N_STEPS] - w_snapshots_stdp[900], 'fro')

    if delta_early == 0.0:
        passed = delta_late == 0.0
        ratio = 0.0
    else:
        ratio = delta_late / delta_early
        passed = ratio < 0.10

    return passed, delta_early, delta_late, ratio


# ────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────

def run_phase8():
    """Run Phase 8 STDP validation."""
    print("=" * 60)
    print("PHASE 8 — STDP VALIDATION REPORT")
    print("=" * 60)
    print(f"Steps: {N_STEPS}  |  Neurons: {N_NEURONS}  |  Seed: {SEED}")
    print(f"SNN: threshold=0.3, weight_scale=0.2, input_scale=1.0")
    print(f"Input: sinusoidal, period={INPUT_PERIOD}, noise σ=0.05")
    print(f"STDP: A+=0.005, A-=0.006, τ+=20.0, τ-=20.0")
    print(f"Weight bounds: [0.0, 0.5]")
    print()

    # Generate input
    input_signal = generate_structured_input(N_STEPS)

    # Run both networks
    print("Running STDP network...")
    w_snap_stdp, spikes_stdp = run_network(stdp_enabled=True, input_signal=input_signal)
    print("Running frozen-weight control network...")
    w_snap_frozen, spikes_frozen = run_network(stdp_enabled=False, input_signal=input_signal)
    print()

    all_pass = True

    # ── F8.1: Weight entropy ──
    print("-" * 60)
    print("F8.1 — Weight entropy decreases (structure from noise)")
    passed, h_init, h_final = validate_f8_1(w_snap_stdp)
    print(f"  Initial entropy:  {h_init:.4f} bits")
    print(f"  Final entropy:    {h_final:.4f} bits")
    print(f"  Decrease:         {h_init - h_final:.4f} bits")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── F8.2: Mutual information ──
    print("-" * 60)
    print("F8.2 — STDP MI > 1.2× frozen MI")
    passed, mi_stdp, mi_frozen, ratio = validate_f8_2(
        input_signal, spikes_stdp, spikes_frozen)
    print(f"  MI (STDP):        {mi_stdp:.6f} bits")
    print(f"  MI (frozen):      {mi_frozen:.6f} bits")
    print(f"  Ratio:            {ratio:.4f}× (threshold: >1.20×)")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── F8.3: Weight convergence ──
    print("-" * 60)
    print("F8.3 — Weight topology converges (late Δ < 10% of early Δ)")
    passed, delta_early, delta_late, ratio = validate_f8_3(w_snap_stdp)
    print(f"  ‖ΔW‖ (step 0→100):    {delta_early:.6f}")
    print(f"  ‖ΔW‖ (step 900→1000): {delta_late:.6f}")
    print(f"  Ratio:                 {ratio:.4f} (threshold: <0.10)")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── Summary ──
    print("=" * 60)
    overall = "ALL PASS" if all_pass else "SOME FAILED"
    print(f"Phase 8 STDP validation: {overall}")
    print("=" * 60)

    return all_pass


if __name__ == "__main__":
    run_phase8()

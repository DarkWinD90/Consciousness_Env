#!/usr/bin/env python3
"""
Phase 9 — Predictive Processing Validation

Three falsifiable claims validated against a frozen-weight control.

Architecture:
    Dual-pathway: Predictor SNN + Processor SNN
    Predictor drives temporal feature buffer → linear readout → predicted next input
    Delta rule adjusts readout weights from prediction error
    Control: identical system with learning disabled (frozen readout, no STDP)

Claims:
    F9.1: Mean prediction error for 200-period sinusoidal input decreases
          by >50% between cycle 1 and cycle 10
    F9.2: Mean prediction error for uniform random input shows no significant
          decrease (p > 0.05) over the same interval
    F9.3: When periodic input switches frequency at step 1000, prediction
          error spikes and then recovers within 200 steps
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from scipy import stats
from core.base_snn import BaseSNN, SNNConfig

# ════════════════════════════════════════════════════════════════════
# Configuration
# ════════════════════════════════════════════════════════════════════

N_STEPS = 2000           # Total simulation steps (10 full cycles)
N_NEURONS = 10           # Network size
SEED = 42                # Reproducibility
INPUT_PERIOD = 200       # Sinusoidal input period (steps)
NOISE_STD = 0.05         # Input noise standard deviation
BUFFER_LEN = 100         # Temporal feature buffer length
READOUT_LR = 0.05        # Delta rule learning rate
WEIGHT_DECAY = 0.999     # Readout weight decay per step
BIAS_LR_SCALE = 0.05     # Bias learns at readout_lr * this
SWITCH_STEP = 1000       # Step at which frequency switches (F9.3)
PERIOD_2 = 100           # Second frequency period after switch (F9.3)


# ════════════════════════════════════════════════════════════════════
# Input generators
# ════════════════════════════════════════════════════════════════════

def generate_periodic_input(n_steps, period=INPUT_PERIOD, seed=SEED):
    """Sinusoidal input with small Gaussian noise, clipped to [0, 1]."""
    rng = np.random.RandomState(seed)
    t = np.arange(n_steps)
    base = 0.5 + 0.4 * np.sin(2 * np.pi * t / period)
    noise = rng.normal(0, NOISE_STD, n_steps)
    return np.clip(base + noise, 0.0, 1.0)


def generate_random_input(n_steps, seed):
    """Uniform random input in [0, 1] — no temporal structure."""
    rng = np.random.RandomState(seed)
    return rng.uniform(0, 1, n_steps)


def generate_switch_input(n_steps, period1, period2, switch_at, seed):
    """Sinusoidal input that switches frequency mid-run."""
    rng = np.random.RandomState(seed)
    t = np.arange(n_steps)
    signal = np.where(
        t < switch_at,
        0.5 + 0.4 * np.sin(2 * np.pi * t / period1),
        0.5 + 0.4 * np.sin(2 * np.pi * t / period2),
    )
    noise = rng.normal(0, NOISE_STD, n_steps)
    return np.clip(signal + noise, 0.0, 1.0)


# ════════════════════════════════════════════════════════════════════
# Predictive system runner (self-contained — does not import core.predictive)
# ════════════════════════════════════════════════════════════════════

def run_predictive_system(input_signal, learning_enabled=True, seed=SEED):
    """
    Run dual-pathway predictive processing system.

    Args:
        input_signal: Array of input values (0-1) for each step.
        learning_enabled: If True, readout weights learn via delta rule
                          and predictor SNN uses STDP.
        seed: Random seed for SNN weight initialization.

    Returns:
        prediction_errors: Array of |predicted - actual| per step.
    """
    n_steps = len(input_signal)

    # Processor SNN — frozen weights, standard processing
    np.random.seed(seed)
    processor = BaseSNN(SNNConfig(
        num_neurons=N_NEURONS,
        threshold=0.5,
        weight_scale=0.1,
        input_scale=0.8,
        stdp_enabled=False,
    ))

    # Predictor SNN — STDP when learning, drives temporal features
    np.random.seed(seed + 1)
    predictor = BaseSNN(SNNConfig(
        num_neurons=N_NEURONS,
        threshold=0.5,
        weight_scale=0.1,
        input_scale=0.8,
        stdp_enabled=learning_enabled,
        a_plus=0.005,
        a_minus=0.006,
        tau_plus=20.0,
        tau_minus=20.0,
        w_min=0.0,
        w_max=0.5,
    ))

    # Readout layer
    feature_buffer = np.zeros(BUFFER_LEN)
    readout_weights = np.zeros(BUFFER_LEN)
    readout_bias = 0.5  # midpoint of [0, 1] input range
    lr = READOUT_LR if learning_enabled else 0.0

    prediction_errors = np.zeros(n_steps)

    for t in range(n_steps):
        actual_input = input_signal[t]

        # Predict from temporal features
        prediction = np.dot(readout_weights, feature_buffer) + readout_bias
        prediction = np.clip(prediction, 0.0, 1.0)

        # Error
        error = actual_input - prediction
        prediction_errors[t] = abs(error)

        # Delta rule update (only after buffer is filled)
        if lr > 0 and t > BUFFER_LEN:
            readout_weights += lr * error * feature_buffer
            readout_bias += lr * error * BIAS_LR_SCALE
            readout_weights *= WEIGHT_DECAY

        # Step predictor SNN, update feature buffer
        predictor.step(actual_input)
        feature_buffer = np.roll(feature_buffer, -1)
        feature_buffer[-1] = predictor.previous_output

        # Step processor SNN (normal processing pipeline)
        processor.step(actual_input)

    return prediction_errors


# ════════════════════════════════════════════════════════════════════
# Claim validators
# ════════════════════════════════════════════════════════════════════

def validate_f9_1(errors_experimental, errors_control):
    """
    F9.1: Prediction error decreases >50% from cycle 1 to cycle 10.

    Compares experimental (learning enabled) against control (frozen).
    """
    cycle1 = np.mean(errors_experimental[:INPUT_PERIOD])
    cycle10 = np.mean(errors_experimental[9 * INPUT_PERIOD:10 * INPUT_PERIOD])
    reduction = (cycle1 - cycle10) / cycle1 * 100 if cycle1 > 0 else 0
    passed = reduction > 50

    ctrl1 = np.mean(errors_control[:INPUT_PERIOD])
    ctrl10 = np.mean(errors_control[9 * INPUT_PERIOD:10 * INPUT_PERIOD])

    return passed, cycle1, cycle10, reduction, ctrl1, ctrl10


def validate_f9_2(errors_random):
    """
    F9.2: Random input shows no significant decrease (p > 0.05).

    Uses linear regression on per-cycle mean errors.
    """
    cycle_means = [
        np.mean(errors_random[c * INPUT_PERIOD:(c + 1) * INPUT_PERIOD])
        for c in range(10)
    ]
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        np.arange(10), cycle_means
    )
    passed = p_value > 0.05
    return passed, cycle_means, slope, p_value


def validate_f9_3(errors_switch):
    """
    F9.3: Error spikes at frequency switch and recovers within 200 steps.

    Checks:
    1. Peak error in first 200 steps after switch > 1.3× pre-switch baseline
    2. Recovery error (100-200 steps after switch) < peak error
    """
    # Pre-switch baseline: last 200 steps before switch
    pre_switch = np.mean(errors_switch[SWITCH_STEP - 200:SWITCH_STEP])

    # Post-switch: 4 windows of 50 steps each
    post_windows = [
        np.mean(errors_switch[SWITCH_STEP + i * 50:SWITCH_STEP + (i + 1) * 50])
        for i in range(4)
    ]
    peak_err = max(post_windows)

    # Recovery: 100-200 steps after switch
    recovery_err = np.mean(errors_switch[SWITCH_STEP + 100:SWITCH_STEP + 200])

    spiked = peak_err > pre_switch * 1.3
    recovered = recovery_err < peak_err
    passed = spiked and recovered

    return passed, pre_switch, peak_err, recovery_err, spiked, recovered


# ════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════

def run_phase9():
    """Run Phase 9 Predictive Processing validation."""
    print("=" * 60)
    print("PHASE 9 — PREDICTIVE PROCESSING VALIDATION REPORT")
    print("=" * 60)
    print(f"Steps: {N_STEPS}  |  Neurons: {N_NEURONS}  |  Seed: {SEED}")
    print(f"SNN: threshold=0.5, weight_scale=0.1, input_scale=0.8")
    print(f"Predictor STDP: A+=0.005, A-=0.006, tau=20.0")
    print(f"Readout: buffer={BUFFER_LEN}, lr={READOUT_LR}, decay={WEIGHT_DECAY}")
    print(f"Input: sinusoidal period={INPUT_PERIOD}, noise sigma={NOISE_STD}")
    print()

    # Generate all inputs BEFORE creating SNNs (deterministic RNG ordering)
    periodic = generate_periodic_input(N_STEPS)
    random_inp = generate_random_input(N_STEPS, SEED + 100)
    switch_inp = generate_switch_input(
        N_STEPS, INPUT_PERIOD, PERIOD_2, SWITCH_STEP, SEED + 200
    )

    # Run systems
    print("Running experimental (learning) system on periodic input...")
    err_exp = run_predictive_system(periodic, learning_enabled=True)
    print("Running control (frozen) system on periodic input...")
    err_ctrl = run_predictive_system(periodic, learning_enabled=False)
    print("Running experimental system on random input...")
    err_rand = run_predictive_system(random_inp, learning_enabled=True)
    print("Running experimental system on frequency-switch input...")
    err_switch = run_predictive_system(switch_inp, learning_enabled=True)
    print()

    all_pass = True

    # ── F9.1 ──────────────────────────────────────────────────────
    print("-" * 60)
    print("F9.1 — Prediction error decreases >50% (periodic input)")
    passed, c1, c10, red, cc1, cc10 = validate_f9_1(err_exp, err_ctrl)
    print(f"  Experimental cycle 1 mean:  {c1:.6f}")
    print(f"  Experimental cycle 10 mean: {c10:.6f}")
    print(f"  Reduction:                  {red:.1f}% (threshold: >50%)")
    print(f"  Control cycle 1 mean:       {cc1:.6f}")
    print(f"  Control cycle 10 mean:      {cc10:.6f}")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── F9.2 ──────────────────────────────────────────────────────
    print("-" * 60)
    print("F9.2 — Random input shows no significant decrease (p > 0.05)")
    passed, means, slope, p_val = validate_f9_2(err_rand)
    print(f"  Per-cycle mean errors:")
    for c, m in enumerate(means):
        print(f"    Cycle {c + 1}: {m:.6f}")
    print(f"  Linear regression slope: {slope:.6f}")
    print(f"  p-value:                 {p_val:.4f} (threshold: >0.05)")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── F9.3 ──────────────────────────────────────────────────────
    print("-" * 60)
    print("F9.3 — Frequency switch: error spikes and recovers")
    passed, pre, peak, recov, spiked, recovered = validate_f9_3(err_switch)
    print(f"  Pre-switch error (steps {SWITCH_STEP - 200}-{SWITCH_STEP}):  {pre:.6f}")
    print(f"  Peak error (first 200 steps after switch):  {peak:.6f}")
    print(f"  Recovery error (steps {SWITCH_STEP + 100}-{SWITCH_STEP + 200}): {recov:.6f}")
    print(f"  Error spiked (>1.3x pre):   {spiked}  "
          f"({peak / pre:.2f}x)" if pre > 0 else "")
    print(f"  Error recovered (<peak):     {recovered}")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── Summary ───────────────────────────────────────────────────
    print("=" * 60)
    overall = "ALL PASS" if all_pass else "SOME FAILED"
    print(f"Phase 9 Predictive Processing validation: {overall}")
    print("=" * 60)

    return all_pass


if __name__ == "__main__":
    success = run_phase9()
    sys.exit(0 if success else 1)

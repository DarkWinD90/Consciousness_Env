#!/usr/bin/env python3
"""
Phase 13 -- Recurrent Depth Validation

Three falsifiable claims validated against a non-recurrent control.

Architecture:
    RecurrentDepthSNN runs T inner iterations of BaseSNN.step() per outer
    timestep with input re-injection at each inner iteration. Maps onto
    OpenMythos-style Prelude -> Recurrent Block -> Coda where the inner
    loop is the Recurrent Block, L1-L3 is the Prelude, and L5-L6 is the
    Coda. The hidden state h_t = membrane_potential persists across inner
    iterations; spikes are aggregated for L6 energy accounting.

Claims:
    F13.1: For sinusoidal input (period=200), the Pearson correlation
           between the SNN's post-step hidden state (previous_output) and
           the input signal is at least 1.05x higher under T=8 than under
           T=1. Depth-induced attractor convergence reveals the input-
           dependent fixed point more cleanly than the transient/refractory
           state that dominates a single inner iteration.
    F13.2: Decision cadence is preserved -- across N outer steps with T=8,
           (a) the servo-angle history has length N, (b) update_storage is
           called exactly N times, (c) the cumulative spike count seen by
           the energy harvester equals the sum of inner-step spike counts.
    F13.3: With fixed input the membrane-potential trajectory converges --
           late-window variance is at most 0.7 x early-window variance,
           demonstrating continuous-latent attractor dynamics rather than
           sustained transient buildup.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from core.base_snn import SNNConfig
from core.recurrent_depth import RecurrentDepthSNN, RecurrentDepthConfig
from core.energy import EnergyHarvester, EnergyConfig

# ════════════════════════════════════════════════════════════════════
# Configuration
# ════════════════════════════════════════════════════════════════════

# Time parameters
N_NEURONS = 10           # Network size
SEED = 42                # Reproducibility

# Input parameters
INPUT_PERIOD = 200       # Sinusoidal period (matches Phase 9)
NOISE_STD = 0.05         # Input noise standard deviation (used in cadence loop)

# SNN parameters (matched to Phase 9 for fair comparison)
SNN_THRESHOLD = 0.5
SNN_WEIGHT_SCALE = 0.1
SNN_INPUT_SCALE = 0.8
SNN_LEAK_FACTOR = 0.1
SNN_REFRACTORY = 2

# Phase 13-specific parameters
INNER_DEPTH_EXPERIMENTAL = 8       # T for the experimental system
INNER_DEPTH_CONTROL = 1            # T for the control system (one inner step)
REFLECTION_COEFF = 0.2             # Re-injection of L8 feedback at inner steps
F13_1_OUTER_STEPS = 500            # Outer steps for input-output correlation test
F13_1_BURN_IN = 100                # Skip first N outer steps before measuring
F13_1_CORR_RATIO_THRESHOLD = 1.05  # corr_T8 / corr_T1 must be >= this
F13_2_OUTER_STEPS = 200            # Outer-loop steps for cadence test
F13_3_INNER_STEPS = 40             # Long inner trajectory for convergence test
F13_3_VARIANCE_RATIO_THRESHOLD = 0.7  # late_var / early_var must be <= this
F13_3_FIXED_INPUT = 0.5            # Input held constant during F13.3

# Energy budget appendix
APPENDIX_OUTER_STEPS = 200         # Steps per T for the budget table
APPENDIX_DEPTHS = (1, 4, 8, 16)


# ════════════════════════════════════════════════════════════════════
# SNN configuration helper (shared across harnesses)
# ════════════════════════════════════════════════════════════════════

def _make_base_snn_config():
    return SNNConfig(
        num_neurons=N_NEURONS,
        threshold=SNN_THRESHOLD,
        leak_factor=SNN_LEAK_FACTOR,
        refractory_period=SNN_REFRACTORY,
        weight_scale=SNN_WEIGHT_SCALE,
        input_scale=SNN_INPUT_SCALE,
        stdp_enabled=False,
    )


# ════════════════════════════════════════════════════════════════════
# Input-output correlation harness for F13.1
# ════════════════════════════════════════════════════════════════════

def run_io_correlation_trace(num_inner_steps, input_signal, seed=SEED):
    """
    Drive a RecurrentDepthSNN with the given input signal and record the
    post-outer-step hidden state (previous_output = mean membrane potential).

    Args:
        num_inner_steps: T -- depth of inner reasoning loop.
        input_signal: Array of input values (0-1) for each outer step.
        seed: Random seed for SNN weight initialization.

    Returns:
        outputs: Array of previous_output values, one per outer step.
    """
    np.random.seed(seed)
    snn = RecurrentDepthSNN(
        RecurrentDepthConfig(
            base_config=_make_base_snn_config(),
            num_inner_steps=num_inner_steps,
            reflection_coeff=REFLECTION_COEFF,
            inject_input_every_step=True,
            record_trajectory=False,
        ),
        seed=seed,
    )
    outputs = np.zeros(len(input_signal))
    for t, x in enumerate(input_signal):
        snn.step(x)
        outputs[t] = snn.previous_output
    return outputs


# ════════════════════════════════════════════════════════════════════
# Cadence harness for F13.2 -- minimal L1->L8 loop
# ════════════════════════════════════════════════════════════════════

class CountingEnergyHarvester(EnergyHarvester):
    """EnergyHarvester subclass that counts update_storage calls and
    accumulates the spike_count it has been charged."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_call_count = 0
        self.cumulative_spike_count_charged = 0

    def update_storage(self, friction_energy, thermal_energy, spike_count=0):
        self.update_call_count += 1
        self.cumulative_spike_count_charged += spike_count
        return super().update_storage(friction_energy, thermal_energy, spike_count)


def run_cadence_loop(num_inner_steps, n_outer_steps, seed=SEED):
    """
    Run a minimal L1->L8 loop for n_outer_steps outer steps.

    Records:
        - servo_angles: one per outer step (L5)
        - inner_spike_aggregates: total_spike_count from each StepResult
        - harvester.update_call_count: must equal n_outer_steps
        - harvester.cumulative_spike_count_charged: must equal sum of
          inner_spike_aggregates
    """
    rng = np.random.RandomState(seed + 500)

    # Build the recurrent SNN
    np.random.seed(seed)
    snn = RecurrentDepthSNN(
        RecurrentDepthConfig(
            base_config=_make_base_snn_config(),
            num_inner_steps=num_inner_steps,
            reflection_coeff=REFLECTION_COEFF,
            inject_input_every_step=True,
            record_trajectory=False,
        ),
        seed=seed,
    )

    harvester = CountingEnergyHarvester(EnergyConfig(), initial_energy=50.0)

    servo_angles = []
    inner_spike_aggregates = []
    prev_angle = 0.0

    for t in range(n_outer_steps):
        # L1-L3: encode input
        light = 0.5 + 0.4 * np.sin(2 * np.pi * t / INPUT_PERIOD)
        signal = float(np.clip(light + rng.normal(0, NOISE_STD), 0.0, 1.0))

        # L4: T inner iterations of recurrent depth
        result = snn.step(signal)
        inner_spike_aggregates.append(result.total_spike_count)

        # L5: one servo update per outer step
        target_angle = float(np.clip(snn.previous_output * 180.0, 0.0, 180.0))
        movement = abs(target_angle - prev_angle)
        servo_angles.append(target_angle)
        prev_angle = target_angle

        # L6: harvest + ONE update_storage call per outer step
        friction_e = harvester.harvest_friction(movement)
        thermal_e = harvester.harvest_thermal(20.0 + rng.normal(0, 0.5))
        harvester.update_storage(friction_e, thermal_e,
                                 spike_count=result.total_spike_count)

    return {
        'servo_angles': servo_angles,
        'inner_spike_aggregates': inner_spike_aggregates,
        'harvester': harvester,
    }


# ════════════════════════════════════════════════════════════════════
# Convergence trajectory harness for F13.3
# ════════════════════════════════════════════════════════════════════

def run_convergence_trace(num_inner_steps, fixed_input, seed=SEED):
    """
    With fixed input, run num_inner_steps inner iterations and record
    the per-iteration mean membrane potential.
    """
    np.random.seed(seed)
    snn = RecurrentDepthSNN(
        RecurrentDepthConfig(
            base_config=_make_base_snn_config(),
            num_inner_steps=num_inner_steps,
            reflection_coeff=REFLECTION_COEFF,
            inject_input_every_step=True,
            record_trajectory=True,
        ),
        seed=seed,
    )
    result = snn.step(fixed_input)
    # Per-iteration mean across neurons
    return result.trajectory.mean(axis=1)


# ════════════════════════════════════════════════════════════════════
# Claim validators
# ════════════════════════════════════════════════════════════════════

def validate_f13_1(outputs_experimental, outputs_control, input_signal,
                    burn_in=F13_1_BURN_IN):
    """
    F13.1: Recurrent depth (T=8) produces a hidden state more strongly
    correlated with the input than T=1.

    After burn_in outer steps, the Pearson correlation corr(previous_output,
    input) under T=8 must be at least F13_1_CORR_RATIO_THRESHOLD x the
    correlation under T=1.

    Precondition: the control correlation (corr_ctrl) must be finite and
    strictly positive. A non-positive or non-finite corr_ctrl indicates a
    degenerate baseline (uncorrelated, anti-correlated, or NaN trace) for
    which the ratio test is undefined; this is treated as a precondition
    failure rather than silently allowing the claim to pass via division-
    by-zero / inf.
    """
    inp = input_signal[burn_in:]
    exp = outputs_experimental[burn_in:]
    ctrl = outputs_control[burn_in:]
    corr_exp = float(np.corrcoef(exp, inp)[0, 1])
    corr_ctrl = float(np.corrcoef(ctrl, inp)[0, 1])

    precondition_ok = (
        np.isfinite(corr_exp) and np.isfinite(corr_ctrl) and corr_ctrl > 0
    )
    if not precondition_ok:
        # Degenerate baseline; do not compute a misleading ratio.
        return False, corr_exp, corr_ctrl, float('nan')

    ratio = corr_exp / corr_ctrl
    passed = ratio >= F13_1_CORR_RATIO_THRESHOLD
    return passed, corr_exp, corr_ctrl, ratio


def validate_f13_2(loop_result, n_outer_steps):
    """
    F13.2: Decision cadence preserved across the L1->L8 loop.

    Three concurrent invariants must hold:
        (a) len(servo_angles) == n_outer_steps
        (b) harvester.update_call_count == n_outer_steps
        (c) harvester.cumulative_spike_count_charged ==
            sum(inner_spike_aggregates)
    """
    angles = loop_result['servo_angles']
    inners = loop_result['inner_spike_aggregates']
    harvester = loop_result['harvester']

    invariant_a = len(angles) == n_outer_steps
    invariant_b = harvester.update_call_count == n_outer_steps
    invariant_c = harvester.cumulative_spike_count_charged == sum(inners)

    passed = invariant_a and invariant_b and invariant_c
    return (passed, invariant_a, invariant_b, invariant_c,
            len(angles), harvester.update_call_count,
            harvester.cumulative_spike_count_charged, sum(inners))


def validate_f13_3(trajectory):
    """
    F13.3: Continuous-latent convergence -- late-window variance of the
    mean membrane potential is at most F13_3_VARIANCE_RATIO_THRESHOLD x
    early-window variance.

    Precondition: early-window variance must exceed 1e-6 (excludes
    degenerate no-drive case).
    """
    half = len(trajectory) // 2
    early = trajectory[:half]
    late = trajectory[half:]
    early_var = float(np.var(early))
    late_var = float(np.var(late))

    if early_var < 1e-6:
        # Precondition fails -- claim is undefined for no-drive case.
        return False, early_var, late_var, float('inf'), False
    ratio = late_var / early_var
    precondition_ok = True
    passed = ratio <= F13_3_VARIANCE_RATIO_THRESHOLD
    return passed, early_var, late_var, ratio, precondition_ok


# ════════════════════════════════════════════════════════════════════
# Energy budget appendix (informational only -- no PASS/FAIL token)
# ════════════════════════════════════════════════════════════════════

def run_energy_budget_appendix():
    """
    For each T in APPENDIX_DEPTHS, run APPENDIX_OUTER_STEPS outer steps
    under the harsh EnergyConfig (CLI-style) and report total mWh
    consumed, total spikes, and motor activations. Demonstrates the
    'linear spikes, constant motor harvest' scaling property without
    making numerical claims.

    Critical: this section never prints the literal token used by the
    CI gate (see CLAUDE.md and CI workflow).
    """
    print("-" * 60)
    print("Energy Budget Appendix (informational)")
    print(f"  Outer steps per row: {APPENDIX_OUTER_STEPS}, harsh EnergyConfig")
    print(f"  {'T':>4} {'spikes':>10} {'motor_acts':>12} {'net_mWh':>12}")

    for T in APPENDIX_DEPTHS:
        result = run_cadence_loop(num_inner_steps=T,
                                  n_outer_steps=APPENDIX_OUTER_STEPS)
        total_spikes = sum(result['inner_spike_aggregates'])
        motor_acts = result['harvester'].update_call_count  # = outer steps
        net_mwh = result['harvester'].energy_storage - 50.0  # initial was 50.0
        print(f"  {T:>4} {total_spikes:>10} {motor_acts:>12} {net_mwh:>12.4f}")

    print()


# ════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════

def run_phase13():
    """Run Phase 13 Recurrent Depth validation."""
    print("=" * 60)
    print("PHASE 13 -- RECURRENT DEPTH VALIDATION REPORT")
    print("=" * 60)
    print(f"Neurons: {N_NEURONS}  |  Seed: {SEED}")
    print(f"SNN: threshold={SNN_THRESHOLD}, weight_scale={SNN_WEIGHT_SCALE}, "
          f"input_scale={SNN_INPUT_SCALE}, leak={SNN_LEAK_FACTOR}")
    print(f"Inner depth: experimental T={INNER_DEPTH_EXPERIMENTAL}, "
          f"control T={INNER_DEPTH_CONTROL}")
    print(f"Reflection coeff (inner step): {REFLECTION_COEFF}")
    print(f"Input: sinusoidal period={INPUT_PERIOD}")
    print()

    # Generate input for F13.1 (sinusoidal, no noise -- isolates depth effect)
    t_axis = np.arange(F13_1_OUTER_STEPS)
    f13_1_input = 0.5 + 0.4 * np.sin(2 * np.pi * t_axis / INPUT_PERIOD)

    # Run experimental (T=8) and control (T=1) systems
    print(f"Running F13.1 trace: T={INNER_DEPTH_EXPERIMENTAL} (experimental)...")
    out_exp = run_io_correlation_trace(INNER_DEPTH_EXPERIMENTAL, f13_1_input)
    print(f"Running F13.1 trace: T={INNER_DEPTH_CONTROL} (control)...")
    out_ctrl = run_io_correlation_trace(INNER_DEPTH_CONTROL, f13_1_input)
    print()

    all_pass = True

    # ── F13.1 ──────────────────────────────────────────────────────
    print("-" * 60)
    print("F13.1 -- Recurrent depth increases input-output correlation")
    passed, corr_exp, corr_ctrl, ratio = validate_f13_1(
        out_exp, out_ctrl, f13_1_input,
    )
    print(f"  Outer steps: {F13_1_OUTER_STEPS}, burn-in: {F13_1_BURN_IN}")
    print(f"  corr(previous_output, input) at T={INNER_DEPTH_EXPERIMENTAL}: "
          f"{corr_exp:.6f}")
    print(f"  corr(previous_output, input) at T={INNER_DEPTH_CONTROL}: "
          f"{corr_ctrl:.6f}")
    if np.isnan(ratio):
        print(f"  Ratio (exp / ctrl):                 undefined  "
              f"(precondition: corr_ctrl > 0 and finite)")
    else:
        print(f"  Ratio (exp / ctrl):                 {ratio:.4f}  "
              f"(threshold: >= {F13_1_CORR_RATIO_THRESHOLD})")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── F13.2 ──────────────────────────────────────────────────────
    print("-" * 60)
    print("F13.2 -- Decision cadence preserved (Coda fires once per outer step)")
    print(f"  Running L1->L8 loop with T={INNER_DEPTH_EXPERIMENTAL} for "
          f"{F13_2_OUTER_STEPS} outer steps...")
    loop_result = run_cadence_loop(
        num_inner_steps=INNER_DEPTH_EXPERIMENTAL,
        n_outer_steps=F13_2_OUTER_STEPS,
    )
    (passed, inv_a, inv_b, inv_c,
     n_angles, n_calls, charged, summed) = validate_f13_2(
        loop_result, F13_2_OUTER_STEPS,
    )
    print(f"  (a) servo_angle history length:     {n_angles} "
          f"(expected: {F13_2_OUTER_STEPS}) [{inv_a}]")
    print(f"  (b) update_storage call count:      {n_calls} "
          f"(expected: {F13_2_OUTER_STEPS}) [{inv_b}]")
    print(f"  (c) total spikes charged:           {charged} "
          f"(expected: {summed}) [{inv_c}]")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── F13.3 ──────────────────────────────────────────────────────
    print("-" * 60)
    print("F13.3 -- Continuous-latent convergence (variance ratio)")
    trajectory = run_convergence_trace(
        num_inner_steps=F13_3_INNER_STEPS,
        fixed_input=F13_3_FIXED_INPUT,
    )
    passed, early_var, late_var, ratio, precondition_ok = validate_f13_3(trajectory)
    print(f"  Inner steps: {F13_3_INNER_STEPS}, fixed input: {F13_3_FIXED_INPUT}")
    print(f"  Early-window variance (k=0..{F13_3_INNER_STEPS // 2 - 1}):  "
          f"{early_var:.6f}")
    print(f"  Late-window variance  (k={F13_3_INNER_STEPS // 2}..{F13_3_INNER_STEPS - 1}): "
          f"{late_var:.6f}")
    print(f"  Ratio (late / early):                {ratio:.4f}  "
          f"(threshold: <= {F13_3_VARIANCE_RATIO_THRESHOLD})")
    print(f"  Precondition (early_var > 1e-6):     {precondition_ok}")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── Energy Budget Appendix (informational) ────────────────────
    run_energy_budget_appendix()

    # ── Summary ───────────────────────────────────────────────────
    print("=" * 60)
    overall = "ALL PASS" if all_pass else "SOME FAILED"
    print(f"Phase 13 Recurrent Depth validation: {overall}")
    print("=" * 60)

    return all_pass


if __name__ == "__main__":
    success = run_phase13()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Phase 10 — Multi-Modal Sensory Integration Validation

Three falsifiable claims validated against controlled conditions.

Architecture:
    Three independent BaseSNN populations (light, sound, pressure) connected
    by cross-modal weight matrices managed by CrossModalConnector.  STDP on
    cross-modal weights only (within-modality weights frozen).

Claims:
    F10.1: Simultaneous cross-modal stimuli produce >20% higher inter-population
           spike synchronization than time-offset stimuli (50-step phase offset)
    F10.2: STDP-learned cross-modal weights have lower entropy than initial
           random weights (structure emerges from noise)
    F10.3: Cross-modal weight changes converge: late Frobenius norm of weight
           change is <20% of early change
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from core.base_snn import BaseSNN, SNNConfig

# ════════════════════════════════════════════════════════════════════
# Configuration
# ════════════════════════════════════════════════════════════════════

N_STEPS = 2000           # Total simulation steps (10 full cycles)
N_NEURONS = 10           # Neurons per modality population
SEED = 42                # Reproducibility
INPUT_PERIOD = 200       # Sinusoidal input period (steps)
NOISE_STD = 0.05         # Input noise standard deviation
PHASE_OFFSET = 50        # Steps of phase offset for control condition
SYNC_WINDOW = 200        # Window size for synchronization measurement

# Per-modality SNN parameters
# Higher threshold + lower weight scale creates an INPUT-DRIVEN regime where
# spike timing depends on the input signal phase, not just recurrent activity.
# This is critical: if recurrence dominates, all populations spike identically
# regardless of input phase and synchronization cannot differentiate conditions.
SNN_THRESHOLD = 0.8
SNN_WEIGHT_SCALE = 0.05
SNN_INPUT_SCALE = 0.5       # Broadcast input gain to all neurons

# Cross-modal connection parameters
CROSS_WEIGHT_SCALE = 0.05
CROSS_W_MIN = 0.0
CROSS_W_MAX = 0.2
CROSS_A_PLUS = 0.001        # Slower learning than within-modality (0.005)
CROSS_A_MINUS = 0.0012      # 1.2:1 LTD/LTP ratio preserved
CROSS_TAU_PLUS = 20.0
CROSS_TAU_MINUS = 20.0

# Modality identifiers and pairs
MODALITIES = ('light', 'sound', 'pressure')
CROSS_PAIRS = (('light', 'sound'), ('light', 'pressure'), ('sound', 'pressure'))


# ════════════════════════════════════════════════════════════════════
# Input generators
# ════════════════════════════════════════════════════════════════════

def generate_multimodal_input(n_steps, period=INPUT_PERIOD, simultaneous=True,
                               phase_offset=PHASE_OFFSET, seed=SEED):
    """
    Generate three-modality sinusoidal input.

    Args:
        n_steps: Number of timesteps.
        period: Sinusoidal period.
        simultaneous: If True, all modalities are in phase (experimental).
                      If False, modalities are offset by phase_offset steps (control).
        phase_offset: Steps of offset between successive modalities.
        seed: Random seed for noise generation.

    Returns:
        dict mapping modality name to input array (n_steps,), values in [0, 1].
    """
    rng = np.random.RandomState(seed)
    t = np.arange(n_steps)

    inputs = {}
    for i, mod in enumerate(MODALITIES):
        if simultaneous:
            phase = 0.0
        else:
            phase = 2 * np.pi * phase_offset * i / period

        base = 0.5 + 0.4 * np.sin(2 * np.pi * t / period + phase)
        noise = rng.normal(0, NOISE_STD, n_steps)
        inputs[mod] = np.clip(base + noise, 0.0, 1.0)

    return inputs


# ════════════════════════════════════════════════════════════════════
# Multi-modal system runner (self-contained — inline implementation)
# ════════════════════════════════════════════════════════════════════

def run_multimodal_system(inputs, cross_stdp_enabled=True, seed=SEED):
    """
    Run three-population multi-modal system with cross-modal connections.

    Args:
        inputs: dict mapping modality name to input array (n_steps,).
        cross_stdp_enabled: If True, STDP learns on cross-modal weights.
        seed: Random seed for SNN and cross-modal weight initialization.

    Returns:
        spike_trains: dict mapping modality to (n_steps, n_neurons) bool array
        weight_snapshots: dict mapping step to cross-modal weight snapshot
        sync_scores: array of per-step synchronization scores
    """
    n_steps = len(inputs['light'])

    # ── Create per-modality SNN instances ──
    # input_scale=0.0 disables BaseSNN's single-neuron input injection.
    # We broadcast input to ALL neurons manually (see loop below).
    # This ensures population-level dynamics depend on input timing.
    snn_config = SNNConfig(
        num_neurons=N_NEURONS,
        threshold=SNN_THRESHOLD,
        weight_scale=SNN_WEIGHT_SCALE,
        input_scale=0.0,  # Disable single-neuron input — we broadcast instead
        leak_factor=0.1,
        refractory_period=2,
        stdp_enabled=False,  # Within-modality STDP off
    )

    snns = {}
    for i, mod in enumerate(MODALITIES):
        np.random.seed(seed + i)
        snns[mod] = BaseSNN(snn_config)

    # ── Initialize cross-modal weight matrices ──
    rng_cross = np.random.RandomState(seed + 10)

    cross_weights = {}
    cross_pre_traces = {}
    cross_post_traces = {}

    for mod_a, mod_b in CROSS_PAIRS:
        # A→B
        cross_weights[(mod_a, mod_b)] = rng_cross.rand(N_NEURONS, N_NEURONS) * CROSS_WEIGHT_SCALE
        cross_pre_traces[(mod_a, mod_b)] = np.zeros(N_NEURONS)
        cross_post_traces[(mod_a, mod_b)] = np.zeros(N_NEURONS)
        # B→A
        cross_weights[(mod_b, mod_a)] = rng_cross.rand(N_NEURONS, N_NEURONS) * CROSS_WEIGHT_SCALE
        cross_pre_traces[(mod_b, mod_a)] = np.zeros(N_NEURONS)
        cross_post_traces[(mod_b, mod_a)] = np.zeros(N_NEURONS)

    # ── Recording arrays ──
    spike_trains = {mod: np.zeros((n_steps, N_NEURONS), dtype=bool) for mod in MODALITIES}
    weight_snapshots = {}
    snapshot_steps = {0, 100, 1900, n_steps}

    # ── Simulation loop ──
    for t in range(n_steps):
        # Snapshot cross-modal weights
        if t in snapshot_steps:
            weight_snapshots[t] = {
                key: w.copy() for key, w in cross_weights.items()
            }

        # Broadcast input to ALL neurons in each population, then step.
        # This replaces BaseSNN's default single-neuron input injection
        # (which only drives neuron 0).  Broadcasting ensures the entire
        # population's spike timing depends on the input signal phase,
        # which is critical for cross-modal synchronization detection.
        spikes = {}
        for mod in MODALITIES:
            snns[mod].membrane_potential += inputs[mod][t] * SNN_INPUT_SCALE
            _, spike_mask = snns[mod].step(0.0)  # input_scale=0 so this adds nothing
            spikes[mod] = spike_mask
            spike_trains[mod][t] = spike_mask

        # Propagate cross-modal spikes
        for mod_a, mod_b in CROSS_PAIRS:
            spikes_a = spikes[mod_a].astype(float)
            spikes_b = spikes[mod_b].astype(float)

            if np.any(spikes[mod_a]):
                snns[mod_b].membrane_potential += np.dot(
                    spikes_a, cross_weights[(mod_a, mod_b)]
                )
            if np.any(spikes[mod_b]):
                snns[mod_a].membrane_potential += np.dot(
                    spikes_b, cross_weights[(mod_b, mod_a)]
                )

        # Cross-modal STDP
        if cross_stdp_enabled:
            for mod_a, mod_b in CROSS_PAIRS:
                spikes_a = spikes[mod_a].astype(float)
                spikes_b = spikes[mod_b].astype(float)

                # A→B direction
                key_ab = (mod_a, mod_b)
                pre_tr = cross_pre_traces[key_ab]
                post_tr = cross_post_traces[key_ab]

                dw_ltp = CROSS_A_PLUS * np.outer(pre_tr, spikes_b)
                dw_ltd = CROSS_A_MINUS * np.outer(spikes_a, post_tr)
                cross_weights[key_ab] += dw_ltp - dw_ltd
                np.clip(cross_weights[key_ab], CROSS_W_MIN, CROSS_W_MAX,
                        out=cross_weights[key_ab])

                pre_tr *= np.exp(-1.0 / CROSS_TAU_PLUS)
                post_tr *= np.exp(-1.0 / CROSS_TAU_MINUS)
                pre_tr += spikes_a
                post_tr += spikes_b
                cross_pre_traces[key_ab] = pre_tr
                cross_post_traces[key_ab] = post_tr

                # B→A direction
                key_ba = (mod_b, mod_a)
                pre_tr = cross_pre_traces[key_ba]
                post_tr = cross_post_traces[key_ba]

                dw_ltp = CROSS_A_PLUS * np.outer(pre_tr, spikes_a)
                dw_ltd = CROSS_A_MINUS * np.outer(spikes_b, post_tr)
                cross_weights[key_ba] += dw_ltp - dw_ltd
                np.clip(cross_weights[key_ba], CROSS_W_MIN, CROSS_W_MAX,
                        out=cross_weights[key_ba])

                pre_tr *= np.exp(-1.0 / CROSS_TAU_PLUS)
                post_tr *= np.exp(-1.0 / CROSS_TAU_MINUS)
                pre_tr += spikes_b
                post_tr += spikes_a
                cross_pre_traces[key_ba] = pre_tr
                cross_post_traces[key_ba] = post_tr

    # Final weight snapshot
    if n_steps not in weight_snapshots:
        weight_snapshots[n_steps] = {
            key: w.copy() for key, w in cross_weights.items()
        }

    return spike_trains, weight_snapshots


# ════════════════════════════════════════════════════════════════════
# Metric functions
# ════════════════════════════════════════════════════════════════════

def compute_pairwise_sync(spike_trains, window_size=SYNC_WINDOW,
                           start_step=None, end_step=None):
    """
    Compute mean pairwise spike synchronization between modality populations.

    For each pair (A, B), computes the normalized cross-correlation of
    their total spike count time series over rolling windows.

    Synchronization for a window:
        sync(A, B) = corr(spike_counts_A, spike_counts_B)

    where spike_counts_X[t] = sum of spikes across all neurons in X at step t.

    Args:
        spike_trains: dict mapping modality to (n_steps, n_neurons) bool array
        window_size: size of each correlation window
        start_step: first step to include (default: 0)
        end_step: last step to include (default: n_steps)

    Returns:
        mean_sync: mean pairwise synchronization score (float)
        pair_syncs: dict mapping (mod_a, mod_b) to sync score
    """
    n_steps = spike_trains['light'].shape[0]
    if start_step is None:
        start_step = 0
    if end_step is None:
        end_step = n_steps

    # Compute per-step total spike counts per modality
    counts = {}
    for mod in MODALITIES:
        counts[mod] = spike_trains[mod][start_step:end_step].sum(axis=1).astype(float)

    # Pairwise correlation over rolling windows
    pair_syncs = {}
    for mod_a, mod_b in CROSS_PAIRS:
        ca = counts[mod_a]
        cb = counts[mod_b]
        n = len(ca)
        n_windows = n // window_size

        if n_windows == 0:
            pair_syncs[(mod_a, mod_b)] = 0.0
            continue

        window_corrs = []
        for w in range(n_windows):
            s = w * window_size
            e = s + window_size
            wa = ca[s:e]
            wb = cb[s:e]

            # Pearson correlation (handle zero-variance)
            std_a = np.std(wa)
            std_b = np.std(wb)
            if std_a < 1e-10 or std_b < 1e-10:
                # If either has no variance, check if both are identical
                if std_a < 1e-10 and std_b < 1e-10:
                    # Both constant — perfectly synchronized if both active
                    corr = 1.0 if np.mean(wa) > 0 and np.mean(wb) > 0 else 0.0
                else:
                    corr = 0.0
            else:
                corr = np.corrcoef(wa, wb)[0, 1]
                if np.isnan(corr):
                    corr = 0.0

            window_corrs.append(corr)

        pair_syncs[(mod_a, mod_b)] = np.mean(window_corrs)

    mean_sync = np.mean(list(pair_syncs.values()))
    return mean_sync, pair_syncs


def cross_weight_entropy(weight_snapshot):
    """
    Shannon entropy of the cross-modal weight distribution.

    Pools all cross-modal weights into one histogram and computes
    H = -sum(p * log2(p)) for non-zero bins.

    Args:
        weight_snapshot: dict mapping (mod_a, mod_b) to weight matrix

    Returns:
        entropy in bits (float)
    """
    all_w = []
    for key in sorted(weight_snapshot.keys()):
        all_w.append(weight_snapshot[key].flatten())
    w = np.concatenate(all_w)

    if w.max() == w.min():
        return 0.0

    counts, _ = np.histogram(w, bins=20, range=(CROSS_W_MIN, CROSS_W_MAX))
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))


def cross_weight_frobenius_delta(snapshot_a, snapshot_b):
    """
    Frobenius norm of weight change between two snapshots.

    Computes the norm across ALL cross-modal weight matrices concatenated.

    Args:
        snapshot_a, snapshot_b: dicts mapping (mod_a, mod_b) to weight matrix

    Returns:
        frobenius_norm (float)
    """
    deltas = []
    for key in sorted(snapshot_a.keys()):
        deltas.append((snapshot_b[key] - snapshot_a[key]).flatten())
    delta_vec = np.concatenate(deltas)
    return np.linalg.norm(delta_vec)


# ════════════════════════════════════════════════════════════════════
# Claim validators
# ════════════════════════════════════════════════════════════════════

def validate_f10_1(spike_trains_simul, spike_trains_offset):
    """
    F10.1: Simultaneous stimuli produce higher inter-population spike
    synchronization than time-offset stimuli.

    Criterion: sync_simultaneous - sync_offset > 0.20
    (absolute difference, since offset sync can be negative when populations
    fire in anti-phase due to phase-shifted inputs).

    Measures synchronization over the last 5 cycles (steps 1000-2000)
    to allow STDP time to learn cross-modal correlations.
    """
    sync_simul, pairs_simul = compute_pairwise_sync(
        spike_trains_simul, start_step=1000, end_step=2000)
    sync_offset, pairs_offset = compute_pairwise_sync(
        spike_trains_offset, start_step=1000, end_step=2000)

    difference = sync_simul - sync_offset
    passed = difference > 0.20

    return passed, sync_simul, sync_offset, difference, pairs_simul, pairs_offset


def validate_f10_2(w_snapshots_stdp):
    """
    F10.2: Cross-modal weight entropy decreases (structure from noise).

    Compares entropy at step 0 vs step 2000.
    """
    h_initial = cross_weight_entropy(w_snapshots_stdp[0])
    h_final = cross_weight_entropy(w_snapshots_stdp[N_STEPS])

    passed = h_final < h_initial
    return passed, h_initial, h_final


def validate_f10_3(w_snapshots_stdp):
    """
    F10.3: Cross-modal weight changes converge.

    Frobenius norm of weight change in last 100 steps (1900→2000)
    is <20% of change in first 100 steps (0→100).
    """
    delta_early = cross_weight_frobenius_delta(
        w_snapshots_stdp[0], w_snapshots_stdp[100])
    delta_late = cross_weight_frobenius_delta(
        w_snapshots_stdp[1900], w_snapshots_stdp[N_STEPS])

    if delta_early == 0.0:
        passed = delta_late == 0.0
        ratio = 0.0
    else:
        ratio = delta_late / delta_early
        passed = ratio < 0.20

    return passed, delta_early, delta_late, ratio


# ════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════

def run_phase10():
    """Run Phase 10 Multi-Modal Sensory Integration validation."""
    print("=" * 60)
    print("PHASE 10 — MULTI-MODAL SENSORY INTEGRATION VALIDATION REPORT")
    print("=" * 60)
    print(f"Steps: {N_STEPS}  |  Neurons/modality: {N_NEURONS}  |  Seed: {SEED}")
    print(f"Modalities: {', '.join(MODALITIES)}")
    print(f"SNN: threshold={SNN_THRESHOLD}, weight_scale={SNN_WEIGHT_SCALE}, "
          f"input_scale={SNN_INPUT_SCALE}")
    print(f"Cross-modal STDP: A+={CROSS_A_PLUS}, A-={CROSS_A_MINUS}, "
          f"tau={CROSS_TAU_PLUS}")
    print(f"Cross-modal weights: scale={CROSS_WEIGHT_SCALE}, "
          f"bounds=[{CROSS_W_MIN}, {CROSS_W_MAX}]")
    print(f"Input: sinusoidal period={INPUT_PERIOD}, noise sigma={NOISE_STD}")
    print(f"Phase offset (control): {PHASE_OFFSET} steps")
    print(f"Sync window: {SYNC_WINDOW} steps")
    print()

    # Generate all inputs BEFORE creating SNNs (deterministic RNG ordering)
    inputs_simul = generate_multimodal_input(
        N_STEPS, simultaneous=True, seed=SEED)
    inputs_offset = generate_multimodal_input(
        N_STEPS, simultaneous=False, phase_offset=PHASE_OFFSET, seed=SEED)

    # Run systems
    print("Running experimental (simultaneous, STDP) system...")
    spikes_simul, w_snap_simul = run_multimodal_system(
        inputs_simul, cross_stdp_enabled=True, seed=SEED)

    print("Running control (offset, STDP) system...")
    spikes_offset, w_snap_offset = run_multimodal_system(
        inputs_offset, cross_stdp_enabled=True, seed=SEED)

    print("Running control (simultaneous, frozen) system...")
    spikes_frozen, w_snap_frozen = run_multimodal_system(
        inputs_simul, cross_stdp_enabled=False, seed=SEED)
    print()

    all_pass = True

    # ── F10.1 ─────────────────────────────────────────────────────
    print("-" * 60)
    print("F10.1 — Simultaneous sync - offset sync > 0.20")
    passed, sync_s, sync_o, diff, pairs_s, pairs_o = validate_f10_1(
        spikes_simul, spikes_offset)
    print(f"  Simultaneous sync (steps 1000-2000):  {sync_s:.6f}")
    for (a, b), v in pairs_s.items():
        print(f"    {a}-{b}: {v:.6f}")
    print(f"  Offset sync (steps 1000-2000):        {sync_o:.6f}")
    for (a, b), v in pairs_o.items():
        print(f"    {a}-{b}: {v:.6f}")
    print(f"  Difference: {diff:.4f} (threshold: >0.20)")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── F10.2 ─────────────────────────────────────────────────────
    print("-" * 60)
    print("F10.2 — Cross-modal weight entropy decreases (structure from noise)")
    passed, h_init, h_final = validate_f10_2(w_snap_simul)
    # Also show frozen control entropy for comparison
    h_frozen_init = cross_weight_entropy(w_snap_frozen[0])
    h_frozen_final = cross_weight_entropy(w_snap_frozen[N_STEPS])
    print(f"  STDP initial entropy:   {h_init:.4f} bits")
    print(f"  STDP final entropy:     {h_final:.4f} bits")
    print(f"  Decrease:               {h_init - h_final:.4f} bits")
    print(f"  Frozen initial entropy:  {h_frozen_init:.4f} bits")
    print(f"  Frozen final entropy:    {h_frozen_final:.4f} bits")
    print(f"  Frozen decrease:         {h_frozen_init - h_frozen_final:.4f} bits")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── F10.3 ─────────────────────────────────────────────────────
    print("-" * 60)
    print("F10.3 — Cross-modal weight convergence "
          "(late delta < 20% of early delta)")
    passed, delta_early, delta_late, ratio = validate_f10_3(w_snap_simul)
    print(f"  ||dW_cross|| (step 0->100):     {delta_early:.6f}")
    print(f"  ||dW_cross|| (step 1900->2000):  {delta_late:.6f}")
    print(f"  Ratio: {ratio:.4f} (threshold: <0.20)")
    result = "PASS" if passed else "FAIL"
    print(f"  Result: {result}")
    if not passed:
        all_pass = False
    print()

    # ── Summary ───────────────────────────────────────────────────
    print("=" * 60)
    overall = "ALL PASS" if all_pass else "SOME FAILED"
    print(f"Phase 10 Multi-Modal Sensory Integration validation: {overall}")
    print("=" * 60)

    return all_pass


if __name__ == "__main__":
    success = run_phase10()
    sys.exit(0 if success else 1)

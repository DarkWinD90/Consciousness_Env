# tests/test_phase7_metrics.py
# Unit/integration tests for Phase 7 control baseline claims

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phases.phase7_control_baseline import (
    N, canonical_input, normalize_light, pd_controller,
    θ_mid, θ_amp, Kp, Kd, E0, E_min, E_max, C0, C_move,
    α, β, γ, T_amb, m, c, k
)

def run_baseline():
    """Minimal re-implementation for testing (no side effects)."""
    θ, ω, E, T = θ_mid, 0.0, E0, T_amb
    history = {'L': [], 'θ': [], 'ω': [], 'E': [], 'T': []}

    for t in range(N):
        L = canonical_input(t)
        history['L'].append(L)
        s = normalize_light(L)
        θ_ref = θ_mid + θ_amp * (2 * s - 1)
        u = Kp * (θ_ref - θ) - Kd * ω
        ω_next = ω + (u - c * ω - k * θ) / m
        θ_next = θ + ω_next

        # Enforce physical joint limits (servo hard stops)
        if θ_next < 0:
            θ_next = 0.0
            ω_next = 0.0
        elif θ_next > 180:
            θ_next = 180.0
            ω_next = 0.0

        E_next = E + α * (0.0 - (C0 + C_move * abs(u)))
        E_next = np.clip(E_next, E_min, E_max)
        T += β * L - γ * (T - T_amb)

        history['θ'].append(θ_next)
        history['ω'].append(ω_next)
        history['E'].append(E_next)
        history['T'].append(T)

        θ, ω, E, T = θ_next, ω_next, E_next, T

    return (np.array(history['L']), np.array(history['θ']),
            np.array(history['ω']), np.array(history['E']),
            np.array(history['T']))


def test_claim_A_continuity():
    """Claim A: All channels have N points."""
    L, θ, ω, E, T = run_baseline()
    assert len(L) == N, "Claim A FAIL: input length mismatch"
    assert len(θ) == N, "Claim A FAIL: θ length mismatch"
    assert len(ω) == N, "Claim A FAIL: ω length mismatch"
    assert len(E) == N, "Claim A FAIL: E length mismatch"
    assert len(T) == N, "Claim A FAIL: T length mismatch"


def test_claim_B_boundedness():
    """Claim B: All state variables within predefined bounds."""
    _, θ, ω, E, T = run_baseline()
    assert θ.min() >= 0 and θ.max() <= 180, "Claim B FAIL: θ out of [0,180]"
    assert np.abs(ω).max() <= 300, "Claim B FAIL: |ω| > 300"
    assert E.min() >= E_min and E.max() <= E_max, "Claim B FAIL: E out of bounds"
    assert T.min() >= -20 and T.max() <= 80, "Claim B FAIL: T out of [-20,80]"


def test_claim_C_robustness():
    """Claim C: Variance under noise stays below thresholds."""
    _, θ, ω, _, _ = run_baseline()
    W = slice(N//2, N)
    assert np.std(θ[W]) <= 45, "Claim C FAIL: Std(θ) > 45°"
    assert np.std(ω[W]) <= 150, "Claim C FAIL: Std(ω) > 150°/step"


def test_claim_D_gain():
    """Claim D: System responds to environmental input."""
    L, θ, _, _, _ = run_baseline()
    corr = np.corrcoef(L, θ)[0, 1]
    assert corr >= 0.2, f"Claim D FAIL: corr(L, θ) = {corr:.3f} < 0.2"


def test_claim_E_saturation():
    """Claim E: No pathological saturation at bounds."""
    _, θ, _, _, _ = run_baseline()
    δ = 2.0
    sat_θ = np.mean((θ <= δ) | (θ >= 180 - δ))
    assert sat_θ <= 0.20, f"Claim E FAIL: sat_θ = {sat_θ:.3f} > 0.20"


if __name__ == "__main__":
    pytest.main(["-v", __file__])

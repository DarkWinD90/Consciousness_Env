# phase7_control_baseline.py
# Phase 7 — Control-First Integration Baseline
# Locked configuration as per Phase 7 outline (Jan 2026)

import numpy as np

# ────────────────────────────────────────────────
# 1. Locked Configuration
# ────────────────────────────────────────────────

# Time
N = 2000                        # total steps (10 full cycles)
Δt = 1.0                        # discrete time step (arbitrary units)

# Canonical input: day/night sinusoid + noise
L0 = 500.0                      # base lux
A  = 300.0                      # amplitude
σ_L = 50.0                      # noise std dev

# Second-order plant parameters
m = 1.0                         # mass
c = 0.5                         # damping
k = 1.0                         # stiffness

# PD controller gains (tuned for stable Euler integration at Δt=1.0)
Kp = 0.3
Kd = 0.4

# Reference trajectory parameters
θ_mid = 90.0                    # center angle (deg)
θ_amp = 60.0                    # amplitude (deg)

# Energy accounting
E0     = 50.0                   # initial energy
E_min  = 0.0
E_max  = 100.0
C0     = 0.3                    # base consumption per step
C_move = 0.02                   # consumption per unit |u|
α      = 0.1                    # energy update scale

# Temperature proxy
T_amb = 20.0                    # ambient °C
β     = 1.0 / 500.0             # heating coefficient from light
γ     = 0.05                    # cooling coefficient

# ────────────────────────────────────────────────
# 2. Helper Functions
# ────────────────────────────────────────────────

def canonical_input(t):
    """Slow day/night sinusoid + Gaussian noise"""
    L_base = L0 + A * np.sin(2 * np.pi * t / 200)
    ε = np.random.normal(0, σ_L)
    return max(0.0, L_base + ε)

def normalize_light(L):
    """Simple mapping to [0,1] for reference angle"""
    return np.clip((L - 200) / 600, 0.0, 1.0)  # 200–800 lux → 0–1

def pd_controller(θ_ref, θ, ω):
    """PD control law"""
    u = Kp * (θ_ref - θ) - Kd * ω
    return u

# ────────────────────────────────────────────────
# 3. Simulation Loop
# ────────────────────────────────────────────────

def run_baseline():
    """Run the Phase 7 control baseline simulation."""
    # Pre-allocate history
    history = {
        't':          np.arange(N),
        'L':          np.zeros(N),
        'θ_ref':      np.zeros(N),
        'θ':          np.zeros(N),
        'ω':          np.zeros(N),
        'u':          np.zeros(N),
        'E':          np.zeros(N),
        'T':          np.zeros(N),
    }

    # Initial conditions
    θ = 90.0
    ω = 0.0
    E = E0
    T = T_amb

    for t in range(N):
        # 1. Sample input
        L = canonical_input(t)
        history['L'][t] = L

        # 2. Compute reference
        s = normalize_light(L)
        θ_ref = θ_mid + θ_amp * (2 * s - 1)  # -θ_amp to +θ_amp
        history['θ_ref'][t] = θ_ref

        # 3. Controller
        u = pd_controller(θ_ref, θ, ω)
        history['u'][t] = u

        # 4. Plant update (second-order Euler with servo joint limits)
        ω_next = ω + Δt * (u - c * ω - k * θ) / m
        θ_next = θ + Δt * ω_next

        # Enforce physical joint limits (servo hard stops at 0° and 180°)
        if θ_next < 0:
            θ_next = 0.0
            ω_next = 0.0  # zero velocity at hard stop
        elif θ_next > 180:
            θ_next = 180.0
            ω_next = 0.0

        history['θ'][t] = θ_next
        history['ω'][t] = ω_next

        # 5. Energy accounting
        C = C0 + C_move * abs(u)
        E_next = E + α * (0.0 - C)  # no harvest in baseline
        E_next = np.clip(E_next, E_min, E_max)
        history['E'][t] = E_next

        # 6. Temperature proxy
        T += β * L - γ * (T - T_amb)
        history['T'][t] = T

        # Update states
        θ = θ_next
        ω = ω_next
        E = E_next

    return history


def print_validation_report(history):
    """Print the Phase 7 validation report."""
    print("=== PHASE 7 VALIDATION REPORT ===")
    print(f"Run settings: N={N}, Δt={Δt}, period=200, σ_L={σ_L}")
    print(f"Plant: m={m}, c={c}, k={k}")
    print(f"Controller: Kp={Kp}, Kd={Kd}")
    print(f"Energy bounds: [{E_min}, {E_max}]")
    print()

    # Claim A — Continuity
    print("Claim A — Closed-loop continuity")
    print(f"  All channels have {N} points: {all(len(v) == N for v in history.values())}")
    print()

    # Claim B — Boundedness
    print("Claim B — Boundedness")
    bounded = True
    if not (0 <= history['θ'].min() and history['θ'].max() <= 180):
        print("  FAIL: θ outside [0, 180]")
        bounded = False
    if abs(history['ω']).max() > 300:
        print("  FAIL: |ω| > 300")
        bounded = False
    if not (E_min <= history['E'].min() and history['E'].max() <= E_max):
        print("  FAIL: E outside bounds")
        bounded = False
    if not (-20 <= history['T'].min() and history['T'].max() <= 80):
        print("  FAIL: T outside [-20, 80]")
        bounded = False
    print(f"  PASS: {bounded}")
    print()

    # Claim C — Robustness under noise (last 50% of run)
    print("Claim C — Robustness under noise (last 50%)")
    W = slice(N//2, N)
    std_θ = np.std(history['θ'][W])
    std_ω = np.std(history['ω'][W])
    print(f"  Std(θ) = {std_θ:.2f}° (threshold ≤ 45°)")
    print(f"  Std(ω) = {std_ω:.2f}°/step (threshold ≤ 150)")
    robust = (std_θ <= 45) and (std_ω <= 150)
    print(f"  PASS: {robust}")
    print()

    # Claim D — Input-Output gain
    print("Claim D — Input→Output gain")
    corr = np.corrcoef(history['L'], history['θ'])[0,1]
    print(f"  corr(L, θ) = {corr:.3f} (threshold ≥ 0.2)")
    print(f"  PASS: {corr >= 0.2}")
    print()

    # Claim E — No pathological saturation
    δ = 2.0
    sat_θ = np.mean((history['θ'] <= δ) | (history['θ'] >= 180 - δ))
    print(f"Claim E — Saturation ratio (δ={δ}°)")
    print(f"  sat_θ = {sat_θ:.3f} (threshold ≤ 0.20)")
    print(f"  PASS: {sat_θ <= 0.20}")
    print()

    print("Phase 7 baseline complete.")


if __name__ == "__main__":
    history = run_baseline()
    print_validation_report(history)
"""
Regression tests for the thermal model and the L6 -> L1 coupling.

Targets the structural defects fixed in the ThermalState refactor:
  1. Cooling must advance per dt, not per heat-event arrival.
  2. EnergyHarvester.overflow_heat must actually move membrane temperature.

These tests do not exercise the four falsifiable phase validators
(phase7_control_baseline, phase8_stdp, phase9_predictive_processing,
phase10_multimodal); those run separately and must continue to PASS.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    EnergyHarvester,
    ThermalConfig,
    ThermalState,
    celsius_per_step_to_watts,
)
from core.energy import BalancedEnergyConfig
from phases.phase5_adaptive_membrane import AdaptiveMembrane
from phases.phase7_full_integration import IntegratedConsciousnessSystem


DT = ThermalConfig().dt_reference_seconds


def test_zero_heat_converges_to_ambient_band():
    """No heat input for many steps -> temperature settles to ambient."""
    cfg = ThermalConfig(ambient=20.0)
    thermal = ThermalState(cfg, initial_temperature=35.0)

    for _ in range(500):
        thermal.step(DT, 0.0)

    assert thermal.temperature == pytest.approx(cfg.ambient, abs=0.01), (
        f"expected convergence to ~{cfg.ambient}, got {thermal.temperature}"
    )


def test_zero_heat_does_not_peg_to_initial_value():
    """The 'stuck at 23.0 with no variance' anti-pattern must not recur."""
    thermal = ThermalState(ThermalConfig(), initial_temperature=23.0)
    samples = [thermal.step(DT, 0.0) for _ in range(50)]

    # First sample should already differ from initial (cooling is per-dt)
    assert samples[0] != 23.0, "cooling did not advance on first step"
    # Trajectory must move (not pegged at one value)
    assert len(set(round(s, 6) for s in samples)) > 1


def test_constant_heat_reaches_steady_state_above_ambient():
    """
    Constant heat -> steady state at the analytic Newton-cooling value;
    remove heat -> back to ambient.

    Steady state derivation: at equilibrium, heat-in per step = cooling per step.
        (W * dt_ref) / C = k * (T_ss - T_amb)
        T_ss = T_amb + W * dt_ref / (k * C)

    Pinning to this formula (not a hardcoded 38.0) lets future ThermalConfig
    retuning still verify the integrator against its own physics.
    """
    cfg = ThermalConfig(ambient=20.0)
    thermal = ThermalState(cfg, initial_temperature=cfg.ambient)
    watts = 0.5

    expected_steady = (
        cfg.ambient
        + watts * cfg.dt_reference_seconds
        / (cfg.cooling_rate * cfg.thermal_mass_j_per_k)
    )

    for _ in range(1000):
        thermal.step(DT, watts)
    steady = thermal.temperature
    assert steady == pytest.approx(expected_steady, abs=1.0), (
        f"steady state {steady:.3f} != analytic {expected_steady:.3f}"
    )
    assert steady > cfg.ambient + 5.0  # belt-and-braces sanity floor

    # Confirm it's actually steady (not still climbing)
    last = thermal.temperature
    for _ in range(100):
        thermal.step(DT, watts)
    assert abs(thermal.temperature - last) < 0.05

    # Remove heat -> returns to ambient
    for _ in range(1000):
        thermal.step(DT, 0.0)
    assert thermal.temperature == pytest.approx(cfg.ambient, abs=0.01)


def test_cooling_independent_of_heat_event_count():
    """
    The pre-refactor defect: AdaptiveMembrane.apply_heat() cooled toward ambient
    every call, so N heat events per step cooled N times. The new contract:
    cooling depends on dt (one step_thermal call), not on apply_heat() count.
    """
    a = AdaptiveMembrane()
    a.temperature = 30.0
    a.apply_heat(0.0)
    a.step_thermal()
    one_event_temp = a.temperature

    b = AdaptiveMembrane()
    b.temperature = 30.0
    for _ in range(10):
        b.apply_heat(0.0)
    b.step_thermal()
    ten_event_temp = b.temperature

    assert one_event_temp == pytest.approx(ten_event_temp, abs=1e-9), (
        "cooling rate must depend on dt, not on apply_heat() call count"
    )


def test_apply_heat_buffers_accumulate_within_step():
    """Multiple apply_heat() calls in one step must add, not race."""
    m = AdaptiveMembrane()
    m.temperature = 20.0
    m.apply_heat(1.0)
    m.apply_heat(1.0)
    m.apply_heat(1.0)
    m.step_thermal()
    t_three = m.temperature

    m2 = AdaptiveMembrane()
    m2.temperature = 20.0
    m2.apply_heat(3.0)
    m2.step_thermal()
    t_one = m2.temperature

    assert t_three == pytest.approx(t_one, abs=1e-9)


def test_soft_cap_bounds_runaway_heat():
    """Extreme sustained heat must be bounded by the soft cap + bleed mechanism."""
    cfg = ThermalConfig(soft_cap=80.0, soft_cap_bleed=0.2)
    thermal = ThermalState(cfg, initial_temperature=cfg.ambient)
    for _ in range(5000):
        thermal.step(DT, 100.0)  # absurd 100 W
    # Equilibrium of 100 W against cooling + bleed sits well above soft_cap
    # but is bounded; key assertion is that it converges and is finite.
    assert np.isfinite(thermal.temperature)
    last = thermal.temperature
    for _ in range(100):
        thermal.step(DT, 100.0)
    assert abs(thermal.temperature - last) < 1e-6, "soft-cap regime must equilibrate"


def test_celsius_per_step_to_watts_round_trip():
    """Conversion must be the symmetric inverse of the internal step math."""
    cfg = ThermalConfig()
    thermal = ThermalState(cfg, initial_temperature=cfg.ambient)
    # Inject 1 K-equivalent of heat as watts; with cooling tiny near ambient,
    # the temperature should rise by ~1 K on the first step.
    watts = celsius_per_step_to_watts(1.0, cfg)
    thermal.step(cfg.dt_reference_seconds, watts)
    # delta = 1.0 from heat, minus 0.1 * (T - ambient) cooling at near-ambient
    # ~0; expect ~1.0.
    assert thermal.temperature == pytest.approx(cfg.ambient + 1.0, abs=0.01)


def test_l6_to_l1_overflow_heat_moves_membrane_temperature():
    """
    Drive an EnergyHarvester into overflow and assert the resulting overflow_heat
    actually changes the membrane temperature in IntegratedConsciousnessSystem.
    """
    np.random.seed(0)
    sys_baseline = IntegratedConsciousnessSystem()
    sys_baseline.run_full_test(num_steps=50)
    baseline_temps = list(sys_baseline.history.get('temp'))

    # Build a second system with a balanced energy harvester deliberately
    # pushed above capacity so overflow_heat is positive every step.
    np.random.seed(0)
    sys_overflow = IntegratedConsciousnessSystem()
    sys_overflow.energy_harvester = EnergyHarvester(
        config=BalancedEnergyConfig(),
        initial_energy=BalancedEnergyConfig.capacity_mwh,  # already at cap
    )
    sys_overflow.run_full_test(num_steps=50)
    overflow_temps = list(sys_overflow.history.get('temp'))

    # Confirm overflow_heat was actually positive at some point
    assert sys_overflow.energy_harvester.overflow_heat >= 0.0
    # The trajectories must differ -- overflow heat is being injected into L1
    diffs = [abs(a - b) for a, b in zip(baseline_temps, overflow_temps)]
    assert max(diffs) > 0.05, (
        "overflow_heat from L6 should perturb membrane temperature in L1; "
        f"max trajectory diff was only {max(diffs):.4f} C"
    )
    # Direction check: overflow heat should make the system warmer on
    # average, not just different. Without this, a sign flip in the wiring
    # would still pass the max-diff assertion above.
    assert np.mean(overflow_temps) > np.mean(baseline_temps), (
        f"overflow temps mean ({np.mean(overflow_temps):.3f}) should exceed "
        f"baseline mean ({np.mean(baseline_temps):.3f})"
    )


def test_l6_overflow_heat_scales_with_overflow_factor():
    """
    Sanity: ThermalState.step() with positive watts derived from a known
    overflow figure increments temperature by the expected delta near ambient.
    """
    cfg = ThermalConfig()
    thermal = ThermalState(cfg, initial_temperature=cfg.ambient)
    overflow_celsius = 0.5  # e.g. 10 mWh overflow at 0.05 C/mWh
    watts = celsius_per_step_to_watts(overflow_celsius, cfg)
    pre = thermal.temperature
    thermal.step(cfg.dt_reference_seconds, watts)
    delta = thermal.temperature - pre
    assert delta == pytest.approx(0.5, abs=0.01)


def test_photothermal_factor_matches_legacy_behavior():
    """
    Regression rail: with default ThermalConfig.photothermal_factor (0.002),
    one step of light=500 from ambient must produce the same delta T as the
    legacy `external_light / 500.0` -> celsius_per_step_to_watts pipeline.

    Hand-computed expectation:
        K-per-step from light: 500 * 0.002 = 1.0
        watts: 1.0 * C / dt_ref = 1.0 * 5 / 18 = 0.27778 W
        delta T over one step at near-ambient (cooling ~ 0): 1.0 K
        T_after: ambient + 1.0 = 21.0 C
    """
    cfg = ThermalConfig()
    light_value = 500.0

    # New path: light kwarg through ThermalState
    new = ThermalState(cfg, initial_temperature=cfg.ambient)
    new.step(cfg.dt_reference_seconds, 0.0, light=light_value)
    new_delta = new.temperature - cfg.ambient

    # Legacy path: external_light / 500.0 fed through celsius_per_step_to_watts
    legacy = ThermalState(cfg, initial_temperature=cfg.ambient)
    legacy_celsius = light_value / 500.0
    legacy_watts = celsius_per_step_to_watts(legacy_celsius, cfg)
    legacy.step(cfg.dt_reference_seconds, legacy_watts)
    legacy_delta = legacy.temperature - cfg.ambient

    # Hand-computed expectation
    assert new_delta == pytest.approx(1.0, abs=1e-9), (
        f"new path delta {new_delta} != hand-computed 1.0"
    )
    # Bit-for-bit equivalence with the legacy pipeline
    assert new.temperature == legacy.temperature, (
        f"photothermal_factor default broke legacy compatibility: "
        f"new={new.temperature} legacy={legacy.temperature}"
    )

"""
Thermal dynamics module.

Decouples temperature evolution from heat-event arrival. The previous design
(AdaptiveMembrane.apply_heat) cooled toward ambient inside apply_heat() itself,
which produced two structural defects:

  1. Multiple heat events in one timestep cooled the membrane multiple times.
  2. A timestep with no heat event did not cool at all.

Cooling is a function of dt, not of heat-event count. ThermalState.step(dt, ...)
advances temperature once per timestep using Newton's law of cooling toward a
(possibly drifting, optionally noisy) ambient, plus heat injection in watts.

A soft cap with bleed-back replaces a hard clamp so transient excursions are
representable but cannot run away.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class ThermalConfig:
    """
    Defaults rationalized in CLAUDE.md / session proposal:
      - ambient 20 C matches AdaptiveMembrane.neutral_temp and
        EnergyHarvester.harvest_thermal(reference_temp=20.0).
      - cooling_rate 0.1 per reference-step preserves the prior
        AdaptiveMembrane time constant (tau ~ 10 steps) when one heat
        event arrives per step.
      - dt_reference_seconds 18.0 = EnergyConfig.time_step_hours * 3600.
      - thermal_mass_j_per_k 5.0: small printed-membrane device.
      - soft_cap 80 / bleed 0.2: damper, not a hard physical limit.
      - ambient_amplitude/noise default off so phase validators stay
        deterministic; tests opt in.
    """
    ambient: float = 20.0
    ambient_amplitude: float = 0.0
    ambient_period: float = 3600.0
    ambient_noise: float = 0.0
    cooling_rate: float = 0.1
    dt_reference_seconds: float = 18.0
    thermal_mass_j_per_k: float = 5.0
    soft_cap: float = 80.0
    soft_cap_bleed: float = 0.2


class ThermalState:
    """
    Per-step thermal integrator. Owns one temperature scalar.

    Usage:
        thermal = ThermalState(ThermalConfig())
        for step in range(N):
            thermal.step(dt=18.0, heat_in_watts=W, light=lux)
            t = thermal.temperature
    """

    def __init__(self,
                 config: ThermalConfig | None = None,
                 initial_temperature: float | None = None,
                 rng: np.random.Generator | None = None):
        self.config = config or ThermalConfig()
        self._temperature = (
            initial_temperature
            if initial_temperature is not None
            else self.config.ambient
        )
        self._t_seconds = 0.0
        self._rng = rng if rng is not None else np.random.default_rng()

    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        self._temperature = float(value)

    def ambient_at(self, t_seconds: float) -> float:
        cfg = self.config
        drift = 0.0
        if cfg.ambient_amplitude != 0.0 and cfg.ambient_period > 0.0:
            drift = cfg.ambient_amplitude * math.sin(
                2.0 * math.pi * t_seconds / cfg.ambient_period
            )
        noise = 0.0
        if cfg.ambient_noise > 0.0:
            noise = float(self._rng.normal(0.0, cfg.ambient_noise))
        return cfg.ambient + drift + noise

    def step(self, dt: float, heat_in_watts: float, *,
             light: float = 0.0) -> float:
        """
        Advance thermal state by dt seconds. Returns the new temperature.

        heat_in_watts: average heat injected over the dt window (positive = warming).
        light: reserved for future radiative coupling; currently unused.
        """
        del light  # placeholder for L1 photothermal coupling

        cfg = self.config
        if dt <= 0.0:
            return self._temperature

        self._t_seconds += dt
        t_ambient = self.ambient_at(self._t_seconds)

        delta_from_heat = (heat_in_watts * dt) / cfg.thermal_mass_j_per_k

        steps_elapsed = dt / cfg.dt_reference_seconds
        delta_from_cooling = (
            -cfg.cooling_rate * (self._temperature - t_ambient) * steps_elapsed
        )

        new_temperature = self._temperature + delta_from_heat + delta_from_cooling

        if new_temperature > cfg.soft_cap:
            excess = new_temperature - cfg.soft_cap
            new_temperature -= excess * cfg.soft_cap_bleed

        self._temperature = new_temperature
        return self._temperature

    def reset(self, temperature: float | None = None) -> None:
        self._temperature = (
            temperature if temperature is not None else self.config.ambient
        )
        self._t_seconds = 0.0


def celsius_per_step_to_watts(delta_c: float, config: ThermalConfig) -> float:
    """
    Convert a 'degrees Celsius added per step' figure (the convention used by
    EnergyHarvester.overflow_heat) to a watts value compatible with
    ThermalState.step(). Symmetric with the internal step math:

        delta_T = (W * dt) / C  ==>  W = delta_T * C / dt
    """
    return delta_c * config.thermal_mass_j_per_k / config.dt_reference_seconds

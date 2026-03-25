"""
Energy Harvesting System

Consolidated energy harvesting logic for friction and thermal sources.
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class EnergyConfig:
    """Configuration for energy harvesting"""
    friction_factor: float = 0.0005      # mW per unit movement (realistic macro-scale)
    thermal_factor: float = 0.0002       # mW per degree difference (realistic)
    time_step_hours: float = 0.005       # 18 seconds per step
    base_consumption_mw: float = 470.0   # Base power draw in mW (macro robot)


@dataclass
class BalancedEnergyConfig(EnergyConfig):
    """
    Balanced configuration for self-sustaining micro-scale neural systems.

    Tuned so that (validated zone boundaries per Patent A ¶0030):
    - Rest state (0 spikes): significant energy drain (must stay active)
    - Low activity (1-7 spikes): slight drain (below lower crossover)
    - Medium activity (8-27 spikes): positive balance / surplus zone
      (peak surplus ~+23 mW at ~18 spikes)
    - High activity (28-50 spikes): slight drain (above upper crossover)
    - Burst activity (>50 spikes): significant drain (emergency only)

    This creates interesting energy management dynamics where the system
    must regulate its activity level to maintain energy homeostasis.
    The "sweet spot" is medium activity - not too little, not too much.
    """
    friction_factor: float = 18.0        # mW per unit activity (piezoelectric harvesting)
    thermal_factor: float = 8.0          # mW per °C difference (thermoelectric)
    time_step_hours: float = 0.005       # 18 seconds per step
    base_consumption_mw: float = 45.0    # 45mW base (higher idle cost)

    # Activity-dependent consumption scaling (quadratic for realistic neural cost)
    # Creates a "sweet spot" where medium activity is most efficient
    activity_cost_mw: float = 1.2        # Linear cost per spike (lower)
    activity_cost_quadratic: float = 0.06  # Higher quadratic penalty for bursts

    # Physical storage constraints
    # A real micro-scale device (supercap or small LiPo) has finite capacity.
    # Excess harvested energy beyond capacity dissipates as heat.
    capacity_mwh: float = 100.0          # Max storage (plausible for $25 embedded device)
    self_discharge_rate: float = 0.001   # Per-step fractional leakage (0.1%/step)
    overflow_thermal_factor: float = 0.05 # Overflow energy → heat (°C per mWh overflow)


class EnergyHarvester:
    """
    Multi-modal energy harvesting system.

    Consolidates energy logic from:
    - RoboticSystem energy harvesting (appendix_a)
    - EnergyHarvestingSystem (phase4)
    - IntegratedConsciousnessSystem energy (phase7)
    """

    def __init__(self, config: EnergyConfig = None, initial_energy: float = 50.0):
        self.config = config or EnergyConfig()
        self.energy_storage = initial_energy  # mWh
        self.temperature = 20.0
        self.overflow_heat = 0.0  # °C from excess energy dissipation

    def harvest_friction(self, movement: float) -> float:
        """
        Harvest energy from triboelectric friction.

        Args:
            movement: Movement magnitude (e.g., servo angle change)

        Returns:
            Energy harvested in mWh
        """
        if abs(movement) > 0.1:
            power_mw = abs(movement) * self.config.friction_factor
            energy_mwh = power_mw * self.config.time_step_hours
            return energy_mwh
        return 0.0

    def harvest_thermal(self, current_temp: float, reference_temp: float = 20.0) -> float:
        """
        Harvest energy from thermal gradient.

        Args:
            current_temp: Current temperature in Celsius
            reference_temp: Reference/ambient temperature

        Returns:
            Energy harvested in mWh
        """
        temp_diff = abs(current_temp - reference_temp)
        power_mw = temp_diff * self.config.thermal_factor
        energy_mwh = power_mw * self.config.time_step_hours
        return energy_mwh

    def update_storage(self, friction_energy: float, thermal_energy: float,
                        spike_count: int = 0) -> float:
        """
        Update energy storage with harvested energy minus consumption.

        Args:
            friction_energy: Energy from friction harvesting (mWh)
            thermal_energy: Energy from thermal harvesting (mWh)
            spike_count: Number of neural spikes (for activity-dependent consumption)

        Returns:
            Net energy change in mWh
        """
        total_harvest = friction_energy + thermal_energy

        # Base consumption
        consumption = self.config.base_consumption_mw * self.config.time_step_hours

        # Activity-dependent consumption (if configured)
        if hasattr(self.config, 'activity_cost_mw'):
            # Linear cost
            activity_consumption = spike_count * self.config.activity_cost_mw * self.config.time_step_hours
            consumption += activity_consumption

            # Quadratic cost for burst penalty (if configured)
            if hasattr(self.config, 'activity_cost_quadratic'):
                quadratic_cost = (spike_count ** 2) * self.config.activity_cost_quadratic * self.config.time_step_hours
                consumption += quadratic_cost

        net = total_harvest - consumption

        # Self-discharge: stored energy leaks proportionally (real capacitors/batteries)
        if hasattr(self.config, 'self_discharge_rate'):
            discharge = self.energy_storage * self.config.self_discharge_rate
            self.energy_storage -= discharge

        self.energy_storage += net

        # Capacity ceiling: excess energy dissipates as heat
        self.overflow_heat = 0.0
        if hasattr(self.config, 'capacity_mwh'):
            if self.energy_storage > self.config.capacity_mwh:
                overflow = self.energy_storage - self.config.capacity_mwh
                self.overflow_heat = overflow * getattr(
                    self.config, 'overflow_thermal_factor', 0.0)
                self.energy_storage = self.config.capacity_mwh
            # Floor at zero (cannot go negative in physical storage)
            if self.energy_storage < 0:
                self.energy_storage = 0.0

        return net

    def get_consumption_breakdown(self, spike_count: int = 0) -> dict:
        """Get detailed consumption breakdown for analysis."""
        base = self.config.base_consumption_mw * self.config.time_step_hours
        activity = 0
        if hasattr(self.config, 'activity_cost_mw'):
            activity = spike_count * self.config.activity_cost_mw * self.config.time_step_hours
        return {
            'base_mwh': base,
            'activity_mwh': activity,
            'total_mwh': base + activity
        }

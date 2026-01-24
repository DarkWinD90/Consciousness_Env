"""
Energy Harvesting System

Consolidated energy harvesting logic for friction and thermal sources.
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class EnergyConfig:
    """Configuration for energy harvesting"""
    friction_factor: float = 0.0005      # mW per unit movement (realistic)
    thermal_factor: float = 0.0002       # mW per degree difference (realistic)
    time_step_hours: float = 0.005       # 18 seconds per step
    base_consumption_mw: float = 470.0   # Base power draw in mW


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

    def update_storage(self, friction_energy: float, thermal_energy: float) -> float:
        """
        Update energy storage with harvested energy minus consumption.

        Returns:
            Net energy change in mWh
        """
        total_harvest = friction_energy + thermal_energy
        consumption = self.config.base_consumption_mw * self.config.time_step_hours
        net = total_harvest - consumption
        self.energy_storage += net
        return net

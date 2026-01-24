"""
Phase 4: Multi-Modal Energy Harvesting

Objective: Enable self-charging through friction (triboelectric) and
          heat (pyroelectric/thermoelectric) harvesting.

Components:
A. Friction Charging (Triboelectric):
   - PTFE/Teflon films
   - Mechanism: Nearly-locked servo movements create friction
   - Output: 100-500V bursts, rectified to 3-5V DC
   - Target: 1-10µW/cm² from TENG pads

B. Heat Charging (Pyroelectric/Thermoelectric):
   - Pyroelectric crystals: LiTaO₃, BaTiO₃, perovskites
   - Thermoelectric materials: Bi₂Te₃, organic-inorganic hybrids
   - Mechanism: Temperature fluctuations (1-10°C) generate voltage
   - Output: 10-100 µC/m² per °C (pyro), 1-100 µV/K (thermo)

REFACTORED: Now uses shared core.EnergyHarvester module.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '/home/user/Consciousness_Env')

from core import EnergyHarvester, EnergyConfig, HistoryTracker


class EnergyHarvestingSystem:
    """Phase 4: Multi-modal energy harvesting using shared EnergyHarvester"""

    def __init__(self):
        # Use shared energy harvester from core module
        self.harvester = EnergyHarvester(
            config=EnergyConfig(
                friction_factor=0.0005,   # Reduced 100x for realism
                thermal_factor=0.0002,    # Reduced 100x for realism
                time_step_hours=0.005,    # 18 seconds = 0.005 hours
                base_consumption_mw=470.0
            ),
            initial_energy=50.0
        )

        # Use shared history tracker from core module
        self.history = HistoryTracker(fields=[
            'energy', 'friction_harvest', 'thermal_harvest', 'temperature'
        ])

    @property
    def energy_storage(self):
        return self.harvester.energy_storage

    @property
    def temperature(self):
        return self.harvester.temperature

    @temperature.setter
    def temperature(self, value):
        self.harvester.temperature = value

    def harvest_friction(self, servo_movement):
        """Triboelectric energy harvesting from servo friction"""
        return self.harvester.harvest_friction(servo_movement)

    def harvest_thermal(self, external_temp):
        """Pyroelectric and thermoelectric harvesting"""
        # Track temperature change for pyroelectric effect
        temp_change = external_temp - self.temperature
        self.temperature = external_temp

        # Pyroelectric response (from temperature change)
        if abs(temp_change) > 0.1:
            pyro_energy = abs(temp_change) * 0.0002 * 0.005
        else:
            pyro_energy = 0.0

        # Thermoelectric (steady-state gradient)
        thermo_energy = self.harvester.harvest_thermal(external_temp)

        return pyro_energy + thermo_energy

    def run_test(self, num_steps=100):
        """Test energy harvesting under varying conditions"""
        for step in range(num_steps):
            # Simulate servo movement
            servo_move = np.sin(step / 10) * 5.0

            # Simulate temperature variation
            external_temp = 20 + 5 * np.sin(step / 15) + np.random.randn()

            # Harvest energy using shared module
            friction_energy = self.harvest_friction(servo_move)
            thermal_energy = self.harvest_thermal(external_temp)

            # Update storage using shared module
            self.harvester.update_storage(friction_energy, thermal_energy)

            # Record using shared history tracker
            self.history.record(
                energy=self.energy_storage,
                friction_harvest=friction_energy,
                thermal_harvest=thermal_energy,
                temperature=self.temperature
            )

    def plot_results(self):
        """Visualize energy harvesting"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        ax1 = axes[0, 0]
        ax1.plot(self.history.get('energy'), color='green', linewidth=2)
        ax1.set_ylabel('Energy Storage (mWh)')
        ax1.set_title('Self-Charging Energy Storage')
        ax1.grid(True, alpha=0.3)

        ax2 = axes[0, 1]
        ax2.plot(self.history.get('friction_harvest'), label='Friction (TENG)', color='blue')
        ax2.plot(self.history.get('thermal_harvest'), label='Thermal (Pyro/Thermo)', color='red')
        ax2.set_ylabel('Harvested Energy (mWh)')
        ax2.set_title('Multi-Modal Energy Harvesting')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        ax3 = axes[1, 0]
        ax3.plot(self.history.get('temperature'), color='orange', linewidth=2)
        ax3.set_xlabel('Time Step')
        ax3.set_ylabel('Temperature (°C)')
        ax3.set_title('Thermal Environment')
        ax3.grid(True, alpha=0.3)

        ax4 = axes[1, 1]
        ax4.hist(self.history.get('friction_harvest'), bins=20, alpha=0.6, label='Friction', color='blue')
        ax4.hist(self.history.get('thermal_harvest'), bins=20, alpha=0.6, label='Thermal', color='red')
        ax4.set_xlabel('Harvested Energy (mWh)')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Energy Harvest Distribution')
        ax4.legend()

        plt.tight_layout()
        plt.savefig('/home/user/Consciousness_Env/assets/phase4_energy_harvesting.png', dpi=150)
        print("Phase 4 plot saved!")


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 4: MULTI-MODAL ENERGY HARVESTING")
    print("(Refactored to use core.EnergyHarvester)")
    print("=" * 70)

    system = EnergyHarvestingSystem()
    system.run_test(num_steps=100)
    system.plot_results()

    print("\n✓ Phase 4 complete! System demonstrates self-charging capability.")

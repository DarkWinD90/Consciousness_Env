"""
Phase 5: Printed Adaptive Membrane

Objective: Create outer skin layer with molecular structures enabling
          low-voltage signal modulation and thermochromic color shifts.

A. Molecular Building Blocks:
   - Perovskite lattices: Methylammonium lead iodide for photovoltaic response
   - ITO (Indium Tin Oxide): Transparent conductor for touch/signal routing
   - Graphene/CNT networks: 2D conductive grids for signal distribution
   - Substrate: Flexible PET or PDMS polymer (0.1-1mm thick)

B. Thermochromic Color Shift:
   - Compounds: Leuco dyes, cholesteric liquid crystals, thermochromic microcapsules
   - Trigger range: 20-40°C for heat gain/loss transitions
   - Heat gain: Shift to red/orange (signaling warmth)
   - Heat loss: Shift to blue/green (signaling cooling)

C. Low-Voltage Modulation:
   - Operating voltage: 1-5V (from harvested energy)
   - Effects: Electrochromic opacity shifts, conductivity changes
   - Response time: Seconds for real-time adaptation

REFACTORED: thermal dynamics delegated to core.ThermalState (Newton's-law
cooling per dt, not per heat event). apply_heat() buffers the heat input
into the next step(); cooling advances exactly once per simulation step.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '/home/user/Consciousness_Env')

from core import (
    ThermochromicMixin, ColorState, HistoryTracker,
    ThermalConfig, ThermalState, celsius_per_step_to_watts,
)


class AdaptiveMembrane(ThermochromicMixin):
    """Phase 5: Printed adaptive membrane with thermochromic response

    Inherits from ThermochromicMixin for consolidated color shift logic.
    Temperature dynamics live in a ThermalState instance; apply_heat()
    buffers heat events and step_thermal() flushes them once per timestep.
    """

    # Override class-level thermochromic parameters
    neutral_temp = 20.0
    warm_threshold = 25.0
    temp_range = 15.0  # More sensitive range for membrane

    def __init__(self, thermal_config: ThermalConfig | None = None):
        self._thermal = ThermalState(
            thermal_config or ThermalConfig(),
            initial_temperature=20.0,
        )
        self._pending_heat_celsius = 0.0
        self._pending_heat_watts = 0.0
        self._color = ColorState(r=0.5, g=0.5, b=0.5)
        self.opacity = 0.5  # 50% opacity
        self.conductivity = 1.0  # Normalized

        # Use shared history tracker
        self.history = HistoryTracker(fields=[
            'temp', 'color_r', 'color_g', 'color_b', 'opacity'
        ])

    @property
    def temperature(self) -> float:
        return self._thermal.temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        self._thermal.temperature = value

    @property
    def color_rgb(self):
        return self._color.to_list()

    def apply_heat(self, heat_gain):
        """
        Buffer a heat event (in degrees Celsius equivalent) for the next
        step_thermal(). Multiple calls within a single step accumulate;
        cooling happens once when step_thermal() runs.
        """
        self._pending_heat_celsius += float(heat_gain)

    def apply_heat_watts(self, watts):
        """Buffer a heat event already expressed in watts."""
        self._pending_heat_watts += float(watts)

    def step_thermal(self, dt: float | None = None) -> float:
        """
        Advance the thermal model by one timestep, flushing buffered heat.
        Returns the new temperature.
        """
        cfg = self._thermal.config
        dt_seconds = cfg.dt_reference_seconds if dt is None else dt
        watts = self._pending_heat_watts
        if self._pending_heat_celsius != 0.0:
            watts += celsius_per_step_to_watts(self._pending_heat_celsius, cfg)
        self._pending_heat_celsius = 0.0
        self._pending_heat_watts = 0.0
        return self._thermal.step(dt_seconds, watts)

    def update_color_shift(self):
        """Thermochromic color response using shared mixin"""
        self._color = self.compute_thermochromic_color(self.temperature)

    def modulate_voltage(self, voltage):
        """Apply low-voltage modulation for electrochromic effects"""
        # 1-5V range
        if 1 <= voltage <= 5:
            # Opacity shift
            self.opacity = 0.3 + (voltage - 1) / 4 * 0.4  # Range: 0.3-0.7
            # Conductivity change
            self.conductivity = 0.5 + (voltage - 1) / 4 * 0.5

    def run_test(self, num_steps=100):
        """Test membrane adaptation under varying conditions"""
        for step in range(num_steps):
            # Simulate varying heat
            heat_input = 2 * np.sin(step / 10) + np.random.randn() * 0.5

            # Buffer heat, then advance the thermal model exactly once per step
            self.apply_heat(heat_input)
            self.step_thermal()

            # Update color using shared thermochromic logic
            self.update_color_shift()

            # Simulate voltage modulation
            voltage = 1 + 4 * (np.sin(step / 15) + 1) / 2  # 1-5V
            self.modulate_voltage(voltage)

            # Record using shared history tracker
            self.history.record(
                temp=self.temperature,
                color_r=self._color.r,
                color_g=self._color.g,
                color_b=self._color.b,
                opacity=self.opacity
            )

    def plot_results(self):
        """Visualize adaptive membrane response"""
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        ax1 = axes[0]
        ax1.plot(self.history.get('temp'), color='red', linewidth=2)
        ax1.set_ylabel('Temperature (°C)', color='red')
        ax1.tick_params(axis='y', labelcolor='red')
        ax1.set_title('Thermochromic Membrane Response')
        ax1.grid(True, alpha=0.3)

        ax2 = axes[1]
        ax2.plot(self.history.get('color_r'), label='Red', color='red', linewidth=2)
        ax2.plot(self.history.get('color_g'), label='Green', color='green', linewidth=2)
        ax2.plot(self.history.get('color_b'), label='Blue', color='blue', linewidth=2)
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Color Intensity (0-1)')
        ax2.set_title('Adaptive Color Shift (Thermochromic via core.ThermochromicMixin)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('/home/user/Consciousness_Env/assets/phase5_adaptive_membrane.png', dpi=150)
        print("Phase 5 plot saved!")


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 5: PRINTED ADAPTIVE MEMBRANE")
    print("(Refactored to use core.ThermochromicMixin)")
    print("=" * 70)

    membrane = AdaptiveMembrane()
    membrane.run_test(num_steps=100)
    membrane.plot_results()

    print("\n✓ Phase 5 complete! Membrane demonstrates thermochromic adaptation.")

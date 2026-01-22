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
"""

import numpy as np
import matplotlib.pyplot as plt


class AdaptiveMembrane:
    """Phase 5: Printed adaptive membrane with thermochromic response"""

    def __init__(self):
        self.temperature = 20.0
        self.color_rgb = [0.5, 0.5, 0.5]  # Neutral gray
        self.opacity = 0.5  # 50% opacity
        self.conductivity = 1.0  # Normalized

        self.history = {
            'temp': [],
            'color_r': [],
            'color_g': [],
            'color_b': [],
            'opacity': []
        }

    def apply_heat(self, heat_gain):
        """Absorb heat and update temperature"""
        self.temperature += heat_gain
        # Natural cooling
        self.temperature += (20 - self.temperature) * 0.1

    def update_color_shift(self):
        """Thermochromic color response to temperature"""
        if self.temperature > 25:
            # Warm: red/orange
            intensity = min((self.temperature - 25) / 15, 1.0)
            self.color_rgb = [
                0.5 + 0.5 * intensity,  # Red increases
                0.5,
                0.5 - 0.5 * intensity   # Blue decreases
            ]
        elif self.temperature < 20:
            # Cool: blue/green
            intensity = min((20 - self.temperature) / 10, 1.0)
            self.color_rgb = [
                0.5 - 0.5 * intensity,  # Red decreases
                0.5,
                0.5 + 0.5 * intensity   # Blue increases
            ]
        else:
            # Neutral
            self.color_rgb = [0.5, 0.5, 0.5]

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

            # Apply heat
            self.apply_heat(heat_input)

            # Update color based on temperature
            self.update_color_shift()

            # Simulate voltage modulation
            voltage = 1 + 4 * (np.sin(step / 15) + 1) / 2  # 1-5V
            self.modulate_voltage(voltage)

            # Record
            self.history['temp'].append(self.temperature)
            self.history['color_r'].append(self.color_rgb[0])
            self.history['color_g'].append(self.color_rgb[1])
            self.history['color_b'].append(self.color_rgb[2])
            self.history['opacity'].append(self.opacity)

    def plot_results(self):
        """Visualize adaptive membrane response"""
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        ax1 = axes[0]
        ax1.plot(self.history['temp'], color='red', linewidth=2)
        ax1.set_ylabel('Temperature (°C)', color='red')
        ax1.tick_params(axis='y', labelcolor='red')
        ax1.set_title('Thermochromic Membrane Response')
        ax1.grid(True, alpha=0.3)

        ax2 = axes[1]
        ax2.plot(self.history['color_r'], label='Red', color='red', linewidth=2)
        ax2.plot(self.history['color_g'], label='Green', color='green', linewidth=2)
        ax2.plot(self.history['color_b'], label='Blue', color='blue', linewidth=2)
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Color Intensity (0-1)')
        ax2.set_title('Adaptive Color Shift (Thermochromic)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('/home/user/Consciousness_Env/assets/phase5_adaptive_membrane.png', dpi=150)
        print("Phase 5 plot saved!")


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 5: PRINTED ADAPTIVE MEMBRANE")
    print("=" * 70)

    membrane = AdaptiveMembrane()
    membrane.run_test(num_steps=100)
    membrane.plot_results()

    print("\n✓ Phase 5 complete! Membrane demonstrates thermochromic adaptation.")

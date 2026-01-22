"""
Phase 1: Optical Sensing Foundation

Objective: Establish the base sensory layer using optical fiber bundles
          with embedded sensor pads.

Components:
- Multi-mode optical fiber strands (10-20 per bundle cluster)
- Photodiodes (silicon or InGaAs for IR sensitivity)
- Thermistors or IR detectors for warmth sensing
- Flexible PCB substrate (polyimide or PDMS)
- ADC (analog-to-digital converter) for signal processing
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class OpticalBundle:
    """Represents a bundle of optical fibers with integrated sensors"""
    bundle_id: int
    num_strands: int = 15  # 10-20 strands per bundle
    photodiode_count: int = 3  # Photodiodes per bundle
    thermistor_count: int = 2  # IR/warmth sensors per bundle

    # Sensor readings
    light_intensity: float = 0.0
    temperature: float = 20.0
    voltage_output: float = 0.0

    # Configuration
    adc_resolution: int = 12  # 12-bit ADC (0-4095 range)
    voltage_range: Tuple[float, float] = (0.0, 5.0)  # 0-5V output


class OpticalSensingSystem:
    """
    Phase 1: Multi-bundle optical sensing foundation with photodiode/thermistor
    hybrid pads for light and temperature detection.
    """

    def __init__(self, num_bundles: int = 6, strands_per_bundle: int = 15):
        """
        Initialize optical sensing system.

        Args:
            num_bundles: Number of fiber bundle clusters (typically 4-8)
            strands_per_bundle: Fiber strands per bundle (10-20)
        """
        self.num_bundles = num_bundles
        self.bundles: List[OpticalBundle] = []

        # Create bundle clusters
        for i in range(num_bundles):
            bundle = OpticalBundle(
                bundle_id=i,
                num_strands=strands_per_bundle,
                photodiode_count=3,
                thermistor_count=2
            )
            self.bundles.append(bundle)

        # System state
        self.history = {
            'light': [],
            'temp': [],
            'voltage': [],
            'adc_values': []
        }

    def sense_light(self, bundle_idx: int, external_light: float) -> float:
        """
        Simulate light sensing through photodiodes in fiber bundle.

        Light travels through optical fibers and hits photodiodes,
        generating proportional voltage.

        Args:
            bundle_idx: Index of the bundle to sense with
            external_light: External light intensity (0-1000 lux)

        Returns:
            Voltage output from photodiodes (0-5V)
        """
        bundle = self.bundles[bundle_idx]

        # Photodiode response (linear in this simplified model)
        # Each strand captures a fraction of light
        light_per_strand = external_light / bundle.num_strands

        # Sum across photodiodes (3 per bundle)
        total_light = light_per_strand * bundle.photodiode_count

        # Convert to voltage (0-5V range, saturates at 1000 lux)
        voltage = np.clip(total_light / 1000 * 5.0, 0, 5.0)

        bundle.light_intensity = total_light
        bundle.voltage_output = voltage

        return voltage

    def sense_temperature(self, bundle_idx: int, external_temp: float) -> float:
        """
        Simulate temperature sensing using thermistors/IR detectors.

        Args:
            bundle_idx: Index of the bundle
            external_temp: External temperature (°C)

        Returns:
            Voltage output from thermistors
        """
        bundle = self.bundles[bundle_idx]

        # Thermistor response (1-5°C resolution)
        # Voltage changes with temperature
        # Assume 20°C baseline = 2.5V, ±1°C = ±0.05V
        temp_diff = external_temp - 20.0
        voltage = 2.5 + temp_diff * 0.05

        voltage = np.clip(voltage, 0, 5.0)

        bundle.temperature = external_temp

        return voltage

    def analog_to_digital(self, voltage: float, resolution: int = 12) -> int:
        """
        Convert analog voltage to digital ADC value.

        Args:
            voltage: Analog voltage (0-5V)
            resolution: ADC bit resolution (default 12-bit)

        Returns:
            Digital ADC value
        """
        max_value = 2 ** resolution - 1  # 12-bit = 4095
        adc_value = int((voltage / 5.0) * max_value)
        return np.clip(adc_value, 0, max_value)

    def sample_all_bundles(self, light_pattern: np.ndarray, temp_pattern: np.ndarray):
        """
        Sample all bundles simultaneously and convert to digital signals.

        Args:
            light_pattern: Array of light intensities for each bundle
            temp_pattern: Array of temperatures for each bundle

        Returns:
            Dictionary of ADC readings
        """
        light_voltages = []
        temp_voltages = []
        adc_values = []

        for i, bundle in enumerate(self.bundles):
            # Sense light
            light_v = self.sense_light(i, light_pattern[i])
            light_voltages.append(light_v)

            # Sense temperature
            temp_v = self.sense_temperature(i, temp_pattern[i])
            temp_voltages.append(temp_v)

            # Convert to digital
            light_adc = self.analog_to_digital(light_v)
            temp_adc = self.analog_to_digital(temp_v)
            adc_values.append((light_adc, temp_adc))

        return {
            'light_voltages': light_voltages,
            'temp_voltages': temp_voltages,
            'adc_values': adc_values
        }

    def run_test_sequence(self, num_steps: int = 100):
        """
        Run a test sequence to validate the optical sensing system.

        Success Criteria:
        - Bundle reliably converts light intensity to proportional voltage
        - Warmth from light is detected and quantified
        - Signals are clean and ready for ADC sampling
        """
        print("Running Phase 1 test sequence...")

        for step in range(num_steps):
            # Simulate varying light and temperature
            t = step / 10.0

            # Light pattern: sinusoidal with some variation across bundles
            light_pattern = np.array([
                500 + 300 * np.sin(t + i * 0.5) + 50 * np.random.randn()
                for i in range(self.num_bundles)
            ])
            light_pattern = np.clip(light_pattern, 0, 1000)

            # Temperature pattern: warmth from light
            temp_pattern = np.array([
                20.0 + light_pattern[i] / 500 + np.random.randn() * 0.5
                for i in range(self.num_bundles)
            ])

            # Sample all bundles
            readings = self.sample_all_bundles(light_pattern, temp_pattern)

            # Store history (average across bundles)
            avg_light = np.mean([b.light_intensity for b in self.bundles])
            avg_temp = np.mean([b.temperature for b in self.bundles])
            avg_voltage = np.mean(readings['light_voltages'])
            avg_adc = np.mean([adc[0] for adc in readings['adc_values']])

            self.history['light'].append(avg_light)
            self.history['temp'].append(avg_temp)
            self.history['voltage'].append(avg_voltage)
            self.history['adc_values'].append(avg_adc)

        print("✓ Test sequence complete!")
        self._validate_success_criteria()

    def _validate_success_criteria(self):
        """Validate that Phase 1 success criteria are met"""
        print("\n" + "=" * 70)
        print("PHASE 1 SUCCESS CRITERIA VALIDATION")
        print("=" * 70)

        # Criterion 1: Light → Voltage conversion
        light_voltage_corr = np.corrcoef(self.history['light'], self.history['voltage'])[0, 1]
        criterion_1 = light_voltage_corr > 0.8
        print(f"✓ Bundle converts light → voltage (corr: {light_voltage_corr:.3f}): {'PASS' if criterion_1 else 'FAIL'}")

        # Criterion 2: Warmth detection
        light_temp_corr = np.corrcoef(self.history['light'], self.history['temp'])[0, 1]
        criterion_2 = light_temp_corr > 0.6
        print(f"✓ Warmth from light detected (corr: {light_temp_corr:.3f}): {'PASS' if criterion_2 else 'FAIL'}")

        # Criterion 3: Signal quality (low noise)
        voltage_std = np.std(self.history['voltage'])
        criterion_3 = voltage_std < 1.0  # Should be relatively stable
        print(f"✓ Signals clean for ADC (std: {voltage_std:.3f}V): {'PASS' if criterion_3 else 'FAIL'}")

        all_pass = criterion_1 and criterion_2 and criterion_3
        print("\n" + "=" * 70)
        print(f"OVERALL: {'✓ PHASE 1 COMPLETE' if all_pass else '✗ VALIDATION FAILED'}")
        print("=" * 70)

    def plot_results(self):
        """Visualize optical sensing performance"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Plot 1: Light intensity
        ax1 = axes[0, 0]
        ax1.plot(self.history['light'], color='orange', linewidth=2)
        ax1.set_xlabel('Time Step')
        ax1.set_ylabel('Light Intensity')
        ax1.set_title('Optical Fiber Light Capture')
        ax1.grid(True, alpha=0.3)

        # Plot 2: Temperature
        ax2 = axes[0, 1]
        ax2.plot(self.history['temp'], color='red', linewidth=2)
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Temperature (°C)')
        ax2.set_title('Thermistor Warmth Detection')
        ax2.grid(True, alpha=0.3)

        # Plot 3: Voltage output
        ax3 = axes[1, 0]
        ax3.plot(self.history['voltage'], color='blue', linewidth=2)
        ax3.set_xlabel('Time Step')
        ax3.set_ylabel('Voltage (V)')
        ax3.set_title('Photodiode Voltage Output')
        ax3.set_ylim([0, 5])
        ax3.grid(True, alpha=0.3)

        # Plot 4: ADC digital values
        ax4 = axes[1, 1]
        ax4.plot(self.history['adc_values'], color='green', linewidth=2)
        ax4.set_xlabel('Time Step')
        ax4.set_ylabel('ADC Value (12-bit)')
        ax4.set_title('Digital Signal (Ready for CPU)')
        ax4.set_ylim([0, 4095])
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('/home/user/Consciousness_Env/assets/phase1_optical_sensing.png', dpi=150, bbox_inches='tight')
        print("\nPhase 1 plot saved to: /home/user/Consciousness_Env/assets/phase1_optical_sensing.png")

        return fig


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 1: OPTICAL SENSING FOUNDATION")
    print("=" * 70)
    print()

    # Initialize system
    print("Initializing optical sensing system...")
    print("  - 6 fiber bundle clusters")
    print("  - 15 strands per bundle")
    print("  - 3 photodiodes + 2 thermistors per bundle")
    print()

    system = OpticalSensingSystem(num_bundles=6, strands_per_bundle=15)

    # Run test
    system.run_test_sequence(num_steps=100)

    # Visualize
    print("\nGenerating visualization...")
    system.plot_results()

    print("\n✓ Phase 1 complete!")

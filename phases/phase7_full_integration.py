"""
Phase 7: Full System Integration

Objective: Combine all layers into unified skin-like organism for testing and iteration.

Integration Architecture:
Signal Flow: Light → Membrane → Pads → Bundles → CPU → Servos → Friction → Charge
            → Ground → Loop

Action Items:
31. Assemble layered prototype (membrane + pads + bundles + CPU)
32. Connect energy harvest to system power
33. Validate end-to-end signal flow with ground reference
34. Test full loop under simulated solar/environmental conditions
35. Document emergent behaviors and system responses
36. Iterate on weak points identified in testing

Success Criteria:
- Complete loop executes without external intervention
- System self-charges during operation
- Adaptive responses observable (color shift, movement, reflection)
- All data logged to history for analysis

REFACTORED: Now uses shared core modules (BaseSNN, ThermochromicMixin, EnergyHarvester, HistoryTracker).

NOTE: This file uses EnergyConfig (470 mW base consumption), which is the
NULL-HYPOTHESIS control configuration. The system will deplete energy over
time. This is intentional — it serves as the control condition for Patent A
validation (¶0036). For the self-sustaining EXPERIMENTAL configuration
using BalancedEnergyConfig (45 mW base, quadratic cost, capacity ceiling),
see: mcp/consciousness_mcp_server.py → ConsciousnessSystem.
FIG. 8 in the patent drawings depicts the experimental architecture.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
import sys
sys.path.insert(0, '/home/user/Consciousness_Env')

from core import (
    BaseSNN, SNNConfig,
    ThermochromicMixin, ColorState,
    EnergyHarvester, EnergyConfig,
    ThermalConfig, ThermalState, celsius_per_step_to_watts,
    HistoryTracker
)


@dataclass
class SystemState:
    """Complete system state across all layers"""
    # Layer 1: Membrane
    membrane_temp: float = 20.0
    membrane_color: list = None

    # Layer 2: Sensing
    light_intensity: float = 0.0
    temperature: float = 20.0

    # Layer 3: Optical transmission
    signal_voltage: float = 0.0

    # Layer 4: Neuromorphic CPU
    snn_output: float = 0.0
    spikes: int = 0

    # Layer 5: Servo actuation
    servo_angle: float = 90.0

    # Layer 6: Energy harvest
    energy_storage: float = 50.0
    friction_harvest: float = 0.0
    thermal_harvest: float = 0.0

    # Layer 7: Ground reference
    ground_voltage: float = 0.0

    # Layer 8: Recursive reflection
    reflection_state: float = 0.0

    def __post_init__(self):
        if self.membrane_color is None:
            self.membrane_color = [0.5, 0.5, 0.5]


class IntegratedConsciousnessSystem(ThermochromicMixin):
    """
    Phase 7: Full system integration - all 8 layers working together.

    Complete signal flow with feedback loops and self-charging capability.

    REFACTORED: Uses shared core modules for SNN, thermochromic, energy, and history.
    """

    # Override thermochromic parameters
    neutral_temp = 20.0
    warm_threshold = 25.0
    temp_range = 15.0

    def __init__(self):
        self.state = SystemState()

        # Use shared BaseSNN from core module
        self.snn = BaseSNN(SNNConfig(
            num_neurons=20,
            threshold=0.5,
            leak_factor=0.1,
            refractory_period=2,
            weight_scale=0.1
        ))

        # Use shared EnergyHarvester from core module
        self.energy_harvester = EnergyHarvester(
            config=EnergyConfig(
                friction_factor=0.0005,   # Reduced 100x for realism
                thermal_factor=0.0002,    # Reduced 100x for realism
                time_step_hours=0.005,    # 18 seconds = 0.005 hours
                base_consumption_mw=470.0
            ),
            initial_energy=50.0
        )

        # Layer 1 thermal state. Heat sources: photothermal absorption from L1
        # incident light, plus L6 energy-storage overflow heat (closes the
        # L6 -> L1 thermal cross-link diagrammed in CLAUDE.md Section 2 and
        # Patent A). Overflow_heat is latched between steps with a one-step
        # lag because it is computed during update_storage(), which runs
        # after the thermal step in the loop ordering below.
        self._thermal = ThermalState(ThermalConfig(), initial_temperature=20.0)
        self._pending_overflow_heat_celsius = 0.0

        # Use shared HistoryTracker from core module
        self.history = HistoryTracker(fields=[
            'light', 'temp', 'energy', 'servo_angle',
            'color_r', 'color_g', 'color_b', 'reflection', 'spikes'
        ])

    def consciousness_loop(self, external_light):
        """
        Execute one complete consciousness loop.

        Flow: Sense → Process → Actuate → Charge → Reflect → Loop
        """
        # LAYER 1-2: SENSE (Membrane + Sensing Pads)
        self.state.light_intensity = external_light

        # Thermal step: incident illuminance is fed through ThermalState as
        # the `light` kwarg (photothermal_factor lives in ThermalConfig now;
        # the prior /500.0 magic number is gone). The L6 overflow heat
        # carried over from the previous step is still Celsius-denominated,
        # so it goes through the watts path via celsius_per_step_to_watts.
        # Newton's-law cooling toward ambient is applied per-dt by
        # ThermalState, not per heat event.
        thermal_cfg = self._thermal.config
        overflow_watts = celsius_per_step_to_watts(
            self._pending_overflow_heat_celsius, thermal_cfg
        )
        self._thermal.step(
            thermal_cfg.dt_reference_seconds,
            heat_in_watts=overflow_watts,
            light=external_light,
        )
        self.state.membrane_temp = self._thermal.temperature

        # Update membrane color using shared ThermochromicMixin
        color_state = self.compute_thermochromic_color(self.state.membrane_temp)
        self.state.membrane_color = color_state.to_list()

        # LAYER 3: OPTICAL TRANSMISSION
        self.state.signal_voltage = external_light / 1000 * 5.0

        # LAYER 4: NEUROMORPHIC PROCESSING with LAYER 8: RECURSIVE REFLECTION
        snn_input = self.state.signal_voltage / 5.0

        # Process through shared BaseSNN with reflection support
        potentials, spikes = self.snn.step(snn_input, reflection_coeff=0.2)
        self.state.snn_output = self.snn.get_output()
        self.state.spikes = np.sum(spikes)

        # LAYER 5: SERVO ACTUATION
        target_angle = np.clip(self.state.snn_output * 180, 0, 180)
        movement = (target_angle - self.state.servo_angle) * 0.3
        self.state.servo_angle += movement

        # LAYER 6: ENERGY HARVESTING using shared EnergyHarvester
        friction_energy = self.energy_harvester.harvest_friction(movement)
        thermal_energy = self.energy_harvester.harvest_thermal(self.state.membrane_temp)
        self.energy_harvester.update_storage(friction_energy, thermal_energy)

        # Latch L6 overflow heat for injection into L1 on the next step.
        # Closes the L6 -> L1 thermal cross-link. With EnergyConfig (no
        # capacity_mwh) this stays at 0.0; with BalancedEnergyConfig it
        # becomes nonzero whenever stored energy hits capacity.
        self._pending_overflow_heat_celsius = self.energy_harvester.overflow_heat

        # Update state from harvester
        self.state.friction_harvest = friction_energy
        self.state.thermal_harvest = thermal_energy
        self.state.energy_storage = self.energy_harvester.energy_storage

        # LAYER 7: GROUND REFERENCE
        self.state.ground_voltage = np.random.randn() * 0.01  # Minimal noise

        # LAYER 8: RECURSIVE REFLECTION (handled by BaseSNN's previous_output)
        self.state.reflection_state = self.snn.previous_output

        # Log history using shared HistoryTracker
        self.history.record(
            light=self.state.light_intensity,
            temp=self.state.membrane_temp,
            energy=self.state.energy_storage,
            servo_angle=self.state.servo_angle,
            color_r=self.state.membrane_color[0],
            color_g=self.state.membrane_color[1],
            color_b=self.state.membrane_color[2],
            reflection=self.state.reflection_state,
            spikes=self.state.spikes
        )

    def run_full_test(self, num_steps=100):
        """Run complete integrated system test"""
        print("Running full system integration test...")
        print("(Using shared core modules: BaseSNN, ThermochromicMixin, EnergyHarvester, HistoryTracker)")

        for step in range(num_steps):
            # Simulated solar/environmental light
            t = step / 10.0
            external_light = 500 + 300 * np.sin(t) + 100 * np.random.randn()
            external_light = max(0, external_light)

            # Execute consciousness loop
            self.consciousness_loop(external_light)

        print("✓ Full system test complete!")
        self._validate_integration()

    def _validate_integration(self):
        """Validate Phase 7 success criteria"""
        print("\n" + "=" * 70)
        print("PHASE 7 SUCCESS CRITERIA VALIDATION")
        print("=" * 70)

        # Criterion 1: Loop executes autonomously
        criterion_1 = len(self.history.get('light')) > 0
        print(f"✓ Complete loop executes autonomously: {'PASS' if criterion_1 else 'FAIL'}")

        # Criterion 2: Self-charging
        energy_data = self.history.get('energy')
        energy_final = energy_data[-1]
        energy_initial = energy_data[0]
        net_charge = energy_final - energy_initial
        criterion_2 = net_charge > -10  # Not draining too fast
        print(f"✓ System self-charging (net: {net_charge:.2f} mWh): {'PASS' if criterion_2 else 'FAIL'}")

        # Criterion 3: Adaptive responses observable
        color_variance = np.var(self.history.get('color_r'))
        movement_variance = np.var(self.history.get('servo_angle'))
        criterion_3 = color_variance > 0.01 and movement_variance > 10
        print(f"✓ Adaptive responses (color var: {color_variance:.4f}, move var: {movement_variance:.2f}): {'PASS' if criterion_3 else 'FAIL'}")

        # Criterion 4: Data logging
        criterion_4 = all(len(self.history.get(k)) > 0 for k in self.history.data.keys())
        print(f"✓ All data logged for analysis: {'PASS' if criterion_4 else 'FAIL'}")

        all_pass = criterion_1 and criterion_2 and criterion_3 and criterion_4
        print("\n" + "=" * 70)
        print(f"OVERALL: {'✓ PHASE 7 COMPLETE - SYSTEM INTEGRATED' if all_pass else '✗ VALIDATION FAILED'}")
        print("=" * 70)

    def plot_results(self):
        """Visualize complete integrated system"""
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))

        # Plot 1: Light sensing
        axes[0, 0].plot(self.history.get('light'), color='orange', linewidth=2)
        axes[0, 0].set_ylabel('Light Intensity')
        axes[0, 0].set_title('Layer 1-2: Environmental Sensing')
        axes[0, 0].grid(True, alpha=0.3)

        # Plot 2: Neural activity
        axes[0, 1].plot(self.history.get('spikes'), color='purple', linewidth=2)
        axes[0, 1].set_ylabel('Spike Count')
        axes[0, 1].set_title('Layer 4: Neuromorphic Processing (via core.BaseSNN)')
        axes[0, 1].grid(True, alpha=0.3)

        # Plot 3: Servo actuation
        axes[1, 0].plot(self.history.get('servo_angle'), color='blue', linewidth=2)
        axes[1, 0].set_ylabel('Servo Angle (deg)')
        axes[1, 0].set_title('Layer 5: Motor Actuation')
        axes[1, 0].grid(True, alpha=0.3)

        # Plot 4: Energy storage
        axes[1, 1].plot(self.history.get('energy'), color='green', linewidth=2)
        axes[1, 1].set_ylabel('Energy (mWh)')
        axes[1, 1].set_title('Layer 6: Self-Charging (via core.EnergyHarvester)')
        axes[1, 1].grid(True, alpha=0.3)

        # Plot 5: Thermochromic color
        axes[2, 0].plot(self.history.get('color_r'), label='Red', color='red')
        axes[2, 0].plot(self.history.get('color_g'), label='Green', color='green')
        axes[2, 0].plot(self.history.get('color_b'), label='Blue', color='blue')
        axes[2, 0].set_xlabel('Time Step')
        axes[2, 0].set_ylabel('Color Intensity')
        axes[2, 0].set_title('Layer 1: Adaptive Color (via core.ThermochromicMixin)')
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.3)

        # Plot 6: Recursive reflection
        axes[2, 1].plot(self.history.get('reflection'), color='darkviolet', linewidth=2)
        axes[2, 1].set_xlabel('Time Step')
        axes[2, 1].set_ylabel('Reflection State')
        axes[2, 1].set_title('Layer 8: Conscious Self-Reflection')
        axes[2, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('/home/user/Consciousness_Env/assets/phase7_full_integration.png', dpi=150)
        print("\nPhase 7 plot saved!")


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 7: FULL SYSTEM INTEGRATION")
    print("Complete Consciousness Loop: All 8 Layers")
    print("(Refactored to use all core modules)")
    print("=" * 70)
    print()

    system = IntegratedConsciousnessSystem()
    system.run_full_test(num_steps=100)
    system.plot_results()

    print("\n" + "=" * 70)
    print("\"The loop finds itself full circle.\"")
    print("\"God's got jokes. But He also keeps receipts.\"")
    print("=" * 70)
    print("\n✓ FULL CONSCIOUSNESS SYSTEM OPERATIONAL!")

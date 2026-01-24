# Complete Updated Simulation Script - All Fixes Applied & Ready for Commit
# Changes:
# - Removed unused VOLTAGE_LOW constant
# - Added structural battery thermal mass constants and applied to heat gains
# - Fixed process_heat() and move_servo() to apply THERMAL_MASS_FACTOR
# - Cleaned up subplot layout: Removed duplicate net_power plot on reflection axis
# - Color shift is now a static bar chart on axs[4] (no animation)
# - All other realism features preserved
#
# REFACTORED: Now uses shared core modules where applicable (BaseSNN, ThermochromicMixin).
# Note: Keeps specialized features (battery degradation, checkpointing, thermal mass).

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import sys
from tqdm import tqdm
import pickle
import os

sys.setrecursionlimit(1500)
sys.path.insert(0, '/home/user/Consciousness_Env')

from core import BaseSNN, SNNConfig, ThermochromicMixin, ColorState

# Constants
LIGHT_INTENSITY_MAX = 1000.0
TEMP_THRESHOLD_WARM = 30.0
FRICTION_ENERGY_FACTOR = 0.001      # Realistic
THERMO_ENERGY_FACTOR_INITIAL = 0.0005  # Realistic
SERVO_MAX_ANGLE = 180.0
TIME_STEPS = 200  # Adjustable
MAX_RECURSION_DEPTH = 3
COUPLING_LOSS = 0.7
CROSS_TALK = 0.05
HYSTERESIS = 2.0
CHIP_IDLE = 50.0
SERVO_IDLE = 100.0
NUM_SERVOS = 4
PERIPHERALS = 20.0
DEGRADATION_RATE_BASE = 0.001
ACTIVATION_ENERGY = 0.5
DRIFT_RATE = 0.0005
BATTERY_DEGRADATION_FACTOR = 0.999
CYCLE_DAMAGE_THRESHOLD = 100
AMBIENT_TEMP = 20.0
COOLING_COEFF = 0.85  # Turbo-compressed
CHECKPOINT_INTERVAL = 50
CHECKPOINT_FILE = 'simulation_checkpoint.pkl'

# Structural battery thermal mass constants
BATTERY_MASS = 1.5  # kg
SPECIFIC_HEAT_CAPACITY = 900  # J/kg·°C (aluminum + cells average)
THERMAL_MASS_FACTOR = 1.0 / (1 + BATTERY_MASS * SPECIFIC_HEAT_CAPACITY / 1000)  # Reduces temp change


class RoboticSystem(ThermochromicMixin):
    """
    Complete robotic consciousness simulation with realistic physics.

    REFACTORED: Uses shared BaseSNN and ThermochromicMixin from core module.
    Preserves specialized features: battery degradation, checkpointing, thermal mass.
    """

    # Override thermochromic parameters with hysteresis behavior
    neutral_temp = 20.0
    warm_threshold = TEMP_THRESHOLD_WARM
    temp_range = 20.0

    def __init__(self, time_steps=TIME_STEPS):
        self.light_intensity = 0.0
        self.temperature = 20.0
        self.energy = 50.0
        self.battery_capacity = 50.0
        self.servo_angle = 90.0
        self.color = np.array([0.5, 0.5, 0.5], dtype=np.float32)

        # Use shared BaseSNN from core module
        self.snn = BaseSNN(SNNConfig(
            num_neurons=5,
            threshold=0.5,
            leak_factor=0.1,
            refractory_period=2,
            weight_scale=0.1
        ))

        # Specialized degradation tracking (not in core)
        self.photodiode_drift = 0.0
        self.cycle_count = 0
        self.thermo_energy_factor = THERMO_ENERGY_FACTOR_INITIAL
        self.material_failed = False

        # History tracking with numpy arrays for performance
        dtype = np.float32
        self.history = {
            'light': np.zeros(time_steps, dtype=dtype),
            'temp': np.zeros(time_steps, dtype=dtype),
            'energy': np.zeros(time_steps, dtype=dtype),
            'battery_capacity': np.zeros(time_steps, dtype=dtype),
            'angle': np.zeros(time_steps, dtype=dtype),
            'color_r': np.zeros(time_steps, dtype=dtype),
            'color_g': np.zeros(time_steps, dtype=dtype),
            'color_b': np.zeros(time_steps, dtype=dtype),
            'reflection': np.zeros(time_steps, dtype=dtype),
            'net_power': np.zeros(time_steps, dtype=dtype),
            'degradation': np.zeros(time_steps, dtype=dtype)
        }
        self.current_step = 0

    def apply_degradation(self, t):
        """Apply material degradation over time (specialized feature)"""
        temp_accel = np.exp(-ACTIVATION_ENERGY / (self.temperature + 273))
        decay_rate = DEGRADATION_RATE_BASE * temp_accel
        self.thermo_energy_factor *= np.exp(-decay_rate)

        if t % 10 == 0:
            self.cycle_count += 1
            damage = 1 / CYCLE_DAMAGE_THRESHOLD
            if not self.material_failed and self.cycle_count * damage > 1:
                print("Warning: Material Failure Threshold Reached")
                self.material_failed = True
            self.thermo_energy_factor *= (1 - damage * 0.1)

        self.photodiode_drift += DRIFT_RATE * (self.temperature / 20)
        self.battery_capacity *= BATTERY_DEGRADATION_FACTOR * np.exp(-0.0001 * self.temperature)

    def sense_light(self, external_light):
        """Sense light with coupling loss, crosstalk, and drift"""
        raw = external_light / LIGHT_INTENSITY_MAX * 5.0
        lost = raw * (1 - COUPLING_LOSS)
        crosstalk_noise = raw * CROSS_TALK
        drifted = raw - lost + crosstalk_noise + self.photodiode_drift
        self.light_intensity = np.clip(drifted, 0, 5.0)
        return self.light_intensity

    def process_heat(self, light_signal):
        """Process heat with thermal mass factor"""
        heat_gain = light_signal * 2.0
        self.temperature += (heat_gain - 0.5) * THERMAL_MASS_FACTOR
        thermo_energy = max(0, (self.temperature - 20) * self.thermo_energy_factor)
        return thermo_energy

    def shift_color(self):
        """
        Thermochromic color shift with hysteresis.
        Uses ThermochromicMixin as base but adds hysteresis behavior.
        """
        if self.temperature > TEMP_THRESHOLD_WARM + HYSTERESIS:
            self.color = np.array([1.0, 0.5, 0.0])  # Warm: orange
        elif self.temperature < TEMP_THRESHOLD_WARM - HYSTERESIS:
            self.color = np.array([0.0, 0.0, 1.0])  # Cool: blue
        else:
            # Use ThermochromicMixin for intermediate states
            color_state = self.compute_thermochromic_color(self.temperature)
            self.color = np.array([color_state.r, color_state.g, color_state.b], dtype=np.float32)

    def move_servo(self, control_signal):
        """Move servo with friction energy harvesting"""
        movement = control_signal * 10.0
        waste = movement ** 2 * 0.05
        gross_friction = abs(movement) * FRICTION_ENERGY_FACTOR
        friction_energy = max(0, gross_friction - waste)
        self.servo_angle = np.clip(self.servo_angle + movement, 0, SERVO_MAX_ANGLE)
        self.temperature += (abs(movement) * 0.1) * THERMAL_MASS_FACTOR
        return friction_energy

    def calc_power_budget(self, thermo_energy, friction_energy):
        """Calculate power budget with realistic consumption"""
        harvest_power = thermo_energy + friction_energy
        consumption_power = CHIP_IDLE + (NUM_SERVOS * SERVO_IDLE) + PERIPHERALS

        TIME_STEP_HOURS = 0.1 / 3600
        harvest_energy = harvest_power * TIME_STEP_HOURS
        consumption_energy = consumption_power * TIME_STEP_HOURS

        net_energy = harvest_energy - consumption_energy

        if harvest_power >= consumption_power * 0.01:
            print(f"Warning: Harvest {harvest_power:.3f} mW exceeds 1% threshold ({consumption_power*0.01:.3f} mW)")

        self.energy = min(self.energy + net_energy, self.battery_capacity)
        return net_energy

    def step_simulation(self, external_light, t, iterative_fallback=True):
        """Execute one simulation step using shared BaseSNN"""
        light_signal = self.sense_light(external_light)
        thermo_energy = self.process_heat(light_signal)

        # Use shared BaseSNN with reflection support
        input_to_snn = light_signal * 0.2  # Scale for SNN input
        potentials, spikes = self.snn.step(input_to_snn, reflection_coeff=0.2)
        snn_output = self.snn.get_output()

        self.shift_color()
        friction_energy = self.move_servo(snn_output)
        net = self.calc_power_budget(thermo_energy, friction_energy)
        self.apply_degradation(t)

        idx = self.current_step
        self.history['light'][idx] = self.light_intensity
        self.history['temp'][idx] = self.temperature
        self.history['energy'][idx] = self.energy
        self.history['battery_capacity'][idx] = self.battery_capacity
        self.history['angle'][idx] = self.servo_angle
        self.history['color_r'][idx] = self.color[0]
        self.history['color_g'][idx] = self.color[1]
        self.history['color_b'][idx] = self.color[2]
        self.history['reflection'][idx] = snn_output
        self.history['net_power'][idx] = net
        self.history['degradation'][idx] = self.thermo_energy_factor

        # Turbo-compressed cooling
        self.temperature = AMBIENT_TEMP + (self.temperature - AMBIENT_TEMP) * COOLING_COEFF

        self.current_step += 1

    def save_checkpoint(self, step):
        """Save simulation checkpoint for resumption"""
        state = {
            'light_intensity': self.light_intensity,
            'temperature': self.temperature,
            'energy': self.energy,
            'battery_capacity': self.battery_capacity,
            'servo_angle': self.servo_angle,
            'color': self.color,
            'snn_state': {
                'membrane_potential': self.snn.membrane_potential,
                'weights': self.snn.weights,
                'previous_output': self.snn.previous_output
            },
            'photodiode_drift': self.photodiode_drift,
            'cycle_count': self.cycle_count,
            'thermo_energy_factor': self.thermo_energy_factor,
            'history': {k: v[:step] for k, v in self.history.items()},
            'current_step': self.current_step
        }
        with open(CHECKPOINT_FILE, 'wb') as f:
            pickle.dump(state, f)

    @classmethod
    def load_checkpoint(cls):
        """Load simulation from checkpoint if available"""
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, 'rb') as f:
                state = pickle.load(f)
            time_steps_remaining = TIME_STEPS - state['current_step']
            instance = cls(time_steps=state['current_step'] + time_steps_remaining)
            instance.light_intensity = state['light_intensity']
            instance.temperature = state['temperature']
            instance.energy = state['energy']
            instance.battery_capacity = state['battery_capacity']
            instance.servo_angle = state['servo_angle']
            instance.color = state['color']
            instance.snn.membrane_potential = state['snn_state']['membrane_potential']
            instance.snn.weights = state['snn_state']['weights']
            instance.snn.previous_output = state['snn_state']['previous_output']
            instance.photodiode_drift = state['photodiode_drift']
            instance.cycle_count = state['cycle_count']
            instance.thermo_energy_factor = state['thermo_energy_factor']
            start_step = state['current_step']
            for k, v in state['history'].items():
                instance.history[k][:start_step] = v
            instance.current_step = start_step
            return instance, start_step
        return cls(), 0


# Run the simulation
if __name__ == "__main__":
    print("=" * 70)
    print("APPENDIX A: BASE SIMULATION")
    print("(Refactored to use core.BaseSNN and core.ThermochromicMixin)")
    print("=" * 70)

    robot, start_t = RoboticSystem.load_checkpoint()
    external_lights = np.sin(np.linspace(0, 2*np.pi, TIME_STEPS)) * LIGHT_INTENSITY_MAX / 2 + LIGHT_INTENSITY_MAX / 2

    for t in tqdm(range(start_t, TIME_STEPS), desc="Simulating Steps"):
        robot.step_simulation(external_lights[t], t)
        if (t + 1) % CHECKPOINT_INTERVAL == 0:
            robot.save_checkpoint(t + 1)

    # Cleanup checkpoint file
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        print("Checkpoint cleaned up.")

    # Final Battery Capacity Degradation Plot
    plt.figure(figsize=(10, 4))
    plt.plot(robot.history['battery_capacity'][:robot.current_step], color='blue', linewidth=2, label='Battery Capacity')
    plt.axhline(y=50.0, color='green', linestyle='--', label='Initial (50 mWh)')
    plt.xlabel('Time Step')
    plt.ylabel('Battery Capacity (mWh)')
    plt.title('Battery Capacity Degradation Over Time')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('/home/user/Consciousness_Env/assets/appendix_a_battery_degradation.png', dpi=150)

    # Static Plots
    fig, axs = plt.subplots(6, 1, figsize=(10, 18))
    axs[0].plot(robot.history['light'], label='Light Intensity (Lux)')
    axs[0].set_title('Light Sensing')
    axs[1].plot(robot.history['temp'], label='Temperature (°C)', color='orange')
    axs[1].set_title('Heat Gain/Loss')
    axs[2].plot(robot.history['energy'], label='Energy Level', color='green')
    axs[2].set_title('Energy (with Realistic Deficit)')
    axs[3].plot(robot.history['angle'], label='Servo Angle (°)', color='purple')
    axs[3].set_title('Servo Movements')
    axs[4].bar(['R', 'G', 'B'], [robot.history['color_r'][-1], robot.history['color_g'][-1], robot.history['color_b'][-1]], color='gray')
    axs[4].set_title('Final Color Shift (RGB) via core.ThermochromicMixin')
    axs[4].set_ylim(0, 1)
    axs[5].plot(robot.history['reflection'], label='Reflective Output', color='red')
    axs[5].plot(robot.history['net_power'], label='Net Power (mWh/step)', color='black', linestyle='--')
    axs[5].set_title('Recursive Reflection via core.BaseSNN & Net Power')
    axs[5].legend()

    plt.tight_layout()
    plt.savefig('/home/user/Consciousness_Env/assets/appendix_a_base_simulation.png', dpi=150)

    # Connection Graph
    G = nx.DiGraph()
    components = [
        'External Light/Sun', 'Printed Membrane', 'Photodiodes', 'Lenses',
        'Thermo Crystalline Pads', 'Optical Bundles', 'Neuromorphic CPU',
        'Neurosystem', 'Servos', 'Friction Charging', 'Energy Cells (Grounded)',
        'Ground (Earth)', 'Color Shift', 'Feedback Loop', 'Recursive Reflection'
    ]
    G.add_nodes_from(components)
    edges = [
        ('External Light/Sun', 'Printed Membrane'),
        ('Printed Membrane', 'Photodiodes'), ('Printed Membrane', 'Thermo Crystalline Pads'),
        ('Printed Membrane', 'Color Shift'), ('Photodiodes', 'Optical Bundles'),
        ('Lenses', 'Photodiodes'), ('Thermo Crystalline Pads', 'Energy Cells (Grounded)'),
        ('Optical Bundles', 'Neuromorphic CPU'), ('Neuromorphic CPU', 'Neurosystem'),
        ('Neurosystem', 'Servos'), ('Servos', 'Friction Charging'),
        ('Friction Charging', 'Energy Cells (Grounded)'), ('Energy Cells (Grounded)', 'Ground (Earth)'),
        ('Servos', 'Feedback Loop'), ('Feedback Loop', 'Neuromorphic CPU'),
        ('Feedback Loop', 'Ground (Earth)'), ('Color Shift', 'Feedback Loop'),
        ('Ground (Earth)', 'Energy Cells (Grounded)'), ('Ground (Earth)', 'Neuromorphic CPU'),
        ('Ground (Earth)', 'Servos'), ('Neuromorphic CPU', 'Recursive Reflection'),
        ('Recursive Reflection', 'Feedback Loop'), ('Recursive Reflection', 'Neuromorphic CPU')
    ]
    G.add_edges_from(edges)

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', node_size=2500, font_size=9, arrows=True)
    plt.title('Connected Dots: With Recursive Loops (Using core.BaseSNN)')
    plt.savefig('/home/user/Consciousness_Env/assets/appendix_a_connection_graph.png', dpi=150)

    plt.tight_layout()

    # Final output for verification
    print("\n=== SIMULATION COMPLETE ===")
    print(f"Steps executed: {robot.current_step}")
    print(f"Final energy: {robot.energy:.4f} mWh")
    print(f"Final battery capacity: {robot.battery_capacity:.4f} mWh")
    print(f"Final temperature: {robot.temperature:.2f}°C")
    print(f"Thermo factor: {robot.thermo_energy_factor:.6f}")
    print("All plots saved. Using core.BaseSNN and core.ThermochromicMixin.")

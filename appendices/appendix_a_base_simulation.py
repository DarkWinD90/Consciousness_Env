"""
Appendix A: Base Robotic System Simulation
Script 1: Core sense → process → actuate → charge loop

Comprehensive Python Simulation Script for the Conceptual Robotic System
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Constants and Configuration
VOLTAGE_LOW = 1.0  # Low voltage for membrane modulation
VOLTAGE_MAX = 1500  # High voltage for membrane modulation
FRICTION_ENERGY_FACTOR = 0.0005  # Reduced 100x: realistic friction harvest
BIO_THERMO_ENERGY_FACTOR = 0.00065  # Reduced 100x: realistic thermal harvest
TIME_STEP_HOURS = 0.005  # 18 seconds per step (18/3600 = 0.005 hours)
SERVO_MAX_ANGLE = 180
NUM_TIME_STEPS = 100  # Simple Spiking Neural Network time steps
TEMP_THRESHOLD_WARN = None
TEMP_THRESHOLD_COOL = None


class SimpleSNN:
    """Simple Spiking Neural Network for Neuromorphic Processing"""

    def __init__(self, num_neurons=5, threshold=0.5):
        self.num_neurons = num_neurons
        self.threshold = threshold
        self.weights = np.random.rand(num_neurons, num_neurons) * 0.1
        self.membrane_potential = np.zeros(num_neurons)

    def step(self, input_signal):
        """Process input and return spike output"""
        # Decay membrane potential
        self.membrane_potential *= 0.9

        # Add input to first neuron
        self.membrane_potential[0] += input_signal * 0.1

        # Check for spikes
        spikes = self.membrane_potential > self.threshold

        # Reset spiking neurons
        self.membrane_potential[spikes] = 0.0

        # Propagate spikes
        if np.any(spikes):
            self.membrane_potential += np.dot(spikes.astype(float), self.weights)

        return self.membrane_potential.copy(), spikes


class RoboticSystem:
    """Robot Class with Sensors, Actuators, and Consciousness Loop"""

    def __init__(self, num_neurons=5, threshold=0.5):
        # Initialize subsystems
        self.snn = SimpleSNN(num_neurons, threshold)
        self.servo_angle = 90.0
        self.temperature = 20.0
        self.energy = 50.0
        self.color = [0.5, 0.5, 0.5]  # RGB neutral gray

        # History tracking
        self.history = {
            'light': [],
            'temp': [],
            'energy': [],
            'angle': [],
            'color_r': [],
            'color_g': [],
            'color_b': []
        }

    def sense_light(self, external_light):
        """Sense light intensity from environment"""
        self.light_intensity = external_light
        return external_light

    def process_heat(self, light_signal):
        """Process heat gain from light absorption"""
        heat_gain = light_signal * 2.0
        self.temperature += heat_gain

        # Thermal energy harvesting (pyro/thermo)
        # Proper unit conversion: (power_mW) * (time_step_hours) = energy_mWh
        thermo_power = (self.temperature - 20.0) * BIO_THERMO_ENERGY_FACTOR
        thermo_energy = thermo_power * TIME_STEP_HOURS
        self.energy += thermo_energy

        # Cooling effect
        self.temperature *= 0.95

        return heat_gain

    def move_servo(self, snn_output):
        """Actuate servo based on neural output"""
        friction_energy = 0.0

        # Convert neural output to movement
        movement = np.clip(snn_output.sum() * 10.0, -10, 10)
        self.servo_angle = np.clip(self.servo_angle + movement, 0, SERVO_MAX_ANGLE)

        # Friction charging from movement
        # Proper unit conversion: (power_mW) * (time_step_hours) = energy_mWh
        if abs(movement) > 0.1:
            friction_power = abs(movement) * FRICTION_ENERGY_FACTOR
            friction_energy = friction_power * TIME_STEP_HOURS
            self.energy += friction_energy

        return friction_energy

    def shift_color(self):
        """Shift color based on temperature"""
        # Temperature-based color shift
        if self.temperature > 25:
            # Warm: shift to red/orange
            self.color = [
                min(1.0, 0.5 + (self.temperature - 25) / 50),
                0.5,
                max(0.0, 0.5 - (self.temperature - 25) / 50)
            ]
        else:
            # Cool: shift to blue/green
            self.color = [
                max(0.0, 0.5 - (25 - self.temperature) / 50),
                0.5,
                min(1.0, 0.5 + (25 - self.temperature) / 50)
            ]

    def step_simulation(self, external_light):
        """Execute one consciousness loop iteration"""
        # SENSE: Get external signals
        light_signal = self.sense_light(external_light)

        # PROCESS: Neural processing
        snn_output, spikes = self.snn.step(light_signal)

        # ACTUATE: Move servo
        friction_energy = self.move_servo(snn_output)

        # CHARGE: Energy harvesting
        heat_gain = self.process_heat(light_signal)

        # ADAPT: Color shift based on temperature
        self.shift_color()

        # Apply voltage modulation for membrane
        voltage_applied = VOLTAGE_LOW if snn_output.sum() > 0.2 else 0

        # Energy consumption (realistic: 470mW base consumption)
        # 470mW * 0.005 hours = 2.35 mWh per step
        consumption_mw = 470.0
        consumption_mwh = consumption_mw * TIME_STEP_HOURS
        self.energy -= consumption_mwh

        # Record history
        self.history['light'].append(self.light_intensity)
        self.history['temp'].append(self.temperature)
        self.history['energy'].append(self.energy)
        self.history['angle'].append(self.servo_angle)
        self.history['color_r'].append(self.color[0])
        self.history['color_g'].append(self.color[1])
        self.history['color_b'].append(self.color[2])

        return {
            'light': light_signal,
            'snn_output': snn_output,
            'spikes': spikes,
            'friction_energy': friction_energy,
            'voltage_applied': voltage_applied
        }


def simulate_system(num_steps=100, external_light_pattern=None):
    """Run the complete robotic system simulation"""
    robot = RoboticSystem(num_neurons=5, threshold=0.5)

    # Generate external light pattern if not provided
    if external_light_pattern is None:
        # Sinusoidal light pattern with some noise
        t = np.linspace(0, 4 * np.pi, num_steps)
        external_light_pattern = 0.5 + 0.3 * np.sin(t) + 0.1 * np.random.randn(num_steps)
        external_light_pattern = np.clip(external_light_pattern, 0, 1)

    # Run simulation
    for step in range(num_steps):
        robot.step_simulation(external_light_pattern[step])

    return robot


def plot_results(robot):
    """Visualize simulation results"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Plot 1: Light intensity and temperature
    ax1 = axes[0, 0]
    ax1.plot(robot.history['light'], label='Light Intensity', color='orange')
    ax1.set_ylabel('Light Intensity', color='orange')
    ax1.tick_params(axis='y', labelcolor='orange')

    ax1_twin = ax1.twinx()
    ax1_twin.plot(robot.history['temp'], label='Temperature', color='red')
    ax1_twin.set_ylabel('Temperature (°C)', color='red')
    ax1_twin.tick_params(axis='y', labelcolor='red')
    ax1.set_xlabel('Time Step')
    ax1.set_title('Environmental Sensing')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Energy over time
    ax2 = axes[0, 1]
    ax2.plot(robot.history['energy'], color='green', linewidth=2)
    ax2.set_xlabel('Time Step')
    ax2.set_ylabel('Energy Level')
    ax2.set_title('Self-Charging Energy Dynamics')
    ax2.grid(True, alpha=0.3)

    # Plot 3: Servo angle
    ax3 = axes[1, 0]
    ax3.plot(robot.history['angle'], color='blue', linewidth=2)
    ax3.set_xlabel('Time Step')
    ax3.set_ylabel('Servo Angle (degrees)')
    ax3.set_title('Actuator Movement')
    ax3.set_ylim([0, 180])
    ax3.grid(True, alpha=0.3)

    # Plot 4: Color shifts (RGB)
    ax4 = axes[1, 1]
    ax4.plot(robot.history['color_r'], label='Red', color='red', alpha=0.7)
    ax4.plot(robot.history['color_g'], label='Green', color='green', alpha=0.7)
    ax4.plot(robot.history['color_b'], label='Blue', color='blue', alpha=0.7)
    ax4.set_xlabel('Time Step')
    ax4.set_ylabel('Color Intensity')
    ax4.set_title('Thermochromic Color Response')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/home/user/Consciousness_Env/assets/appendix_a_simulation.png', dpi=150)
    print("Simulation plot saved to: /home/user/Consciousness_Env/assets/appendix_a_simulation.png")

    return fig


if __name__ == "__main__":
    print("=" * 70)
    print("APPENDIX A: BASE ROBOTIC SYSTEM SIMULATION")
    print("Core Loop: Sense → Process → Actuate → Charge")
    print("=" * 70)

    # Run simulation
    print("\nRunning simulation...")
    robot = simulate_system(num_steps=100)

    print(f"\nFinal State:")
    print(f"  Energy: {robot.energy:.2f}")
    print(f"  Temperature: {robot.temperature:.2f}°C")
    print(f"  Servo Angle: {robot.servo_angle:.2f}°")
    print(f"  Color (RGB): [{robot.color[0]:.2f}, {robot.color[1]:.2f}, {robot.color[2]:.2f}]")

    # Generate plots
    print("\nGenerating visualization...")
    plot_results(robot)

    print("\n✓ Simulation complete!")

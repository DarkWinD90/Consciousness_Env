"""
Phase 3: Closed-Loop Feedback with Ground Reference

Objective: Establish stable feedback loops grounded to earth reference
          for signal integrity and servo control.

Components:
- Star-ground topology PCB layout
- DAC (digital-to-analog converter) for feedback signals
- PWM servo controllers (50Hz, 1-2ms pulse width)
- Ground plane copper layers in flexible PCB
- Shielded bundles and ferrite beads for EMI protection
"""

import numpy as np
import matplotlib.pyplot as plt


class GroundedFeedbackSystem:
    """Phase 3: Closed-loop feedback with ground reference"""

    def __init__(self, num_servos=4):
        self.num_servos = num_servos
        self.servo_positions = np.zeros(num_servos)
        self.target_positions = np.zeros(num_servos)
        self.ground_reference_voltage = 0.0

        self.history = {
            'servo_pos': [],
            'target': [],
            'error': [],
            'ground_noise': []
        }

    def set_target(self, snn_output):
        """Convert SNN output to servo target positions"""
        self.target_positions = np.clip(snn_output * 180, 0, 180)

    def update_servos(self, dt=0.01):
        """Update servo positions with PWM control"""
        # P-controller for servo movement
        error = self.target_positions - self.servo_positions
        self.servo_positions += error * 0.3

        # Ground-referenced feedback
        ground_noise = np.random.randn() * 0.01  # Minimal noise with grounding
        self.ground_reference_voltage = ground_noise

        return self.servo_positions, error

    def run_test(self, num_steps=100):
        """Test feedback loop stability"""
        for step in range(num_steps):
            # Simulated SNN output
            snn_out = np.random.rand(self.num_servos) * 0.5 + 0.25
            self.set_target(snn_out)
            pos, error = self.update_servos()

            self.history['servo_pos'].append(pos.mean())
            self.history['target'].append(self.target_positions.mean())
            self.history['error'].append(np.abs(error).mean())
            self.history['ground_noise'].append(self.ground_reference_voltage)

    def plot_results(self):
        """Visualize feedback performance"""
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        ax1 = axes[0]
        ax1.plot(self.history['target'], label='Target', linestyle='--', color='blue')
        ax1.plot(self.history['servo_pos'], label='Actual Position', color='green', linewidth=2)
        ax1.set_ylabel('Servo Position (degrees)')
        ax1.set_title('Closed-Loop Servo Control')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2 = axes[1]
        ax2.plot(self.history['error'], color='red', linewidth=2)
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Tracking Error')
        ax2.set_title('Feedback Loop Stability')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('/home/user/Consciousness_Env/assets/phase3_closed_loop_feedback.png', dpi=150)
        print("Phase 3 plot saved!")


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 3: CLOSED-LOOP FEEDBACK WITH GROUND REFERENCE")
    print("=" * 70)

    system = GroundedFeedbackSystem(num_servos=4)
    system.run_test(num_steps=100)
    system.plot_results()

    print("\n✓ Phase 3 complete!")

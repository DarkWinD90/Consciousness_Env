"""
Base Spiking Neural Network

Consolidated SNN implementation used across all phases.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, List


@dataclass
class SNNConfig:
    """Configuration for Spiking Neural Network"""
    num_neurons: int = 10
    threshold: float = 0.5
    leak_factor: float = 0.1
    refractory_period: int = 2
    weight_scale: float = 0.1


class BaseSNN:
    """
    Base Spiking Neural Network with leaky integrate-and-fire neurons.

    Consolidates common SNN logic from:
    - SimpleSNN (appendix_a)
    - SpikingNeuralNetwork (phase2)
    - RecursiveSNN (appendix_c)
    - RecursiveReflectionLayer (phase6)
    """

    def __init__(self, config: Optional[SNNConfig] = None):
        config = config or SNNConfig()

        self.num_neurons = config.num_neurons
        self.threshold = config.threshold
        self.leak_factor = config.leak_factor
        self.refractory_period = config.refractory_period

        # Network state
        self.weights = np.random.rand(self.num_neurons, self.num_neurons) * config.weight_scale
        np.fill_diagonal(self.weights, 0)
        self.membrane_potential = np.zeros(self.num_neurons)
        self.refractory_counters = np.zeros(self.num_neurons, dtype=int)

        # For recursive reflection
        self.previous_output: Optional[float] = None
        self.spike_history: List[np.ndarray] = []

    def step(self, input_signal: float, reflection_coeff: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Execute one timestep of SNN processing.

        Args:
            input_signal: External input (normalized 0-1)
            reflection_coeff: Weight for self-reflection feedback (0 = no reflection)

        Returns:
            Tuple of (membrane_potentials, spike_mask)
        """
        # Apply leak
        self.membrane_potential *= (1 - self.leak_factor)

        # Add input to first neuron
        adjusted_input = input_signal * 0.1
        if self.previous_output is not None and reflection_coeff > 0:
            adjusted_input += self.previous_output * reflection_coeff

        self.membrane_potential[0] += adjusted_input

        # Check for spikes (respecting refractory period)
        can_spike = self.refractory_counters == 0
        spikes = (self.membrane_potential > self.threshold) & can_spike

        # Reset spiking neurons
        self.membrane_potential[spikes] = 0.0
        self.refractory_counters[spikes] = self.refractory_period

        # Decrement refractory counters
        self.refractory_counters = np.maximum(0, self.refractory_counters - 1)

        # Propagate spikes
        if np.any(spikes):
            self.membrane_potential += np.dot(spikes.astype(float), self.weights)

        # Store for reflection
        self.previous_output = self.membrane_potential.mean()
        self.spike_history.append(spikes.copy())

        return self.membrane_potential.copy(), spikes

    def get_output(self) -> float:
        """Get current output (mean membrane potential)"""
        return self.membrane_potential.mean()

    def reset(self):
        """Reset network state"""
        self.membrane_potential = np.zeros(self.num_neurons)
        self.refractory_counters = np.zeros(self.num_neurons, dtype=int)
        self.previous_output = None
        self.spike_history = []

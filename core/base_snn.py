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
    input_scale: float = 0.8  # Scale factor for external input
    # STDP parameters
    stdp_enabled: bool = False
    a_plus: float = 0.01      # LTP amplitude (potentiation)
    a_minus: float = 0.012    # LTD amplitude (depression, slightly stronger for stability)
    tau_plus: float = 20.0    # LTP trace time constant (steps)
    tau_minus: float = 20.0   # LTD trace time constant (steps)
    w_min: float = 0.0        # Minimum synaptic weight
    w_max: float = 0.5        # Maximum synaptic weight


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
        self.input_scale = config.input_scale

        # Network state
        self.weights = np.random.rand(self.num_neurons, self.num_neurons) * config.weight_scale
        np.fill_diagonal(self.weights, 0)
        self.membrane_potential = np.zeros(self.num_neurons)
        self.refractory_counters = np.zeros(self.num_neurons, dtype=int)

        # For recursive reflection
        self.previous_output: Optional[float] = None
        self.spike_history: List[np.ndarray] = []

        # STDP state
        self.stdp_enabled = config.stdp_enabled
        self.a_plus = config.a_plus
        self.a_minus = config.a_minus
        self.tau_plus = config.tau_plus
        self.tau_minus = config.tau_minus
        self.w_min = config.w_min
        self.w_max = config.w_max
        self.pre_trace = np.zeros(self.num_neurons)
        self.post_trace = np.zeros(self.num_neurons)

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

        # Add input to first neuron (scaled for proper threshold crossings)
        adjusted_input = input_signal * self.input_scale
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

        # STDP weight update (before storing history)
        if self.stdp_enabled:
            self._stdp_update(spikes)

        # Store for reflection
        self.previous_output = self.membrane_potential.mean()
        self.spike_history.append(spikes.copy())

        return self.membrane_potential.copy(), spikes

    def _stdp_update(self, spikes: np.ndarray):
        """
        Apply Spike-Timing Dependent Plasticity weight update.

        Uses trace-based STDP: each neuron maintains pre- and post-synaptic
        eligibility traces that decay exponentially and increment on spike.

        Weight convention: weights[i, j] = connection from neuron i to neuron j.

        LTP: When post-synaptic neuron j fires, strengthen connections from
             recently-active pre-synaptic neurons: w[i,j] += A+ * pre_trace[i]
        LTD: When pre-synaptic neuron i fires, weaken connections to
             recently-active post-synaptic neurons: w[i,j] -= A- * post_trace[j]
        """
        spike_float = spikes.astype(float)

        # LTP: potentiate incoming weights to neurons that just fired
        dw_ltp = self.a_plus * np.outer(self.pre_trace, spike_float)

        # LTD: depress outgoing weights from neurons that just fired
        dw_ltd = self.a_minus * np.outer(spike_float, self.post_trace)

        # Apply weight update
        self.weights += dw_ltp - dw_ltd

        # Enforce constraints
        np.fill_diagonal(self.weights, 0)
        np.clip(self.weights, self.w_min, self.w_max, out=self.weights)

        # Update traces: decay then increment for spiking neurons
        self.pre_trace *= np.exp(-1.0 / self.tau_plus)
        self.post_trace *= np.exp(-1.0 / self.tau_minus)
        self.pre_trace += spike_float
        self.post_trace += spike_float

    def get_output(self) -> float:
        """Get current output (mean membrane potential)"""
        return self.membrane_potential.mean()

    def reset(self):
        """Reset network state (preserves weights and STDP config)"""
        self.membrane_potential = np.zeros(self.num_neurons)
        self.refractory_counters = np.zeros(self.num_neurons, dtype=int)
        self.previous_output = None
        self.spike_history = []
        self.pre_trace = np.zeros(self.num_neurons)
        self.post_trace = np.zeros(self.num_neurons)

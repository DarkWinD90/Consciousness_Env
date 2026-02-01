"""
Multi-Modal Sensory Integration Module — Phase 10

Processes multiple sensor modalities (light, sound, pressure) through separate
SNN populations and binds them through cross-modal spike synchronization.

Architecture:
    - Three independent BaseSNN instances (one per modality)
    - CrossModalConnector: manages cross-modal weight matrices + STDP
    - MultiModalSystem: wraps all components into one step() interface

Cross-modal connections are EXTERNAL to the BaseSNN instances.  After each
SNN steps, the connector propagates spikes from one population to others
by adding to membrane potentials.  STDP on cross-modal weights uses the
same trace-based algorithm as BaseSNN._stdp_update() but is implemented
independently here to avoid modifying base_snn.py.

Design principle: No modifications to base_snn.py.  All cross-modal logic
is contained in this module.  Regression safety is guaranteed by isolation.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, List
from .base_snn import BaseSNN, SNNConfig


# Modality identifiers
MODALITIES = ('light', 'sound', 'pressure')
# Cross-modal pairs (bidirectional)
CROSS_PAIRS = (('light', 'sound'), ('light', 'pressure'), ('sound', 'pressure'))


@dataclass
class MultiModalConfig:
    """Configuration for Multi-Modal Sensory Integration."""

    # Per-modality SNN parameters (same for all modalities)
    num_neurons: int = 10
    threshold: float = 0.3
    weight_scale: float = 0.2
    input_scale: float = 1.0
    leak_factor: float = 0.1
    refractory_period: int = 2

    # Within-modality STDP (disabled by default to isolate cross-modal effect)
    within_stdp_enabled: bool = False

    # Cross-modal connection parameters
    cross_weight_scale: float = 0.1    # Initial random weight scale
    cross_w_min: float = 0.0
    cross_w_max: float = 0.3           # Lower than within-modality (0.5)

    # Cross-modal STDP parameters
    cross_stdp_enabled: bool = True
    cross_a_plus: float = 0.005
    cross_a_minus: float = 0.006       # 1.2:1 LTD/LTP ratio
    cross_tau_plus: float = 20.0
    cross_tau_minus: float = 20.0


class CrossModalConnector:
    """
    Manages cross-modal connections between SNN populations.

    For each pair of modalities (A, B), maintains:
    - A weight matrix W_AB (N_A x N_B): connections from A to B
    - A weight matrix W_BA (N_B x N_A): connections from B to A
    - Pre/post eligibility traces for STDP on each direction

    Cross-modal spike propagation: when neurons in population A spike,
    their spikes are propagated to population B via W_AB, adding to B's
    membrane potentials (and vice versa).

    STDP: uses the same trace-based algorithm as BaseSNN._stdp_update()
    but operates on cross-modal weight matrices independently.
    """

    def __init__(self, config: MultiModalConfig, seed: int = 42):
        self.config = config
        n = config.num_neurons

        # Initialize cross-modal weight matrices and STDP traces
        # For each pair (A, B), we have W_AB (A→B) and W_BA (B→A)
        rng = np.random.RandomState(seed + 10)

        self.weights: Dict[Tuple[str, str], np.ndarray] = {}
        self.pre_traces: Dict[Tuple[str, str], np.ndarray] = {}
        self.post_traces: Dict[Tuple[str, str], np.ndarray] = {}

        for mod_a, mod_b in CROSS_PAIRS:
            # A→B direction
            self.weights[(mod_a, mod_b)] = rng.rand(n, n) * config.cross_weight_scale
            self.pre_traces[(mod_a, mod_b)] = np.zeros(n)
            self.post_traces[(mod_a, mod_b)] = np.zeros(n)

            # B→A direction
            self.weights[(mod_b, mod_a)] = rng.rand(n, n) * config.cross_weight_scale
            self.pre_traces[(mod_b, mod_a)] = np.zeros(n)
            self.post_traces[(mod_b, mod_a)] = np.zeros(n)

    def propagate(self, spikes: Dict[str, np.ndarray],
                  snns: Dict[str, BaseSNN]):
        """
        Propagate cross-modal spikes between populations.

        For each pair (A, B): if A spiked, add A's spikes weighted by W_AB
        to B's membrane potentials, and vice versa.

        Args:
            spikes: dict mapping modality name to spike mask (boolean array)
            snns: dict mapping modality name to BaseSNN instance
        """
        for mod_a, mod_b in CROSS_PAIRS:
            spikes_a = spikes[mod_a].astype(float)
            spikes_b = spikes[mod_b].astype(float)

            # A→B: add weighted spikes from A to B's membrane potential
            if np.any(spikes[mod_a]):
                snns[mod_b].membrane_potential += np.dot(
                    spikes_a, self.weights[(mod_a, mod_b)]
                )

            # B→A: add weighted spikes from B to A's membrane potential
            if np.any(spikes[mod_b]):
                snns[mod_a].membrane_potential += np.dot(
                    spikes_b, self.weights[(mod_b, mod_a)]
                )

    def stdp_update(self, spikes: Dict[str, np.ndarray]):
        """
        Apply STDP to cross-modal weight matrices.

        Same trace-based algorithm as BaseSNN._stdp_update():
        - LTP: w[i,j] += A+ * pre_trace[i] when post neuron j fires
        - LTD: w[i,j] -= A- * post_trace[j] when pre neuron i fires
        - Traces decay exponentially, increment on spike

        Applied independently to each cross-modal direction.
        """
        if not self.config.cross_stdp_enabled:
            return

        a_plus = self.config.cross_a_plus
        a_minus = self.config.cross_a_minus
        tau_plus = self.config.cross_tau_plus
        tau_minus = self.config.cross_tau_minus
        w_min = self.config.cross_w_min
        w_max = self.config.cross_w_max

        for mod_a, mod_b in CROSS_PAIRS:
            spikes_a = spikes[mod_a].astype(float)
            spikes_b = spikes[mod_b].astype(float)

            # ── A→B direction: pre=A, post=B ──
            key_ab = (mod_a, mod_b)
            pre_trace = self.pre_traces[key_ab]
            post_trace = self.post_traces[key_ab]

            # LTP: when post (B) fires, strengthen from recently-active pre (A)
            dw_ltp = a_plus * np.outer(pre_trace, spikes_b)
            # LTD: when pre (A) fires, weaken to recently-active post (B)
            dw_ltd = a_minus * np.outer(spikes_a, post_trace)

            self.weights[key_ab] += dw_ltp - dw_ltd
            np.clip(self.weights[key_ab], w_min, w_max, out=self.weights[key_ab])

            # Update traces
            pre_trace *= np.exp(-1.0 / tau_plus)
            post_trace *= np.exp(-1.0 / tau_minus)
            pre_trace += spikes_a
            post_trace += spikes_b

            self.pre_traces[key_ab] = pre_trace
            self.post_traces[key_ab] = post_trace

            # ── B→A direction: pre=B, post=A ──
            key_ba = (mod_b, mod_a)
            pre_trace = self.pre_traces[key_ba]
            post_trace = self.post_traces[key_ba]

            dw_ltp = a_plus * np.outer(pre_trace, spikes_a)
            dw_ltd = a_minus * np.outer(spikes_b, post_trace)

            self.weights[key_ba] += dw_ltp - dw_ltd
            np.clip(self.weights[key_ba], w_min, w_max, out=self.weights[key_ba])

            pre_trace *= np.exp(-1.0 / tau_plus)
            post_trace *= np.exp(-1.0 / tau_minus)
            pre_trace += spikes_b
            post_trace += spikes_a

            self.pre_traces[key_ba] = pre_trace
            self.post_traces[key_ba] = post_trace

    def get_all_cross_weights(self) -> np.ndarray:
        """
        Return all cross-modal weights concatenated into a single array.
        Useful for entropy computation across all cross-modal connections.
        """
        all_w = []
        for key in sorted(self.weights.keys()):
            all_w.append(self.weights[key].flatten())
        return np.concatenate(all_w)

    def get_weight_snapshot(self) -> Dict[Tuple[str, str], np.ndarray]:
        """Return a copy of all cross-modal weight matrices."""
        return {key: w.copy() for key, w in self.weights.items()}


class MultiModalSystem:
    """
    Multi-Modal Sensory Integration System (Phase 10).

    Wraps three independent BaseSNN instances (one per modality) and a
    CrossModalConnector into a single step() interface.

    Each step:
    1. Step all three SNNs with their respective inputs
    2. Propagate cross-modal spikes via the connector
    3. Apply STDP on cross-modal weights
    4. Return per-modality spikes for synchronization measurement
    """

    def __init__(self, config: Optional[MultiModalConfig] = None,
                 cross_stdp_enabled: bool = True, seed: int = 42):
        config = config or MultiModalConfig()
        self.config = config

        # Override cross STDP setting
        config.cross_stdp_enabled = cross_stdp_enabled

        # Create per-modality SNN configs
        snn_config = SNNConfig(
            num_neurons=config.num_neurons,
            threshold=config.threshold,
            weight_scale=config.weight_scale,
            input_scale=config.input_scale,
            leak_factor=config.leak_factor,
            refractory_period=config.refractory_period,
            stdp_enabled=config.within_stdp_enabled,
        )

        # Three independent SNN instances with different seeds
        self.snns: Dict[str, BaseSNN] = {}
        for i, mod in enumerate(MODALITIES):
            np.random.seed(seed + i)
            self.snns[mod] = BaseSNN(snn_config)

        # Cross-modal connector
        self.connector = CrossModalConnector(config, seed=seed)

    def step(self, inputs: Dict[str, float]) -> Dict[str, np.ndarray]:
        """
        Execute one timestep of multi-modal processing.

        Args:
            inputs: dict mapping modality name to input value (0-1).
                    Keys: 'light', 'sound', 'pressure'

        Returns:
            spikes: dict mapping modality name to spike mask (boolean array)
        """
        # Step each SNN independently
        spikes = {}
        for mod in MODALITIES:
            _, spike_mask = self.snns[mod].step(inputs[mod])
            spikes[mod] = spike_mask

        # Propagate cross-modal spikes
        self.connector.propagate(spikes, self.snns)

        # Apply STDP on cross-modal weights
        self.connector.stdp_update(spikes)

        return spikes

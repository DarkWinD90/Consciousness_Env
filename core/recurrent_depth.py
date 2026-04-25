"""
Recurrent Depth Module — Phase 13

Exposes an inner loop around BaseSNN.step() so the SNN can reason in
continuous latent space for T iterations per outer simulation timestep
before the consciousness loop's L5 (servo) and L6 (energy) read its output.

Architectural mapping to OpenMythos-style recurrent transformer:
    Prelude → Recurrent Block → Coda
    h_{t+1} = A·h_t + B·e + Transformer(h_t, e)

    BaseSNN.step() already implements one iteration of this rule:
        A·h_t            ← V *= (1 - leak_factor)
        B·e              ← V[0] += input * input_scale
        Transformer(...) ← V += spikes @ weights

    RecurrentDepthSNN exposes the *inner* loop — calling step() T times
    per outer timestep with input re-injection at every iteration — without
    modifying BaseSNN. Composes the same way PredictiveProcessor (Phase 9)
    composes BaseSNN: by wrapping, not subclassing or modifying.

Out of scope for Phase 13:
    - Mixture-of-Experts (MoE) routing across depth steps. Each inner
      iteration uses the same SNN weights — no per-depth subnetwork
      selection. A future Phase 14 candidate ("Depth-conditioned
      subnetwork routing") could implement this by masking different
      neuron subpopulations at different inner-step indices.
    - Multi-head Latent Attention (MLA). The SNN has no token sequence
      and no KV cache; MLA is structurally not applicable.

    Phase 13 implements the recurrent inner loop only.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Tuple
from .base_snn import BaseSNN, SNNConfig


@dataclass
class RecurrentDepthConfig:
    """Configuration for inner-loop recurrent depth."""

    base_config: SNNConfig = field(default_factory=SNNConfig)
    num_inner_steps: int = 8           # T — depth of inner reasoning loop
    reflection_coeff: float = 0.2      # passed to BaseSNN.step at each inner iter
    inject_input_every_step: bool = True   # OpenMythos rule: re-inject e every iter
    record_trajectory: bool = False        # if True, populate trajectory in StepResult


@dataclass
class StepResult:
    """Result of one outer step (T inner iterations)."""

    membrane_potential: np.ndarray              # h_T after T inner iterations
    spikes: np.ndarray                          # spike mask from final inner iteration
    total_spike_count: int                      # cumulative across all T inner steps
    trajectory: Optional[np.ndarray] = None     # (T, num_neurons) if recording
    inner_step_spike_counts: Optional[np.ndarray] = None  # (T,) if recording


class RecurrentDepthSNN:
    """
    Wraps a BaseSNN and runs T inner iterations per outer step.

    Hidden state h_t = membrane_potential persists across inner iterations
    (BaseSNN already maintains this). At each inner iteration the input
    signal e is re-injected (if inject_input_every_step=True) and the
    reflection coefficient feeds the previous mean back through L8.

    Energy accounting contract: callers must call EnergyHarvester.update_storage()
    exactly ONCE per outer step with spike_count = StepResult.total_spike_count.
    Calling update_storage T times per outer step would charge energy T× and
    silently break the homeostatic equilibrium of CLAUDE.md §3.2.
    """

    def __init__(self, config: Optional[RecurrentDepthConfig] = None, seed: int = 42):
        self.config = config or RecurrentDepthConfig()
        np.random.seed(seed)
        self.snn = BaseSNN(self.config.base_config)

    @property
    def num_neurons(self) -> int:
        return self.snn.num_neurons

    @property
    def membrane_potential(self) -> np.ndarray:
        return self.snn.membrane_potential

    @property
    def previous_output(self) -> Optional[float]:
        return self.snn.previous_output

    @property
    def weights(self) -> np.ndarray:
        return self.snn.weights

    def step(self, input_signal: float) -> StepResult:
        """
        Run T inner iterations of the wrapped SNN.

        Args:
            input_signal: External input (normalized 0-1) — injected at every
                          inner iteration if inject_input_every_step=True,
                          otherwise injected only at the first inner iteration.

        Returns:
            StepResult with final state, cumulative spike count across all T
            inner iterations, and optionally the per-iteration trajectory.
        """
        T = self.config.num_inner_steps
        coeff = self.config.reflection_coeff
        record = self.config.record_trajectory

        total_spikes = 0
        trajectory = np.zeros((T, self.snn.num_neurons)) if record else None
        inner_counts = np.zeros(T, dtype=int) if record else None

        last_spikes = np.zeros(self.snn.num_neurons, dtype=bool)

        for k in range(T):
            inj = input_signal if (self.config.inject_input_every_step or k == 0) else 0.0
            V, spikes = self.snn.step(inj, reflection_coeff=coeff)
            n_spikes = int(spikes.sum())
            total_spikes += n_spikes
            last_spikes = spikes

            if record:
                trajectory[k] = V
                inner_counts[k] = n_spikes

        return StepResult(
            membrane_potential=self.snn.membrane_potential.copy(),
            spikes=last_spikes,
            total_spike_count=total_spikes,
            trajectory=trajectory,
            inner_step_spike_counts=inner_counts,
        )

    def reset(self) -> None:
        """Reset network state (preserves weights and config)."""
        self.snn.reset()

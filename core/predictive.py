"""
Predictive Processing Module — Phase 9

The system predicts its own next input before it arrives.
Prediction error becomes a learning signal.

Architecture:
    - Processor SNN: Fixed weights, processes actual input
    - Predictor SNN: STDP-enabled, processes actual input, drives temporal features
    - Readout Layer: Linear mapping from temporal feature buffer to prediction
    - Delta Rule: Adjusts readout weights based on prediction error

The prediction is of the NEXT INPUT signal, not the processor output.
This ensures:
    - Periodic input: predictable → error decreases (F9.1)
    - Random input: unpredictable → error stays flat (F9.2)
    - Frequency switch: brief error spike then recovery (F9.3)
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple
from .base_snn import BaseSNN, SNNConfig


@dataclass
class PredictiveConfig:
    """Configuration for Predictive Processing."""

    # SNN parameters (shared by processor and predictor)
    num_neurons: int = 10
    threshold: float = 0.5
    weight_scale: float = 0.1
    input_scale: float = 0.8
    leak_factor: float = 0.1
    refractory_period: int = 2

    # Predictor STDP parameters
    stdp_enabled: bool = True
    a_plus: float = 0.005
    a_minus: float = 0.006
    tau_plus: float = 20.0
    tau_minus: float = 20.0
    w_min: float = 0.0
    w_max: float = 0.5

    # Readout layer parameters
    buffer_length: int = 100      # Temporal feature buffer size
    readout_lr: float = 0.05      # Delta rule learning rate
    weight_decay: float = 0.999   # Readout weight decay
    bias_lr_scale: float = 0.05   # Bias learning rate = readout_lr * this


class PredictiveProcessor:
    """
    Predictive Processing System (Phase 9).

    Dual-pathway architecture:
    - Processor SNN: processes actual input with fixed weights
    - Predictor SNN: processes actual input with STDP, drives temporal features
    - Readout: linear mapping from temporal features to next-input prediction

    The prediction error = |predicted_input - actual_input| serves as:
    1. Learning signal for the readout weights (delta rule)
    2. A measure of how well the system has learned the input pattern
    """

    def __init__(self, config: Optional[PredictiveConfig] = None,
                 learning_enabled: bool = True, seed: int = 42):
        config = config or PredictiveConfig()
        self.config = config
        self.learning_enabled = learning_enabled

        # Processor SNN (frozen weights)
        np.random.seed(seed)
        self.processor = BaseSNN(SNNConfig(
            num_neurons=config.num_neurons,
            threshold=config.threshold,
            weight_scale=config.weight_scale,
            input_scale=config.input_scale,
            leak_factor=config.leak_factor,
            refractory_period=config.refractory_period,
            stdp_enabled=False,
        ))

        # Predictor SNN (STDP-enabled when learning)
        np.random.seed(seed + 1)
        self.predictor = BaseSNN(SNNConfig(
            num_neurons=config.num_neurons,
            threshold=config.threshold,
            weight_scale=config.weight_scale,
            input_scale=config.input_scale,
            leak_factor=config.leak_factor,
            refractory_period=config.refractory_period,
            stdp_enabled=config.stdp_enabled and learning_enabled,
            a_plus=config.a_plus,
            a_minus=config.a_minus,
            tau_plus=config.tau_plus,
            tau_minus=config.tau_minus,
            w_min=config.w_min,
            w_max=config.w_max,
        ))

        # Temporal feature buffer and readout
        self.feature_buffer = np.zeros(config.buffer_length)
        self.readout_weights = np.zeros(config.buffer_length)
        self.readout_bias = 0.5  # midpoint of [0, 1] input range

        self.step_count = 0

    def step(self, actual_input: float) -> Tuple[float, float]:
        """
        Execute one predictive processing step.

        Args:
            actual_input: The actual input signal at this timestep (0-1)

        Returns:
            (prediction, prediction_error):
                prediction: What the system predicted for this input
                prediction_error: |prediction - actual_input|
        """
        self.step_count += 1

        # Make prediction from temporal features
        prediction = np.dot(self.readout_weights, self.feature_buffer) + self.readout_bias
        prediction = float(np.clip(prediction, 0.0, 1.0))

        # Prediction error
        error = actual_input - prediction
        prediction_error = abs(error)

        # Update readout weights via delta rule
        if self.learning_enabled and self.step_count > self.config.buffer_length:
            lr = self.config.readout_lr
            self.readout_weights += lr * error * self.feature_buffer
            self.readout_bias += lr * error * self.config.bias_lr_scale
            self.readout_weights *= self.config.weight_decay

        # Step predictor SNN with actual input
        self.predictor.step(actual_input)

        # Update feature buffer with predictor's temporal state
        self.feature_buffer = np.roll(self.feature_buffer, -1)
        self.feature_buffer[-1] = self.predictor.previous_output

        # Step processor SNN with actual input (normal processing)
        self.processor.step(actual_input)

        return prediction, prediction_error

    def get_prediction_error_modulation(self, prediction_error: float) -> float:
        """
        Convert prediction error to a modulation signal for the consciousness loop.

        High prediction error (surprise) -> positive modulation (increase attention)
        Low prediction error (expected) -> negative modulation (conserve energy)

        Returns modulation in range [-0.2, 0.5].
        """
        normalized = min(prediction_error / 0.3, 1.0)
        return normalized * 0.7 - 0.2

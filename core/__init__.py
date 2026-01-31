"""
Consciousness System Core Module

Shared components for the consciousness simulation system.
Consolidates common patterns to reduce code duplication.

Architecture:
    Physical Layer:
        - BaseSNN: Spiking Neural Network processing
        - ThermochromicMixin: Temperature-based color adaptation
        - EnergyHarvester: Energy harvesting and management
        - HistoryTracker: State history logging

    Cognitive Layer (Claude Integration):
        - ClaudeNeuralInterface: Bidirectional SNN <-> Claude communication
        - NeuralRouter: Claude-assisted packet routing
        - ConsciousnessEnhancer: Higher-order cognitive features

    Integrated System:
        - EnhancedConsciousnessSystem: Full hybrid SNN + Claude system
"""

# Physical Layer Components
from .base_snn import BaseSNN, SNNConfig
from .thermochromic import ThermochromicMixin, ColorState
from .energy import EnergyHarvester, EnergyConfig
from .history import HistoryTracker
from .predictive import PredictiveProcessor, PredictiveConfig

# Cognitive Layer Components (Claude Integration)
from .claude_interface import (
    ClaudeNeuralInterface,
    NeuralQuery,
    CognitiveResponse,
    EncodedPattern,
    PatternType,
    encode_spikes
)
from .neural_router import (
    ClaudeOptimizedRouter,
    NetworkTopology,
    NeuralPacket,
    SignalType,
    NodeState,
    RouteMetrics,
    create_mesh_topology,
    create_random_topology
)
from .consciousness_enhancer import (
    ConsciousnessEnhancer,
    CognitiveMode,
    Intention,
    SelfModel,
    AttentionState
)

# Integrated System
from .enhanced_consciousness import (
    EnhancedConsciousnessSystem,
    SystemState,
    demo_enhanced_consciousness
)

__all__ = [
    # Physical Layer
    'BaseSNN', 'SNNConfig',
    'ThermochromicMixin', 'ColorState',
    'EnergyHarvester', 'EnergyConfig',
    'HistoryTracker',
    'PredictiveProcessor', 'PredictiveConfig',

    # Cognitive Layer - Claude Interface
    'ClaudeNeuralInterface',
    'NeuralQuery',
    'CognitiveResponse',
    'EncodedPattern',
    'PatternType',
    'encode_spikes',

    # Cognitive Layer - Neural Router
    'ClaudeOptimizedRouter',
    'NetworkTopology',
    'NeuralPacket',
    'SignalType',
    'NodeState',
    'RouteMetrics',
    'create_mesh_topology',
    'create_random_topology',

    # Cognitive Layer - Consciousness Enhancer
    'ConsciousnessEnhancer',
    'CognitiveMode',
    'Intention',
    'SelfModel',
    'AttentionState',

    # Integrated System
    'EnhancedConsciousnessSystem',
    'SystemState',
    'demo_enhanced_consciousness'
]

"""
Consciousness System Core Module

Shared components for the consciousness simulation system.
Consolidates common patterns to reduce code duplication.
"""

from .base_snn import BaseSNN, SNNConfig
from .thermochromic import ThermochromicMixin, ColorState
from .energy import EnergyHarvester, EnergyConfig
from .history import HistoryTracker

__all__ = [
    'BaseSNN', 'SNNConfig',
    'ThermochromicMixin', 'ColorState',
    'EnergyHarvester', 'EnergyConfig',
    'HistoryTracker'
]

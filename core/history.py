"""
History Tracking System

Consolidated history/logging functionality.
"""

from typing import Any, Dict, List, Optional
import numpy as np


class HistoryTracker:
    """
    Generic history tracking for simulation metrics.

    Consolidates history dictionaries from all phases.
    """

    def __init__(self, fields: Optional[List[str]] = None):
        """
        Initialize history tracker.

        Args:
            fields: List of field names to track. If None, uses defaults.
        """
        default_fields = [
            'light', 'temp', 'energy', 'servo_angle',
            'color_r', 'color_g', 'color_b',
            'spikes', 'reflection', 'voltage'
        ]
        self.fields = fields or default_fields
        self.data: Dict[str, List[Any]] = {f: [] for f in self.fields}

    def record(self, **kwargs):
        """Record values for specified fields"""
        for key, value in kwargs.items():
            if key in self.data:
                self.data[key].append(value)

    def get(self, field: str) -> List[Any]:
        """Get history for a specific field"""
        return self.data.get(field, [])

    def get_last(self, field: str, default: Any = None) -> Any:
        """Get most recent value for a field"""
        values = self.data.get(field, [])
        return values[-1] if values else default

    def get_stats(self, field: str) -> Dict[str, float]:
        """Get statistics for a field"""
        values = self.data.get(field, [])
        if not values:
            return {}
        arr = np.array(values)
        return {
            'mean': float(np.mean(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr))
        }

    def clear(self):
        """Clear all history"""
        self.data = {f: [] for f in self.fields}

    def __len__(self) -> int:
        """Return number of recorded timesteps"""
        if not self.data:
            return 0
        first_field = list(self.data.keys())[0]
        return len(self.data[first_field])

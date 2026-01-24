"""
Thermochromic Color System

Consolidated temperature-based color shifting logic.
"""

import numpy as np
from dataclasses import dataclass
from typing import List


@dataclass
class ColorState:
    """RGB color state"""
    r: float = 0.5
    g: float = 0.5
    b: float = 0.5

    def to_list(self) -> List[float]:
        return [self.r, self.g, self.b]

    @classmethod
    def from_list(cls, rgb: List[float]) -> 'ColorState':
        return cls(r=rgb[0], g=rgb[1], b=rgb[2])


class ThermochromicMixin:
    """
    Mixin for thermochromic color response.

    Consolidates color shift logic from:
    - RoboticSystem.shift_color (appendix_a)
    - RecursiveSNN color logic (appendix_c)
    - AdaptiveMembrane.update_color_shift (phase5)
    - IntegratedConsciousnessSystem color logic (phase7)
    """

    # Class-level defaults
    neutral_temp: float = 20.0
    warm_threshold: float = 25.0
    temp_range: float = 50.0

    def compute_thermochromic_color(self, temperature: float) -> ColorState:
        """
        Compute RGB color based on temperature.

        - Warm (>25°C): Shift to red/orange
        - Neutral (20-25°C): Gray
        - Cool (<20°C): Shift to blue/green

        Args:
            temperature: Current temperature in Celsius

        Returns:
            ColorState with RGB values (0-1 range)
        """
        if temperature > self.warm_threshold:
            # Warm colors
            intensity = min((temperature - self.warm_threshold) / self.temp_range, 1.0)
            return ColorState(
                r=min(1.0, 0.5 + 0.5 * intensity),
                g=0.5,
                b=max(0.0, 0.5 - 0.5 * intensity)
            )
        elif temperature < self.neutral_temp:
            # Cool colors
            intensity = min((self.neutral_temp - temperature) / self.temp_range, 1.0)
            return ColorState(
                r=max(0.0, 0.5 - 0.5 * intensity),
                g=0.5,
                b=min(1.0, 0.5 + 0.5 * intensity)
            )
        else:
            # Neutral
            return ColorState(r=0.5, g=0.5, b=0.5)

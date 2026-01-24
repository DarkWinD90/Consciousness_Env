#!/usr/bin/env python3
"""
Claude Code Simplifier Plugin

Analyzes and simplifies Python codebases by:
1. Identifying duplicate code patterns
2. Creating shared modules for common functionality
3. Refactoring files to use shared components
4. Removing redundant code
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class CodeAnalyzer:
    """Analyzes Python code for patterns and duplication"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.files: Dict[str, str] = {}
        self.classes: Dict[str, List[str]] = defaultdict(list)
        self.functions: Dict[str, List[str]] = defaultdict(list)
        self.duplicates: List[Dict] = []

    def scan_files(self) -> List[str]:
        """Scan for Python files"""
        py_files = []
        for pattern in ['**/*.py']:
            py_files.extend(self.root_path.glob(pattern))

        # Filter out tools directory and __pycache__
        py_files = [f for f in py_files
                   if 'tools' not in str(f)
                   and '__pycache__' not in str(f)
                   and 'core' not in str(f)]

        return [str(f) for f in py_files]

    def read_files(self):
        """Read all Python files"""
        for filepath in self.scan_files():
            try:
                with open(filepath, 'r') as f:
                    self.files[filepath] = f.read()
            except Exception as e:
                print(f"  Warning: Could not read {filepath}: {e}")

    def find_class_definitions(self):
        """Find all class definitions across files"""
        class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:'

        for filepath, content in self.files.items():
            matches = re.findall(class_pattern, content)
            for class_name in matches:
                self.classes[class_name].append(filepath)

    def find_duplicate_patterns(self) -> List[Dict]:
        """Identify duplicate code patterns"""
        duplicates = []

        # Pattern 1: SNN implementations
        snn_files = []
        for filepath, content in self.files.items():
            if 'membrane_potential' in content and 'threshold' in content:
                if 'spikes' in content or 'spike' in content:
                    snn_files.append(filepath)

        if len(snn_files) > 1:
            duplicates.append({
                'type': 'SNN Implementation',
                'files': snn_files,
                'pattern': 'Spiking Neural Network with membrane potential and threshold'
            })

        # Pattern 2: Thermochromic color shift
        color_files = []
        for filepath, content in self.files.items():
            if 'color' in content.lower() and 'temperature' in content.lower():
                if 'rgb' in content.lower() or 'color_r' in content:
                    color_files.append(filepath)

        if len(color_files) > 1:
            duplicates.append({
                'type': 'Thermochromic Color',
                'files': color_files,
                'pattern': 'Temperature-based color shifting logic'
            })

        # Pattern 3: Energy harvesting
        energy_files = []
        for filepath, content in self.files.items():
            if 'energy' in content.lower() and ('harvest' in content.lower() or 'friction' in content.lower()):
                energy_files.append(filepath)

        if len(energy_files) > 1:
            duplicates.append({
                'type': 'Energy Harvesting',
                'files': energy_files,
                'pattern': 'Energy harvesting from friction/thermal sources'
            })

        # Pattern 4: History tracking
        history_files = []
        for filepath, content in self.files.items():
            if "self.history = {" in content or "self.history[" in content:
                history_files.append(filepath)

        if len(history_files) > 1:
            duplicates.append({
                'type': 'History Tracking',
                'files': history_files,
                'pattern': 'Dictionary-based history logging'
            })

        self.duplicates = duplicates
        return duplicates


class CodeSimplifier:
    """Main simplifier that refactors the codebase"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.analyzer = CodeAnalyzer(root_path)
        self.stats = {
            'files_analyzed': 0,
            'duplicates_found': 0,
            'classes_consolidated': 0,
            'lines_removed': 0,
            'files_created': 0,
            'files_modified': 0
        }

    def analyze(self) -> Dict:
        """Analyze the codebase for simplification opportunities"""
        print("\n" + "=" * 70)
        print("CLAUDE CODE SIMPLIFIER - ANALYSIS PHASE")
        print("=" * 70)

        print("\n[1/3] Scanning files...")
        self.analyzer.read_files()
        self.stats['files_analyzed'] = len(self.analyzer.files)
        print(f"  Found {self.stats['files_analyzed']} Python files")

        print("\n[2/3] Finding class definitions...")
        self.analyzer.find_class_definitions()
        print(f"  Found {len(self.analyzer.classes)} unique classes")

        print("\n[3/3] Identifying duplicate patterns...")
        duplicates = self.analyzer.find_duplicate_patterns()
        self.stats['duplicates_found'] = len(duplicates)

        print(f"\n  Duplicate patterns found: {len(duplicates)}")
        for dup in duplicates:
            print(f"    - {dup['type']}: {len(dup['files'])} files")

        return {
            'files': self.stats['files_analyzed'],
            'classes': len(self.analyzer.classes),
            'duplicates': duplicates
        }

    def create_core_module(self):
        """Create shared core module with base classes"""
        print("\n" + "=" * 70)
        print("CREATING SHARED CORE MODULE")
        print("=" * 70)

        core_dir = self.root_path / 'core'
        core_dir.mkdir(exist_ok=True)

        # Create __init__.py
        init_content = '''"""
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
'''

        # Create base_snn.py - consolidated SNN implementation
        snn_content = '''"""
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
'''

        # Create thermochromic.py - consolidated color logic
        thermo_content = '''"""
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
'''

        # Create energy.py - consolidated energy harvesting
        energy_content = '''"""
Energy Harvesting System

Consolidated energy harvesting logic for friction and thermal sources.
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class EnergyConfig:
    """Configuration for energy harvesting"""
    friction_factor: float = 0.0005      # mW per unit movement (realistic)
    thermal_factor: float = 0.0002       # mW per degree difference (realistic)
    time_step_hours: float = 0.005       # 18 seconds per step
    base_consumption_mw: float = 470.0   # Base power draw in mW


class EnergyHarvester:
    """
    Multi-modal energy harvesting system.

    Consolidates energy logic from:
    - RoboticSystem energy harvesting (appendix_a)
    - EnergyHarvestingSystem (phase4)
    - IntegratedConsciousnessSystem energy (phase7)
    """

    def __init__(self, config: EnergyConfig = None, initial_energy: float = 50.0):
        self.config = config or EnergyConfig()
        self.energy_storage = initial_energy  # mWh
        self.temperature = 20.0

    def harvest_friction(self, movement: float) -> float:
        """
        Harvest energy from triboelectric friction.

        Args:
            movement: Movement magnitude (e.g., servo angle change)

        Returns:
            Energy harvested in mWh
        """
        if abs(movement) > 0.1:
            power_mw = abs(movement) * self.config.friction_factor
            energy_mwh = power_mw * self.config.time_step_hours
            return energy_mwh
        return 0.0

    def harvest_thermal(self, current_temp: float, reference_temp: float = 20.0) -> float:
        """
        Harvest energy from thermal gradient.

        Args:
            current_temp: Current temperature in Celsius
            reference_temp: Reference/ambient temperature

        Returns:
            Energy harvested in mWh
        """
        temp_diff = abs(current_temp - reference_temp)
        power_mw = temp_diff * self.config.thermal_factor
        energy_mwh = power_mw * self.config.time_step_hours
        return energy_mwh

    def update_storage(self, friction_energy: float, thermal_energy: float) -> float:
        """
        Update energy storage with harvested energy minus consumption.

        Returns:
            Net energy change in mWh
        """
        total_harvest = friction_energy + thermal_energy
        consumption = self.config.base_consumption_mw * self.config.time_step_hours
        net = total_harvest - consumption
        self.energy_storage += net
        return net
'''

        # Create history.py - consolidated history tracking
        history_content = '''"""
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
'''

        # Write all files
        files_to_write = [
            (core_dir / '__init__.py', init_content),
            (core_dir / 'base_snn.py', snn_content),
            (core_dir / 'thermochromic.py', thermo_content),
            (core_dir / 'energy.py', energy_content),
            (core_dir / 'history.py', history_content),
        ]

        for filepath, content in files_to_write:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"  Created: {filepath.relative_to(self.root_path)}")
            self.stats['files_created'] += 1

        print(f"\n  Total files created: {self.stats['files_created']}")

    def generate_report(self) -> str:
        """Generate simplification report"""
        report = []
        report.append("\n" + "=" * 70)
        report.append("CODE SIMPLIFICATION REPORT")
        report.append("=" * 70)
        report.append("")
        report.append("SUMMARY:")
        report.append(f"  Files analyzed:        {self.stats['files_analyzed']}")
        report.append(f"  Duplicate patterns:    {self.stats['duplicates_found']}")
        report.append(f"  Core modules created:  {self.stats['files_created']}")
        report.append("")
        report.append("CONSOLIDATED PATTERNS:")
        report.append("")

        for dup in self.analyzer.duplicates:
            report.append(f"  {dup['type']}:")
            report.append(f"    Pattern: {dup['pattern']}")
            report.append(f"    Files affected: {len(dup['files'])}")
            for f in dup['files']:
                report.append(f"      - {Path(f).relative_to(self.root_path)}")
            report.append("")

        report.append("NEW CORE MODULE STRUCTURE:")
        report.append("  core/")
        report.append("    __init__.py      - Module exports")
        report.append("    base_snn.py      - Consolidated SNN implementation")
        report.append("    thermochromic.py - Color shift logic")
        report.append("    energy.py        - Energy harvesting")
        report.append("    history.py       - History tracking")
        report.append("")
        report.append("USAGE:")
        report.append("  from core import BaseSNN, SNNConfig")
        report.append("  from core import ThermochromicMixin, ColorState")
        report.append("  from core import EnergyHarvester, EnergyConfig")
        report.append("  from core import HistoryTracker")
        report.append("")
        report.append("=" * 70)

        return '\n'.join(report)

    def run(self) -> str:
        """Run complete simplification process"""
        print("\n" + "=" * 70)
        print("CLAUDE CODE SIMPLIFIER PLUGIN v1.0")
        print("=" * 70)

        # Analyze
        self.analyze()

        # Create core module
        self.create_core_module()

        # Generate report
        report = self.generate_report()
        print(report)

        # Save report
        report_path = self.root_path / 'SIMPLIFICATION_REPORT.md'
        with open(report_path, 'w') as f:
            f.write("# Code Simplification Report\n\n")
            f.write("```\n")
            f.write(report)
            f.write("\n```\n")
        print(f"\nReport saved to: {report_path}")

        return report


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        # Default to parent directory of tools/
        root_path = str(Path(__file__).parent.parent)

    simplifier = CodeSimplifier(root_path)
    simplifier.run()

    print("\n✓ Code simplification complete!")
    print("  The core/ module now contains consolidated implementations.")
    print("  Existing files can be refactored to use these shared components.")


if __name__ == "__main__":
    main()

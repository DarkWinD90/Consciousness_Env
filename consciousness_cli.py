#!/usr/bin/env python3
"""
Consciousness System CLI
Command-line interface for the Consciousness_Env system.
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path


def get_script_path(module_dir, script_name):
    """Get the absolute path to a script file in the package.

    Resolution order:
    1. Relative to this file (works for development and standard installs)
    2. Parent directory fallback (handles alternate layouts)
    3. importlib.resources (handles wheel/zip installs where the package
       is properly installed but located outside the CLI module's parent)
    """
    # First, try relative to this file (works for both installed and development mode)
    script_dir = Path(__file__).parent.resolve()
    script_path = script_dir / module_dir / script_name

    if script_path.exists():
        return str(script_path)

    # Fallback: search in common installation paths
    parent_path = script_dir.parent / module_dir / script_name
    if parent_path.exists():
        return str(parent_path)

    # Fallback: use importlib.resources to locate the script inside an
    # installed package.  This covers wheels and other packaging layouts
    # where the file-relative approach does not resolve.
    try:
        import importlib.resources as _resources
        if sys.version_info >= (3, 9):
            ref = _resources.files(module_dir).joinpath(script_name)
            resource_path = str(ref)
            if os.path.exists(resource_path):
                return resource_path
        else:
            # Python 3.8: use the older context-manager API
            with _resources.path(module_dir, script_name) as p:
                if p.exists():
                    return str(p)
    except (ImportError, ModuleNotFoundError, TypeError):
        pass

    searched = [
        str(script_dir / module_dir / script_name),
        str(parent_path),
        f"importlib.resources({module_dir}/{script_name})",
    ]
    raise FileNotFoundError(
        f"Could not find {module_dir}/{script_name}. "
        f"Searched in: {searched}"
    )


def run_script(script_path, description):
    """Run a Python script and exit with its return code."""
    print(description)
    result = subprocess.run([sys.executable, script_path])
    sys.exit(result.returncode)


def run_simulation(phase=None):
    """Run a consciousness simulation."""
    phase_map = {
        '1': ('phase1_optical_sensing.py', 'Running optical sensing simulation (Phase 1)...'),
        '2': ('phase2_neuromorphic_processing.py', 'Running neuromorphic processing simulation (Phase 2)...'),
        '3': ('phase3_closed_loop_feedback.py', 'Running closed-loop feedback simulation (Phase 3)...'),
        '4': ('phase4_energy_harvesting.py', 'Running energy harvesting simulation (Phase 4)...'),
        '5': ('phase5_adaptive_membrane.py', 'Running adaptive membrane simulation (Phase 5)...'),
        '6': ('phase6_recursive_reflection.py', 'Running recursive reflection simulation (Phase 6)...'),
        '7': ('phase7_full_integration.py', 'Running full integration simulation (Phase 7)...'),
    }
    
    if phase is None:
        phase = '7'
    
    if phase in phase_map:
        script_name, description = phase_map[phase]
        script_path = get_script_path('phases', script_name)
        run_script(script_path, description)
    else:
        print(f"Unknown phase: {phase}")
        sys.exit(1)


def run_appendix(name):
    """Run an appendix simulation."""
    appendix_map = {
        'a': ('appendix_a_base_simulation.py', 'Running base simulation (Appendix A)...'),
        'base': ('appendix_a_base_simulation.py', 'Running base simulation (Appendix A)...'),
        'b': ('appendix_b_system_graph.py', 'Running system graph visualization (Appendix B)...'),
        'graph': ('appendix_b_system_graph.py', 'Running system graph visualization (Appendix B)...'),
        'c': ('appendix_c_recursive_reflection.py', 'Running recursive reflection (Appendix C)...'),
        'reflection': ('appendix_c_recursive_reflection.py', 'Running recursive reflection (Appendix C)...'),
    }
    
    if name in appendix_map:
        script_name, description = appendix_map[name]
        script_path = get_script_path('appendices', script_name)
        run_script(script_path, description)
    else:
        print(f"Unknown appendix: {name}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Consciousness System Environment CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  consciousness run               # Run full integration (Phase 7)
  consciousness run --phase 1     # Run Phase 1 (optical sensing)
  consciousness appendix a        # Run base simulation (Appendix A)
  consciousness appendix graph    # Run system graph visualization
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a simulation phase')
    run_parser.add_argument(
        '--phase',
        choices=['1', '2', '3', '4', '5', '6', '7'],
        default='7',
        help='Phase to run (default: 7 - full integration)'
    )
    
    # Appendix command
    appendix_parser = subparsers.add_parser('appendix', help='Run an appendix simulation')
    appendix_parser.add_argument(
        'name',
        choices=['a', 'base', 'b', 'graph', 'c', 'reflection'],
        help='Appendix to run'
    )
    
    # Version command
    subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        run_simulation(args.phase)
    elif args.command == 'appendix':
        run_appendix(args.name)
    elif args.command == 'version':
        print("Consciousness System Environment v3.0.0")
        print("Multi-Layer Architecture for Synthetic Proto-Consciousness")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

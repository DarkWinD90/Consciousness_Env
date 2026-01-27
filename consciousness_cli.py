#!/usr/bin/env python3
"""
Consciousness System CLI
Command-line interface for the Consciousness_Env system.
"""

import argparse
import sys
import os

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_simulation(phase=None):
    """Run a consciousness simulation."""
    if phase is None or phase == '7':
        print("Running full integration simulation (Phase 7)...")
        import subprocess
        result = subprocess.run([sys.executable, 'phases/phase7_full_integration.py'], 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        sys.exit(result.returncode)
    elif phase == '1':
        print("Running optical sensing simulation (Phase 1)...")
        import subprocess
        result = subprocess.run([sys.executable, 'phases/phase1_optical_sensing.py'],
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        sys.exit(result.returncode)
    elif phase == '2':
        print("Running neuromorphic processing simulation (Phase 2)...")
        import subprocess
        result = subprocess.run([sys.executable, 'phases/phase2_neuromorphic_processing.py'],
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        sys.exit(result.returncode)
    elif phase == '3':
        print("Running closed-loop feedback simulation (Phase 3)...")
        import subprocess
        result = subprocess.run([sys.executable, 'phases/phase3_closed_loop_feedback.py'],
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        sys.exit(result.returncode)
    elif phase == '4':
        print("Running energy harvesting simulation (Phase 4)...")
        import subprocess
        result = subprocess.run([sys.executable, 'phases/phase4_energy_harvesting.py'],
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        sys.exit(result.returncode)
    elif phase == '5':
        print("Running adaptive membrane simulation (Phase 5)...")
        import subprocess
        result = subprocess.run([sys.executable, 'phases/phase5_adaptive_membrane.py'],
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        sys.exit(result.returncode)
    elif phase == '6':
        print("Running recursive reflection simulation (Phase 6)...")
        import subprocess
        result = subprocess.run([sys.executable, 'phases/phase6_recursive_reflection.py'],
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        sys.exit(result.returncode)
    else:
        print(f"Unknown phase: {phase}")
        sys.exit(1)


def run_appendix(name):
    """Run an appendix simulation."""
    import subprocess
    if name == 'a' or name == 'base':
        print("Running base simulation (Appendix A)...")
        result = subprocess.run([sys.executable, 'appendices/appendix_a_base_simulation.py'],
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        sys.exit(result.returncode)
    elif name == 'b' or name == 'graph':
        print("Running system graph visualization (Appendix B)...")
        result = subprocess.run([sys.executable, 'appendices/appendix_b_system_graph.py'],
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        sys.exit(result.returncode)
    elif name == 'c' or name == 'reflection':
        print("Running recursive reflection (Appendix C)...")
        result = subprocess.run([sys.executable, 'appendices/appendix_c_recursive_reflection.py'],
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        sys.exit(result.returncode)
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
        print("Consciousness System Environment v1.0.0")
        print("Multi-Layer Architecture for Synthetic Proto-Consciousness")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

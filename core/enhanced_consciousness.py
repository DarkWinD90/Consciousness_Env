"""
Enhanced Consciousness System - Full integration of SNN with Claude cognitive layer.

This module provides the complete integrated system that combines:
- Fast SNN processing (microsecond-scale reflexes)
- Slow Claude processing (deliberative reasoning)
- Adaptive attention allocation
- Self-modeling and intention formation
- Energy-aware cognitive gating

The architecture mirrors biological brain organization where subcortical
structures handle fast reflexes while cortical areas provide higher cognition.

Example:
    >>> system = EnhancedConsciousnessSystem()
    >>> system.set_goal("optimize energy efficiency")
    >>> for _ in range(100):
    ...     system.step(external_input=0.5)
    >>> print(system.get_status())
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import time

from .base_snn import BaseSNN, SNNConfig
from .thermochromic import ThermochromicMixin, ColorState
from .energy import EnergyHarvester, EnergyConfig
from .history import HistoryTracker
from .claude_interface import ClaudeNeuralInterface, NeuralQuery, CognitiveResponse
from .neural_router import ClaudeOptimizedRouter, NetworkTopology, NeuralPacket, SignalType
from .consciousness_enhancer import ConsciousnessEnhancer, CognitiveMode


@dataclass
class SystemState:
    """Complete system state across all layers"""
    # Physical state
    temperature: float = 25.0
    energy_storage: float = 50.0
    color: ColorState = field(default_factory=lambda: ColorState(0.5, 0.5, 0.5))

    # Neural state
    spike_count: int = 0
    mean_potential: float = 0.0
    snn_output: float = 0.0

    # Cognitive state
    cognitive_mode: str = "reactive"
    attention_focus: Optional[str] = None
    active_intentions: int = 0
    self_model_confidence: float = 0.5

    # Performance metrics
    step_count: int = 0
    cognitive_queries: int = 0
    cache_hits: int = 0


class EnhancedConsciousnessSystem(ThermochromicMixin):
    """
    Full integration of SNN with Claude cognitive layer.

    This system implements a hybrid architecture:

    FAST PATH (every step):
    - SNN spike processing
    - Energy harvesting
    - Thermochromic adaptation
    - Basic stimulus-response

    SLOW PATH (periodic):
    - Claude cognitive queries
    - Attention reallocation
    - Intention management
    - Self-model updates

    The system adaptively balances between fast and slow processing
    based on energy availability and task demands.
    """

    # Thermochromic parameters
    neutral_temp = 25.0
    warm_threshold = 30.0
    temp_range = 15.0

    def __init__(self,
                 num_neurons: int = 50,
                 cognitive_interval: int = 10,
                 mock_claude: bool = True,
                 enable_routing: bool = True):
        """
        Initialize the Enhanced Consciousness System.

        Args:
            num_neurons: Number of neurons in the SNN
            cognitive_interval: Steps between Claude consultations
            mock_claude: If True, simulate Claude responses
            enable_routing: If True, enable neural packet routing
        """
        # === PHYSICAL LAYER ===
        self.snn = BaseSNN(SNNConfig(
            num_neurons=num_neurons,
            threshold=0.5,
            leak_factor=0.1,
            refractory_period=2,
            weight_scale=0.1
        ))

        self.harvester = EnergyHarvester(
            config=EnergyConfig(
                friction_factor=0.0005,
                thermal_factor=0.0002,
                time_step_hours=0.005,
                base_consumption_mw=100.0  # Lower for simulation
            ),
            initial_energy=50.0
        )

        self.history = HistoryTracker(fields=[
            'spikes', 'energy', 'temperature', 'snn_output',
            'cognitive_mode', 'attention', 'color_r', 'color_g', 'color_b'
        ])

        # === COGNITIVE LAYER ===
        self.claude = ClaudeNeuralInterface(
            energy_harvester=self.harvester,
            mock_mode=mock_claude,
            latency_budget_ms=500,
            query_energy_cost=0.02
        )

        self.consciousness = ConsciousnessEnhancer(
            snn=self.snn,
            claude_interface=self.claude,
            history_tracker=self.history,
            reflection_interval=30.0
        )

        # === ROUTING LAYER (optional) ===
        self.enable_routing = enable_routing
        if enable_routing:
            self.topology = self._create_neural_topology(num_neurons)
            self.router = ClaudeOptimizedRouter(
                topology=self.topology,
                claude_interface=self.claude,
                priority_threshold=0.7
            )
        else:
            self.topology = None
            self.router = None

        # === SYSTEM STATE ===
        self.state = SystemState()
        self.cognitive_interval = cognitive_interval
        self.step_counter = 0

        # === CURRENT STIMULI ===
        self.current_stimuli: Dict[str, float] = {}
        self.attention_weights: Dict[str, float] = {}

        # === COLOR STATE ===
        self._color = ColorState(0.5, 0.5, 0.5)

    def _create_neural_topology(self, num_neurons: int) -> NetworkTopology:
        """Create a neural network topology for routing"""
        topology = NetworkTopology()

        # Create nodes for each neuron
        for i in range(num_neurons):
            topology.add_node(i, energy=1.0, load=0.0)

        # Create small-world connectivity
        # Each neuron connects to k nearest neighbors + random long-range
        k = min(4, num_neurons - 1)  # Local connectivity
        p_long = 0.1  # Probability of long-range connection

        for i in range(num_neurons):
            # Local connections
            for j in range(1, k + 1):
                neighbor = (i + j) % num_neurons
                topology.add_edge(i, neighbor, weight=1.0)

            # Random long-range connections
            for j in range(num_neurons):
                if j != i and np.random.random() < p_long:
                    if (i, j) not in topology.edges:
                        topology.add_edge(i, j, weight=1.5)

        return topology

    def step(self, external_input: float, stimuli: Optional[Dict[str, float]] = None) -> SystemState:
        """
        Execute one consciousness cycle.

        This is the main loop that combines fast SNN processing
        with periodic slow cognitive processing.

        Args:
            external_input: External stimulus value [0, 1]
            stimuli: Optional dictionary of named stimuli

        Returns:
            Updated SystemState
        """
        self.step_counter += 1
        self.state.step_count = self.step_counter

        # Update stimuli
        if stimuli:
            self.current_stimuli = stimuli
        else:
            self.current_stimuli = {'external': external_input}

        # === FAST PATH: SNN Processing ===
        potentials, spikes = self._fast_path_processing(external_input)

        # === SLOW PATH: Cognitive Processing (periodic) ===
        if self.step_counter % self.cognitive_interval == 0:
            self._slow_path_processing()

        # === PHYSICAL UPDATES ===
        self._update_physical_state(spikes)

        # === RECORD HISTORY ===
        self._record_history()

        return self.state

    def _fast_path_processing(self, external_input: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fast path: SNN spike processing (every step).

        This handles:
        - Spike generation and propagation
        - Basic stimulus-response behavior
        - Reflex-like reactions
        """
        # Apply attention weighting to input if available
        if self.attention_weights and 'external' in self.attention_weights:
            weighted_input = external_input * self.attention_weights['external']
        else:
            weighted_input = external_input

        # Get modulation from last cognitive response
        modulation = getattr(self, '_last_modulation', 0.0)

        # Process through SNN with reflection
        reflection_coeff = 0.2 + modulation * 0.1  # Modulate reflection
        potentials, spikes = self.snn.step(weighted_input, reflection_coeff=reflection_coeff)

        # Update state
        self.state.spike_count = int(np.sum(spikes))
        self.state.mean_potential = float(np.mean(potentials))
        self.state.snn_output = self.snn.get_output()

        # Route spikes if enabled
        if self.enable_routing and self.router and self.state.spike_count > 0:
            self._route_spikes(spikes)

        return potentials, spikes

    def _route_spikes(self, spikes: np.ndarray):
        """Route spike packets through the network"""
        # Find neurons that spiked
        spiking_neurons = np.where(spikes)[0]

        for src in spiking_neurons[:5]:  # Limit routing per step
            # Create packet to random target
            target = np.random.randint(0, self.snn.num_neurons)
            if target != src:
                packet = NeuralPacket(
                    source=int(src),
                    target=int(target),
                    payload=np.array([self.snn.membrane_potential[src]]),
                    signal_type=SignalType.SPIKE,
                    priority=0.5
                )
                self.router.enqueue_packet(packet)

        # Process some packets
        self.router.process_queue(max_packets=3)

    def _slow_path_processing(self):
        """
        Slow path: Claude cognitive processing (periodic).

        This handles:
        - Attention reallocation
        - Intention checking
        - Self-model updates
        - Cognitive mode adjustments
        """
        # Build neural query
        query = NeuralQuery(
            spike_pattern=self.snn.membrane_potential,
            energy_state=self.harvester.energy_storage,
            temperature=self.state.temperature,
            context=f"Regular cognitive cycle. Step {self.step_counter}. "
                    f"Recent spike rate: {self.state.spike_count}. "
                    f"Current mode: {self.consciousness.mode.value}",
            urgency=0.5,
            history_window=self._get_recent_history()
        )

        # Query Claude
        response = self.claude.query_cognitive_layer(query)

        if response:
            self.state.cognitive_queries += 1
            self._apply_cognitive_response(response)

        # Update attention
        if self.current_stimuli:
            self.attention_weights = self.consciousness.allocate_attention(self.current_stimuli)
            self.state.attention_focus = self.consciousness.attention.focus

        # Check for self-model update
        self.consciousness.update_self_model()

        # Update cognitive state
        self.state.cognitive_mode = self.consciousness.mode.value
        self.state.active_intentions = len(self.consciousness.get_active_intentions())
        self.state.self_model_confidence = self.consciousness.self_model.confidence

    def _apply_cognitive_response(self, response: CognitiveResponse):
        """Apply Claude's cognitive response to the system"""
        # Store modulation for fast path
        self._last_modulation = response.modulation_signal

        # Apply attention weights to SNN thresholds
        if len(response.attention_weights) == self.snn.num_neurons:
            # Lower threshold for attended neurons (more sensitive)
            attention_factor = 1.0 - response.attention_weights * 0.3
            # Note: We store this but don't modify SNN threshold directly
            # to keep fast path fast

        # Execute action directive if present
        if response.action_directive:
            self._execute_directive(response.action_directive)

        # Record experience
        self.consciousness.record_experience({
            'step': self.step_counter,
            'modulation': response.modulation_signal,
            'confidence': response.confidence,
            'action': response.action_directive
        })

    def _execute_directive(self, directive: str):
        """Execute a high-level action directive from Claude"""
        directive_lower = directive.lower()

        # Mode switching
        if 'explore' in directive_lower:
            self.consciousness.set_mode(CognitiveMode.EXPLORATORY)
        elif 'reflect' in directive_lower:
            self.consciousness.set_mode(CognitiveMode.REFLECTIVE)
        elif 'habit' in directive_lower:
            self.consciousness.set_mode(CognitiveMode.HABITUAL)
        elif 'deliberate' in directive_lower or 'think' in directive_lower:
            self.consciousness.set_mode(CognitiveMode.DELIBERATIVE)
        elif 'react' in directive_lower:
            self.consciousness.set_mode(CognitiveMode.REACTIVE)

        # Energy management
        if 'conserve' in directive_lower or 'save energy' in directive_lower:
            # Reduce cognitive query frequency temporarily
            self.cognitive_interval = min(20, self.cognitive_interval + 5)
        elif 'active' in directive_lower or 'engage' in directive_lower:
            self.cognitive_interval = max(5, self.cognitive_interval - 2)

    def _update_physical_state(self, spikes: np.ndarray):
        """Update physical state (energy, temperature, color)"""
        # Energy harvesting from neural activity
        activity_level = np.mean(spikes) * 10  # Scale activity
        friction_energy = self.harvester.harvest_friction(activity_level)
        thermal_energy = self.harvester.harvest_thermal(self.state.temperature)
        self.harvester.update_storage(friction_energy, thermal_energy)

        self.state.energy_storage = self.harvester.energy_storage

        # Temperature dynamics
        activity_heat = self.state.spike_count * 0.01
        cooling = (self.state.temperature - 20.0) * 0.05
        self.state.temperature += activity_heat - cooling
        self.state.temperature = np.clip(self.state.temperature, 15.0, 45.0)

        # Thermochromic color update
        self._color = self.compute_thermochromic_color(self.state.temperature)
        self.state.color = self._color

    def _record_history(self):
        """Record current state to history"""
        self.history.record(
            spikes=self.state.spike_count,
            energy=self.state.energy_storage,
            temperature=self.state.temperature,
            snn_output=self.state.snn_output,
            cognitive_mode=hash(self.state.cognitive_mode) % 100 / 100,  # Encode as float
            attention=self.attention_weights.get('external', 0.5) if self.attention_weights else 0.5,
            color_r=self._color.r,
            color_g=self._color.g,
            color_b=self._color.b
        )

    def _get_recent_history(self, window: int = 10) -> List[Dict]:
        """Get recent history for cognitive context"""
        history = []
        for i in range(window):
            idx = -(i + 1)
            try:
                history.append({
                    'spikes': self.history.get('spikes')[idx],
                    'energy': self.history.get('energy')[idx],
                    'temp': self.history.get('temperature')[idx]
                })
            except (IndexError, KeyError):
                break
        return history

    def set_goal(self, goal: str, priority: float = 0.5) -> bool:
        """
        Set a high-level goal for the system.

        Args:
            goal: Goal description
            priority: Goal priority [0, 1]

        Returns:
            True if intention was formed successfully
        """
        intention = self.consciousness.form_intention(goal, priority)
        return intention is not None

    def run_simulation(self, num_steps: int, input_generator=None) -> Dict[str, Any]:
        """
        Run a complete simulation.

        Args:
            num_steps: Number of steps to simulate
            input_generator: Optional function(step) -> input_value

        Returns:
            Dictionary with simulation results
        """
        print(f"Running Enhanced Consciousness simulation for {num_steps} steps...")
        print(f"(Cognitive interval: {self.cognitive_interval}, Routing: {self.enable_routing})")

        start_time = time.time()

        for step in range(num_steps):
            # Generate input
            if input_generator:
                external_input = input_generator(step)
            else:
                # Default: sinusoidal input with noise
                external_input = 0.5 + 0.3 * np.sin(step / 10) + 0.1 * np.random.randn()
                external_input = np.clip(external_input, 0, 1)

            self.step(external_input)

            # Progress update
            if (step + 1) % (num_steps // 10) == 0:
                print(f"  Step {step + 1}/{num_steps}: "
                      f"Energy={self.state.energy_storage:.2f}, "
                      f"Mode={self.state.cognitive_mode}, "
                      f"Queries={self.state.cognitive_queries}")

        elapsed = time.time() - start_time

        return {
            'num_steps': num_steps,
            'elapsed_seconds': elapsed,
            'steps_per_second': num_steps / elapsed,
            'final_state': self.state,
            'cognitive_stats': self.claude.get_statistics(),
            'consciousness_stats': self.consciousness.get_statistics(),
            'router_stats': self.router.get_statistics() if self.router else None
        }

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'state': {
                'step': self.state.step_count,
                'energy': self.state.energy_storage,
                'temperature': self.state.temperature,
                'spike_count': self.state.spike_count,
                'snn_output': self.state.snn_output,
                'color': self.state.color.to_list()
            },
            'cognitive': {
                'mode': self.state.cognitive_mode,
                'focus': self.state.attention_focus,
                'active_intentions': self.state.active_intentions,
                'self_model_confidence': self.state.self_model_confidence,
                'queries': self.state.cognitive_queries
            },
            'interface_stats': self.claude.get_statistics(),
            'consciousness_stats': self.consciousness.get_statistics()
        }


def demo_enhanced_consciousness():
    """Demonstrate the Enhanced Consciousness System"""
    print("=" * 70)
    print("ENHANCED CONSCIOUSNESS SYSTEM DEMO")
    print("Integrating SNN with Claude Cognitive Layer")
    print("=" * 70)
    print()

    # Create system
    system = EnhancedConsciousnessSystem(
        num_neurons=30,
        cognitive_interval=10,
        mock_claude=True,
        enable_routing=True
    )

    # Set a goal
    print("Setting goal: 'optimize energy efficiency'")
    system.set_goal("optimize energy efficiency", priority=0.7)
    print()

    # Run simulation
    results = system.run_simulation(num_steps=100)

    print()
    print("=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print(f"Steps per second: {results['steps_per_second']:.2f}")
    print(f"Cognitive queries: {results['cognitive_stats']['total_queries']}")
    print(f"Cache hit rate: {results['cognitive_stats']['cache_hit_rate']:.2%}")
    print()

    status = system.get_status()
    print("Final Status:")
    print(f"  Energy: {status['state']['energy']:.2f} mWh")
    print(f"  Mode: {status['cognitive']['mode']}")
    print(f"  Self-model confidence: {status['cognitive']['self_model_confidence']:.2f}")
    print(f"  Active intentions: {status['cognitive']['active_intentions']}")

    return system, results


if __name__ == "__main__":
    system, results = demo_enhanced_consciousness()

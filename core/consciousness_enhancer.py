"""
Consciousness Enhancer - Higher-order cognitive features via Claude integration.

This module implements meta-cognitive capabilities that emerge from
integrating Claude's reasoning with the SNN substrate:

- Self-model maintenance (introspection)
- Intention formation (goal-directed behavior)
- Attention allocation (resource management)
- Counterfactual reasoning (learning from hypotheticals)
- Temporal binding (integrating past/present/future)

These features enable the system to exhibit behaviors associated with
higher-order consciousness: self-awareness, planning, and reflection.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import numpy as np
import time
import json
from collections import deque


class CognitiveMode(Enum):
    """Operating modes for cognitive processing"""
    REACTIVE = "reactive"          # Pure stimulus-response
    DELIBERATIVE = "deliberative"  # Slow, thoughtful processing
    HABITUAL = "habitual"          # Learned automatic responses
    EXPLORATORY = "exploratory"    # Novelty-seeking behavior
    REFLECTIVE = "reflective"      # Self-examination mode


@dataclass
class Intention:
    """
    Represents a goal-directed intention.

    Intentions bridge the gap between goals (what to achieve)
    and actions (how to achieve it).
    """
    goal: str                      # What we want to achieve
    plan: List[str]               # Steps to achieve it
    priority: float               # Importance [0, 1]
    confidence: float             # Likelihood of success [0, 1]
    created_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None  # Optional deadline
    prerequisites: List[str] = field(default_factory=list)
    status: str = "pending"       # pending, active, completed, failed
    attention_allocation: Optional[np.ndarray] = None

    def is_expired(self) -> bool:
        """Check if intention has passed deadline"""
        if self.deadline is None:
            return False
        return time.time() > self.deadline

    def age(self) -> float:
        """Get intention age in seconds"""
        return time.time() - self.created_at


@dataclass
class SelfModel:
    """
    The system's model of itself.

    Maintains beliefs about capabilities, limitations, and behavioral patterns.
    Updated through introspection and experience.
    """
    capabilities: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    current_goals: List[str] = field(default_factory=list)
    behavioral_patterns: Dict[str, float] = field(default_factory=dict)
    performance_history: Dict[str, List[float]] = field(default_factory=dict)
    last_updated: float = field(default_factory=time.time)
    confidence: float = 0.5  # Confidence in self-model accuracy

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'capabilities': self.capabilities,
            'limitations': self.limitations,
            'current_goals': self.current_goals,
            'behavioral_patterns': self.behavioral_patterns,
            'performance_metrics': {
                k: {'mean': np.mean(v), 'std': np.std(v), 'trend': self._compute_trend(v)}
                for k, v in self.performance_history.items() if len(v) > 0
            },
            'confidence': self.confidence
        }

    def _compute_trend(self, values: List[float]) -> str:
        """Compute trend direction"""
        if len(values) < 3:
            return "unknown"
        recent = np.mean(values[-3:])
        older = np.mean(values[:-3]) if len(values) > 3 else values[0]
        if recent > older * 1.1:
            return "improving"
        elif recent < older * 0.9:
            return "declining"
        return "stable"

    def update_performance(self, metric: str, value: float, max_history: int = 100):
        """Record a performance metric"""
        if metric not in self.performance_history:
            self.performance_history[metric] = []
        self.performance_history[metric].append(value)
        if len(self.performance_history[metric]) > max_history:
            self.performance_history[metric].pop(0)


@dataclass
class AttentionState:
    """Current state of attention allocation"""
    focus: Optional[str] = None          # Current primary focus
    weights: Dict[str, float] = field(default_factory=dict)  # Attention distribution
    suppressed: List[str] = field(default_factory=list)      # Actively suppressed
    duration: float = 0.0                # Time in current focus
    switches: int = 0                    # Number of attention switches


class ConsciousnessEnhancer:
    """
    Higher-order consciousness features via Claude integration.

    This class implements meta-cognitive capabilities:

    1. Self-Model Maintenance
       - Tracks capabilities and limitations
       - Updates through experience and reflection
       - Provides self-awareness for planning

    2. Intention Formation
       - Converts goals into actionable plans
       - Manages competing intentions
       - Tracks intention execution

    3. Attention Allocation
       - Distributes cognitive resources
       - Balances exploration vs exploitation
       - Handles attention switching

    4. Counterfactual Reasoning
       - "What-if" analysis for learning
       - Causal understanding
       - Planning improvements

    5. Temporal Integration
       - Binds past experiences with present
       - Projects into future scenarios
       - Maintains temporal coherence

    Example:
        >>> enhancer = ConsciousnessEnhancer(snn, claude, history)
        >>> enhancer.form_intention("optimize energy efficiency")
        >>> attention = enhancer.allocate_attention({
        ...     'sensor_input': 0.8,
        ...     'motor_control': 0.3,
        ...     'energy_monitoring': 0.6
        ... })
    """

    def __init__(self,
                 snn: Any,
                 claude_interface: Any,
                 history_tracker: Any,
                 reflection_interval: float = 10.0,
                 max_intentions: int = 5):
        """
        Initialize the ConsciousnessEnhancer.

        Args:
            snn: BaseSNN instance for neural processing
            claude_interface: ClaudeNeuralInterface for cognitive queries
            history_tracker: HistoryTracker for state history
            reflection_interval: Seconds between self-model updates
            max_intentions: Maximum concurrent intentions
        """
        self.snn = snn
        self.claude = claude_interface
        self.history = history_tracker
        self.reflection_interval = reflection_interval
        self.max_intentions = max_intentions

        # Meta-cognitive state
        self.self_model = SelfModel()
        self.intentions: List[Intention] = []
        self.attention = AttentionState()
        self.mode = CognitiveMode.REACTIVE

        # Experience buffer for learning
        self.experience_buffer: deque = deque(maxlen=1000)
        self.counterfactual_cache: Dict[str, str] = {}

        # Timing
        self.last_reflection_time = time.time()
        self.last_intention_check = time.time()

        # Statistics
        self.reflection_count = 0
        self.intentions_formed = 0
        self.intentions_completed = 0
        self.attention_switches = 0

    def update_self_model(self, force: bool = False) -> bool:
        """
        Have Claude update the system's self-model.

        Analyzes recent behavior to update beliefs about
        capabilities, limitations, and patterns.

        Args:
            force: Force update even if interval hasn't passed

        Returns:
            True if update was performed
        """
        # Check if update is due
        if not force and (time.time() - self.last_reflection_time) < self.reflection_interval:
            return False

        self.last_reflection_time = time.time()
        self.reflection_count += 1

        # Gather recent experience
        recent_experiences = list(self.experience_buffer)[-50:]

        # Get recent history from tracker
        recent_history = {}
        if hasattr(self.history, 'data'):
            for key in self.history.data:
                data = self.history.get(key)
                if len(data) > 0:
                    recent_history[key] = {
                        'recent_mean': float(np.mean(data[-20:])) if len(data) >= 20 else float(np.mean(data)),
                        'recent_std': float(np.std(data[-20:])) if len(data) >= 20 else float(np.std(data)),
                        'trend': 'up' if len(data) > 5 and np.mean(data[-5:]) > np.mean(data[-10:-5]) else 'down'
                    }

        # Import here to avoid circular dependency
        from .claude_interface import NeuralQuery

        # Build introspection query
        query = NeuralQuery(
            spike_pattern=self.snn.membrane_potential if hasattr(self.snn, 'membrane_potential') else np.zeros(10),
            energy_state=getattr(self.claude.harvester, 'energy_storage', 50.0) if self.claude.harvester else 50.0,
            temperature=25.0,
            context=f"""SELF_MODEL_UPDATE: Analyze recent behavior and update self-understanding.

Current self-model:
{json.dumps(self.self_model.to_dict(), indent=2, default=str)}

Recent performance history:
{json.dumps(recent_history, indent=2, default=str)}

Active intentions: {len([i for i in self.intentions if i.status == 'active'])}
Completed intentions: {self.intentions_completed}
Current mode: {self.mode.value}

What capabilities have been demonstrated? What limitations observed?
What behavioral patterns are emerging?""",
            urgency=0.3,
            history_window=recent_experiences[-10:]
        )

        response = self.claude.query_cognitive_layer(query)

        if response and response.action_directive:
            self._integrate_model_update(response.action_directive, response.confidence)
            return True

        return False

    def _integrate_model_update(self, update_text: str, confidence: float):
        """Parse and integrate self-model updates"""
        # Update confidence based on response
        self.self_model.confidence = 0.7 * self.self_model.confidence + 0.3 * confidence
        self.self_model.last_updated = time.time()

        # Parse capabilities from update text
        update_lower = update_text.lower()

        # Look for capability indicators
        if 'can' in update_lower or 'able' in update_lower or 'capable' in update_lower:
            if 'pattern' in update_lower:
                self._add_capability('pattern_recognition')
            if 'energy' in update_lower:
                self._add_capability('energy_management')
            if 'adapt' in update_lower:
                self._add_capability('adaptation')

        # Look for limitation indicators
        if 'cannot' in update_lower or 'unable' in update_lower or 'limited' in update_lower:
            if 'speed' in update_lower:
                self._add_limitation('processing_speed')
            if 'memory' in update_lower:
                self._add_limitation('memory_capacity')

    def _add_capability(self, capability: str):
        """Add a capability if not already present"""
        if capability not in self.self_model.capabilities:
            self.self_model.capabilities.append(capability)

    def _add_limitation(self, limitation: str):
        """Add a limitation if not already present"""
        if limitation not in self.self_model.limitations:
            self.self_model.limitations.append(limitation)

    def form_intention(self, goal: str, priority: float = 0.5,
                      deadline: Optional[float] = None) -> Optional[Intention]:
        """
        Form an intention to achieve a goal.

        Uses Claude to decompose the goal into actionable steps
        and assess feasibility given current capabilities.

        Args:
            goal: The goal to achieve
            priority: Importance of the goal [0, 1]
            deadline: Optional deadline timestamp

        Returns:
            Formed Intention or None if unable to plan
        """
        # Check intention limit
        active_intentions = [i for i in self.intentions if i.status in ['pending', 'active']]
        if len(active_intentions) >= self.max_intentions:
            # Remove lowest priority or oldest intention
            if active_intentions:
                to_remove = min(active_intentions, key=lambda i: (i.priority, -i.age()))
                self.intentions.remove(to_remove)

        # Import here to avoid circular dependency
        from .claude_interface import NeuralQuery

        # Query Claude for plan formation
        query = NeuralQuery(
            spike_pattern=self.snn.membrane_potential if hasattr(self.snn, 'membrane_potential') else np.zeros(10),
            energy_state=getattr(self.claude.harvester, 'energy_storage', 50.0) if self.claude.harvester else 50.0,
            temperature=25.0,
            context=f"""FORM_INTENTION: Create a plan to achieve the goal.

Goal: {goal}
Priority: {priority}
Deadline: {deadline if deadline else 'None'}

Current capabilities: {self.self_model.capabilities}
Current limitations: {self.self_model.limitations}
Active intentions: {[i.goal for i in self.intentions if i.status == 'active']}

Provide a JSON response with:
- "plan": list of action steps
- "confidence": likelihood of success (0-1)
- "prerequisites": what must be true first
- "attention": suggested attention weights""",
            urgency=priority,
            history_window=[]
        )

        response = self.claude.query_cognitive_layer(query)

        if response:
            # Parse plan from response
            plan = self._parse_plan(response.action_directive)

            intention = Intention(
                goal=goal,
                plan=plan,
                priority=priority,
                confidence=response.confidence,
                deadline=deadline,
                attention_allocation=response.attention_weights
            )

            self.intentions.append(intention)
            self.intentions_formed += 1

            # Add to current goals in self-model
            if goal not in self.self_model.current_goals:
                self.self_model.current_goals.append(goal)

            return intention

        return None

    def _parse_plan(self, directive: Optional[str]) -> List[str]:
        """Parse action plan from Claude's directive"""
        if not directive:
            return ["Assess situation", "Execute default behavior"]

        # Try to parse as JSON
        try:
            data = json.loads(directive)
            if isinstance(data, dict) and 'plan' in data:
                return data['plan']
        except json.JSONDecodeError:
            pass

        # Fall back to splitting by newlines or semicolons
        steps = []
        for line in directive.replace(';', '\n').split('\n'):
            line = line.strip()
            if line and len(line) > 2:
                # Remove numbering
                if line[0].isdigit() and line[1] in '.):':
                    line = line[2:].strip()
                steps.append(line)

        return steps if steps else ["Execute directive: " + directive[:50]]

    def allocate_attention(self, stimuli: Dict[str, float],
                          mode_override: Optional[CognitiveMode] = None) -> Dict[str, float]:
        """
        Allocate attention across competing stimuli.

        Uses current goals, cognitive mode, and Claude's guidance
        to distribute attention optimally.

        Args:
            stimuli: Dictionary of stimulus_name -> salience
            mode_override: Optional mode override

        Returns:
            Dictionary of stimulus_name -> attention_weight (sum to 1)
        """
        mode = mode_override or self.mode

        # Track attention switch
        old_focus = self.attention.focus

        # Mode-based baseline allocation
        if mode == CognitiveMode.REACTIVE:
            # Attention proportional to salience
            weights = self._salience_based_attention(stimuli)

        elif mode == CognitiveMode.DELIBERATIVE:
            # Query Claude for nuanced allocation
            weights = self._claude_guided_attention(stimuli)

        elif mode == CognitiveMode.HABITUAL:
            # Use cached/learned allocations
            weights = self._habitual_attention(stimuli)

        elif mode == CognitiveMode.EXPLORATORY:
            # Favor novel/unexpected stimuli
            weights = self._exploratory_attention(stimuli)

        elif mode == CognitiveMode.REFLECTIVE:
            # Focus inward, reduce external attention
            weights = self._reflective_attention(stimuli)

        else:
            weights = self._salience_based_attention(stimuli)

        # Update attention state
        max_stimulus = max(weights, key=weights.get)
        if max_stimulus != old_focus:
            self.attention_switches += 1
            self.attention.switches += 1
            self.attention.duration = 0
        else:
            self.attention.duration += 1

        self.attention.focus = max_stimulus
        self.attention.weights = weights

        return weights

    def _salience_based_attention(self, stimuli: Dict[str, float]) -> Dict[str, float]:
        """Allocate attention proportional to stimulus salience"""
        total = sum(stimuli.values()) + 1e-10
        return {k: v / total for k, v in stimuli.items()}

    def _claude_guided_attention(self, stimuli: Dict[str, float]) -> Dict[str, float]:
        """Use Claude for nuanced attention allocation"""
        from .claude_interface import NeuralQuery

        query = NeuralQuery(
            spike_pattern=np.array(list(stimuli.values())),
            energy_state=getattr(self.claude.harvester, 'energy_storage', 50.0) if self.claude.harvester else 50.0,
            temperature=25.0,
            context=f"""ATTENTION_ALLOCATION: Distribute attention across stimuli.

Stimuli (salience): {stimuli}
Current goals: {self.self_model.current_goals}
Active intentions: {[i.goal for i in self.intentions if i.status == 'active']}
Current focus: {self.attention.focus}
Focus duration: {self.attention.duration}

Which stimuli deserve attention given current goals?""",
            urgency=0.6,
            history_window=[]
        )

        response = self.claude.query_cognitive_layer(query)

        if response and len(response.attention_weights) >= len(stimuli):
            weights = response.attention_weights[:len(stimuli)]
            weights = weights / (np.sum(weights) + 1e-10)
            return dict(zip(stimuli.keys(), weights))

        return self._salience_based_attention(stimuli)

    def _habitual_attention(self, stimuli: Dict[str, float]) -> Dict[str, float]:
        """Use learned attention patterns"""
        weights = {}
        for stimulus in stimuli:
            # Check behavioral patterns for learned weights
            pattern_key = f"attention_{stimulus}"
            learned_weight = self.self_model.behavioral_patterns.get(pattern_key, 0.5)
            weights[stimulus] = stimuli[stimulus] * learned_weight

        # Normalize
        total = sum(weights.values()) + 1e-10
        return {k: v / total for k, v in weights.items()}

    def _exploratory_attention(self, stimuli: Dict[str, float]) -> Dict[str, float]:
        """Favor novel or unexpected stimuli"""
        weights = {}
        for stimulus, salience in stimuli.items():
            # Check if stimulus is novel (not in history)
            pattern_key = f"seen_{stimulus}"
            familiarity = self.self_model.behavioral_patterns.get(pattern_key, 0.0)
            novelty = 1.0 - familiarity
            weights[stimulus] = salience * (1 + novelty)

            # Update familiarity
            self.self_model.behavioral_patterns[pattern_key] = min(1.0, familiarity + 0.1)

        # Normalize
        total = sum(weights.values()) + 1e-10
        return {k: v / total for k, v in weights.items()}

    def _reflective_attention(self, stimuli: Dict[str, float]) -> Dict[str, float]:
        """Reduce external attention, focus inward"""
        weights = {}
        for stimulus, salience in stimuli.items():
            # Suppress external stimuli
            if 'internal' in stimulus.lower() or 'self' in stimulus.lower():
                weights[stimulus] = salience * 2.0
            else:
                weights[stimulus] = salience * 0.3

        # Normalize
        total = sum(weights.values()) + 1e-10
        return {k: v / total for k, v in weights.items()}

    def counterfactual_reasoning(self, event: Dict[str, Any],
                                 alternative: str) -> str:
        """
        Perform "what-if" reasoning about alternative scenarios.

        Useful for:
        - Learning from mistakes
        - Planning future actions
        - Understanding causality

        Args:
            event: Description of what actually happened
            alternative: Description of alternative scenario

        Returns:
            Analysis of counterfactual scenario
        """
        # Check cache
        cache_key = f"{json.dumps(event, sort_keys=True)}|{alternative}"
        if cache_key in self.counterfactual_cache:
            return self.counterfactual_cache[cache_key]

        from .claude_interface import NeuralQuery

        query = NeuralQuery(
            spike_pattern=np.zeros(10),
            energy_state=50.0,
            temperature=25.0,
            context=f"""COUNTERFACTUAL_REASONING: Analyze alternative scenario.

What actually happened:
{json.dumps(event, indent=2, default=str)}

Alternative scenario to consider:
{alternative}

Self-model context:
- Capabilities: {self.self_model.capabilities}
- Limitations: {self.self_model.limitations}

Questions to address:
1. What would have happened differently?
2. What can be learned from this comparison?
3. How should future behavior be adjusted?""",
            urgency=0.2,
            history_window=list(self.experience_buffer)[-5:]
        )

        response = self.claude.query_cognitive_layer(query)

        result = response.action_directive if response and response.action_directive else \
                 "Unable to reason about counterfactual scenario"

        # Cache result
        self.counterfactual_cache[cache_key] = result

        return result

    def record_experience(self, experience: Dict[str, Any]):
        """
        Record an experience for learning and reflection.

        Args:
            experience: Dictionary describing the experience
        """
        experience['timestamp'] = time.time()
        self.experience_buffer.append(experience)

    def set_mode(self, mode: CognitiveMode):
        """Set the cognitive operating mode"""
        self.mode = mode

    def update_intention_status(self, goal: str, status: str):
        """Update the status of an intention"""
        for intention in self.intentions:
            if intention.goal == goal:
                intention.status = status
                if status == 'completed':
                    self.intentions_completed += 1
                    if goal in self.self_model.current_goals:
                        self.self_model.current_goals.remove(goal)
                break

    def get_active_intentions(self) -> List[Intention]:
        """Get all active intentions"""
        return [i for i in self.intentions if i.status == 'active']

    def get_statistics(self) -> Dict[str, Any]:
        """Get consciousness enhancer statistics"""
        return {
            'mode': self.mode.value,
            'reflection_count': self.reflection_count,
            'intentions_formed': self.intentions_formed,
            'intentions_completed': self.intentions_completed,
            'active_intentions': len(self.get_active_intentions()),
            'attention_switches': self.attention_switches,
            'current_focus': self.attention.focus,
            'self_model_confidence': self.self_model.confidence,
            'capabilities': len(self.self_model.capabilities),
            'experience_buffer_size': len(self.experience_buffer)
        }

"""
Claude Neural Interface - Bidirectional communication between SNN and Claude CLI.

This module implements the translation layer between low-level spike patterns
and high-level semantic processing via Claude, enabling:
- Spike pattern encoding to semantic representations
- Cognitive response decoding to modulatory signals
- Energy-aware query management
- Latency-conscious processing with caching

Architecture:
    SNN Layer <---> ClaudeNeuralInterface <---> Claude CLI
    (spikes)        (translation)              (reasoning)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import json
import subprocess
import hashlib
import time
from enum import Enum


class PatternType(Enum):
    """Classification of neural spike patterns"""
    BURST = "burst"           # High-frequency clustered spikes
    TONIC = "tonic"           # Regular sustained firing
    SPARSE = "sparse"         # Low-frequency isolated spikes
    SILENT = "silent"         # No activity
    SYNCHRONOUS = "synchronous"  # Multiple neurons firing together
    IRREGULAR = "irregular"   # No clear pattern
    OSCILLATORY = "oscillatory"  # Rhythmic firing
    RAMPING = "ramping"       # Gradually increasing/decreasing


@dataclass
class NeuralQuery:
    """
    Query from SNN to Claude cognitive layer.

    Encapsulates the neural state and context for cognitive processing.
    """
    spike_pattern: np.ndarray      # Raw neural activity [neurons x time] or [time]
    energy_state: float            # Current energy reserves (mWh)
    temperature: float             # System temperature (C)
    context: str                   # Situational context / query type
    urgency: float = 0.5           # 0-1, affects latency budget and processing depth
    history_window: List[dict] = field(default_factory=list)  # Recent state history
    metadata: Dict[str, Any] = field(default_factory=dict)    # Additional context

    def __post_init__(self):
        if isinstance(self.spike_pattern, list):
            self.spike_pattern = np.array(self.spike_pattern)


@dataclass
class CognitiveResponse:
    """
    Response from Claude to SNN.

    Contains modulatory signals and high-level directives that
    influence neural processing.
    """
    modulation_signal: float           # Global gain adjustment [-1, 1]
    attention_weights: np.ndarray      # Per-neuron attention allocation
    synaptic_adjustments: Dict[Tuple[int, int], float] = field(default_factory=dict)
    action_directive: Optional[str] = None    # High-level action command
    routing_optimization: Dict[int, float] = field(default_factory=dict)
    confidence: float = 0.5            # Response confidence [0, 1]
    reasoning: str = ""                # Explanation of the response
    processing_time_ms: float = 0.0    # Time taken to generate response

    def __post_init__(self):
        if isinstance(self.attention_weights, list):
            self.attention_weights = np.array(self.attention_weights)


@dataclass
class EncodedPattern:
    """Semantic encoding of a spike pattern"""
    firing_rate: float
    variance: float
    synchrony: float
    pattern_type: PatternType
    trend: float
    active_ratio: float
    entropy: float
    burst_index: float

    def to_dict(self) -> dict:
        return {
            'firing_rate': self.firing_rate,
            'variance': self.variance,
            'synchrony': self.synchrony,
            'pattern_type': self.pattern_type.value,
            'trend': self.trend,
            'active_ratio': self.active_ratio,
            'entropy': self.entropy,
            'burst_index': self.burst_index
        }

    def summary(self) -> str:
        trend_str = 'increasing' if self.trend > 0.01 else 'decreasing' if self.trend < -0.01 else 'stable'
        return (f"{self.pattern_type.value} pattern: rate={self.firing_rate:.3f}, "
                f"sync={self.synchrony:.3f}, trend={trend_str}")


class SpikePatternCodebook:
    """
    Codebook for spike pattern classification.

    Maps raw spike patterns to semantic categories using
    template matching and statistical features.
    """

    def __init__(self):
        # Template patterns (8 time bins)
        self.templates = {
            PatternType.BURST: np.array([0, 0, 1, 1, 1, 1, 0, 0]),
            PatternType.TONIC: np.array([1, 0, 1, 0, 1, 0, 1, 0]),
            PatternType.SPARSE: np.array([0, 0, 1, 0, 0, 0, 1, 0]),
            PatternType.SILENT: np.array([0, 0, 0, 0, 0, 0, 0, 0]),
            PatternType.SYNCHRONOUS: np.array([1, 1, 1, 1, 0, 0, 0, 0]),
            PatternType.OSCILLATORY: np.array([1, 0, 0, 1, 0, 0, 1, 0]),
            PatternType.RAMPING: np.array([0, 0, 0, 0.3, 0.5, 0.7, 1, 1]),
        }

    def classify(self, spikes: np.ndarray) -> PatternType:
        """Classify spike pattern against templates"""
        # Flatten and normalize to 8 bins
        flat = spikes.flatten()
        if len(flat) < 8:
            flat = np.pad(flat, (0, 8 - len(flat)))
        elif len(flat) > 8:
            # Downsample to 8 bins
            indices = np.linspace(0, len(flat) - 1, 8).astype(int)
            flat = flat[indices]

        # Normalize
        if np.std(flat) > 0:
            flat = (flat - np.mean(flat)) / np.std(flat)

        # Match against templates
        best_match = PatternType.IRREGULAR
        best_score = -1

        for pattern_type, template in self.templates.items():
            if np.std(template) > 0:
                norm_template = (template - np.mean(template)) / np.std(template)
                score = np.corrcoef(flat, norm_template)[0, 1]
                if not np.isnan(score) and score > best_score:
                    best_score = score
                    best_match = pattern_type

        # Require minimum correlation for classification
        if best_score < 0.3:
            best_match = PatternType.IRREGULAR

        return best_match


class ClaudeNeuralInterface:
    """
    Bidirectional interface between SNN and Claude CLI.

    Handles:
    - Encoding spike patterns into semantic representations
    - Querying Claude for cognitive processing
    - Decoding responses into neural modulatory signals
    - Energy-aware query gating
    - Response caching for efficiency

    Example:
        >>> interface = ClaudeNeuralInterface(energy_harvester)
        >>> query = NeuralQuery(
        ...     spike_pattern=np.random.rand(50, 100),
        ...     energy_state=45.0,
        ...     temperature=25.0,
        ...     context="Process sensory input"
        ... )
        >>> response = interface.query_cognitive_layer(query)
        >>> if response:
        ...     snn.weights *= (1 + response.modulation_signal * 0.1)
    """

    def __init__(self,
                 energy_harvester: Optional[Any] = None,
                 latency_budget_ms: float = 500,
                 query_energy_cost: float = 0.05,
                 cache_size: int = 100,
                 min_energy_threshold: float = 0.15,
                 mock_mode: bool = True):
        """
        Initialize the Claude Neural Interface.

        Args:
            energy_harvester: EnergyHarvester instance for energy tracking
            latency_budget_ms: Maximum time (ms) for Claude queries
            query_energy_cost: Energy cost per query (mWh)
            cache_size: Maximum number of cached responses
            min_energy_threshold: Minimum energy ratio to allow queries
            mock_mode: If True, simulate Claude responses (for testing)
        """
        self.harvester = energy_harvester
        self.latency_budget = latency_budget_ms
        self.query_cost = query_energy_cost
        self.cache_size = cache_size
        self.min_energy_threshold = min_energy_threshold
        self.mock_mode = mock_mode

        # Pattern encoding
        self.codebook = SpikePatternCodebook()

        # Caching
        self.response_cache: Dict[str, CognitiveResponse] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.cache_ttl = 60.0  # Cache time-to-live in seconds

        # Statistics
        self.total_queries = 0
        self.cache_hits = 0
        self.energy_rejections = 0
        self.query_history: List[Dict] = []

    def encode_spike_pattern(self, spikes: np.ndarray) -> EncodedPattern:
        """
        Encode raw spike pattern into semantic representation.

        Extracts statistical and temporal features that capture
        the essential characteristics of neural activity.

        Args:
            spikes: Spike data [neurons x time] or [time]

        Returns:
            EncodedPattern with semantic features
        """
        spikes = np.atleast_2d(spikes)

        # Basic statistics
        firing_rate = np.mean(spikes)
        variance = np.var(spikes)
        active_ratio = np.mean(spikes > 0)

        # Synchrony (cross-correlation between neurons)
        if spikes.shape[0] > 1:
            correlations = []
            for i in range(min(spikes.shape[0], 10)):  # Sample up to 10 pairs
                for j in range(i + 1, min(spikes.shape[0], 10)):
                    if np.std(spikes[i]) > 0 and np.std(spikes[j]) > 0:
                        corr = np.corrcoef(spikes[i], spikes[j])[0, 1]
                        if not np.isnan(corr):
                            correlations.append(corr)
            synchrony = np.mean(correlations) if correlations else 0.0
        else:
            synchrony = 0.0

        # Temporal trend
        mean_activity = spikes.mean(axis=0) if spikes.ndim > 1 else spikes
        if len(mean_activity) > 2:
            trend = np.polyfit(range(len(mean_activity)), mean_activity, 1)[0]
        else:
            trend = 0.0

        # Pattern classification
        pattern_type = self.codebook.classify(spikes)

        # Entropy (information content)
        flat = spikes.flatten()
        if len(flat) > 0 and np.sum(flat) > 0:
            probs = np.histogram(flat, bins=10, density=True)[0]
            probs = probs[probs > 0]
            entropy = -np.sum(probs * np.log2(probs + 1e-10))
        else:
            entropy = 0.0

        # Burst index (ratio of high-activity periods)
        threshold = np.mean(flat) + np.std(flat)
        burst_index = np.mean(flat > threshold)

        return EncodedPattern(
            firing_rate=float(firing_rate),
            variance=float(variance),
            synchrony=float(synchrony),
            pattern_type=pattern_type,
            trend=float(trend),
            active_ratio=float(active_ratio),
            entropy=float(entropy),
            burst_index=float(burst_index)
        )

    def _hash_query(self, query: NeuralQuery) -> str:
        """Generate cache key for query"""
        # Use pattern statistics + context for hashing (not raw data)
        encoded = self.encode_spike_pattern(query.spike_pattern)
        key_data = f"{encoded.pattern_type.value}:{encoded.firing_rate:.2f}:{query.context}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]

    def _check_cache(self, cache_key: str) -> Optional[CognitiveResponse]:
        """Check if valid cached response exists"""
        if cache_key in self.response_cache:
            timestamp = self.cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < self.cache_ttl:
                self.cache_hits += 1
                return self.response_cache[cache_key]
            else:
                # Expired - remove from cache
                del self.response_cache[cache_key]
                del self.cache_timestamps[cache_key]
        return None

    def _update_cache(self, cache_key: str, response: CognitiveResponse):
        """Add response to cache, evicting old entries if needed"""
        # Evict oldest entries if cache is full
        if len(self.response_cache) >= self.cache_size:
            oldest_key = min(self.cache_timestamps, key=self.cache_timestamps.get)
            del self.response_cache[oldest_key]
            del self.cache_timestamps[oldest_key]

        self.response_cache[cache_key] = response
        self.cache_timestamps[cache_key] = time.time()

    def _check_energy(self) -> bool:
        """Check if sufficient energy for query"""
        if self.harvester is None:
            return True

        current_energy = getattr(self.harvester, 'energy_storage', 50.0)
        max_energy = getattr(self.harvester, 'max_storage', 100.0)

        return (current_energy / max_energy) > self.min_energy_threshold

    def _deduct_energy(self):
        """Deduct query energy cost"""
        if self.harvester is not None:
            self.harvester.energy_storage = max(
                0,
                self.harvester.energy_storage - self.query_cost
            )

    def query_cognitive_layer(self, query: NeuralQuery) -> Optional[CognitiveResponse]:
        """
        Query Claude for cognitive processing.

        Handles:
        - Energy gating
        - Cache lookup
        - Query construction and execution
        - Response parsing

        Args:
            query: NeuralQuery containing spike data and context

        Returns:
            CognitiveResponse or None if query was rejected/failed
        """
        self.total_queries += 1
        start_time = time.time()

        # Energy gate
        if not self._check_energy():
            self.energy_rejections += 1
            return self._fallback_response(query)

        # Cache check
        cache_key = self._hash_query(query)
        cached = self._check_cache(cache_key)
        if cached is not None and cached.confidence > 0.7:
            return cached

        # Deduct energy cost
        self._deduct_energy()

        # Build prompt
        prompt = self._build_prompt(query)

        # Execute query
        if self.mock_mode:
            raw_response = self._mock_claude_response(query)
        else:
            raw_response = self._call_claude(prompt, query.urgency)

        # Parse response
        response = self._parse_response(raw_response, query)
        response.processing_time_ms = (time.time() - start_time) * 1000

        # Update cache
        self._update_cache(cache_key, response)

        # Log query
        self.query_history.append({
            'timestamp': time.time(),
            'context': query.context,
            'pattern_type': self.encode_spike_pattern(query.spike_pattern).pattern_type.value,
            'response_confidence': response.confidence,
            'processing_time_ms': response.processing_time_ms
        })

        return response

    def _build_prompt(self, query: NeuralQuery) -> str:
        """Construct prompt for Claude"""
        encoded = self.encode_spike_pattern(query.spike_pattern)

        prompt = f"""NEURAL SYSTEM COGNITIVE QUERY

=== CURRENT STATE ===
Pattern: {encoded.summary()}
Energy: {query.energy_state:.2f} mWh
Temperature: {query.temperature:.1f}°C
Urgency: {query.urgency:.2f}

=== DETAILED METRICS ===
- Firing rate: {encoded.firing_rate:.4f}
- Variance: {encoded.variance:.4f}
- Synchrony: {encoded.synchrony:.4f}
- Active ratio: {encoded.active_ratio:.4f}
- Entropy: {encoded.entropy:.4f}
- Burst index: {encoded.burst_index:.4f}
- Trend: {encoded.trend:.4f}

=== CONTEXT ===
{query.context}

=== RECENT HISTORY ===
{json.dumps(query.history_window[-5:], indent=2, default=str) if query.history_window else 'None'}

=== RESPONSE FORMAT ===
Respond with valid JSON only:
{{
    "modulation": <float -1 to 1, global gain adjustment>,
    "attention": <list of floats 0-1, length {len(query.spike_pattern)}>,
    "action": <string or null, high-level directive>,
    "routing": {{}},
    "confidence": <float 0-1>,
    "reasoning": <brief explanation string>
}}"""
        return prompt

    def _call_claude(self, prompt: str, urgency: float) -> str:
        """Call Claude API using Anthropic SDK"""
        try:
            import anthropic

            client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

            # Use haiku for fast responses, sonnet for complex queries
            model = "claude-3-5-haiku-20241022" if urgency > 0.7 else "claude-3-5-sonnet-20241022"

            message = client.messages.create(
                model=model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt + "\n\nRespond with valid JSON only, no markdown formatting."
                    }
                ]
            )

            # Extract text from response
            response_text = message.content[0].text

            # Clean up any markdown formatting
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            return response_text

        except ImportError:
            return '{"error": "anthropic_not_installed"}'
        except anthropic.AuthenticationError:
            return '{"error": "invalid_api_key"}'
        except anthropic.RateLimitError:
            return '{"error": "rate_limited"}'
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'

    def _mock_claude_response(self, query: NeuralQuery) -> str:
        """Generate mock response for testing"""
        encoded = self.encode_spike_pattern(query.spike_pattern)

        # Generate contextually appropriate mock response
        if encoded.pattern_type == PatternType.BURST:
            modulation = 0.3  # Increase sensitivity
            action = "High activity detected - increase attention"
        elif encoded.pattern_type == PatternType.SILENT:
            modulation = -0.2  # Decrease threshold
            action = "Low activity - lower thresholds to increase sensitivity"
        elif encoded.pattern_type == PatternType.SYNCHRONOUS:
            modulation = 0.5  # Strong response to synchrony
            action = "Synchronous activity - potential pattern detected"
        else:
            modulation = 0.0
            action = None

        # Generate attention weights based on activity
        if len(query.spike_pattern.shape) > 1:
            activity = query.spike_pattern.mean(axis=1)
        else:
            activity = query.spike_pattern

        if np.std(activity) > 0:
            attention = (activity - activity.min()) / (activity.max() - activity.min() + 1e-10)
        else:
            attention = np.ones_like(activity) * 0.5

        response = {
            "modulation": modulation,
            "attention": attention.tolist(),
            "action": action,
            "routing": {},
            "confidence": 0.8,
            "reasoning": f"Pattern type: {encoded.pattern_type.value}, rate: {encoded.firing_rate:.3f}"
        }

        return json.dumps(response)

    def _parse_response(self, raw: str, query: NeuralQuery) -> CognitiveResponse:
        """Parse Claude's response into CognitiveResponse"""
        try:
            data = json.loads(raw)

            if 'error' in data:
                return self._fallback_response(query)

            # Extract and validate fields
            modulation = np.clip(float(data.get('modulation', 0)), -1, 1)

            attention_raw = data.get('attention', [])
            if isinstance(attention_raw, list) and len(attention_raw) > 0:
                attention = np.array(attention_raw, dtype=np.float32)
            else:
                attention = np.ones(len(query.spike_pattern)) / len(query.spike_pattern)

            return CognitiveResponse(
                modulation_signal=modulation,
                attention_weights=attention,
                synaptic_adjustments={},
                action_directive=data.get('action'),
                routing_optimization=data.get('routing', {}),
                confidence=float(data.get('confidence', 0.5)),
                reasoning=data.get('reasoning', '')
            )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            return self._fallback_response(query)

    def _fallback_response(self, query: NeuralQuery) -> CognitiveResponse:
        """Generate fallback response when Claude is unavailable"""
        n_neurons = len(query.spike_pattern) if query.spike_pattern.ndim == 1 else query.spike_pattern.shape[0]

        return CognitiveResponse(
            modulation_signal=0.0,
            attention_weights=np.ones(n_neurons) / n_neurons,
            synaptic_adjustments={},
            action_directive=None,
            routing_optimization={},
            confidence=0.2,
            reasoning="Fallback response - Claude unavailable"
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get interface statistics"""
        return {
            'total_queries': self.total_queries,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': self.cache_hits / max(1, self.total_queries),
            'energy_rejections': self.energy_rejections,
            'cache_size': len(self.response_cache),
            'recent_queries': self.query_history[-10:]
        }

    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        self.cache_timestamps.clear()


# Convenience function for quick encoding
def encode_spikes(spikes: np.ndarray) -> EncodedPattern:
    """Quick spike pattern encoding without full interface"""
    interface = ClaudeNeuralInterface(mock_mode=True)
    return interface.encode_spike_pattern(spikes)

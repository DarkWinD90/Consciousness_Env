"""
Neural Router - Claude-assisted packet routing for inter-node communication.

This module implements intelligent routing for neural signals between nodes,
using Claude's pattern recognition for optimization when beneficial.

Features:
- Adaptive routing based on network topology and state
- Congestion prediction and avoidance
- Priority-based packet arbitration
- Energy-aware path selection
- Hybrid fast/slow path processing
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple, Set, Any
from enum import Enum
import numpy as np
import heapq
import time
from collections import defaultdict


class SignalType(Enum):
    """Types of neural signals"""
    SPIKE = "spike"              # Action potential
    MODULATION = "modulation"    # Neuromodulatory signal
    SYNC = "sync"                # Synchronization signal
    QUERY = "query"              # Cognitive query
    RESPONSE = "response"        # Cognitive response
    FEEDBACK = "feedback"        # Feedback signal
    INHIBITION = "inhibition"    # Inhibitory signal


@dataclass
class NeuralPacket:
    """
    Packet for inter-node neural communication.

    Encapsulates signal data with routing metadata.
    """
    source: int                    # Source node ID
    target: int                    # Target node ID
    payload: np.ndarray            # Signal data
    signal_type: SignalType        # Type of signal
    priority: float = 0.5          # Priority [0, 1]
    timestamp: float = field(default_factory=time.time)
    ttl: int = 10                  # Time-to-live (max hops)
    sequence_num: int = 0          # Sequence number for ordering
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        """For priority queue ordering (higher priority first)"""
        return self.priority > other.priority


@dataclass
class NodeState:
    """State of a single node in the network"""
    node_id: int
    energy: float = 1.0            # Energy level [0, 1]
    load: float = 0.0              # Current processing load [0, 1]
    temperature: float = 25.0      # Temperature (C)
    active: bool = True            # Whether node is active
    last_spike_time: float = 0.0   # Time of last spike
    neighbors: Set[int] = field(default_factory=set)

    def congestion_score(self) -> float:
        """Calculate congestion score (higher = more congested)"""
        return self.load * (2 - self.energy) * (1 if self.active else 10)


@dataclass
class RouteMetrics:
    """Metrics for a routing path"""
    path: List[int]
    total_cost: float
    hop_count: int
    estimated_latency_ms: float
    energy_cost: float
    congestion_score: float


class NetworkTopology:
    """
    Neural network topology manager.

    Maintains the graph structure and provides pathfinding utilities.
    """

    def __init__(self):
        self.nodes: Dict[int, NodeState] = {}
        self.edges: Dict[Tuple[int, int], float] = {}  # (src, dst) -> weight
        self.adjacency: Dict[int, Set[int]] = defaultdict(set)

    def add_node(self, node_id: int, **kwargs) -> NodeState:
        """Add a node to the topology"""
        state = NodeState(node_id=node_id, **kwargs)
        self.nodes[node_id] = state
        return state

    def add_edge(self, src: int, dst: int, weight: float = 1.0, bidirectional: bool = True):
        """Add an edge between nodes"""
        self.edges[(src, dst)] = weight
        self.adjacency[src].add(dst)
        self.nodes[src].neighbors.add(dst)

        if bidirectional:
            self.edges[(dst, src)] = weight
            self.adjacency[dst].add(src)
            self.nodes[dst].neighbors.add(src)

    def get_neighbors(self, node_id: int) -> Set[int]:
        """Get neighboring nodes"""
        return self.adjacency.get(node_id, set())

    def get_edge_weight(self, src: int, dst: int) -> float:
        """Get edge weight (infinity if no edge)"""
        return self.edges.get((src, dst), float('inf'))

    def update_node_state(self, node_id: int, **kwargs):
        """Update node state"""
        if node_id in self.nodes:
            for key, value in kwargs.items():
                if hasattr(self.nodes[node_id], key):
                    setattr(self.nodes[node_id], key, value)

    def get_network_stats(self) -> Dict[str, float]:
        """Get network-wide statistics"""
        if not self.nodes:
            return {}

        loads = [n.load for n in self.nodes.values()]
        energies = [n.energy for n in self.nodes.values()]

        return {
            'avg_load': np.mean(loads),
            'max_load': np.max(loads),
            'avg_energy': np.mean(energies),
            'min_energy': np.min(energies),
            'active_nodes': sum(1 for n in self.nodes.values() if n.active),
            'total_nodes': len(self.nodes)
        }


class ClaudeOptimizedRouter:
    """
    Neural router with Claude-assisted path optimization.

    Implements a hybrid routing strategy:
    - Fast path: Dijkstra's algorithm for low-priority packets
    - Slow path: Claude-assisted optimization for high-priority packets

    The router maintains:
    - Routing table cache for fast lookups
    - Congestion tracking for load balancing
    - Energy-aware path selection
    """

    def __init__(self,
                 topology: Optional[NetworkTopology] = None,
                 claude_interface: Optional[Any] = None,
                 priority_threshold: float = 0.7,
                 cache_ttl: float = 5.0):
        """
        Initialize the router.

        Args:
            topology: Network topology (created if None)
            claude_interface: ClaudeNeuralInterface for cognitive routing
            priority_threshold: Priority above which Claude is consulted
            cache_ttl: Route cache time-to-live in seconds
        """
        self.topology = topology or NetworkTopology()
        self.claude = claude_interface
        self.priority_threshold = priority_threshold
        self.cache_ttl = cache_ttl

        # Routing cache: (src, dst, signal_type) -> (route, timestamp)
        self.routing_cache: Dict[Tuple[int, int, str], Tuple[List[int], float]] = {}

        # Statistics
        self.packets_routed = 0
        self.cache_hits = 0
        self.claude_consultations = 0
        self.dropped_packets = 0

        # Packet queue (priority queue)
        self.packet_queue: List[NeuralPacket] = []

        # Congestion history for prediction
        self.congestion_history: Dict[int, List[float]] = defaultdict(list)
        self.history_window = 100

    def route_packet(self, packet: NeuralPacket) -> Optional[RouteMetrics]:
        """
        Determine optimal route for a packet.

        Args:
            packet: NeuralPacket to route

        Returns:
            RouteMetrics with path and cost information, or None if no route
        """
        self.packets_routed += 1

        # Validate source and target
        if packet.source not in self.topology.nodes or packet.target not in self.topology.nodes:
            self.dropped_packets += 1
            return None

        # Same source and target
        if packet.source == packet.target:
            return RouteMetrics(
                path=[packet.source],
                total_cost=0,
                hop_count=0,
                estimated_latency_ms=0,
                energy_cost=0,
                congestion_score=0
            )

        # Check cache
        cache_key = (packet.source, packet.target, packet.signal_type.value)
        cached_route = self._check_cache(cache_key)
        if cached_route is not None and packet.priority < self.priority_threshold:
            self.cache_hits += 1
            return self._compute_metrics(cached_route, packet)

        # Choose routing strategy based on priority
        if packet.priority >= self.priority_threshold and self.claude is not None:
            route = self._claude_assisted_routing(packet)
            self.claude_consultations += 1
        else:
            route = self._dijkstra_route(packet.source, packet.target)

        # Update cache
        if route:
            self._update_cache(cache_key, route)
            return self._compute_metrics(route, packet)

        self.dropped_packets += 1
        return None

    def _check_cache(self, key: Tuple[int, int, str]) -> Optional[List[int]]:
        """Check if valid cached route exists"""
        if key in self.routing_cache:
            route, timestamp = self.routing_cache[key]
            if time.time() - timestamp < self.cache_ttl:
                # Validate route still exists
                if self._validate_route(route):
                    return route
            # Expired or invalid
            del self.routing_cache[key]
        return None

    def _update_cache(self, key: Tuple[int, int, str], route: List[int]):
        """Update routing cache"""
        self.routing_cache[key] = (route, time.time())

    def _validate_route(self, route: List[int]) -> bool:
        """Check if route is still valid"""
        for i in range(len(route) - 1):
            if route[i + 1] not in self.topology.get_neighbors(route[i]):
                return False
            if not self.topology.nodes.get(route[i], NodeState(0)).active:
                return False
        return True

    def _dijkstra_route(self, source: int, target: int,
                        weight_overrides: Optional[Dict[int, float]] = None) -> Optional[List[int]]:
        """
        Find shortest path using Dijkstra's algorithm.

        Args:
            source: Source node ID
            target: Target node ID
            weight_overrides: Optional node weight overrides for biased routing

        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        # Priority queue: (cost, node, path)
        pq = [(0, source, [source])]
        visited = set()

        while pq:
            cost, node, path = heapq.heappop(pq)

            if node == target:
                return path

            if node in visited:
                continue
            visited.add(node)

            for neighbor in self.topology.get_neighbors(node):
                if neighbor not in visited:
                    # Base edge weight
                    edge_cost = self.topology.get_edge_weight(node, neighbor)

                    # Add congestion cost
                    neighbor_state = self.topology.nodes.get(neighbor, NodeState(neighbor))
                    congestion_cost = neighbor_state.congestion_score()

                    # Apply weight overrides (from Claude hints)
                    if weight_overrides and neighbor in weight_overrides:
                        edge_cost *= weight_overrides[neighbor]

                    new_cost = cost + edge_cost + congestion_cost * 0.5
                    heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

        return None  # No path found

    def _claude_assisted_routing(self, packet: NeuralPacket) -> Optional[List[int]]:
        """
        Use Claude for intelligent routing decisions.

        Queries Claude with network state for routing optimization hints,
        then applies hints to weighted Dijkstra.
        """
        if self.claude is None:
            return self._dijkstra_route(packet.source, packet.target)

        # Import here to avoid circular dependency
        from .claude_interface import NeuralQuery

        # Build network state summary
        network_stats = self.topology.get_network_stats()
        congestion_info = {
            nid: state.congestion_score()
            for nid, state in self.topology.nodes.items()
        }

        # Query Claude
        query = NeuralQuery(
            spike_pattern=packet.payload,
            energy_state=network_stats.get('avg_energy', 1.0) * 100,
            temperature=25.0,
            context=f"ROUTING: {packet.signal_type.value} from node {packet.source} to {packet.target}. "
                    f"Network load: {network_stats.get('avg_load', 0):.2f}. "
                    f"High congestion nodes: {[n for n, c in congestion_info.items() if c > 0.5]}",
            urgency=packet.priority,
            history_window=[]
        )

        response = self.claude.query_cognitive_layer(query)

        # Apply routing hints
        weight_overrides = None
        if response and response.routing_optimization:
            weight_overrides = {
                int(k): float(v)
                for k, v in response.routing_optimization.items()
            }

        return self._dijkstra_route(packet.source, packet.target, weight_overrides)

    def _compute_metrics(self, route: List[int], packet: NeuralPacket) -> RouteMetrics:
        """Compute routing metrics for a path"""
        total_cost = 0.0
        energy_cost = 0.0
        congestion_score = 0.0

        for i in range(len(route) - 1):
            edge_cost = self.topology.get_edge_weight(route[i], route[i + 1])
            total_cost += edge_cost

            node_state = self.topology.nodes.get(route[i], NodeState(route[i]))
            energy_cost += 0.01 * (1 - node_state.energy)
            congestion_score += node_state.congestion_score()

        hop_count = len(route) - 1
        estimated_latency = hop_count * 0.1 + congestion_score * 0.05  # ms

        return RouteMetrics(
            path=route,
            total_cost=total_cost,
            hop_count=hop_count,
            estimated_latency_ms=estimated_latency,
            energy_cost=energy_cost,
            congestion_score=congestion_score / max(1, hop_count)
        )

    def enqueue_packet(self, packet: NeuralPacket):
        """Add packet to processing queue"""
        heapq.heappush(self.packet_queue, packet)

    def process_queue(self, max_packets: int = 10) -> List[Tuple[NeuralPacket, RouteMetrics]]:
        """
        Process packets from queue.

        Args:
            max_packets: Maximum number of packets to process

        Returns:
            List of (packet, route_metrics) tuples
        """
        results = []

        for _ in range(min(max_packets, len(self.packet_queue))):
            packet = heapq.heappop(self.packet_queue)

            # Check TTL
            if packet.ttl <= 0:
                self.dropped_packets += 1
                continue

            metrics = self.route_packet(packet)
            if metrics:
                results.append((packet, metrics))

        return results

    def update_congestion(self, node_id: int, load: float):
        """
        Update congestion tracking for a node.

        Maintains history for congestion prediction.
        """
        self.topology.update_node_state(node_id, load=load)

        # Update history
        self.congestion_history[node_id].append(load)
        if len(self.congestion_history[node_id]) > self.history_window:
            self.congestion_history[node_id].pop(0)

    def predict_congestion(self, node_id: int, steps_ahead: int = 5) -> float:
        """
        Predict future congestion using simple linear extrapolation.

        Args:
            node_id: Node to predict for
            steps_ahead: How many steps to predict

        Returns:
            Predicted congestion level
        """
        history = self.congestion_history.get(node_id, [])

        if len(history) < 3:
            return self.topology.nodes.get(node_id, NodeState(node_id)).load

        # Simple linear regression
        x = np.arange(len(history))
        coeffs = np.polyfit(x, history, 1)
        predicted = coeffs[0] * (len(history) + steps_ahead) + coeffs[1]

        return np.clip(predicted, 0, 1)

    def get_statistics(self) -> Dict[str, Any]:
        """Get router statistics"""
        return {
            'packets_routed': self.packets_routed,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': self.cache_hits / max(1, self.packets_routed),
            'claude_consultations': self.claude_consultations,
            'dropped_packets': self.dropped_packets,
            'queue_size': len(self.packet_queue),
            'cache_size': len(self.routing_cache),
            'network_stats': self.topology.get_network_stats()
        }

    def clear_cache(self):
        """Clear routing cache"""
        self.routing_cache.clear()


def create_mesh_topology(rows: int, cols: int) -> NetworkTopology:
    """
    Create a mesh network topology.

    Args:
        rows: Number of rows
        cols: Number of columns

    Returns:
        NetworkTopology with mesh connectivity
    """
    topology = NetworkTopology()

    # Create nodes
    for r in range(rows):
        for c in range(cols):
            node_id = r * cols + c
            topology.add_node(node_id)

    # Create edges (4-connectivity)
    for r in range(rows):
        for c in range(cols):
            node_id = r * cols + c

            # Right neighbor
            if c < cols - 1:
                topology.add_edge(node_id, node_id + 1)

            # Down neighbor
            if r < rows - 1:
                topology.add_edge(node_id, node_id + cols)

    return topology


def create_random_topology(num_nodes: int, edge_probability: float = 0.3) -> NetworkTopology:
    """
    Create a random network topology (Erdos-Renyi model).

    Args:
        num_nodes: Number of nodes
        edge_probability: Probability of edge between any two nodes

    Returns:
        NetworkTopology with random connectivity
    """
    topology = NetworkTopology()

    # Create nodes
    for i in range(num_nodes):
        topology.add_node(i)

    # Create random edges
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if np.random.random() < edge_probability:
                weight = np.random.uniform(0.5, 1.5)
                topology.add_edge(i, j, weight)

    return topology

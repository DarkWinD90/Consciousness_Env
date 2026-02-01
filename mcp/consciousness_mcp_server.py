#!/usr/bin/env python3
"""
Consciousness System MCP Server

This MCP server exposes the Enhanced Consciousness System as tools
that Claude Code can interact with directly using your Max plan.

Architecture:
    Claude Code (Max Plan)
         ↓ calls tools
    MCP Server (this file)
         ↓ controls
    Consciousness System (SNN + Energy + Thermochromic)

Usage:
    claude --mcp-config mcp/mcp-config.json

Tools exposed:
    - initialize_consciousness: Start a new consciousness system
    - step_simulation: Advance simulation by N steps
    - get_neural_state: Read current SNN activity
    - get_system_status: Full system status
    - apply_cognitive_response: Apply modulation from Claude's reasoning
    - set_goal: Set a goal for the system
    - get_attention_needs: What stimuli need attention?
"""

import sys
import json
import asyncio
import numpy as np
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_snn import BaseSNN, SNNConfig
from core.thermochromic import ThermochromicMixin, ColorState
from core.energy import EnergyHarvester, BalancedEnergyConfig
from core.history import HistoryTracker


@dataclass
class ConsciousnessState:
    """Current state of the consciousness system"""
    step: int = 0

    # Neural state
    num_neurons: int = 50
    spike_count: int = 0
    mean_potential: float = 0.0
    snn_output: float = 0.0
    pattern_type: str = "unknown"

    # Physical state
    energy_mwh: float = 50.0
    temperature_c: float = 25.0
    color_rgb: tuple = (0.5, 0.5, 0.5)

    # Cognitive state
    current_goal: Optional[str] = None
    attention_focus: Optional[str] = None
    last_modulation: float = 0.0


class ConsciousnessSystem(ThermochromicMixin):
    """
    The consciousness system that MCP exposes to Claude.

    This is a simplified but complete implementation that Claude
    can interact with through MCP tools.
    """

    neutral_temp = 25.0
    warm_threshold = 30.0
    temp_range = 15.0

    def __init__(self, num_neurons: int = 50):
        self.snn = BaseSNN(SNNConfig(
            num_neurons=num_neurons,
            threshold=0.5,
            leak_factor=0.1,
            refractory_period=2,
            weight_scale=0.15,  # Strong enough for activity propagation
            input_scale=0.8    # Strong enough to trigger firing
        ))

        self.harvester = EnergyHarvester(
            config=BalancedEnergyConfig(),  # Self-sustaining at medium activity
            initial_energy=50.0
        )

        self.history = HistoryTracker(fields=[
            'spikes', 'energy', 'temperature', 'output'
        ])

        self.state = ConsciousnessState(num_neurons=num_neurons)
        self.stimuli: Dict[str, float] = {}
        self._color = ColorState(0.5, 0.5, 0.5)

    def step(self, external_input: float = 0.5, modulation: float = 0.0) -> ConsciousnessState:
        """Advance simulation by one step"""
        self.state.step += 1

        # Apply modulation to input
        modulated_input = external_input * (1 + modulation * 0.3)
        modulated_input = np.clip(modulated_input, 0, 1)

        # SNN processing
        reflection_coeff = 0.2 + modulation * 0.1
        potentials, spikes = self.snn.step(modulated_input, reflection_coeff=reflection_coeff)

        self.state.spike_count = int(np.sum(spikes))
        self.state.mean_potential = float(np.mean(potentials))
        self.state.snn_output = float(self.snn.get_output())
        self.state.pattern_type = self._classify_pattern(spikes)

        # Energy harvesting (BalancedEnergyConfig: activity drives piezoelectric harvest)
        activity = self.state.spike_count  # Direct spike count for balanced config
        friction_energy = self.harvester.harvest_friction(activity)
        thermal_energy = self.harvester.harvest_thermal(self.state.temperature_c)
        self.harvester.update_storage(friction_energy, thermal_energy, spike_count=self.state.spike_count)
        self.state.energy_mwh = float(self.harvester.energy_storage)

        # Temperature dynamics
        activity_heat = self.state.spike_count * 0.02
        overflow_heat = self.harvester.overflow_heat  # Excess energy dissipated as heat
        cooling = (self.state.temperature_c - 20.0) * 0.05
        self.state.temperature_c += activity_heat + overflow_heat - cooling
        self.state.temperature_c = float(np.clip(self.state.temperature_c, 15.0, 45.0))

        # Thermochromic color
        self._color = self.compute_thermochromic_color(self.state.temperature_c)
        self.state.color_rgb = (self._color.r, self._color.g, self._color.b)

        # Store modulation
        self.state.last_modulation = modulation

        # Record history
        self.history.record(
            spikes=self.state.spike_count,
            energy=self.state.energy_mwh,
            temperature=self.state.temperature_c,
            output=self.state.snn_output
        )

        return self.state

    def _classify_pattern(self, spikes: np.ndarray) -> str:
        """Classify the spike pattern"""
        firing_rate = np.mean(spikes)

        if firing_rate > 0.7:
            return "burst"
        elif firing_rate > 0.4:
            return "tonic"
        elif firing_rate > 0.1:
            return "sparse"
        elif firing_rate > 0:
            return "minimal"
        else:
            return "silent"

    def set_stimuli(self, stimuli: Dict[str, float]):
        """Set current stimuli for attention allocation"""
        self.stimuli = stimuli

    def get_attention_needs(self) -> Dict[str, Any]:
        """Return stimuli that need attention based on current state"""
        needs = {}

        for name, salience in self.stimuli.items():
            urgency = salience

            # Boost urgency based on system state
            if "energy" in name.lower() and self.state.energy_mwh < 20:
                urgency *= 2.0
            if "temperature" in name.lower() and abs(self.state.temperature_c - 25) > 10:
                urgency *= 1.5

            needs[name] = {
                "salience": salience,
                "urgency": min(1.0, urgency),
                "recommended_attention": urgency / (sum(self.stimuli.values()) + 0.01)
            }

        return needs


class MCPConsciousnessServer:
    """
    MCP Server that exposes consciousness system tools to Claude Code.
    """

    def __init__(self):
        self.system: Optional[ConsciousnessSystem] = None
        self.name = "consciousness-system"
        self.version = "1.0.0"

    def get_tools(self):
        """Return tool definitions"""
        return [
            {
                "name": "initialize_consciousness",
                "description": "Initialize a new consciousness system with specified number of neurons. Call this first before other tools.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "num_neurons": {
                            "type": "integer",
                            "description": "Number of neurons in the SNN (default: 50)",
                            "default": 50
                        }
                    }
                }
            },
            {
                "name": "step_simulation",
                "description": "Advance the consciousness simulation by N steps. Returns the final state.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "num_steps": {
                            "type": "integer",
                            "description": "Number of steps to simulate (default: 1)",
                            "default": 1
                        },
                        "external_input": {
                            "type": "number",
                            "description": "External stimulus level 0-1 (default: 0.5)",
                            "default": 0.5
                        },
                        "modulation": {
                            "type": "number",
                            "description": "Cognitive modulation signal from -1 to 1 (default: 0)",
                            "default": 0
                        }
                    }
                }
            },
            {
                "name": "get_neural_state",
                "description": "Get detailed current state of the neural network including spike patterns, potentials, and activity classification.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_system_status",
                "description": "Get complete system status including neural, physical, and cognitive state.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "apply_cognitive_response",
                "description": "Apply a cognitive response (modulation, attention, action) to the system based on Claude's reasoning.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "modulation": {
                            "type": "number",
                            "description": "Global gain adjustment from -1 (inhibit) to 1 (excite)"
                        },
                        "attention_focus": {
                            "type": "string",
                            "description": "What to focus attention on"
                        },
                        "action": {
                            "type": "string",
                            "description": "High-level action directive"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Explanation for this cognitive response"
                        }
                    },
                    "required": ["modulation"]
                }
            },
            {
                "name": "set_goal",
                "description": "Set a goal for the consciousness system to work towards.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "The goal to achieve"
                        }
                    },
                    "required": ["goal"]
                }
            },
            {
                "name": "set_stimuli",
                "description": "Set the current environmental stimuli for attention allocation.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "stimuli": {
                            "type": "object",
                            "description": "Dictionary of stimulus_name: salience (0-1)"
                        }
                    },
                    "required": ["stimuli"]
                }
            },
            {
                "name": "get_attention_needs",
                "description": "Get analysis of what stimuli need attention based on current system state.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_history",
                "description": "Get recent history of system metrics.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "num_steps": {
                            "type": "integer",
                            "description": "Number of recent steps to return (default: 20)",
                            "default": 20
                        }
                    }
                }
            }
        ]

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool call from Claude"""

        if name == "initialize_consciousness":
            num_neurons = arguments.get("num_neurons", 50)
            self.system = ConsciousnessSystem(num_neurons=num_neurons)
            return {
                "status": "initialized",
                "num_neurons": num_neurons,
                "initial_state": asdict(self.system.state)
            }

        # All other tools require initialization
        if self.system is None:
            return {"error": "System not initialized. Call initialize_consciousness first."}

        if name == "step_simulation":
            num_steps = arguments.get("num_steps", 1)
            external_input = arguments.get("external_input", 0.5)
            modulation = arguments.get("modulation", 0)

            for _ in range(num_steps):
                state = self.system.step(external_input, modulation)

            return asdict(state)

        elif name == "get_neural_state":
            return {
                "step": self.system.state.step,
                "num_neurons": self.system.state.num_neurons,
                "spike_count": self.system.state.spike_count,
                "mean_potential": self.system.state.mean_potential,
                "snn_output": self.system.state.snn_output,
                "pattern_type": self.system.state.pattern_type,
                "membrane_potentials_sample": self.system.snn.membrane_potential[:10].tolist()
            }

        elif name == "get_system_status":
            return {
                "state": asdict(self.system.state),
                "energy_status": "critical" if self.system.state.energy_mwh < 10 else
                                "low" if self.system.state.energy_mwh < 25 else "ok",
                "temperature_status": "hot" if self.system.state.temperature_c > 35 else
                                     "cold" if self.system.state.temperature_c < 18 else "ok",
                "current_stimuli": self.system.stimuli
            }

        elif name == "apply_cognitive_response":
            modulation = arguments.get("modulation", 0)
            attention = arguments.get("attention_focus")
            action = arguments.get("action")
            reasoning = arguments.get("reasoning", "")

            self.system.state.last_modulation = modulation
            if attention:
                self.system.state.attention_focus = attention

            return {
                "applied": True,
                "modulation": modulation,
                "attention_focus": attention,
                "action": action,
                "reasoning": reasoning
            }

        elif name == "set_goal":
            goal = arguments.get("goal", "")
            self.system.state.current_goal = goal
            return {"goal_set": goal}

        elif name == "set_stimuli":
            stimuli = arguments.get("stimuli", {})
            self.system.set_stimuli(stimuli)
            return {"stimuli_set": list(stimuli.keys())}

        elif name == "get_attention_needs":
            needs = self.system.get_attention_needs()
            return {
                "attention_needs": needs,
                "recommended_focus": max(needs, key=lambda k: needs[k]["urgency"]) if needs else None
            }

        elif name == "get_history":
            num_steps = arguments.get("num_steps", 20)
            history = {}
            for field in ['spikes', 'energy', 'temperature', 'output']:
                data = self.system.history.get(field)
                history[field] = data[-num_steps:] if len(data) > num_steps else data
            return {"history": history, "total_steps": self.system.state.step}

        return {"error": f"Unknown tool: {name}"}

    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP request"""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": self.name, "version": self.version}
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": self.get_tools()}
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})

            result = await self.handle_tool_call(tool_name, arguments)

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            }

        elif method == "notifications/initialized":
            return None

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }

    async def run(self):
        """Run the MCP server on stdin/stdout"""
        print(f"Consciousness MCP Server v{self.version} starting...", file=sys.stderr)

        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break

                request = json.loads(line.strip())
                response = await self.handle_request(request)

                if response:
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)}
                }), flush=True)


def main():
    server = MCPConsciousnessServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()

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
         ↓ (on disconnect)
    Autonomous Fallback (keeps the loop alive)

Fallback support:
    When the cognitive layer (Claude) stops sending commands for longer
    than ``heartbeat_timeout`` seconds, the system enters autonomous
    fallback mode.  It continues stepping the SNN with a self-regulating
    input generator, snapshots state to disk periodically, and buffers
    all history.  When Claude reconnects, a ``resync`` tool returns
    everything that happened while the connection was down.

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
    - get_fallback_status: Check autonomous fallback state
    - resync: Retrieve buffered history from an autonomous fallback period
"""

import sys
import json
import asyncio
import time
import numpy as np
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict, field
from pathlib import Path
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_snn import BaseSNN, SNNConfig
from core.thermochromic import ThermochromicMixin, ColorState
from core.energy import EnergyHarvester, BalancedEnergyConfig
from core.history import HistoryTracker


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SNAPSHOT_DIR = Path(__file__).parent / ".snapshots"

@dataclass
class FallbackConfig:
    """Configuration for autonomous fallback behaviour."""
    heartbeat_timeout: float = 30.0     # seconds without a tool call before fallback
    fallback_step_interval: float = 0.5 # seconds between autonomous steps
    snapshot_interval: int = 50         # steps between disk snapshots
    max_autonomous_steps: int = 10000   # hard cap so runaway loops can't spin forever


# ---------------------------------------------------------------------------
# Consciousness state
# ---------------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Snapshot / restore (for crash recovery)
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Serialise the full system state to a JSON-safe dict."""
        return {
            "state": asdict(self.state),
            "energy_storage": float(self.harvester.energy_storage),
            "temperature": float(self.state.temperature_c),
            "membrane_potential": self.snn.membrane_potential.tolist(),
            "refractory_counters": self.snn.refractory_counters.tolist(),
            "previous_output": self.snn.previous_output,
            "weights": self.snn.weights.tolist(),
            "stimuli": self.stimuli,
        }

    def restore(self, snap: Dict[str, Any]):
        """Restore system state from a snapshot dict."""
        s = snap["state"]
        self.state.step = s["step"]
        self.state.num_neurons = s["num_neurons"]
        self.state.spike_count = s["spike_count"]
        self.state.mean_potential = s["mean_potential"]
        self.state.snn_output = s["snn_output"]
        self.state.pattern_type = s["pattern_type"]
        self.state.energy_mwh = s["energy_mwh"]
        self.state.temperature_c = s["temperature_c"]
        self.state.color_rgb = tuple(s["color_rgb"])
        self.state.current_goal = s.get("current_goal")
        self.state.attention_focus = s.get("attention_focus")
        self.state.last_modulation = s.get("last_modulation", 0.0)

        self.harvester.energy_storage = snap["energy_storage"]
        self.snn.membrane_potential = np.array(snap["membrane_potential"])
        self.snn.refractory_counters = np.array(snap["refractory_counters"], dtype=int)
        self.snn.previous_output = snap["previous_output"]
        self.snn.weights = np.array(snap["weights"])
        self.stimuli = snap.get("stimuli", {})


# ---------------------------------------------------------------------------
# Autonomous fallback runner
# ---------------------------------------------------------------------------

class AutonomousRunner:
    """
    Background loop that keeps the consciousness system alive when the
    cognitive layer (Claude / MCP connection) is unavailable.

    Uses a self-regulating input generator:
      - Circadian-like sinusoidal base signal
      - Random attention bursts (10% chance each step)
      - Energy-aware modulation: inhibits when energy is low,
        excites when energy is abundant
    """

    def __init__(self, system: ConsciousnessSystem, config: FallbackConfig):
        self.system = system
        self.config = config

        # Bookkeeping
        self.active = False
        self.steps_taken: int = 0
        self.entered_at_step: int = 0
        self.entered_at_time: float = 0.0
        self.exited_at_step: Optional[int] = None

        # Buffer history recorded during fallback so resync can report it
        self._buffer: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Input generator
    # ------------------------------------------------------------------

    def _generate_input(self, step: int) -> tuple:
        """Produce (external_input, modulation) for one autonomous step."""
        t = step / 200.0  # normalised time

        # Circadian base
        circadian = 0.5 + 0.2 * np.sin(2 * np.pi * t * 3)

        # Random attention burst
        burst = 0.3 if np.random.random() < 0.10 else 0.0
        external_input = float(np.clip(circadian + burst, 0.0, 1.0))

        # Self-regulating modulation based on energy
        energy = self.system.state.energy_mwh
        if energy < 15:
            modulation = -0.4   # conserve
        elif energy < 30:
            modulation = -0.1   # cautious
        elif energy > 80:
            modulation = 0.3    # spend surplus
        else:
            modulation = 0.0    # neutral

        return external_input, modulation

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def enter(self):
        """Activate autonomous fallback."""
        self.active = True
        self.steps_taken = 0
        self.entered_at_step = self.system.state.step
        self.entered_at_time = time.time()
        self.exited_at_step = None
        self._buffer.clear()

    def exit(self):
        """Deactivate autonomous fallback (Claude is back)."""
        self.active = False
        self.exited_at_step = self.system.state.step

    async def run_loop(self):
        """
        Async loop that steps the system while ``self.active`` is True.
        Yields control between steps so the MCP server can still process
        incoming requests that would deactivate fallback.
        """
        while self.active and self.steps_taken < self.config.max_autonomous_steps:
            ext, mod = self._generate_input(self.system.state.step)
            state = self.system.step(ext, mod)
            self.steps_taken += 1

            # Buffer a summary for resync
            self._buffer.append({
                "step": state.step,
                "input": round(ext, 4),
                "modulation": round(mod, 4),
                "spikes": state.spike_count,
                "energy": round(state.energy_mwh, 2),
                "temperature": round(state.temperature_c, 2),
                "pattern": state.pattern_type,
            })

            # Periodic snapshot
            if self.steps_taken % self.config.snapshot_interval == 0:
                self._write_snapshot()

            await asyncio.sleep(self.config.fallback_step_interval)

        # Final snapshot on exit
        if self.steps_taken > 0:
            self._write_snapshot()

    def _write_snapshot(self):
        """Persist current state to disk."""
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        snap = self.system.snapshot()
        snap["_meta"] = {
            "fallback_steps": self.steps_taken,
            "timestamp": time.time(),
        }
        path = SNAPSHOT_DIR / "latest.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(snap))
        tmp.replace(path)  # atomic on POSIX

    def get_resync_payload(self) -> Dict[str, Any]:
        """Return everything that happened during the last fallback period."""
        payload = {
            "fallback_occurred": len(self._buffer) > 0,
            "steps_autonomous": self.steps_taken,
            "entered_at_step": self.entered_at_step,
            "exited_at_step": self.exited_at_step,
            "duration_seconds": round(time.time() - self.entered_at_time, 2) if self.entered_at_time else 0,
            "current_state": asdict(self.system.state),
            "buffer_length": len(self._buffer),
        }
        if self._buffer:
            payload["first_buffered"] = self._buffer[0]
            payload["last_buffered"] = self._buffer[-1]
            # Energy delta across the autonomous period
            payload["energy_delta"] = round(
                self._buffer[-1]["energy"] - self._buffer[0]["energy"], 2
            )
            # Summary stats
            energies = [b["energy"] for b in self._buffer]
            spikes = [b["spikes"] for b in self._buffer]
            payload["summary"] = {
                "energy_min": round(min(energies), 2),
                "energy_max": round(max(energies), 2),
                "energy_mean": round(sum(energies) / len(energies), 2),
                "spikes_mean": round(sum(spikes) / len(spikes), 2),
            }
        return payload

    def drain_buffer(self) -> List[Dict[str, Any]]:
        """Return and clear the full buffer (for detailed resync)."""
        buf = list(self._buffer)
        self._buffer.clear()
        return buf


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

class MCPConsciousnessServer:
    """
    MCP Server that exposes consciousness system tools to Claude Code.
    Includes autonomous fallback when the cognitive layer disconnects.
    """

    def __init__(self, fallback_config: FallbackConfig = None):
        self.system: Optional[ConsciousnessSystem] = None
        self.name = "consciousness-system"
        self.version = "1.1.0"

        self._fb_config = fallback_config or FallbackConfig()
        self._runner: Optional[AutonomousRunner] = None
        self._fallback_task: Optional[asyncio.Task] = None
        self._last_heartbeat: float = time.time()

    # ------------------------------------------------------------------
    # Heartbeat / fallback management
    # ------------------------------------------------------------------

    def _touch_heartbeat(self):
        """Record that Claude is alive (a tool call just arrived)."""
        self._last_heartbeat = time.time()
        # If fallback is running, stop it — Claude is back
        if self._runner and self._runner.active:
            self._runner.exit()
            if self._fallback_task and not self._fallback_task.done():
                self._fallback_task.cancel()
            print("[fallback] cognitive layer reconnected — "
                  f"autonomous ran {self._runner.steps_taken} steps",
                  file=sys.stderr)

    async def _heartbeat_watchdog(self):
        """
        Background coroutine that monitors the heartbeat and engages
        autonomous fallback when Claude goes silent.
        """
        while True:
            await asyncio.sleep(5)  # check every 5 s

            if self.system is None:
                continue

            elapsed = time.time() - self._last_heartbeat
            already_running = self._runner and self._runner.active

            if elapsed > self._fb_config.heartbeat_timeout and not already_running:
                print(f"[fallback] no heartbeat for {elapsed:.0f}s — "
                      "engaging autonomous mode", file=sys.stderr)
                self._runner = AutonomousRunner(self.system, self._fb_config)
                self._runner.enter()
                self._fallback_task = asyncio.ensure_future(self._runner.run_loop())

    def _try_restore_snapshot(self) -> bool:
        """Attempt to restore from the latest disk snapshot."""
        path = SNAPSHOT_DIR / "latest.json"
        if not path.exists():
            return False
        try:
            snap = json.loads(path.read_text())
            if self.system is None:
                num_neurons = snap["state"]["num_neurons"]
                self.system = ConsciousnessSystem(num_neurons=num_neurons)
            self.system.restore(snap)
            print(f"[fallback] restored from snapshot at step "
                  f"{self.system.state.step}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[fallback] snapshot restore failed: {e}", file=sys.stderr)
            return False

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
            },
            {
                "name": "get_fallback_status",
                "description": "Check whether autonomous fallback is active, and if so how many steps it has run.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "resync",
                "description": "Retrieve buffered history from an autonomous fallback period. Returns summary stats and energy delta so the cognitive layer can catch up.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_full_buffer": {
                            "type": "boolean",
                            "description": "Include every buffered step (can be large). Default false.",
                            "default": False
                        }
                    }
                }
            }
        ]

    # ── Tool handlers ──────────────────────────────────────────────
    # Each _handle_<tool> method returns a dict.  Adding a new tool
    # requires only a new method and a TOOL_HANDLERS entry.

    def _handle_initialize_consciousness(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        num_neurons = arguments.get("num_neurons", 50)
        # Try restoring from a previous snapshot first
        if self._try_restore_snapshot():
            return {
                "status": "restored_from_snapshot",
                "num_neurons": self.system.state.num_neurons,
                "restored_step": self.system.state.step,
                "state": asdict(self.system.state)
            }
        self.system = ConsciousnessSystem(num_neurons=num_neurons)
        return {
            "status": "initialized",
            "num_neurons": num_neurons,
            "initial_state": asdict(self.system.state)
        }

    def _handle_step_simulation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        num_steps = arguments.get("num_steps", 1)
        external_input = arguments.get("external_input", 0.5)
        modulation = arguments.get("modulation", 0)

        for _ in range(num_steps):
            state = self.system.step(external_input, modulation)

        return asdict(state)

    def _handle_get_neural_state(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "step": self.system.state.step,
            "num_neurons": self.system.state.num_neurons,
            "spike_count": self.system.state.spike_count,
            "mean_potential": self.system.state.mean_potential,
            "snn_output": self.system.state.snn_output,
            "pattern_type": self.system.state.pattern_type,
            "membrane_potentials_sample": self.system.snn.membrane_potential[:10].tolist()
        }

    def _handle_get_system_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        fb_active = self._runner.active if self._runner else False
        return {
            "state": asdict(self.system.state),
            "energy_status": "critical" if self.system.state.energy_mwh < 10 else
                            "low" if self.system.state.energy_mwh < 25 else "ok",
            "temperature_status": "hot" if self.system.state.temperature_c > 35 else
                                 "cold" if self.system.state.temperature_c < 18 else "ok",
            "current_stimuli": self.system.stimuli,
            "fallback_active": fb_active,
        }

    def _handle_apply_cognitive_response(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
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

    def _handle_set_goal(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        goal = arguments.get("goal", "")
        self.system.state.current_goal = goal
        return {"goal_set": goal}

    def _handle_set_stimuli(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        stimuli = arguments.get("stimuli", {})
        self.system.set_stimuli(stimuli)
        return {"stimuli_set": list(stimuli.keys())}

    def _handle_get_attention_needs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        needs = self.system.get_attention_needs()
        return {
            "attention_needs": needs,
            "recommended_focus": max(needs, key=lambda k: needs[k]["urgency"]) if needs else None
        }

    def _handle_get_history(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        num_steps = arguments.get("num_steps", 20)
        history = {}
        for field in ['spikes', 'energy', 'temperature', 'output']:
            data = self.system.history.get(field)
            history[field] = data[-num_steps:] if len(data) > num_steps else data
        return {"history": history, "total_steps": self.system.state.step}

    def _handle_get_fallback_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if self._runner is None:
            return {"fallback_available": True, "fallback_active": False,
                    "steps_autonomous": 0}
        return {
            "fallback_available": True,
            "fallback_active": self._runner.active,
            "steps_autonomous": self._runner.steps_taken,
            "entered_at_step": self._runner.entered_at_step,
            "heartbeat_timeout": self._fb_config.heartbeat_timeout,
        }

    def _handle_resync(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if self._runner is None:
            return {"fallback_occurred": False, "message": "No fallback period recorded."}
        payload = self._runner.get_resync_payload()
        if arguments.get("include_full_buffer", False):
            payload["full_buffer"] = self._runner.drain_buffer()
        else:
            self._runner.drain_buffer()  # clear it either way
        return payload

    # Tools that do NOT require an initialized system
    _NO_INIT_REQUIRED = {"initialize_consciousness"}

    # Dispatch table: tool name → handler method name
    TOOL_HANDLERS = {
        "initialize_consciousness": "_handle_initialize_consciousness",
        "step_simulation": "_handle_step_simulation",
        "get_neural_state": "_handle_get_neural_state",
        "get_system_status": "_handle_get_system_status",
        "apply_cognitive_response": "_handle_apply_cognitive_response",
        "set_goal": "_handle_set_goal",
        "set_stimuli": "_handle_set_stimuli",
        "get_attention_needs": "_handle_get_attention_needs",
        "get_history": "_handle_get_history",
        "get_fallback_status": "_handle_get_fallback_status",
        "resync": "_handle_resync",
    }

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool call from Claude via dispatch table."""
        self._touch_heartbeat()

        handler_name = self.TOOL_HANDLERS.get(name)
        if handler_name is None:
            return {"error": f"Unknown tool: {name}"}

        if name not in self._NO_INIT_REQUIRED and self.system is None:
            return {"error": "System not initialized. Call initialize_consciousness first."}

        return getattr(self, handler_name)(arguments)

    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP request"""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            self._touch_heartbeat()
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
            self._touch_heartbeat()
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
            self._touch_heartbeat()
            return None

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }

    async def run(self):
        """Run the MCP server on stdin/stdout with heartbeat watchdog."""
        print(f"Consciousness MCP Server v{self.version} starting...",
              file=sys.stderr)
        print(f"[fallback] heartbeat timeout: "
              f"{self._fb_config.heartbeat_timeout}s", file=sys.stderr)

        # Start the heartbeat watchdog
        watchdog = asyncio.ensure_future(self._heartbeat_watchdog())

        try:
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
        finally:
            watchdog.cancel()
            # Final snapshot on shutdown
            if self.system is not None:
                runner = AutonomousRunner(self.system, self._fb_config)
                runner._write_snapshot()
                print("[fallback] shutdown snapshot saved", file=sys.stderr)


def main():
    server = MCPConsciousnessServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
MCP Server for Consciousness System - Cognitive Query Interface

This MCP server provides tools for the Enhanced Consciousness System
to communicate with Claude through the Model Context Protocol.

Run with: python consciousness_server.py
"""

import sys
import json
import asyncio
from typing import Any, Dict, List
import numpy as np


class MCPServer:
    """Simple MCP Server for consciousness cognitive queries"""

    def __init__(self):
        self.name = "consciousness-cognitive"
        self.version = "1.0.0"
        self.tools = {
            "cognitive_query": {
                "description": "Process a cognitive query from the neural system",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pattern_type": {"type": "string", "description": "Type of neural pattern (burst, tonic, sparse, etc.)"},
                        "firing_rate": {"type": "number", "description": "Neural firing rate"},
                        "energy_state": {"type": "number", "description": "Current energy in mWh"},
                        "temperature": {"type": "number", "description": "System temperature in C"},
                        "context": {"type": "string", "description": "Query context"},
                        "urgency": {"type": "number", "description": "Query urgency 0-1"}
                    },
                    "required": ["context"]
                }
            },
            "form_intention": {
                "description": "Form an intention/plan for a goal",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "goal": {"type": "string", "description": "Goal to achieve"},
                        "capabilities": {"type": "array", "items": {"type": "string"}, "description": "Current capabilities"},
                        "limitations": {"type": "array", "items": {"type": "string"}, "description": "Current limitations"}
                    },
                    "required": ["goal"]
                }
            },
            "allocate_attention": {
                "description": "Allocate attention across competing stimuli",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "stimuli": {"type": "object", "description": "Dictionary of stimulus_name: salience"},
                        "current_goals": {"type": "array", "items": {"type": "string"}, "description": "Current active goals"}
                    },
                    "required": ["stimuli"]
                }
            }
        }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC request"""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            return self._initialize_response(request_id, params)
        elif method == "tools/list":
            return self._tools_list_response(request_id)
        elif method == "tools/call":
            return await self._tool_call_response(request_id, params)
        elif method == "notifications/initialized":
            return None  # No response needed
        else:
            return self._error_response(request_id, -32601, f"Method not found: {method}")

    def _initialize_response(self, request_id: Any, params: Dict) -> Dict[str, Any]:
        """Respond to initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                }
            }
        }

    def _tools_list_response(self, request_id: Any) -> Dict[str, Any]:
        """Return list of available tools"""
        tools = [
            {
                "name": name,
                "description": info["description"],
                "inputSchema": info["inputSchema"]
            }
            for name, info in self.tools.items()
        ]

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }

    async def _tool_call_response(self, request_id: Any, params: Dict) -> Dict[str, Any]:
        """Execute a tool and return result"""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "cognitive_query":
            result = self._handle_cognitive_query(arguments)
        elif tool_name == "form_intention":
            result = self._handle_form_intention(arguments)
        elif tool_name == "allocate_attention":
            result = self._handle_allocate_attention(arguments)
        else:
            return self._error_response(request_id, -32602, f"Unknown tool: {tool_name}")

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result)
                    }
                ]
            }
        }

    def _handle_cognitive_query(self, args: Dict) -> Dict[str, Any]:
        """Process cognitive query - returns modulation signals"""
        pattern_type = args.get("pattern_type", "unknown")
        firing_rate = args.get("firing_rate", 0.5)
        energy = args.get("energy_state", 50)
        context = args.get("context", "")
        urgency = args.get("urgency", 0.5)

        # Generate response based on pattern
        if pattern_type == "burst":
            modulation = 0.3
            action = "High activity - increase attention"
        elif pattern_type == "silent":
            modulation = -0.2
            action = "Low activity - lower thresholds"
        elif pattern_type == "synchronous":
            modulation = 0.5
            action = "Synchronous pattern detected - potential coherent signal"
        else:
            modulation = 0.0
            action = None

        # Energy-aware modulation
        if energy < 20:
            modulation -= 0.2
            action = "Low energy - conserve resources"

        return {
            "modulation": modulation,
            "attention": [0.5] * 10,  # Default attention weights
            "action": action,
            "routing": {},
            "confidence": 0.85,
            "reasoning": f"Pattern: {pattern_type}, Rate: {firing_rate:.3f}, Energy: {energy:.1f}mWh"
        }

    def _handle_form_intention(self, args: Dict) -> Dict[str, Any]:
        """Form an intention/plan for a goal"""
        goal = args.get("goal", "")
        capabilities = args.get("capabilities", [])

        # Generate plan based on goal
        plan = []
        if "energy" in goal.lower():
            plan = [
                "Monitor current energy levels",
                "Identify high-consumption processes",
                "Reduce cognitive query frequency when low",
                "Prioritize energy harvesting behaviors"
            ]
        elif "temperature" in goal.lower():
            plan = [
                "Monitor temperature sensors",
                "Adjust activity based on thermal state",
                "Activate cooling behaviors if overheating"
            ]
        else:
            plan = [
                f"Analyze requirements for: {goal}",
                "Identify relevant capabilities",
                "Execute plan steps",
                "Monitor progress"
            ]

        return {
            "goal": goal,
            "plan": plan,
            "confidence": 0.8,
            "prerequisites": []
        }

    def _handle_allocate_attention(self, args: Dict) -> Dict[str, Any]:
        """Allocate attention across stimuli"""
        stimuli = args.get("stimuli", {})
        goals = args.get("current_goals", [])

        if not stimuli:
            return {"weights": {}, "focus": None}

        # Weight stimuli based on salience and goal relevance
        weights = {}
        total = 0

        for name, salience in stimuli.items():
            weight = salience
            # Boost if related to goals
            for goal in goals:
                if name.lower() in goal.lower() or goal.lower() in name.lower():
                    weight *= 1.5
            weights[name] = weight
            total += weight

        # Normalize
        if total > 0:
            weights = {k: v/total for k, v in weights.items()}

        focus = max(weights, key=weights.get) if weights else None

        return {
            "weights": weights,
            "focus": focus,
            "reasoning": f"Allocated attention based on {len(stimuli)} stimuli and {len(goals)} goals"
        }

    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    async def run(self):
        """Run the MCP server on stdin/stdout"""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
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
    """Entry point"""
    server = MCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()

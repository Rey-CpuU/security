"""
Office & Agent State Manager for 8-Bit Cyber Operations Office GUI.
Coordinates the 3 MVP agent workstations, FIFO task card queue, concurrency limits (max 2),
and real-time event broadcasting to WebSocket subscribers.
"""

import asyncio
import json
import os
import time
import uuid
from typing import Dict, Any, List, Optional, Set, Callable, Awaitable

from gui.server.triage_bridge import run_triage
from gui.server.harnesses.claude_code import ClaudeCodeAdapter

SETTINGS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "settings.json"))


class OfficeStateManager:
    """
    Central state store and dispatcher for office agents and task cards.
    """

    def __init__(self):
        self.lock = asyncio.Lock()
        self.settings: Dict[str, Any] = self._load_settings()
        self.max_parallel: int = int(self.settings.get("max_parallel_agents", 2))
        self.dry_run_default: bool = bool(self.settings.get("dry_run_default", True))

        # 3 MVP Agent Workstations
        self.agents: Dict[str, Dict[str, Any]] = {
            "pentest": {
                "id": "pentest",
                "name": "Rex",
                "role": "Penetration Tester",
                "title": "Offensive Lead",
                "status": "idle",  # idle | walking | working | alert | completed
                "color": "#ff3366",
                "desk": {"x": 120, "y": 140},
                "pos": {"x": 120, "y": 140},
                "target_pos": {"x": 120, "y": 140},
                "current_card_id": None,
                "current_thought": "Ready for penetration testing & exploit audit.",
                "model": self.settings.get("agent_models", {}).get("pentest", "claude-3-7-sonnet-20250219"),
                "harness": "claude_code"
            },
            "appsec": {
                "id": "appsec",
                "name": "Ada",
                "role": "AppSec Engineer",
                "title": "Code Audit Lead",
                "status": "idle",
                "color": "#00f0ff",
                "desk": {"x": 280, "y": 140},
                "pos": {"x": 280, "y": 140},
                "target_pos": {"x": 280, "y": 140},
                "current_card_id": None,
                "current_thought": "Ready for SAST, invariants, and code review.",
                "model": self.settings.get("agent_models", {}).get("appsec", "claude-3-5-sonnet-20241022"),
                "harness": "claude_code"
            },
            "devsecops": {
                "id": "devsecops",
                "name": "Gears",
                "role": "DevSecOps & Cloud Security",
                "title": "Pipeline & Container Lead",
                "status": "idle",
                "color": "#00ff66",
                "desk": {"x": 440, "y": 140},
                "pos": {"x": 440, "y": 140},
                "target_pos": {"x": 440, "y": 140},
                "current_card_id": None,
                "current_thought": "Ready for CI/CD, Docker & K8s pipeline hardening.",
                "model": self.settings.get("agent_models", {}).get("devsecops", "gpt-4o"),
                "harness": "claude_code"
            }
        }

        # Office Landmarks
        self.office = {
            "width": 640,
            "height": 480,
            "landmarks": {
                "card_dispenser": {"x": 280, "y": 320, "label": "TASK DISPENSER"},
                "meeting_area": {"x": 280, "y": 40, "label": "CISO BRIEFING AREA"}
            }
        }

        # Task Cards Storage & FIFO Queue
        self.cards: Dict[str, Dict[str, Any]] = {}
        self.card_queue: List[str] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}

        # WebSocket Event Broadcast subscribers
        self.subscribers: Set[Callable[[Dict[str, Any]], Awaitable[None]]] = set()

        # Harness adapters registry
        self.harnesses = {
            "claude_code": ClaudeCodeAdapter()
        }

    def _load_settings(self) -> Dict[str, Any]:
        """Read settings from settings.json or return defaults."""
        defaults = {
            "default_harness": "claude_code",
            "dry_run_default": True,
            "max_parallel_agents": 2,
            "agent_models": {
                "pentest": "claude-3-7-sonnet-20250219",
                "appsec": "claude-3-5-sonnet-20241022",
                "devsecops": "gpt-4o",
                "custom_models_list": [
                    "claude-3-7-sonnet-20250219",
                    "claude-3-5-sonnet-20241022",
                    "gpt-4.5-preview",
                    "gpt-4o",
                    "gemini-2.0-flash",
                    "deepseek-reasoner",
                    "ollama/qwen2.5-coder:32b"
                ]
            }
        }
        if os.path.isfile(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "agent_models" in data and isinstance(data["agent_models"], dict):
                        defaults["agent_models"].update(data["agent_models"])
                    top_level = {k: v for k, v in data.items() if k != "agent_models"}
                    defaults.update(top_level)
            except Exception:
                pass
        return defaults

    def save_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update and persist settings with deep dictionary merge for agent_models."""
        if "agent_models" in new_settings and isinstance(new_settings["agent_models"], dict):
            current_models = self.settings.setdefault("agent_models", {})
            current_models.update(new_settings["agent_models"])
            top_level = {k: v for k, v in new_settings.items() if k != "agent_models"}
            self.settings.update(top_level)
        else:
            self.settings.update(new_settings)

        self.max_parallel = int(self.settings.get("max_parallel_agents", 2))
        self.dry_run_default = bool(self.settings.get("dry_run_default", True))

        # Update live agent models if specified
        models = self.settings.get("agent_models", {})
        for agent_id, model_name in models.items():
            if agent_id in self.agents and isinstance(model_name, str):
                self.agents[agent_id]["model"] = model_name

        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

        return self.settings

    def register_subscriber(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Register a WebSocket client callback for state events."""
        self.subscribers.add(callback)

    def unregister_subscriber(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Remove a disconnected WebSocket client."""
        self.subscribers.discard(callback)

    async def broadcast(self, message: Dict[str, Any]):
        """Send message to all connected clients."""
        dead_subs = set()
        for sub in list(self.subscribers):
            try:
                await sub(message)
            except Exception:
                dead_subs.add(sub)
        for dead in dead_subs:
            self.subscribers.discard(dead)

    def get_full_state(self) -> Dict[str, Any]:
        """Return snapshot of the entire office state."""
        return {
            "agents": self.agents,
            "office": self.office,
            "cards": list(self.cards.values()),
            "queue": self.card_queue,
            "settings": self.settings,
            "active_workers_count": sum(1 for a in self.agents.values() if a["status"] in ["walking", "working", "alert"])
        }

    async def add_card(
        self,
        title: str,
        description: str = "",
        assigned_agent: Optional[str] = None,
        dry_run: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Create a new task card, perform automated triage if unassigned,
        queue it, and schedule processing.
        """
        async with self.lock:
            card_id = f"card-{uuid.uuid4().hex[:8]}"
            if dry_run is None:
                dry_run = self.dry_run_default

            # Run triage analysis
            query_for_triage = f"{title}. {description}".strip()
            triage_info = run_triage(query_for_triage)

            resolved_agent = assigned_agent
            if not resolved_agent or resolved_agent == "auto" or resolved_agent not in self.agents:
                resolved_agent = triage_info["recommended_agent_id"]

            card = {
                "id": card_id,
                "title": title.strip() or "Untitled Security Task",
                "description": description.strip(),
                "created_at": time.time(),
                "assigned_agent": resolved_agent,
                "recommended_role": triage_info["recommended_role"],
                "recommended_skills": triage_info["primary_skills"],
                "secondary_role": triage_info.get("secondary_role"),
                "secondary_skills": triage_info.get("secondary_skills", []),
                "status": "queued",  # queued | assigned | running | completed | failed | cancelled
                "dry_run": dry_run,
                "logs": [],
                "result": None
            }

            self.cards[card_id] = card
            self.card_queue.append(card_id)

        # Notify clients that a new card arrived at the dispenser
        await self.broadcast({
            "type": "card_added",
            "card": card,
            "sfx": "coin"
        })

        # Trigger queue processing safely
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(self.process_queue())
        except RuntimeError:
            pass
        return card

    async def cancel_card(self, card_id: str) -> bool:
        """Cancel a queued or running task card."""
        async with self.lock:
            if card_id not in self.cards:
                return False

            card = self.cards[card_id]
            card["status"] = "cancelled"

            if card_id in self.card_queue:
                self.card_queue.remove(card_id)

            if card_id in self.running_tasks:
                task = self.running_tasks.pop(card_id)
                task.cancel()

            # Reset any agent assigned to this card
            for agent in self.agents.values():
                if agent.get("current_card_id") == card_id:
                    agent["status"] = "idle"
                    agent["current_card_id"] = None
                    agent["current_thought"] = "Task cancelled. Standing by."
                    agent["pos"] = dict(agent["desk"])

        await self.broadcast({
            "type": "card_cancelled",
            "card_id": card_id,
            "sfx": "bleep"
        })
        await self.broadcast({
            "type": "state_sync",
            "data": self.get_full_state()
        })

        # Check if queued cards can now be picked up by the idle agent
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(self.process_queue())
        except RuntimeError:
            pass
        return True

    async def process_queue(self):
        """
        Evaluate queue and dispatch eligible cards up to max_parallel concurrency limit.
        Loops to fill all available worker slots if multiple cards and idle agents are available.
        Ensures cards explicitly assigned or triaged to a specific agent are NOT hijacked by others.
        """
        cards_to_launch = []

        async with self.lock:
            while True:
                active_count = sum(1 for a in self.agents.values() if a["status"] in ["walking", "working", "alert"])
                if active_count >= self.max_parallel:
                    break

                if not self.card_queue:
                    break

                eligible_card_id = None
                assigned_agent_id = None

                # 1. Match card to its designated agent if that agent is currently idle
                for cid in self.card_queue:
                    c = self.cards.get(cid)
                    if not c or c.get("status") != "queued":
                        continue
                    target_agent = c.get("assigned_agent")
                    if target_agent in self.agents and self.agents[target_agent]["status"] == "idle":
                        eligible_card_id = cid
                        assigned_agent_id = target_agent
                        break
                    elif not target_agent or target_agent == "auto":
                        # Unassigned card: can be taken by any idle agent
                        for aid, a in self.agents.items():
                            if a["status"] == "idle":
                                eligible_card_id = cid
                                assigned_agent_id = aid
                                c["assigned_agent"] = aid
                                break
                        if eligible_card_id:
                            break

                if not eligible_card_id or not assigned_agent_id:
                    # No more cards can be serviced by currently idle agents
                    break

                self.card_queue.remove(eligible_card_id)
                card = self.cards[eligible_card_id]
                agent = self.agents[assigned_agent_id]

                card["status"] = "assigned"
                agent["status"] = "walking"
                agent["current_card_id"] = eligible_card_id
                agent["current_thought"] = f"Picking up task '{card['title'][:25]}' from dispenser..."

                cards_to_launch.append((card, agent))

        # Launch card lifecycles outside the lock
        for card, agent in cards_to_launch:
            task = asyncio.create_task(self._run_card_lifecycle(card, agent))
            self.running_tasks[card["id"]] = task

    async def _run_card_lifecycle(self, card: Dict[str, Any], agent: Dict[str, Any]):
        """
        Orchestrate the physical animation sequence and harness execution.
        """
        card_id = card["id"]
        agent_id = agent["id"]
        dispenser_pos = self.office["landmarks"]["card_dispenser"]
        desk_pos = agent["desk"]

        try:
            # 1. Walk to Card Dispenser
            agent["pos"] = dict(dispenser_pos)
            await self.broadcast({
                "type": "agent_moved",
                "agent_id": agent_id,
                "pos": dispenser_pos,
                "status": "walking",
                "thought": f"Picking up card at dispenser desk."
            })
            await asyncio.sleep(0.5)

            # 2. Pick up Card (Coin SFX)
            card["status"] = "running"
            await self.broadcast({
                "type": "card_pickup",
                "agent_id": agent_id,
                "card_id": card_id,
                "sfx": "coin"
            })
            await asyncio.sleep(0.4)

            # 3. Walk back to Workstation Desk
            agent["pos"] = dict(desk_pos)
            agent["status"] = "working"
            agent["current_thought"] = f"Executing: {card['title']}"
            await self.broadcast({
                "type": "agent_moved",
                "agent_id": agent_id,
                "pos": desk_pos,
                "status": "working",
                "thought": agent["current_thought"]
            })

            # Callback for harness log streaming
            async def on_log_chunk(chunk: Dict[str, Any]):
                card["logs"].append(chunk)
                if len(card["logs"]) > 500:
                    card["logs"].pop(0)

                # If alert chunk, momentarily change agent to alert status
                if chunk.get("type") == "alert":
                    agent["status"] = "alert"
                    agent["current_thought"] = f"⚠️ Alert: {chunk.get('content')[:35]}"
                    await self.broadcast({
                        "type": "terminal_log",
                        "chunk": chunk,
                        "sfx": "alert"
                    })
                else:
                    if agent["status"] == "alert":
                        agent["status"] = "working"
                    await self.broadcast({
                        "type": "terminal_log",
                        "chunk": chunk,
                        "sfx": "typewriter"
                    })

            # 4. Invoke Harness Adapter
            harness_name = agent.get("harness", "claude_code")
            adapter = self.harnesses.get(harness_name, self.harnesses["claude_code"])

            result = await adapter.execute_task(
                card=card,
                agent=agent,
                settings=self.settings,
                on_log_chunk=on_log_chunk
            )

            # 5. Finalize Task
            card["result"] = result
            card["status"] = result.get("status", "completed")
            agent["status"] = "idle"
            agent["current_card_id"] = None
            agent["current_thought"] = f"Finished {card['title'][:25]}. Standing by."
            agent["pos"] = dict(desk_pos)

            await self.broadcast({
                "type": "card_completed",
                "card_id": card_id,
                "result": result,
                "sfx": "success"
            })

        except asyncio.CancelledError:
            card["status"] = "cancelled"
            agent["status"] = "idle"
            agent["current_card_id"] = None
            agent["pos"] = dict(desk_pos)
        except Exception as e:
            card["status"] = "failed"
            card["result"] = {"error": str(e)}
            agent["status"] = "idle"
            agent["current_card_id"] = None
            agent["pos"] = dict(desk_pos)
            await self.broadcast({
                "type": "terminal_log",
                "chunk": {
                    "card_id": card_id,
                    "agent_id": agent_id,
                    "type": "alert",
                    "content": f"Task execution failed with error: {str(e)}",
                    "timestamp": time.time()
                },
                "sfx": "alert"
            })
        finally:
            if card_id in self.running_tasks:
                self.running_tasks.pop(card_id, None)

            # Sync office state
            await self.broadcast({
                "type": "state_sync",
                "data": self.get_full_state()
            })

            # Check if more cards are waiting in queue
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    loop.create_task(self.process_queue())
            except RuntimeError:
                pass


# Singleton instance
state_manager = OfficeStateManager()

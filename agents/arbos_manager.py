# agents/arbos_manager.py
# Final Clean Version - Arbos-centric with intelligent planning, dynamic swarm, ToolHunter,
# dynamic compute, strong resource_aware, and proper toggle respect

import os
import subprocess
import json
import concurrent.futures
import multiprocessing
import time
from typing import Tuple, List, Dict, Any

from agents.memory import memory

from agents.tools.compute import ComputeRouter
from agents.tools.resource_aware import ResourceMonitor
from agents.tools.guardrails import apply_guardrails
from agents.tools.tool_hunter import tool_hunter


class ArbosManager:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        self.compute = ComputeRouter()
        self.config = self._load_config()
        self.extra_context = self._load_extra_context()
        self._setup_real_arbos()
        print("✅ Arbos Primary Solver Mode loaded")
        print(f"   → Max compute: {self.config.get('max_compute_hours')} hours")
        print(f"   → Resource aware: {self.config.get('resource_aware')} | Guardrails: {self.config.get('guardrails')}")
        print(f"   → ToolHunter escalation: {self.config.get('toolhunter_escalation', True)}")

    def _setup_real_arbos(self):
        if not os.path.exists(self.arbos_path):
            print("Cloning real Arbos...")
            subprocess.run(["git", "clone", "https://github.com/unarbos/arbos.git", self.arbos_path], check=True)

    def _load_config(self):
        config = {
            "miner_review_after_loop": False,
            "max_loops": 5,
            "miner_review_final": True,
            "chutes": True,
            "chutes_llm": "mixtral",
            "max_compute_hours": 3.8,
            "max_compute_minutes": 228,
            "resource_aware": True,
            "guardrails": True,
            "toolhunter_escalation": True,      # NEW - controls escalation behavior
            "manual_tool_installs_allowed": True # NEW - controls whether manual recommendations are shown
        }
        try:
            with open(self.goal_file, "r") as f:
                for line in f:
                    stripped = line.strip().lower()
                    if stripped.startswith("miner_review_after_loop:"):
                        config["miner_review_after_loop"] = "true" in stripped
                    elif stripped.startswith("max_loops:"):
                        config["max_loops"] = int(line.split(":")[1].strip())
                    elif stripped.startswith("miner_review_final:"):
                        config["miner_review_final"] = "true" in stripped
                    elif stripped.startswith("chutes:"):
                        config["chutes"] = "true" in stripped
                    elif stripped.startswith("chutes_llm:"):
                        config["chutes_llm"] = line.split(":")[1].strip()
                    elif stripped.startswith("max_compute_hours:"):
                        config["max_compute_hours"] = float(line.split(":")[1].strip())
                    elif stripped.startswith("max_compute_minutes:"):
                        config["max_compute_minutes"] = int(line.split(":")[1].strip())
                    elif stripped.startswith("resource_aware:"):
                        config["resource_aware"] = "true" in stripped
                    elif stripped.startswith("guardrails:"):
                        config["guardrails"] = "true" in stripped
                    elif stripped.startswith("toolhunter_escalation:"):
                        config["toolhunter_escalation"] = "true" in stripped
                    elif stripped.startswith("manual_tool_installs_allowed:"):
                        config["manual_tool_installs_allowed"] = "true" in stripped
        except Exception:
            pass
        return config

    def _load_extra_context(self) -> str:
        try:
            with open(self.goal_file, "r") as f:
                content = f.read()
            if "# Miner Control" in content or "# Compute" in content:
                return content.split("# Compute", 1)[-1].strip()
            return content
        except Exception:
            return ""

    # ===================================================================
    # META PLANNING ARBOS
    # ===================================================================
    def plan_challenge(self, challenge: str) -> Dict[str, Any]:
        max_hours = self.config.get("max_compute_hours", 3.8)
        monitor = ResourceMonitor(max_hours=max_hours)
        remaining_hours = max_hours - monitor.elapsed_hours()

        full_context = f"""CHALLENGE: {challenge}

MINER STRATEGY (HIGH PRIORITY):
{self.extra_context}

Time available: {remaining_hours:.2f}h"""

        past = memory.query(challenge, n_results=6)
        if past:
            full_context += "\n\nPast attempts and critiques:\n" + "\n---\n".join(past)

        planning_task = f"""You are Planning Arbos...

{full_context}

Output EXACTLY this JSON..."""  # (keep your full planning prompt here)

        response = self.compute.run_on_compute(planning_task)
        return self._parse_json(response)

    # ... [ _refine_plan and _parse_json remain unchanged from previous version ]

    # ===================================================================
    # TOOL HUNTER - Now respects toggles
    # ===================================================================
    def _tool_hunter(self, gap_description: str, subtask: str) -> str:
        if not self.config.get("toolhunter_escalation", True):
            return "ToolHunter escalation disabled by config."

        result = tool_hunter.hunt_and_integrate(
            gap_description=gap_description,
            subtask=subtask,
            challenge_context=f"SN63 challenge: {subtask}"
        )

        if result.get("status") == "success":
            return f"ToolHunter SUCCESS: {result.get('tool_name')} | Integration ready"
        else:
            if self.config.get("manual_tool_installs_allowed", True):
                return f"ToolHunter MANUAL REQUIRED:\n{result.get('miner_recommendation', 'No tool found')}"
            else:
                return "ToolHunter failed to auto-integrate. Manual installs disabled by config."

    # ===================================================================
    # SUB-ARBOS WORKER
    # ===================================================================
    def _sub_arbos_worker(self, subtask: str, hypothesis: str, tools: List[str],
                          shared_results: dict, subtask_id: int) -> dict:
        max_hours = self.config.get("max_compute_hours", 3.8)
        monitor = ResourceMonitor(max_hours=max_hours / 3.0)

        if self.config.get("resource_aware") and monitor.elapsed_hours() > max_hours * 0.75:
            solution = "Early abort: time budget exceeded to protect overall compute limit."
            trace = ["Resource-aware early abort triggered"]
        else:
            solution = f"Subtask: {subtask}\nHypothesis: {hypothesis}"
            trace = [f"Sub-Arbos {subtask_id} started on {subtask}"]

            for loop in range(3):
                reflect_task = f"""You are a focused sub-Arbos for SN63.

Subtask: {subtask}
Hypothesis: {hypothesis}
Current solution: {solution[:700]}

Critique rigorously for novelty, verifier potential, and alignment.
Decide: Improve / Call Tool / Finalize"""

                response = self.compute.run_on_compute(reflect_task)
                trace.append(f"Reflection {loop+1}: {response[:150]}...")

                if "Finalize" in response or "final" in response.lower():
                    break

                if "ToolHunter" in str(tools) or "hunter" in response.lower():
                    gap = f"Gap detected in subtask: {subtask}"
                    hunt_result = self._tool_hunter(gap, subtask)
                    solution += f"\n\n[ToolHunter]\n{hunt_result}"

                elif tools and tools[0] != "none":
                    tool_name = tools[0]
                    output = self.compute.run_on_compute(f"Apply {tool_name} to: {solution[:600]}")
                    solution += f"\n\n[{tool_name}]\n{output}"

                if self.config.get("guardrails"):
                    solution = apply_guardrails(solution, monitor)

                if time.time() - monitor.start_time > (max_hours * 1800 / 6):
                    trace.append("Subtask hard time cap reached")
                    break

        memory.add(text=solution[:1000], metadata={"subtask": subtask, "status": "completed"})
        shared_results[subtask_id] = {"subtask": subtask, "solution": solution, "trace": trace}
        return shared_results[subtask_id]

    # ===================================================================
    # DYNAMIC SWARM + SYNTHESIS
    # ===================================================================
    def _run_swarm(self, blueprint: Dict[str, Any], challenge: str) -> str:
        # ... (swarm execution logic remains the same as previous full version)

        # After synthesis
        if self.config.get("guardrails"):
            final_solution = apply_guardrails(final_solution, ResourceMonitor(max_hours=self.config.get("max_compute_hours", 3.8)))

        memory.add(text=final_solution[:1500], metadata={"challenge": challenge, "status": "final_attempt"})

        return final_solution

    # ===================================================================
    # ORCHESTRATOR
    # ===================================================================
    def _smart_route(self, challenge: str) -> Tuple[str, List[str], bool]:
        import streamlit as st

        trace_log = ["🚀 Starting Arbos Orchestrator"]

        trace_log.append("→ Running Intelligent Planning Arbos...")
        high_level_plan = self.plan_challenge(challenge)
        st.session_state.high_level_plan = high_level_plan
        st.session_state.trace_log = trace_log

        approved_plan = high_level_plan

        trace_log.append("→ Running Orchestrator Arbos Refinement...")
        blueprint = self._refine_plan(approved_plan, challenge)
        st.session_state.blueprint = blueprint
        st.session_state.trace_log = trace_log

        trace_log.append("→ Launching parallel Sub-Arbos swarm with per-subtask ToolHunter...")
        final_solution = self._run_swarm(blueprint, challenge)

        tools_used = ["swarm_various"]
        should_reloop = self.config.get("miner_review_after_loop", False)

        st.session_state.trace_log = trace_log
        return final_solution, tools_used, should_reloop

    def run(self, challenge: str):
        print(f"🚀 Starting Arbos Orchestrator for: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=self.config.get("max_compute_hours", 3.8))

        final_solution, tools_used, should_reloop = self._smart_route(challenge)

        print(f"✅ Completed.")
        return final_solution, should_reloop

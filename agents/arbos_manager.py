# agents/arbos_manager.py
# PRIMARY SOLVER VERSION - Arbos-centric with Meta Planning + Refinement + Dynamic Swarm
# Includes conditional ToolHunter per sub-Arbos instance

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
from agents.tools.exploration import explore_novel_variant


class ArbosManager:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        self.compute = ComputeRouter()
        self.config = self._load_config()
        self.extra_context = self._load_extra_context()
        self._setup_real_arbos()
        print("✅ Arbos Primary Solver Mode loaded")
        print("   → Meta Planning Arbos + Refinement + Dynamic Swarm + ToolHunter enabled")

    def _setup_real_arbos(self):
        if not os.path.exists(self.arbos_path):
            print("Cloning real Arbos...")
            subprocess.run(["git", "clone", "https://github.com/unarbos/arbos.git", self.arbos_path], check=True)

    def _load_config(self):
        config = {
            "reflection": 4,
            "exploration": True,
            "resource_aware": True,
            "guardrails": True,
            "miner_review_after_loop": False,
            "max_loops": 5,
            "miner_review_final": True,
            "chutes": True,
            "chutes_llm": "mixtral",
            # NEW: Dynamic compute limit (easily configurable in killer_base.md)
            "max_compute_hours": 3.8,      # Default fallback
            "max_compute_minutes": 228     # For finer control in prompts
        }
        try:
            with open(self.goal_file, "r") as f:
                for line in f:
                    stripped = line.strip().lower()
                    if stripped.startswith("reflection:"):
                        config["reflection"] = int(line.split(":")[1].strip())
                    elif stripped.startswith("exploration:"):
                        config["exploration"] = "true" in stripped
                    elif stripped.startswith("resource_aware:"):
                        config["resource_aware"] = "true" in stripped
                    elif stripped.startswith("guardrails:"):
                        config["guardrails"] = "true" in stripped
                    elif stripped.startswith("miner_review_after_loop:"):
                        config["miner_review_after_loop"] = "true" in stripped
                    elif stripped.startswith("max_loops:"):
                        config["max_loops"] = int(line.split(":")[1].strip())
                    elif stripped.startswith("miner_review_final:"):
                        config["miner_review_final"] = "true" in stripped
                    elif stripped.startswith("chutes:"):
                        config["chutes"] = "true" in stripped
                    elif stripped.startswith("chutes_llm:"):
                        config["chutes_llm"] = line.split(":")[1].strip()
                    # NEW toggles for dynamic compute
                    elif stripped.startswith("max_compute_hours:"):
                        config["max_compute_hours"] = float(line.split(":")[1].strip())
                    elif stripped.startswith("max_compute_minutes:"):
                        config["max_compute_minutes"] = int(line.split(":")[1].strip())
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
        """Meta Planning Arbos - high-level plan for miner approval."""
        monitor = ResourceMonitor(max_hours=3.8)
        remaining_hours = 3.8 - monitor.elapsed_hours()

        full_context = f"""CHALLENGE: {challenge}

MINER STRATEGY (HIGH PRIORITY):
{self.extra_context}

Time available: {remaining_hours:.2f}h on H100"""

        past = memory.query(challenge, n_results=4)
        if past:
            full_context += "\n\nPast similar challenges:\n" + "\n---\n".join(past)

        planning_task = f"""You are Planning Arbos, a meta-planner specialized for Bittensor SN63 challenges.

{full_context}

Create a high-level executable plan for an extremely hard, well-defined computational problem.
Strictly follow miner strategy. Bias toward novelty, verifier potential, and H100 realism.

Output EXACTLY this JSON (no extra text):
{{
  "high_level_goals": "one sentence summary",
  "risks_and_mitigations": ["risk1", "risk2", ...],
  "rough_decomposition": ["subtask1 description", "subtask2 description", ...],
  "suggested_swarm_size": 4,
  "high_level_tool_hints": {{"subtask1": ["ScienceClaw"], "subtask2": ["ToolHunter"]}},
  "compute_ballpark_minutes": 210,
  "quality_gate_targets": {{"novelty": 8.5, "verifier": 9.0, "alignment": 9.5, "completeness": 9.0}}
}}

Critique your own plan for SN63 optimality before outputting."""

        response = self.compute.run_on_compute(planning_task)
        return self._parse_json(response)

    # ===================================================================
    # PLAN REFINEMENT
    # ===================================================================
    def _refine_plan(self, approved_plan: Dict[str, Any], challenge: str) -> Dict[str, Any]:
        """Main Arbos refinement: produces executable blueprint for swarm."""
        monitor = ResourceMonitor(max_hours=3.8)
        remaining_hours = 3.8 - monitor.elapsed_hours()

        refinement_task = f"""You are Arbos, the primary orchestrator.

CHALLENGE: {challenge}
APPROVED HIGH-LEVEL PLAN:
{json.dumps(approved_plan, indent=2)}

MINER STRATEGY:
{self.extra_context}

Time left: {remaining_hours:.2f}h

Refine into precise executable blueprint.

Output EXACTLY this JSON:
{{
  "decomposition": ["detailed subtask1", "detailed subtask2", ...],
  "swarm_config": {{
    "total_instances": 5,
    "assignment": {{"subtask1": 1, "subtask2": 2, ...}},
    "hypothesis_diversity": ["classical baseline", "quantum VQE", "bio-inspired", ...]
  }},
  "tool_map": {{"subtask1": ["ScienceClaw"], "subtask2": ["ToolHunter"], ...}},
  "compute_projection_minutes": 195,
  "risk_flags": ["high_simulation_load"],
  "quality_gate_targets": {{"novelty": 9.0, "verifier": 9.5, ...}},
  "early_abort_triggers": ["if any subtask > 40min"]
}}

Project realistic H100 time. Propose conservative fallback if needed."""

        response = self.compute.run_on_compute(refinement_task)
        return self._parse_json(response)

    def _parse_json(self, raw_response: str) -> Dict[str, Any]:
        """Robust JSON parser with fallback."""
        try:
            start = raw_response.find("{")
            end = raw_response.rfind("}") + 1
            json_str = raw_response[start:end]
            return json.loads(json_str)
        except Exception:
            return {
                "decomposition": ["Fallback: process full challenge as one subtask"],
                "swarm_config": {"total_instances": 1, "assignment": {}},
                "tool_map": {},
                "compute_projection_minutes": 210,
                "risk_flags": ["JSON parse fallback - review recommended"]
            }

    # ===================================================================
    # TOOL HUNTER (per sub-Arbos)
    # ===================================================================

    def _tool_hunter(self, gap_description: str, subtask: str) -> str:
        """Real ToolHunter integration."""
        from agents.tools.tool_hunter import tool_hunter
        
        # Pass challenge context from memory or blueprint if available
        result = tool_hunter.hunt_and_integrate(
            gap_description=gap_description,
            subtask=subtask,
            challenge_context="SN63 quantum/optimization challenge on Quantum Rings simulator"
        )
        
        if result["status"] == "success":
            return f"ToolHunter SUCCESS: {result['tool_name']} | Integration: {result.get('integration_code', '')[:300]}"
        else:
            return f"ToolHunter: {result.get('reason', 'No suitable tool found')}"

    # ===================================================================
    # SUB-ARBOS WORKER (runs in parallel)
    # ===================================================================
    def _sub_arbos_worker(self, subtask: str, hypothesis: str, tools: List[str],
                          shared_results: dict, subtask_id: int) -> dict:
        """Individual sub-Arbos for one subtask/hypothesis."""
        monitor = ResourceMonitor(max_hours=1.5)  # conservative per-worker budget
        start_time = time.time()

        solution = f"Subtask: {subtask}\nHypothesis: {hypothesis}"
        used_tools = []
        trace = [f"Sub-Arbos {subtask_id} started on {subtask}"]

        for loop in range(3):  # limited loops per subtask
            reflect_task = f"""You are a focused sub-Arbos.

Subtask: {subtask}
Hypothesis: {hypothesis}
Current: {solution[:800]}

Critique novelty, verifier potential, alignment with miner strategy.
Decide: Improve / Call Tool / Finalize"""

            response = self.compute.run_on_compute(reflect_task)
            trace.append(f"Loop {loop+1}: {response[:120]}...")

            if "Finalize" in response or "final" in response.lower():
                break

            # Tool logic including ToolHunter
            if "ToolHunter" in tools or "hunter" in response.lower():
                gap = "Specialized tool needed for this subtask gap"
                hunt_result = self._tool_hunter(gap, subtask)
                solution += f"\n\n[ToolHunter]\n{hunt_result}"
                used_tools.append("ToolHunter")
            elif tools and tools[0] != "none":
                tool_name = tools[0]
                output = self.compute.run_on_compute(f"Apply {tool_name} style to: {solution[:600]}")
                solution += f"\n\n[{tool_name}]\n{output}"
                used_tools.append(tool_name)
            else:
                solution = response  # pure Arbos improvement

            if time.time() - start_time > 1800:  # 30 min hard cap
                trace.append("Subtask time cap reached")
                break

        shared_results[subtask_id] = {
            "subtask": subtask,
            "hypothesis": hypothesis,
            "solution": solution,
            "tools_used": used_tools,
            "trace": trace
        }
        return shared_results[subtask_id]

    # ===================================================================
    # DYNAMIC SWARM EXECUTION
    # ===================================================================
    def _run_swarm(self, blueprint: Dict[str, Any], challenge: str) -> str:
        """Launch parallel sub-Arbos swarm based on blueprint."""
        decomposition = blueprint.get("decomposition", ["Full challenge"])
        swarm_config = blueprint.get("swarm_config", {"total_instances": 1, "assignment": {}})
        tool_map = blueprint.get("tool_map", {})

        total_instances = min(swarm_config.get("total_instances", 4), 6)  # H100 safe
        assignment = swarm_config.get("assignment", {})
        hypotheses = swarm_config.get("hypothesis_diversity", ["standard approach"] * len(decomposition))

        trace_log = ["🚀 Launching Dynamic Swarm...", f"Subtasks: {len(decomposition)} | Instances: {total_instances}"]

        # Shared results across processes
        manager_dict = multiprocessing.Manager().dict()

        with concurrent.futures.ProcessPoolExecutor(max_workers=total_instances) as executor:
            futures = []
            subtask_id = 0
            for i, subtask in enumerate(decomposition):
                assigned_count = assignment.get(subtask, 1)
                tools_for_subtask = tool_map.get(subtask, ["none"])

                for _ in range(assigned_count):
                    hyp = hypotheses[i % len(hypotheses)] if hypotheses else "standard"
                    futures.append(
                        executor.submit(
                            self._sub_arbos_worker,
                            subtask, hyp, tools_for_subtask,
                            manager_dict, subtask_id
                        )
                    )
                    subtask_id += 1

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    trace_log.append(f"✓ Subtask completed: {result.get('subtask', '')[:80]}...")
                except Exception as e:
                    trace_log.append(f"✗ Subtask error: {e}")

        # Synthesis by main Orchestrator Arbos
        all_results = dict(manager_dict)
        synthesis_task = f"""You are Arbos Orchestrator. Synthesize the swarm results into one coherent, high-novelty, verifier-strong solution for SN63.

Challenge: {challenge}

Swarm results:
{json.dumps(all_results, indent=2)}

Prioritize best novelty + verifier paths. Follow miner strategy from killer_base.md.

Final Synthesized Solution:"""

        final_solution = self.compute.run_on_compute(synthesis_task)
        trace_log.append("Swarm synthesis complete by main Arbos")

        # Store trace for Streamlit
        import streamlit as st
        if "trace_log" not in st.session_state:
            st.session_state.trace_log = []
        st.session_state.trace_log.extend(trace_log)

        return final_solution

    # ===================================================================
    # ORCHESTRATOR
    # ===================================================================
    def _smart_route(self, challenge: str) -> Tuple[str, List[str], bool]:
        import streamlit as st

        trace_log = ["🚀 Starting Arbos Orchestrator"]

        # 1. Meta Planning Arbos
        trace_log.append("→ Running Meta Planning Arbos...")
        high_level_plan = self.plan_challenge(challenge)
        trace_log.append(f"High-level plan generated (suggested swarm: {high_level_plan.get('suggested_swarm_size', 1)})")

        st.session_state.high_level_plan = high_level_plan
        st.session_state.trace_log = trace_log

        # Assume approval for now (Streamlit will handle real approval and set approved_plan)
        # In full flow, approved_plan comes from Streamlit after miner clicks Approve
        approved_plan = high_level_plan

        # 2. Refinement
        trace_log.append("→ Running Plan Refinement...")
        blueprint = self._refine_plan(approved_plan, challenge)
        trace_log.append(f"Blueprint ready - {len(blueprint.get('decomposition', []))} subtasks")

        st.session_state.blueprint = blueprint
        st.session_state.trace_log = trace_log

        # 3. Dynamic Swarm
        trace_log.append("→ Launching parallel sub-Arbos swarm with ToolHunter support...")
        final_solution = self._run_swarm(blueprint, challenge)

        tools_used = ["swarm_various"]
        should_reloop = self.config.get("miner_review_after_loop", False)

        st.session_state.trace_log = trace_log
        return final_solution, tools_used, should_reloop

    def run(self, challenge: str):
        print(f"🚀 Starting Arbos Orchestrator for challenge: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=3.8)

        final_solution, tools_used, should_reloop = self._smart_route(challenge)

        final_output = apply_guardrails(final_solution, monitor)

        if self.config.get("exploration", True):
            final_output = explore_novel_variant(challenge, final_output)

        print(f"✅ Completed with swarm execution. Tools involved: {tools_used}")
        return final_output, should_reloop

# agents/arbos_manager.py
# PRIMARY SOLVER VERSION - Arbos is the main intelligence, tools are optional boosters

import os
import subprocess
from pathlib import Path
from typing import Tuple, List

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
        print("✅ Arbos Primary Solver Mode loaded - Arbos is the main intelligence")

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
            "chutes_llm": "mixtral"
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

    def _smart_route(self, challenge: str) -> Tuple[str, List[str], bool]:
        from agents.tool_study import tool_study
        import streamlit as st

        full_context = f"""GOAL: {challenge}

MINER STRATEGY (HIGH PRIORITY):
{self.extra_context}""".strip()

        results = []
        used_tools = []
        cumulative_context = full_context
        trace_log = []

        past = memory.query(challenge, n_results=6)
        if past:
            cumulative_context += "\n\nPast knowledge:\n" + "\n---\n".join(past)

        monitor = ResourceMonitor(max_hours=3.8)
        remaining_hours = 3.8 - monitor.elapsed_hours()

        trace_log.append(f"Starting Primary Solver | Time left: {remaining_hours:.2f}h")

        def arbos_reflect(current_solution: str, stage: str) -> dict:
            task = f"""You are Arbos, the primary solver.

GOAL: {challenge}

MINER STRATEGY:
{self.extra_context}

Current solution:
{current_solution}

Stage: {stage}
Time left: {remaining_hours:.2f}h

Critique rigorously for:
- Alignment with miner strategy
- Novelty
- Verifier score potential
- Completeness
- Weaknesses

Then decide:
- Finalize?
- Improve?
- Call a tool? (ScienceClaw, GPD, AI-Researcher, AutoResearch)

Reply exactly:
Critique: [detailed]
Decision: [Finalize / Improve / Call Tool: TOOLNAME]
Next Action: [what to do]
Improved Solution: [if improving]"""

            response = self.compute.run_on_compute(task)
            trace_log.append(f"Arbos Reflection ({stage}): {response[:200]}...")

            decision = "Improve"
            tool_to_call = None
            if "Finalize" in response:
                decision = "Finalize"
            elif "Call Tool:" in response:
                tool_to_call = response.split("Call Tool:")[-1].split()[0].strip()

            return {
                "decision": decision,
                "tool_to_call": tool_to_call,
                "response": response
            }

        last_solution = "No solution yet."

        for loop in range(self.config.get("max_loops", 5)):
            trace_log.append(f"--- Arbos Primary Loop {loop+1} ---")

            reflection = arbos_reflect(last_solution, f"Loop {loop+1}")

            if reflection["decision"] == "Finalize":
                trace_log.append("Arbos decided to finalize")
                break

            if reflection["tool_to_call"]:
                tool_name = reflection["tool_to_call"]
                if tool_name == "ScienceClaw":
                    result = run_scienceclaw(task=reflection["response"])
                    output = result.get("output", result.get("error", "No output"))
                else:
                    # Mimic for other tools
                    output = self.compute.run_on_compute(f"Continue solving using {tool_name} style. Current solution: {last_solution[:800]}")

                results.append(f"[{tool_name}]\n{output}")
                used_tools.append(tool_name)
                cumulative_context += f"\n\n[{tool_name}]\n{output}"
                last_solution = output
            else:
                # Pure Arbos improvement
                last_solution = reflection["response"]

            memory.add(text=last_solution, metadata={"loop": loop+1})

            if self.config.get("miner_review_after_loop", False):
                break

        st.session_state.trace_log = trace_log
        return last_solution, used_tools, self.config.get("miner_review_after_loop", False)

    def run(self, challenge: str):
        print(f"🚀 Starting Arbos Primary Solver for: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=3.8)

        final_solution, tools_used, should_reloop = self._smart_route(challenge)

        final_output = apply_guardrails(final_solution, monitor)

        if self.config.get("exploration", True):
            final_output = explore_novel_variant(challenge, final_output)

        print(f"✅ Completed with tools: {tools_used}")
        return final_output, should_reloop

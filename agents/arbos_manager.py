# agents/arbos_manager.py
# STRONGER VERSION - Full GOAL.md context + Adaptive Re-loop + Strong Critique

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
        print("✅ REAL Arbos + Strong GOAL.md Context + Adaptive Re-Loop loaded")

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
            "max_loops": 4,
            "miner_review_final": True,
            "chutes": True,
            "targon": False,
            "celium": False,
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
                    elif stripped.startswith("targon:"):
                        config["targon"] = "true" in stripped
                    elif stripped.startswith("celium:"):
                        config["celium"] = "true" in stripped
                    elif stripped.startswith("chutes_llm:"):
                        config["chutes_llm"] = line.split(":")[1].strip()
        except Exception:
            pass
        return config

    def _load_extra_context(self) -> str:
        """Load all strategic text from GOAL.md after toggles"""
        try:
            with open(self.goal_file, "r") as f:
                content = f.read()

            # Take everything after the last known toggle section
            if "# Miner Control" in content or "# Compute" in content:
                parts = content.split("# Compute", 1)
                return parts[1].strip() if len(parts) > 1 else content
            return content
        except Exception:
            return ""

    def _smart_route(self, challenge: str, approved_plan: str = "") -> Tuple[str, List[str], bool]:
        from agents.tool_study import tool_study
        import streamlit as st

        # Strong context injection - miner strategy is now prominent
        full_context = f"""GOAL: {challenge}

MINER STRATEGY / CONTEXT FROM GOAL.md:
{self.extra_context}

APPROVED PLAN:
{approved_plan}""".strip()

        results = []
        used_tools = []
        cumulative_context = full_context
        trace_log = []

        past = memory.query(challenge, n_results=4)
        if past:
            cumulative_context += "\n\nPast knowledge:\n" + "\n---\n".join(past)

        monitor = ResourceMonitor(max_hours=3.8)
        remaining_hours = 3.8 - monitor.elapsed_hours()
        reflection_depth = 3 if remaining_hours > 2.0 else 2 if remaining_hours > 1.0 else 1

        trace_log.append(f"Time left: {remaining_hours:.2f}h | Depth: {reflection_depth} | Strategy context: {len(self.extra_context)} chars")

        def reflect_and_redesign(last_output: str, next_tool: str) -> dict:
            tool_profile = tool_study.load_relevant_profile(next_tool, query=cumulative_context)
            try:
                task = f"""You are Arbos.

GOAL: {challenge}

MINER STRATEGY (HIGH PRIORITY):
{self.extra_context}

Previous output: {last_output}
Next tool: {next_tool}
Time left: {remaining_hours:.2f}h

Tool Profile: {tool_profile}

Mimic the tool intelligently. Stay aligned with the miner's strategy above. Prioritize novelty and verifier score.

Reply exactly:
Prompt: [full prompt]
Recommended Compute: [chutes/targon/celium/local]"""

                response = self.compute.run_on_compute(task)
                prompt_part = response.split("Prompt:")[-1] if "Prompt:" in response else response
                compute_override = response.split("Recommended Compute:")[-1].strip().lower() if "Recommended Compute:" in response else None

                trace_log.append(f"[{next_tool}] Strong context used | Compute: {compute_override or 'default'}")
                return {"prompt": prompt_part.strip(), "compute_override": compute_override}
            except Exception:
                trace_log.append(f"[{next_tool}] Fallback")
                return {"prompt": f"Continue with previous findings using {next_tool}.", "compute_override": None}

        last_output = ""
        max_loops = self.config.get("max_loops", 4)

        for loop in range(max_loops):
            trace_log.append(f"--- Loop {loop+1}/{max_loops} ---")

            for tool_name in ["AI-Researcher", "AutoResearch", "GPD", "ScienceClaw"]:
                decide = self.compute.run_on_compute(f"Given the miner strategy above, should we use {tool_name} now?")
                if "YES" in decide.upper():
                    redesign = reflect_and_redesign(last_output, tool_name)
                    result = self.compute.run_on_compute(redesign["prompt"], override_compute=redesign.get("compute_override"))
                    output = result

                    results.append(f"[{tool_name}]\n{output}")
                    used_tools.append(tool_name)
                    cumulative_context += f"\n\n[{tool_name} Output]\n{output}"
                    last_output = output

            # Real ScienceClaw
            if any(k in lower for k in ["analyze", "experiment", "data", "science", "conclude"]):
                redesign = reflect_and_redesign(last_output, "ScienceClaw")
                result = run_scienceclaw(task=redesign["prompt"])
                output = result.get("output", result.get("error", "No output"))
                results.append(f"[ScienceClaw - REAL]\n{output}")
                used_tools.append("ScienceClaw")
                cumulative_context += f"\n\n[ScienceClaw REAL]\n{output}"

            memory.add(text="\n\n".join(results), metadata={"loop": loop+1})

            if self.config.get("miner_review_after_loop", False):
                break

        st.session_state.trace_log = trace_log
        return "\n\n".join(results), used_tools, self.config.get("miner_review_after_loop", False)

    def run(self, challenge: str):
        print(f"🚀 Starting Arbos for challenge: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=3.8)

        tool_results, tools_used, should_reloop = self._smart_route(challenge)

        final_output = apply_guardrails(tool_results, monitor)

        if self.config.get("exploration", True):
            final_output = explore_novel_variant(challenge, final_output)

        print(f"✅ Completed with tools: {tools_used}")
        return final_output, should_reloop

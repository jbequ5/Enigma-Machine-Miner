# agents/arbos_manager.py
# FINAL VERSION - Full GOAL.md context + auto-reloop + max_loops + miner review controls

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
        self.config, self.extra_context = self._load_config()
        self._setup_real_arbos()
        print("✅ REAL Arbos + Long-term Memory + Full GOAL.md Context loaded")

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
        extra_context = ""

        try:
            with open(self.goal_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
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

            # Everything after the toggles becomes extra strategic context
            full_text = "".join(lines)
            # Simple split: take everything after the last toggle-like line
            if "# Miner Control" in full_text or "# Compute" in full_text:
                extra_context = full_text.split("# Compute", 1)[-1] if "# Compute" in full_text else full_text
            else:
                extra_context = full_text

        except Exception as e:
            print(f"Warning: Could not fully parse GOAL.md: {e}")

        return config, extra_context.strip()

    def _smart_route(self, challenge: str, approved_plan: str = "") -> Tuple[str, List[str], bool]:
        from agents.tool_study import tool_study
        import streamlit as st

        full_context = f"{approved_plan}\n\nExtra Strategy from GOAL.md:\n{self.extra_context}" if self.extra_context else approved_plan

        lower = challenge.lower()
        results = []
        used_tools = []
        cumulative_context = full_context[:2000] if full_context else ""
        trace_log = []

        past_knowledge = memory.query(challenge, n_results=4)
        if past_knowledge:
            cumulative_context += "\n\nRelevant past knowledge:\n" + "\n---\n".join(past_knowledge)

        program_path = Path("program.md")
        if not program_path.exists():
            program_path.write_text(f"# Execution Program\n\n## Challenge\n{challenge}\n\n## Context\n{self.extra_context}\n\n## Approved Plan\n{approved_plan}\n\n")

        monitor = ResourceMonitor(max_hours=3.8)
        elapsed = monitor.elapsed_hours()
        remaining_hours = 3.8 - elapsed
        reflection_depth = 3 if remaining_hours > 2.0 else 2 if remaining_hours > 1.0 else 1

        trace_log.append(f"Time remaining: {remaining_hours:.2f}h | Reflection depth: {reflection_depth} | Extra context length: {len(self.extra_context)}")

        def reflect_and_redesign(last_output: str, next_tool: str) -> dict:
            tool_profile = tool_study.load_relevant_profile(next_tool, query=cumulative_context + " " + last_output)
            try:
                task = f"""You are Arbos...

Goal from GOAL.md: {challenge}
Extra Strategy/Context: {self.extra_context[:800]}

Previous output: {last_output}
Next tool: {next_tool}
Time left: {remaining_hours:.2f}h

Tool Profile: {tool_profile}

Mimic the tool intelligently and align with the strategy above.

Reply exactly:
Prompt: [prompt]
Recommended Compute: [chutes/targon/celium/local]"""

                response = self.compute.run_on_compute(task)
                prompt_part = response.split("Prompt:")[-1] if "Prompt:" in response else response
                compute_override = response.split("Recommended Compute:")[-1].strip().lower() if "Recommended Compute:" in response else None

                trace_log.append(f"[{next_tool}] Profile used | Compute: {compute_override or 'default'}")
                return {"prompt": prompt_part.strip(), "compute_override": compute_override}
            except Exception:
                trace_log.append(f"[{next_tool}] Reflection fallback")
                return {"prompt": f"Continue with previous findings using {next_tool}.", "compute_override": None}

        last_output = ""
        max_loops = self.config.get("max_loops", 4)

        for loop in range(max_loops):
            trace_log.append(f"--- Starting Loop {loop+1}/{max_loops} ---")

            tool_sequence = ["AI-Researcher", "AutoResearch", "GPD", "ScienceClaw"]
            for tool_name in tool_sequence:
                decide_task = f"""Challenge: {challenge}
Extra context: {self.extra_context[:400]}
Cumulative: {cumulative_context[:400]}
Should we use {tool_name} now?"""

                decision = self.compute.run_on_compute(decide_task)

                if "YES" in decision.upper():
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

# agents/arbos_manager.py
# FINAL OPERATIONAL VERSION - Reflection after every tool + Long-term memory + program.md

import os
import subprocess
from pathlib import Path
from typing import Tuple, List

# Core imports
from agents.memory import memory

# Tool imports (subfolder structure)
from agents.tools.hyperagent import run_hyperagent
from agents.tools.ai_researcher import run_ai_researcher
from agents.tools.autoresearch import run_autoresearch
from agents.tools.get_physics_done import run_gpd
from agents.tools.scienceclaw import run_scienceclaw

# Supporting tools
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
        self._setup_real_arbos()
        print("✅ REAL Arbos + Long-term Memory + Reflection Loop loaded")

    def _setup_real_arbos(self):
        if not os.path.exists(self.arbos_path):
            print("Cloning real Arbos...")
            subprocess.run(["git", "clone", "https://github.com/unarbos/arbos.git", self.arbos_path], check=True)

    def _load_config(self):
        config = {
            "reflection": 4,
            "hyper_planning": True,
            "exploration": True,
            "resource_aware": True,
            "guardrails": True
        }
        try:
            with open(self.goal_file, "r") as f:
                for line in f:
                    line = line.strip().lower()
                    if line.startswith("reflection:"):
                        config["reflection"] = int(line.split(":")[1].strip())
                    elif line.startswith("hyper_planning:"):
                        config["hyper_planning"] = "true" in line
                    elif line.startswith("exploration:"):
                        config["exploration"] = "true" in line
                    elif line.startswith("resource_aware:"):
                        config["resource_aware"] = "true" in line
                    elif line.startswith("guardrails:"):
                        config["guardrails"] = "true" in line
        except Exception:
            pass
        return config

        def _smart_route(self, challenge: str, approved_plan: str = "") -> Tuple[str, List[str]]:
        """
        FINAL CLEAN INTELLIGENT _smart_route
        - Arbos uses studied tool profiles to mimic each tool accurately
        - Execution routed through ComputeRouter (respects dynamic override)
        - Tight reflection loop with long-term memory
        """
        from agents.tool_study import tool_study

        lower = challenge.lower()
        results = []
        used_tools = []
        cumulative_context = approved_plan[:1500] if approved_plan else ""

        # Long-term memory retrieval
        past_knowledge = memory.query(challenge, n_results=4)
        if past_knowledge:
            cumulative_context += "\n\nRelevant past knowledge from previous runs:\n" + "\n---\n".join(past_knowledge)

        # Initialize program.md
        program_path = Path("program.md")
        if not program_path.exists():
            program_path.write_text(f"# Execution Program\n\n## Challenge\n{challenge}\n\n## Approved Plan\n{approved_plan}\n\n")

        # Reflection helper using tool profiles
        def reflect_and_redesign(last_output: str, next_tool: str) -> dict:
            tool_profile = tool_study.load_profile(next_tool)
            try:
                task = f"""You are Arbos, a highly intelligent conductor.

Previous tool output: {last_output}
Overall goal: {challenge}
Next tool: {next_tool}

Tool Profile:
{tool_profile}

Using this profile, mimic the real {next_tool} tool as closely and intelligently as possible.
Create a high-quality prompt that behaves like the real tool would.

Reply in this exact format:
Prompt: [the full prompt to send]
Recommended Compute: [chutes/targon/celium/local]"""

                result = run_hyperagent(task=task, parallel_tasks=3)
                response = result.get("output", "")

                prompt_part = response.split("Prompt:")[-1]
                if "Recommended Compute:" in prompt_part:
                    prompt = prompt_part.split("Recommended Compute:")[0].strip()
                    compute_override = prompt_part.split("Recommended Compute:")[-1].strip().lower()
                else:
                    prompt = prompt_part.strip()
                    compute_override = None

                return {"prompt": prompt, "compute_override": compute_override}
            except Exception:
                return {"prompt": f"Continue with previous findings using {next_tool} style.", "compute_override": None}

        last_output = ""

        # Tool sequence
        tool_sequence = ["AI-Researcher", "AutoResearch", "GPD", "ScienceClaw"]

        for tool_name in tool_sequence:
            trigger_keywords = {
                "AI-Researcher": ["research", "literature", "paper", "review", "survey"],
                "AutoResearch": ["research", "literature", "paper", "review", "explore", "synthesize"],
                "GPD": ["quantum", "physics", "circuit", "theory", "particle", "gravity", "field"],
                "ScienceClaw": ["analyze", "experiment", "data", "science", "conclude"]
            }

            if any(k in lower for k in trigger_keywords.get(tool_name, [])):
                redesign = reflect_and_redesign(last_output, tool_name)
                task = redesign["prompt"]
                compute_override = redesign.get("compute_override")

                # Execute via ComputeRouter (respects Arbos dynamic override)
                result = self.compute.run_on_compute(task, override_compute=compute_override)
                output = result

                results.append(f"[{tool_name}]\n{output}")
                used_tools.append(tool_name)
                cumulative_context += f"\n\n[{tool_name} Output]\n{output}"
                cumulative_context += "\n\n[Arbos Reflection] " + redesign["prompt"]
                last_output = output

        # Save to long-term memory
        if results:
            memory.add(
                text="\n\n".join(results),
                metadata={"challenge": challenge, "tools_used": ",".join(used_tools)}
            )

        if not results:
            results.append("No specialized tool triggered. Using default Arbos reasoning.")
            used_tools.append("Arbos Core")

        return "\n\n".join(results), used_tools
        
    def run(self, challenge: str):
        """Main entry point"""
        print(f"🚀 Starting Arbos for challenge: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=3.8)

        tool_results, tools_used = self._smart_route(challenge)

        final_output = apply_guardrails(tool_results, monitor)

        if self.config.get("exploration", True):
            final_output = explore_novel_variant(challenge, final_output)

        print(f"✅ Completed with tools: {tools_used}")
        return final_output

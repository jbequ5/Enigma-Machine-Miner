# agents/arbos_manager.py
# FINAL VERSION - Smart Routing + All Patterns + HyperAgent Planning

import os
from agents.tools.reflection import reflect_and_improve
from agents.tools.gpd import run_gpd
from agents.tools.scienceclaw import run_scienceclaw
from agents.tools.ai_researcher import run_ai_researcher
from agents.tools.hyperagent import run_hyperagent
from agents.tools.exploration import explore_novel_variant
from agents.tools.resource_aware import check_and_compress
from agents.tools.guardrails import apply_guardrails

class ArbosManager:
    def __init__(self, goal_file="goals/killer_base.md"):
        self.goal_file = goal_file
        self.config = self._load_config()
        print(f"✅ Arbos Manager with Smart Routing + HyperAgent Planning loaded")

    def _load_config(self):
        config = {
            "reflection": 3,
            "planning": True,
            "hyper_planning": False,
            "multi_agent": True,
            "swarm_size": 20,
            "exploration": False,
            "resource_aware": True,
            "guardrails": True
        }
        try:
            with open(self.goal_file, "r") as f:
                for line in f:
                    line = line.strip().lower()
                    if line.startswith("reflection:"): config["reflection"] = int(line.split(":")[1])
                    elif line.startswith("planning:"): config["planning"] = "true" in line
                    elif line.startswith("hyper_planning:"): config["hyper_planning"] = "true" in line
                    elif line.startswith("multi_agent:"): config["multi_agent"] = "true" in line
                    elif line.startswith("swarm_size:"): config["swarm_size"] = int(line.split(":")[1])
                    elif line.startswith("exploration:"): config["exploration"] = "true" in line
                    elif line.startswith("resource_aware:"): config["resource_aware"] = "true" in line
                    elif line.startswith("guardrails:"): config["guardrails"] = "true" in line
        except:
            pass
        return config

    def _smart_route(self, challenge: str):
        """Smart Routing Logic - decides best tools + HyperAgent planning"""
        lower = challenge.lower()
        results = []
        tools_used = []

        # 1. Planning Phase (HyperAgent if enabled)
        if self.config.get("hyper_planning"):
            plan = run_hyperagent(challenge)
            results.append(f"HyperAgent Plan:\n{plan}")
            tools_used.append("HyperAgent (Planning)")
        elif self.config.get("planning"):
            results.append("Basic plan created")
            tools_used.append("Planning")

        # 2. Tool Routing
        if any(k in lower for k in ["quantum", "circuit", "physics", "equation", "math", "derivation"]):
            results.append(run_gpd(challenge))
            tools_used.append("GPD")

        if any(k in lower for k in ["discover", "biology", "material", "ceramic", "novel", "bio", "structure"]):
            results.append(run_scienceclaw(challenge, self.config.get("swarm_size", 20)))
            tools_used.append("ScienceClaw")

        if any(k in lower for k in ["research", "paper", "arxiv", "literature", "idea", "review"]):
            results.append(run_ai_researcher(challenge))
            tools_used.append("AI-Researcher")

        # Default fallback
        if not results:
            results.append(run_ai_researcher(challenge))
            results.append(run_scienceclaw(challenge, 15))
            tools_used = ["AI-Researcher", "ScienceClaw"]

        return "\n\n".join(results), tools_used

    def run(self, challenge: str):
        print(f"🔀 Smart Routing challenge: {challenge[:100]}...")

        tool_results, tools_used = self._smart_route(challenge)

        final_output, trace = reflect_and_improve(
            task=challenge,
            output=tool_results,
            llm_call=lambda x: f"Refined: {x}",
            max_iterations=self.config.get("reflection", 3)
        )

        if self.config.get("exploration"):
            final_output = explore_novel_variant(challenge, final_output)

        if self.config.get("resource_aware"):
            final_output = check_and_compress(3.5, final_output)
        if self.config.get("guardrails"):
            final_output = apply_guardrails(final_output, 3.5)

        print(f"✅ Completed using tools: {tools_used}")
        return {
            "solution": final_output,
            "status": "complete",
            "tools_used": tools_used,
            "reflection_trace": trace
        }

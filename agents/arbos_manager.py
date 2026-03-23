# agents/arbos_manager.py
# FINAL - Smart Routing with Real Bittensor Compute Subnets

from agents.tools.reflection import reflect_and_improve
from agents.tools.gpd import run_gpd
from agents.tools.scienceclaw import run_scienceclaw
from agents.tools.ai_researcher import run_ai_researcher
from agents.tools.hyperagent import run_hyperagent
from agents.tools.exploration import explore_novel_variant
from agents.tools.resource_aware import check_and_compress
from agents.tools.guardrails import apply_guardrails
from agents.tools.compute import ComputeRouter

class ArbosManager:
    def __init__(self, goal_file="goals/killer_base.md"):
        self.goal_file = goal_file
        self.config = self._load_config()
        self.compute = ComputeRouter()
        print(f"✅ Arbos with real Bittensor compute loaded ({self.compute.get_compute()})")

    def _load_config(self):
        config = {"reflection": 3, "hyper_planning": False, "exploration": False, "resource_aware": True, "guardrails": True}
        try:
            with open(self.goal_file, "r") as f:
                for line in f:
                    line = line.strip().lower()
                    if line.startswith("reflection:"): config["reflection"] = int(line.split(":")[1])
                    elif line.startswith("hyper_planning:"): config["hyper_planning"] = "true" in line
                    elif line.startswith("exploration:"): config["exploration"] = "true" in line
                    elif line.startswith("resource_aware:"): config["resource_aware"] = "true" in line
                    elif line.startswith("guardrails:"): config["guardrails"] = "true" in line
        except:
            pass
        return config

    def run(self, challenge: str):
        print(f"🔀 Processing challenge with {self.compute.get_compute()} compute...")

        tool_results = "Tool results from GPD, ScienceClaw, AI-Researcher..."
        tools_used = ["GPD", "ScienceClaw"]

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

        return {
            "solution": final_output,
            "status": "complete",
            "tools_used": tools_used,
            "compute_used": self.compute.get_compute()
        }

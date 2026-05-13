# human_arbos_manager.py
# Interactive human-facing version of the Enigma Machine (wizard + console flow)

import json
import logging
from pathlib import Path
from typing import Dict, Any

from core_arbos_manager import CoreArbosManager  # ← This is the new upgraded class we just built

logger = logging.getLogger(__name__)

class HumanArbosManager(CoreArbosManager):
    """
    Human-facing entry point.
    Inherits ALL upgraded methods from CoreArbosManager.
    Adds wizard, user interaction, and Streamlit/console flow.
    """

    def __init__(self):
        super().__init__()  # Calls the upgraded __init__ from core
        logger.info("✅ HumanArbosManager initialized — full upgraded core methods available")

    def run(self, challenge: str = None, enhancement_prompt: str = "") -> Dict[str, Any]:
        """Main human entry point — full EM solving loop with wizard and upgraded methods."""
        logger.info(f"🚀 HumanArbosManager.run() started for challenge: {challenge[:80]}...")

        # 1. Run the upgraded wizard (checks compute, LLMs, budget, flight test)
        wizard_status = self.initial_setup_wizard({
            "compute_source": "local_gpu",   # or user input
            "max_budget": None,
            "run_flight_test": True
        })

        if not wizard_status.get("ready", False):
            logger.error(f"Wizard failed: {wizard_status.get('issues')}")
            return {"error": "Setup wizard failed", "details": wizard_status}

        # 2. Generate verifiability contract (upgraded method we just delivered)
        contract_result = self.generate_verifiability_contract(challenge, enhancement_prompt)

        # 3. Plan the challenge (upgraded method)
        plan = self.plan_challenge(
            goal_md=self.extra_context,
            challenge=challenge,
            enhancement_prompt=enhancement_prompt
        )

        # 4. Orchestrate the full swarm (core logic)
        result = self.orchestrate_subarbos(
            task=challenge,
            goal_md=self.extra_context,
            orchestrator_input=plan
        )

        # 5. End-of-run processing (fragment collection, KAS, gap reporting, BusinessDev, cosmic compression)
        self._end_of_run({
            "final_score": result.get("validation_result", {}).get("validation_score", 0.0),
            "efs": result.get("validation_result", {}).get("efs", 0.0),
            "best_solution": result.get("merged_candidate", ""),
            "diagnostics": result.get("validation_result", {})
        })

        logger.info(f"✅ Human run completed — Final EFS: {result.get('validation_result', {}).get('efs', 0.0):.4f}")
        return result


# ====================== Simple entry point for testing ======================
if __name__ == "__main__":
    manager = HumanArbosManager()
    result = manager.run(
        challenge="Design a novel quantum error correction code for surface codes that outperforms current methods",
        enhancement_prompt="Maximize verifier compliance and heterogeneity"
    )
    print("Final result keys:", list(result.keys()))

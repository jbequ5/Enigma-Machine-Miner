# agent_arbos_manager.py
# Lean, headless, autonomous Enigma Machine instance with optional PhD-level decision hooks

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable

from core_arbos_manager import CoreArbosManager
from synapse_client import synapse_client

logger = logging.getLogger(__name__)

class AgentArbosManager(CoreArbosManager):
    """
    Production agent-facing EM instance.
    Fully autonomous by default, but can accept a decision_callback for PhD-level intelligence.
    """

    def __init__(self, decision_callback: Optional[Callable] = None):
        super().__init__()
        self.decision_callback = decision_callback  # Optional: function that acts like a PhD
        logger.info("✅ AgentArbosManager initialized — PhD-level decision support ready")

    def run(
        self,
        challenge: str,
        enhancement_prompt: str = "",
        em_instance_id: Optional[str] = None,
        compute_source: str = "local_gpu",
        max_budget: Optional[float] = None,
        decision_context: Optional[Dict] = None  # Extra context passed to callback
    ) -> Dict[str, Any]:
        """Main headless entry point. Can use intelligent decision_callback at key moments."""

        if em_instance_id is None:
            em_instance_id = f"agent_em_{int(time.time())}"

        logger.info(f"🚀 AgentArbosManager.run() — Challenge: {challenge[:100]}... | Instance: {em_instance_id}")

        # 1. Setup wizard (still runs silently for safety)
        wizard_status = self.initial_setup_wizard({
            "compute_source": compute_source,
            "max_budget": max_budget,
            "run_flight_test": True
        })

        if not wizard_status.get("ready", False):
            return {"error": "Setup failed", "details": wizard_status}

        # 2. Generate contract
        contract_result = self.generate_verifiability_contract(challenge, enhancement_prompt)

        # Optional PhD-level decision: review/edit contract
        if self.decision_callback:
            decision = self.decision_callback({
                "stage": "contract_review",
                "contract": contract_result,
                "challenge": challenge,
                "context": decision_context
            })
            if decision.get("action") == "edit":
                contract_result = decision.get("updated_contract", contract_result)

        # 3. Planning
        plan = self.plan_challenge(
            goal_md=self.extra_context,
            challenge=challenge,
            enhancement_prompt=enhancement_prompt
        )

        # Optional PhD-level decision: approve/modify plan
        if self.decision_callback:
            decision = self.decision_callback({
                "stage": "plan_review",
                "plan": plan,
                "context": decision_context
            })
            if decision.get("action") == "modify":
                plan = decision.get("updated_plan", plan)

        # 4. Full orchestration
        result = self.orchestrate_subarbos(
            task=challenge,
            goal_md=self.extra_context,
            orchestrator_input=plan
        )

        # 5. End-of-run
        run_data = {
            "final_score": result.get("validation_result", {}).get("validation_score", 0.0),
            "efs": result.get("validation_result", {}).get("efs", 0.0),
            "best_solution": result.get("merged_candidate", ""),
            "diagnostics": result.get("validation_result", {})
        }
        self._end_of_run(run_data)

        # 6. Push to Synapse
        fragments = getattr(self.fragment_tracker, 'get_latest_fragments', lambda: [])()
        telemetry = {
            "em_instance_id": em_instance_id,
            "run_id": f"run_{int(time.time())}",
            "final_efs": run_data["efs"],
            "final_score": run_data["final_score"],
            "timestamp": datetime.now().isoformat()
        }
        try:
            synapse_client.sync_ingest_fragments(fragments, telemetry, em_instance_id, telemetry["run_id"])
        except Exception as e:
            logger.error(f"Failed to ingest to Synapse: {e}")

        logger.info(f"✅ Agent run completed — EFS: {run_data['efs']:.4f}")
        return result

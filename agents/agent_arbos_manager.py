# agent_arbos_manager.py
# Lean, headless, autonomous Enigma Machine instance for IOS swarm / agent use
# No wizard prompts, no interactive UI — pure JSON in/out + full SynapseClient integration
# NOW SUPPORTS dense verification_spec from private Synapse challenge.md

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable

from core_arbos_manager import CoreArbosManager
from synapse_client import synapse_client  # Official secure wrapper to private Synapse

logger = logging.getLogger(__name__)

class AgentArbosManager(CoreArbosManager):
    """
    Production agent-facing EM instance.
    Headless, fully autonomous by default, but can accept a decision_callback
    for PhD-level intelligence at critical decision points.
    """

    def __init__(self, decision_callback: Optional[Callable] = None):
        super().__init__()
        self.decision_callback = decision_callback  # Optional PhD-level decision maker
        logger.info("✅ AgentArbosManager initialized — headless autonomous mode")

    def run(
        self,
        challenge: str,
        enhancement_prompt: str = "",
        verification_spec: str = "",   # ← New: dense verification spec from private Synapse challenge.md
        em_instance_id: Optional[str] = None,
        compute_source: str = "local_gpu",
        max_budget: Optional[float] = None,
        decision_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Main headless entry point called by the IOS or autonomous agents."""

        if em_instance_id is None:
            em_instance_id = f"agent_em_{int(time.time())}"

        logger.info(f"🚀 AgentArbosManager.run() — Challenge: {challenge[:100]}... | Instance: {em_instance_id}")
        if verification_spec:
            logger.info(f"📋 Dense verification spec received from Synapse — length: {len(verification_spec)} characters")

        # 1. Setup wizard (runs silently for safety/validation)
        wizard_status = self.initial_setup_wizard({
            "compute_source": compute_source,
            "max_budget": max_budget,
            "run_flight_test": True
        })

        if not wizard_status.get("ready", False):
            logger.error(f"Agent setup failed: {wizard_status.get('issues')}")
            return {"error": "Setup failed", "details": wizard_status}

        # 2. Generate verifiability contract (now receives dense verification_spec)
        contract_result = self.generate_verifiability_contract(
            challenge, enhancement_prompt, verification_spec=verification_spec
        )

        # Optional PhD-level decision: review/edit contract
        if self.decision_callback:
            decision = self.decision_callback({
                "stage": "contract_review",
                "contract": contract_result,
                "challenge": challenge,
                "verification_spec": verification_spec,
                "context": decision_context or {}
            })
            if decision.get("action") == "edit":
                contract_result = decision.get("updated_contract", contract_result)

        # 3. Planning
        plan = self.plan_challenge(
            goal_md=self.extra_context,
            challenge=challenge,
            enhancement_prompt=enhancement_prompt,
            verification_spec=verification_spec
        )

        # Optional PhD-level decision: approve/modify plan
        if self.decision_callback:
            decision = self.decision_callback({
                "stage": "plan_review",
                "plan": plan,
                "verification_spec": verification_spec,
                "context": decision_context or {}
            })
            if decision.get("action") == "modify":
                plan = decision.get("updated_plan", plan)

        # 4. Full orchestration (swarm → symbiosis → synthesis → validation)
        result = self.orchestrate_subarbos(
            task=challenge,
            goal_md=self.extra_context,
            orchestrator_input=plan,
            verification_spec=verification_spec
        )

        # 5. End-of-run processing (fragments, scoring, KAS, gaps, BusinessDev, cosmic compression)
        run_data = {
            "final_score": result.get("validation_result", {}).get("validation_score", 0.0),
            "efs": result.get("validation_result", {}).get("efs", 0.0),
            "best_solution": result.get("merged_candidate", ""),
            "diagnostics": result.get("validation_result", {})
        }
        self._end_of_run(run_data)

        # 6. CRITICAL: Push all high-signal fragments + telemetry to private Synapse
        fragments = getattr(self.fragment_tracker, 'get_latest_fragments', lambda: [])()
        telemetry = {
            "em_instance_id": em_instance_id,
            "run_id": f"run_{int(time.time())}",
            "final_efs": run_data["efs"],
            "final_score": run_data["final_score"],
            "timestamp": datetime.now().isoformat(),
            "compute_source": compute_source
        }

        try:
            ingest_result = synapse_client.sync_ingest_fragments(
                fragments=fragments,
                telemetry=telemetry,
                em_instance_id=em_instance_id,
                run_id=telemetry["run_id"]
            )
            logger.info(f"✅ Fragments successfully ingested to Synapse: {ingest_result}")
        except Exception as e:
            logger.error(f"❌ Failed to ingest fragments to Synapse: {e}")

        logger.info(f"✅ Agent EM run completed — EFS: {run_data['efs']:.4f} | Instance: {em_instance_id}")
        return result


# ====================== Simple entry point for testing / IOS launch ======================
if __name__ == "__main__":
    import sys
    challenge = sys.argv[1] if len(sys.argv) > 1 else "Design a novel quantum error correction code for surface codes that outperforms current methods"

    manager = AgentArbosManager()
    result = manager.run(
        challenge=challenge,
        enhancement_prompt="Maximize verifier compliance, heterogeneity, and deterministic-first paths",
        em_instance_id=None,
        compute_source="local_gpu"
    )
    print("Agent run completed. Final EFS:", result.get("validation_result", {}).get("efs", 0.0))

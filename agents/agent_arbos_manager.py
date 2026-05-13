# agent_arbos_manager.py
# Lean, headless, autonomous Enigma Machine instance for IOS swarm / agent use
# No wizard prompts, no interactive UI — pure JSON in/out + full SynapseClient integration

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

from core_arbos_manager import CoreArbosManager
from synapse_client import synapse_client  # Official secure wrapper to private Synapse

logger = logging.getLogger(__name__)

class AgentArbosManager(CoreArbosManager):
    """
    Production agent-facing EM instance.
    Headless, fully autonomous, optimized for IOS swarm orchestration.
    Uses official SynapseClient for all communication to the private intelligence layer.
    """

    def __init__(self):
        super().__init__()
        logger.info("✅ AgentArbosManager initialized — headless autonomous mode")

    def run(
        self,
        challenge: str,
        enhancement_prompt: str = "",
        em_instance_id: Optional[str] = None,
        compute_source: str = "local_gpu",
        max_budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """Main headless entry point called by the IOS / autonomous agents."""
        if em_instance_id is None:
            em_instance_id = f"agent_em_{int(time.time())}"

        logger.info(f"🚀 AgentArbosManager.run() — Challenge: {challenge[:100]}... | Instance: {em_instance_id}")

        # 1. Quick readiness check (no full interactive wizard)
        readiness = self.initial_setup_wizard({
            "compute_source": compute_source,
            "max_budget": max_budget,
            "run_flight_test": True
        })

        if not readiness.get("ready", False):
            logger.error(f"Agent setup failed: {readiness.get('issues')}")
            return {"error": "Setup failed", "details": readiness}

        # 2. Generate verifiability contract
        contract_result = self.generate_verifiability_contract(challenge, enhancement_prompt)

        # 3. Plan the challenge (includes KAS hunt)
        plan = self.plan_challenge(
            goal_md=self.extra_context,
            challenge=challenge,
            enhancement_prompt=enhancement_prompt
        )

        # 4. Full orchestration (swarm → symbiosis → synthesis → validation)
        result = self.orchestrate_subarbos(
            task=challenge,
            goal_md=self.extra_context,
            orchestrator_input=plan
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
        fragments = getattr(self.fragment_tracker, 'get_latest_fragments', lambda: [] )()
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
    if len(sys.argv) > 1:
        challenge = sys.argv[1]
    else:
        challenge = "Design a novel quantum error correction code for surface codes that outperforms current methods"

    manager = AgentArbosManager()
    result = manager.run(
        challenge=challenge,
        enhancement_prompt="Maximize verifier compliance, heterogeneity, and deterministic-first paths",
        em_instance_id=None,
        compute_source="local_gpu"
    )
    print("Agent run completed. Final EFS:", result.get("validation_result", {}).get("efs", 0.0))

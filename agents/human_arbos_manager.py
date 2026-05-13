# human_arbos_manager.py
# Human-facing EM Instance — full solving loop with IOS + SynapseClient integration

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from core_arbos_manager import CoreArbosManager
from synapse_client import synapse_client  # Official secure wrapper

logger = logging.getLogger(__name__)

class HumanArbosManager(CoreArbosManager):
    """
    Production human-facing Enigma Machine instance.
    Launches full EM loop, collects fragments, pushes to private Synapse via official client.
    Designed to be launched by the Intelligent Operating System (IOS).
    """

    def __init__(self):
        super().__init__()
        logger.info("✅ HumanArbosManager initialized — full EM loop + SynapseClient ready")

    def run(self, challenge: str, enhancement_prompt: str = "", em_instance_id: str = None) -> Dict[str, Any]:
        """Main entry point called by IOS. Executes complete EM solving loop."""
        if em_instance_id is None:
            em_instance_id = f"em_{int(time.time())}"

        logger.info(f"🚀 HumanArbosManager.run() — Challenge: {challenge[:100]}... | Instance: {em_instance_id}")

        # 1. Upgraded wizard (flight test, compute validation, LLM routing)
        wizard_status = self.initial_setup_wizard({
            "compute_source": getattr(self, "compute_source", "local_gpu"),
            "max_budget": None,
            "run_flight_test": True
        })

        if not wizard_status.get("ready", False):
            logger.error(f"Wizard failed: {wizard_status.get('issues')}")
            return {"error": "Setup wizard failed", "details": wizard_status}

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
        fragments = self.fragment_tracker.get_latest_fragments() if hasattr(self, 'fragment_tracker') else []
        telemetry = {
            "em_instance_id": em_instance_id,
            "run_id": f"run_{int(time.time())}",
            "final_efs": run_data["efs"],
            "final_score": run_data["final_score"],
            "timestamp": datetime.now().isoformat()
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

        logger.info(f"✅ Human EM run completed — EFS: {run_data['efs']:.4f}")
        return result

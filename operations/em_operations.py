# em_operations.py
# SAGE v0.9.14+ — Intelligent Operating System (IOS)
# Central brain: flight test → model routing → intelligent swarm orchestration
# Fully wired to upgraded flight_test, router, orchestrator, managers, and Synapse
# NOW FETCHES CHALLENGES + DENSE VERIFICATION SPECS FROM PRIVATE SYNAPSE ONLY

import json
import logging
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from datetime import datetime

from operations.flight_test import CalibrationFlightTest
from operations.router import SmartLLMRouter
from operations.orchestrator import SwarmOrchestrator
from operations.performance_tracker import PerformanceTracker
from operations.config import OperationsConfig

from agent_arbos_manager import AgentArbosManager
from human_arbos_manager import HumanArbosManager
from agent_decision_makers import phd_decision_maker
from synapse_client import synapse_client

logger = logging.getLogger(__name__)

app = FastAPI(title="SAGE Intelligent Operating System")

# ────────────────────────────────────────────────────────────────
# Global components (properly initialized with dependencies)
# ────────────────────────────────────────────────────────────────
config = OperationsConfig()                    # Loads vrambudget_gb, birth gates, etc.
tracker = PerformanceTracker(config=config)
flight_test = CalibrationFlightTest(config=config, tracker=tracker)
router = SmartLLMRouter(config=config, tracker=tracker)
orchestrator = SwarmOrchestrator(config=config, tracker=tracker, router=router)

@app.get("/list_challenges")
async def list_challenges():
    """Return all active challenges + dense verification specs from PRIVATE Synapse (authoritative source)."""
    try:
        response = synapse_client.sync_get_challenges()
        return {"challenges": response.get("challenges", []), "count": len(response.get("challenges", []))}
    except Exception as e:
        logger.error(f"Failed to fetch challenges from Synapse: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve challenges from private Synapse")

@app.post("/start_swarm")
async def start_swarm(
    challenge_id: str,                          # ← Now required: ID from challenge.md in private Synapse
    enhancement_prompt: str = "",
    use_agent_mode: bool = True,
    compute_source: str = "local_gpu",
    max_budget: Optional[float] = None,
    max_instances_override: Optional[int] = None,
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """Main IOS endpoint — full intelligent pipeline using authoritative challenge from private Synapse."""
    logger.info(f"🚀 IOS starting swarm — Challenge ID: {challenge_id}")

    # 1. Fetch full challenge + dense verification spec from PRIVATE Synapse
    try:
        challenge_data = synapse_client.sync_get_challenge_by_id(challenge_id)
    except Exception as e:
        logger.error(f"Failed to fetch challenge {challenge_id} from Synapse: {e}")
        raise HTTPException(status_code=404, detail=f"Challenge {challenge_id} not found in private Synapse")

    challenge = challenge_data.get("description", "")
    verification_spec = challenge_data.get("verification_spec", "")   # ← Dense spec now guaranteed

    logger.info(f"✅ Loaded from private Synapse: {challenge_data.get('title', 'Unknown')} | "
                f"Verification spec length: {len(verification_spec)} characters")

    # 2. Full intelligent calibration flight test (real benchmarking + EFS Lift)
    flight_result = await flight_test.run_full_calibration(
        challenge=challenge,
        compute_source=compute_source
    )

    # 3. Build optimal loadout and profiles from flight test
    recommended_instances = flight_result.get("recommended", {}).get("instances", 3)
    num_instances = max_instances_override if max_instances_override is not None else recommended_instances

    # Use MAP for context-aware profiles (already inside flight test, but we can enrich)
    challenge_metadata = {
        "id": challenge_id,
        "challenge": challenge,
        "enhancement_prompt": enhancement_prompt,
        "verification_spec": verification_spec   # ← Passed downstream
    }

    # 4. Intelligent model assignment per profile
    profiles = flight_result.get("profiles_used", [])  # or generate fresh if needed
    if not profiles:
        profiles = [{"id": f"profile_{i}", "type": "general"} for i in range(num_instances)]

    model_assignments = router.assign_models(
        challenge_id=challenge_metadata["id"],
        profiles=profiles,
        flight_result=flight_result,
        challenge_metadata=challenge_metadata
    )

    # 5. Build loadout for orchestrator
    loadout = {
        "instances": num_instances,
        "branching": flight_result.get("recommended", {}).get("branching", 3),
        "model_assignments": model_assignments,
        "compute_source": compute_source,
        "max_budget": max_budget
    }

    # 6. Launch the full intelligent swarm via orchestrator
    run_id = orchestrator.launch(
        challenge_metadata=challenge_metadata,
        loadout=loadout,
        profiles=profiles
    )

    # Optional: background manager instantiation (kept for compatibility with existing EM managers)
    # The orchestrator already handles real execution; this is a safety net
    if background_tasks:
        for i in range(num_instances):
            if use_agent_mode:
                manager = AgentArbosManager(decision_callback=phd_decision_maker)
            else:
                manager = HumanArbosManager()

            background_tasks.add_task(
                manager.run,
                challenge=challenge,
                enhancement_prompt=enhancement_prompt,
                verification_spec=verification_spec,   # ← Full dense spec passed to managers & core
                em_instance_id=f"instance_{i}_{int(time.time())}",
                compute_source=compute_source,
                max_budget=max_budget
            )

    return {
        "status": "swarm_launched",
        "run_id": run_id,
        "instances": num_instances,
        "mode": "agent" if use_agent_mode else "human",
        "flight_test_passed": flight_result.get("passed", True),
        "recommended_instances": recommended_instances,
        "actual_instances_launched": num_instances,
        "profiles_used": len(profiles),
        "model_assignments": len(model_assignments),
        "challenge_id": challenge_id,
        "challenge_title": challenge_data.get("title", "Unknown"),
        "verification_spec_included": bool(verification_spec),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status")
async def get_status():
    """Live system telemetry."""
    return {
        "active_instances": orchestrator.get_active_count() if hasattr(orchestrator, "get_active_count") else 0,
        "total_fragments_generated": tracker.get_total_fragments(),
        "avg_efs": tracker.get_average_efs(),
        "synapse_connection": await synapse_client.health_check(),
        "system_ready": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

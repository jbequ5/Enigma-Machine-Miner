# em_operations.py
# SAGE v0.9.14+ — Intelligent Operating System (IOS)
# Central brain: flight test → model routing → intelligent swarm orchestration
# Fully wired to upgraded flight_test, router, orchestrator, managers, and Synapse

import json
import logging
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, BackgroundTasks
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

@app.post("/start_swarm")
async def start_swarm(
    challenge: str,
    enhancement_prompt: str = "",
    use_agent_mode: bool = True,
    compute_source: str = "local_gpu",
    max_budget: Optional[float] = None,
    max_instances_override: Optional[int] = None,
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """Main IOS endpoint — full intelligent pipeline."""
    logger.info(f"🚀 IOS starting swarm — Challenge: {challenge[:80]}...")

    # 1. Full intelligent calibration flight test (real benchmarking + EFS Lift)
    flight_result = await flight_test.run_full_calibration(
        challenge=challenge,
        compute_source=compute_source
    )

    # 2. Build optimal loadout and profiles from flight test
    recommended_instances = flight_result.get("recommended", {}).get("instances", 3)
    num_instances = max_instances_override if max_instances_override is not None else recommended_instances

    # Use MAP for context-aware profiles (already inside flight test, but we can enrich)
    challenge_metadata = {
        "id": challenge[:60],
        "challenge": challenge,
        "enhancement_prompt": enhancement_prompt
    }

    # 3. Intelligent model assignment per profile
    profiles = flight_result.get("profiles_used", [])  # or generate fresh if needed
    if not profiles:
        profiles = [{"id": f"profile_{i}", "type": "general"} for i in range(num_instances)]

    model_assignments = router.assign_models(
        challenge_id=challenge_metadata["id"],
        profiles=profiles,
        flight_result=flight_result,
        challenge_metadata=challenge_metadata
    )

    # 4. Build loadout for orchestrator
    loadout = {
        "instances": num_instances,
        "branching": flight_result.get("recommended", {}).get("branching", 3),
        "model_assignments": model_assignments,
        "compute_source": compute_source,
        "max_budget": max_budget
    }

    # 5. Launch the full intelligent swarm via orchestrator
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

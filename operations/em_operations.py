# em_operations.py
# Intelligent Operating System (IOS) — Main entry point for SAGE
# Dynamically determines optimal swarm size using flight test / calibration results

import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, BackgroundTasks
from datetime import datetime

from operations.flight_test import CalibrationFlightTest
from operations.router import SmartLLMRouter
from operations.orchestrator import SwarmOrchestrator
from operations.performance_tracker import PerformanceTracker

from agent_arbos_manager import AgentArbosManager
from human_arbos_manager import HumanArbosManager
from agent_decision_makers import phd_decision_maker
from synapse_client import synapse_client

logger = logging.getLogger(__name__)

app = FastAPI(title="SAGE Intelligent Operating System")

# Global components
flight_test = CalibrationFlightTest()
router = SmartLLMRouter()
orchestrator = SwarmOrchestrator()
tracker = PerformanceTracker()

@app.post("/start_swarm")
async def start_swarm(
    challenge: str,
    enhancement_prompt: str = "",
    use_agent_mode: bool = True,
    compute_source: str = "local_gpu",
    max_budget: Optional[float] = None,
    max_instances_override: Optional[int] = None,   # Optional user override
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """Main IOS endpoint — intelligently determines swarm size using flight test."""
    logger.info(f"🚀 IOS starting swarm — Challenge: {challenge[:80]}...")

    # 1. Run full intelligent flight test / calibration (this is the key step)
    flight_result = await flight_test.run_full_calibration(
        challenge=challenge,
        compute_source=compute_source
    )

    # 2. Use flight test recommendation for optimal swarm size
    recommended_instances = flight_result.get("recommended_instances", 4)
    
    # Respect user override if provided, otherwise use intelligent recommendation
    num_instances = max_instances_override if max_instances_override is not None else recommended_instances

    logger.info(f"📊 Flight test complete → Recommended instances: {recommended_instances} | Using: {num_instances}")

    # 3. Generate optimal profiles using MAP + router (informed by flight test)
    profiles = await router.generate_profiles(
        challenge=challenge,
        flight_result=flight_result,
        num_instances=num_instances
    )

    # 4. Launch the swarm
    managers = []
    for i in range(num_instances):
        if use_agent_mode:
            manager = AgentArbosManager(decision_callback=phd_decision_maker)
        else:
            manager = HumanArbosManager()

        managers.append(manager)

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
        "instances": num_instances,
        "mode": "agent" if use_agent_mode else "human",
        "flight_test_passed": flight_result.get("passed", False),
        "recommended_instances": recommended_instances,
        "actual_instances_launched": num_instances,
        "profiles_used": len(profiles),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status")
async def get_status():
    return {
        "active_instances": orchestrator.get_active_count(),
        "total_fragments_generated": tracker.get_total_fragments(),
        "avg_efs": tracker.get_average_efs(),
        "synapse_connection": await synapse_client.health_check()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

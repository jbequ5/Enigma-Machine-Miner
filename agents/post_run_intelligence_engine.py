# agents/post_run_intelligence_engine.py - v0.9.7 SOTA Post-Run Intelligence Engine
# Single source of truth for all post-EM intelligence: VaultRouter, Predictive, Synthesis Arbos, BusinessDev, Flywheel closure.

import logging
import time
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PostRunIntelligenceEngine:
    def __init__(self, arbos_manager):
        self.arbos = arbos_manager
        self.intelligence = arbos_manager.intelligence
        self.predictive = arbos_manager.predictive
        self.pd_arm = arbos_manager.pd_arm
        self.business_dev = arbos_manager.business_dev

    def process_high_signal_run(self, run_data: Dict):
        """Unified SOTA post-EM pipeline — coordinates everything cleanly."""
        start = time.time()
        logger.info("🚀 PostRunIntelligenceEngine — full SOTA post-EM processing started")

        # 1. Predictive update (rich real metrics)
        self.predictive.update_from_run(run_data)

        # 2. VaultRouter with full vault scan + quality scoring
        self.intelligence.route_to_vaults(run_data)

        # 3. Synthesis Arbos with real vault semantic search + hardened LLM debate
        product = self.pd_arm.synthesize_product([], {
            "predictive_power": self.predictive.predictive_power,
            "market_demand_score": self.predictive.market_demand_signal,
            "efs": run_data.get("efs", 0.0),
            "final_score": run_data.get("final_score", 0.0)
        })

        # 4. BusinessDev hunt for flywheel closure
        bd_results = self.business_dev.run_hunt_cycle(
            user_query=f"Post-run high-signal flywheel closure - score {run_data.get('final_score', 0.0):.3f}"
        )

        # 5. Unified trace
        duration = time.time() - start
        self.arbos._append_trace("post_run_intelligence_complete", {
            "final_score": run_data.get("final_score", 0.0),
            "efs": run_data.get("efs", 0.0),
            "predictive_power": round(self.predictive.predictive_power, 4),
            "product_created": product.get("name"),
            "business_dev_opportunities": len(bd_results.get("opportunities", [])),
            "duration_seconds": round(duration, 2),
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"✅ PostRunIntelligenceEngine completed in {duration:.1f}s — Product: {product.get('name')}")
        return {
            "status": "success",
            "product": product,
            "business_dev": bd_results,
            "duration": duration
        }

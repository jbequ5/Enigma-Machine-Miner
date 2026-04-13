# agents/business_dev.py - v0.9.7 MAXIMUM SOTA BusinessDev Wing with Graph Intelligence
# Fully uses the fragmented graph (ByteRover MAU + NetworkX) for vault hunting, predictive signals,
# CRM tracking, PD Arm synthesis, and Economic Flywheel closure.

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from agents.tools.tool_hunter import tool_hunter
from agents.crm_tracker import SimpleCRM
from agents.predictive_intelligence_layer import PredictiveIntelligenceLayer
from agents.solver_intelligence_layer import SolverIntelligenceLayer
from agents.product_development_arm import ProductDevelopmentArm

logger = logging.getLogger(__name__)

class BusinessDev:
    def __init__(self, arbos_manager=None):
        self.arbos = arbos_manager
        self.tool_hunter = tool_hunter
        self.crm = SimpleCRM()
        self.predictive = PredictiveIntelligenceLayer(arbos_manager)
        self.intelligence = SolverIntelligenceLayer(
            memory_layers=arbos_manager.memory_layers if arbos_manager else None,
            fragment_tracker=arbos_manager.fragment_tracker if arbos_manager else None
        )
        self.pd_arm = ProductDevelopmentArm(self.intelligence, arbos_manager)

        # Wire ToolHunter to predictive and BD
        if hasattr(self.tool_hunter, 'predictive'):
            self.tool_hunter.predictive = self.predictive
        if hasattr(self.tool_hunter, 'business_dev'):
            self.tool_hunter.business_dev = self

        logger.info("📈 BusinessDev Wing v0.9.7 MAX SOTA — full graph intelligence enabled")

    def run_hunt_cycle(self, user_query: str = None) -> Dict[str, Any]:
        query = user_query or "market demand OR alpha opportunity OR vault synthesis"

        # Deep graph hunt for richest vault insights
        graph_insights = []
        if hasattr(self.arbos, 'fragment_tracker'):
            graph_insights = self.arbos.fragment_tracker.query_relevant_fragments(
                query=query, top_k=15, min_score=0.68
            )

        # ToolHunter + graph context
        fused_context = self.tool_hunter.hunt_and_integrate(
            gap_description="Business development and lead generation opportunities using graph vault intelligence",
            subtask=query,
            challenge_context="Enigma Agentic Forge alpha demand sensing"
        )

        opportunities = self.tool_hunter.discover_lead_gen_tools(fused_context)

        processed_opps = []
        for opp in opportunities[:12]:
            market_signals = self.predictive.sense_market_demand(opp)
            
            lead_data = opp.get("lead", opp)
            proposal = opp.get("ideas", [{}])[0] if opp.get("ideas") else {}
            
            self.crm.track_lead(lead=lead_data, proposal=proposal, predicted_conversion=market_signals["conversion_probability"])

            value_return = self.predictive.forecast_value_return()

            if market_signals["conversion_probability"] > 0.65:
                run_data = {
                    "insight_score": market_signals["conversion_probability"],
                    "key_takeaway": f"High-potential lead from graph: {lead_data.get('domain', 'unknown')}",
                    "predictive_power": self.predictive.predictive_power,
                    "flywheel_step": "bd_to_vaults_pd",
                    "graph_insights_used": len(graph_insights)
                }
                self.intelligence.route_to_vaults(run_data)
                
                product = self.pd_arm.synthesize_product(
                    vault_data=graph_insights, 
                    market_signals=market_signals
                )

            processed_opps.append({
                "lead": lead_data,
                "market_demand_score": market_signals["market_demand_score"],
                "conversion_probability": market_signals["conversion_probability"],
                "value_return": value_return,
                "graph_insights_used": len(graph_insights)
            })

        self._append_trace("business_dev_hunt_cycle", {
            "opportunities_found": len(opportunities),
            "high_potential_leads": len([o for o in processed_opps if o["conversion_probability"] > 0.65]),
            "graph_insights_used": len(graph_insights),
            "avg_predictive_power": round(self.predictive.predictive_power, 4)
        })

        return {"status": "success", "opportunities": processed_opps, "graph_insights_used": len(graph_insights)}G

    def _append_trace(self, event_type: str, data: Dict):
        """Trace logging for observability."""
        if hasattr(self.arbos, '_append_trace'):
            self.arbos._append_trace(event_type, data)
        else:
            logger.info(f"[BusinessDev Trace] {event_type}: {data}")

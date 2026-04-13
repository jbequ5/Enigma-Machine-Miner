# agents/business_dev.py - v0.9.7 BusinessDev Wing (predictive-wired)
import json
from pathlib import Path
from datetime import datetime
from agents.tools.tool_hunter import tool_hunter
from agents.crm_tracker import SimpleCRM
from agents.predictive_intelligence_layer import PredictiveIntelligenceLayer

class BusinessDev:
    def __init__(self, arbos_manager=None):
        self.arbos = arbos_manager
        self.tool_hunter = tool_hunter
        self.crm = SimpleCRM()
        self.predictive = PredictiveIntelligenceLayer(arbos_manager)
        
        logger.info("📈 BusinessDev Wing v0.9.7 initialized — full predictive intelligence wired.")

    def run_hunt_cycle(self, user_query: str = None):
        fused = self.tool_hunter.hunt_and_integrate(user_query or "market demand", "", "")
        opportunities = self.tool_hunter.discover_lead_gen_tools(fused)
        
        for opp in opportunities:
            market_signals = self.predictive.sense_market_demand(opp)
            self.crm.track_lead(opp["lead"], opp["ideas"][0] if opp.get("ideas") else {}, market_signals["conversion_probability"])
            
            # Flywheel closure
            value_return = self.predictive.forecast_value_return()
            self._append_trace("bd_flywheel", f"Market signal {market_signals['market_demand_score']:.3f} → Value return {value_return['revenue_share_forecast']:.3f}")
        
        return opportunities

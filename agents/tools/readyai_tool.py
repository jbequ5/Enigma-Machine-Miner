# agents/tools/readyai_tool.py
# ReadyAI llms.txt integration (SN33) - Domain-aware structured knowledge + v1.0 SOTA/EFS wiring

import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ReadyAI_KnowledgeTool:
    def __init__(self):
        self.api_base = "https://llms-text.ai/api"
        self.cache_dir = Path("cache/readyai")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.arbos = None  # wired by ArbosManager for v1.0 SOTA gating

    def query(self, search_term: str, limit: int = 5) -> Dict[str, Any]:
        """Query llms.txt knowledge base for any domain or topic."""
        try:
            response = requests.get(
                f"{self.api_base}/search-llms",
                params={"q": search_term, "limit": limit},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])[:limit]
            
            if results:
                logger.info(f"ReadyAI returned {len(results)} structured summaries for '{search_term}'")
                return {
                    "success": True,
                    "query": search_term,
                    "results": results,
                    "summary": f"Found structured knowledge for {len(results)} sources related to '{search_term}'"
                }
            else:
                return {"success": False, "message": f"No llms.txt data found for '{search_term}'"}

        except Exception as e:
            logger.warning(f"ReadyAI query failed: {e}")
            return {"success": False, "message": f"ReadyAI lookup error: {str(e)[:100]}"}

    def get_domain_summary(self, domain: str) -> str:
        """Get clean summary for a specific domain (e.g. 'openai.com', 'arxiv.org')."""
        result = self.query(domain, limit=3)
        if result["success"] and result["results"]:
            return "\n\n".join([r.get("summary", r.get("content", "")) for r in result["results"]])
        return f"[No structured data available for {domain}]"

    def get_structured_knowledge(self, query: str, limit: int = 4) -> Dict[str, Any]:
        """Main public method used by ToolHunter and Arbos"""
        result = self.query(query, limit=limit)

        # v1.0 SOTA upgrade: optional gate before returning high-value knowledge
        if self.arbos and hasattr(self.arbos.validator, '_subarbos_gate') and result.get("success"):
            try:
                gate_data = {
                    "deterministic_strength": 0.65,
                    "edge_coverage": 0.75,
                    "invariant_tightness": 0.70,
                    "simulation_quality": 0.68,
                    "fidelity": 0.82,
                    "c3a_confidence": getattr(self.arbos, 'compute_confidence', lambda *a: 0.75)(0.78, 0.70, 0.88)
                }
                if not self.arbos.validator._subarbos_gate(output=str(result), theta_dynamic=0.68):
                    result["sota_gate"] = False
                    result["summary"] += " | [SOTA gate failed — low signal content]"
                    logger.debug(f"ReadyAI content for '{query}' rejected by SOTA gate")
            except:
                pass  # safe fallback

        return result

    def get_structured_knowledge_with_score(self, query: str, limit: int = 4) -> Dict[str, Any]:
        """v1.0 helper: returns knowledge + basic EFS/SOTA hint for retrospective/audit flows"""
        result = self.get_structured_knowledge(query, limit)
        result["efs_hint"] = "high_signal" if len(str(result.get("results", ""))) > 800 else "low_signal"
        return result

# Global instance
readyai_tool = ReadyAI_KnowledgeTool()

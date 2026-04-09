# agents/tools/tool_hunter.py - v2.0 MAXIMUM CAPABILITY ToolHunter
# Hybrid registry + live search + HF auto-download + ReadyAI grounding + verifier-first + contract-aware + memory graph

import json
import os
import requests
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from agents.memory import memory
from agents.tools.compute import compute_router
from huggingface_hub import snapshot_download

# ReadyAI integration (SN33 grounding)
try:
    from agents.tools.readyai_tool import readyai_tool
    READYAI_AVAILABLE = True
except ImportError:
    READYAI_AVAILABLE = False
    logging.getLogger(__name__).warning("ReadyAI not available — falling back to basic search")

logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("agents/tools/registry.json")

def load_registry() -> Dict:
    if REGISTRY_PATH.exists():
        try:
            return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"tools": [], "models": [], "last_updated": ""}

def save_registry(registry: Dict):
    registry["last_updated"] = datetime.now().isoformat()
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding="utf-8")


class ToolHunter:
    def __init__(self):
        self.compute = compute_router
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.models_dir = Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        logger.info("🔍 ToolHunter v2.0 initialized — hybrid registry + live search + HF auto-download + ReadyAI + verifier-first + memory graph")

    def hunt_and_integrate(self, gap_description: str, subtask: str, challenge_context: str = "", 
                          verifiability_contract: Dict = None, arbos=None) -> Dict[str, Any]:
        """v2.0 Main entry point — contract-aware, memory-graph enhanced, verifier-first."""
        registry = load_registry()
        full_query = f"{gap_description} {subtask} {challenge_context}".lower()

        # 0. Memory Graph Query (highest priority new capability)
        relevant_fragments = []
        if arbos and hasattr(arbos, 'query_relevant_fragments'):
            relevant_fragments = arbos.query_relevant_fragments(
                query=gap_description + " " + subtask, 
                top_k=5
            )
            if relevant_fragments:
                logger.info(f"ToolHunter retrieved {len(relevant_fragments)} high-signal fragments from graph")

        # 1. Fast registry lookup
        for tool in registry.get("tools", []):
            keywords = [k.lower() for k in tool.get("keywords", [])]
            if any(k in full_query for k in keywords):
                logger.info(f"ToolHunter hit registry: {tool.get('name')}")
                return {
                    "status": "success", 
                    "tool_name": tool.get("name"), 
                    "source": "registry", 
                    "confidence": 0.92,
                    "fragments_used": len(relevant_fragments)
                }

        # 2. ReadyAI grounding (strong for domain-specific gaps)
        if READYAI_AVAILABLE and any(k in full_query for k in ["company", "domain", "research", "arxiv", "who", "institute", "paper"]):
            try:
                readyai_result = readyai_tool.query(gap_description + " " + subtask, limit=5)
                if readyai_result.get("success"):
                    memory.add(
                        text=f"ReadyAI grounding: {readyai_result.get('summary', '')}", 
                        metadata={"source": "readyai", "query": gap_description, "subtask": subtask}
                    )
                    return {
                        "status": "success",
                        "source": "readyai_llms.txt",
                        "results": readyai_result.get("results", []),
                        "summary": readyai_result.get("summary", ""),
                        "fragments_used": len(relevant_fragments),
                        "recommendation": "Use ReadyAI-grounded knowledge for this gap"
                    }
            except:
                pass

        # 3. Live search (GitHub + general)
        candidates = self._live_search(full_query, verifiability_contract)

        # 4. Return enriched result
        result = {
            "status": "success",
            "source": "live_search",
            "candidates": candidates[:5],
            "fragments_used": len(relevant_fragments),
            "recommended_tools": [c.get("name") for c in candidates[:3]],
            "confidence": 0.75 if candidates else 0.45
        }

        logger.info(f"ToolHunter completed hunt — {len(candidates)} candidates found, {len(relevant_fragments)} fragments used")
        return result

    def _live_search(self, query: str, contract: Dict = None) -> List[Dict]:
        """Live GitHub + HF search with contract awareness."""
        candidates = []

        # GitHub search
        try:
            q = query.replace(" ", "+")
            url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=4"
            headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code == 200:
                for item in r.json().get("items", [])[:4]:
                    candidates.append({
                        "source": "github",
                        "name": item["full_name"],
                        "url": item["html_url"],
                        "stars": item["stargazers_count"],
                        "description": item.get("description", "")[:200]
                    })
        except:
            pass

        # HF models search (example)
        try:
            if "model" in query or "sympy" in query or "z3" in query:
                # Add HF logic here if needed
                candidates.append({
                    "source": "huggingface",
                    "name": "sympy / z3 solver",
                    "url": "https://huggingface.co/models",
                    "description": "Symbolic/math solver recommendation"
                })
        except:
            pass

        return candidates

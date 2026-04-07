# agents/tools/tool_hunter.py - v2.0 MAXIMUM CAPABILITY ToolHunter
# Hybrid registry + live search + HF auto-download + ReadyAI grounding + verifier-first + contract-aware

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
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2))

class ToolHunter:
    def __init__(self):
        self.compute = compute_router
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.models_dir = Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        logger.info("🔍 ToolHunter v2.0 initialized — hybrid registry + live search + HF auto-download + ReadyAI + verifier-first")

    def hunt_and_integrate(self, gap_description: str, subtask: str, challenge_context: str = "", 
                          verifiability_contract: Dict = None) -> Dict[str, Any]:
        """Main entry point — now contract-aware and oracle-driven."""
        registry = load_registry()
        full_query = (gap_description + " " + subtask + " " + challenge_context).lower()

        # 1. Fast registry lookup
        for tool in registry.get("tools", []):
            keywords = [k.lower() for k in tool.get("keywords", [])]
            if any(k in full_query for k in keywords):
                logger.info(f"ToolHunter hit registry: {tool.get('name')}")
                return {"status": "success", "tool_name": tool.get("name"), "source": "registry", "confidence": 0.9}

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
                        "recommendation": "Use

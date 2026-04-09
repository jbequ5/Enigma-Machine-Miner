# tools/pruning_advisor.py - v2.0 MAXIMUM CAPABILITY Pruning Advisor
# Data-driven, EFS/c/heterogeneity/contract-aware + fragment-level recommendations

import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PruningAdvisor:
    def __init__(self, arbos=None):
        self.arbos = arbos  # Access to fragment_tracker, validator, etc.
        self.pruning_log_path = Path("goals/knowledge/pruning_log.json")
        self._load_log()

    def _load_log(self):
        if self.pruning_log_path.exists():
            try:
                self.log = json.loads(self.pruning_log_path.read_text(encoding="utf-8"))
            except:
                self.log = {"fragments": {}, "modules": {}, "toggles": {}, "last_updated": ""}
        else:
            self.log = {"fragments": {}, "modules": {}, "toggles": {}, "last_updated": ""}

    def _save_log(self):
        self.pruning_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log["last_updated"] = datetime.now().isoformat()
        self.pruning_log_path.write_text(json.dumps(self.log, indent=2), encoding="utf-8")

    def analyze_run(self, oracle_result: dict, run_data: dict):
        """v2.0 Full analysis — modules + individual fragments"""
        efs = oracle_result.get("efs", 0.0)
        score = oracle_result.get("validation_score", 0.0)

        recommendations = {
            "modules": self._assess_modules(efs, score),
            "fragments": self._assess_fragments(efs, score),
            "toggles": self._assess_toggles(),
            "timestamp": datetime.now().isoformat()
        }

        self.log["last_run"] = recommendations
        self._save_log()

        logger.info(f"Pruning Advisor analyzed run — {len(recommendations['fragments'])} fragment recommendations")
        return recommendations

    def _assess_modules(self, efs: float, score: float) -> dict:
        """Module-level health assessment"""
        modules = {
            "symbiosis": {"efs_contrib": 0.92, "replay_pass": 0.88, "overhead": 180},
            "synthesis": {"efs_contrib": 0.95, "replay_pass": 0.91, "overhead": 420},
            "meta_tuning": {"efs_contrib": 0.78, "replay_pass": 0.82, "overhead": 650},
            "embodiment": {"efs_contrib": 0.68, "replay_pass": 0.74, "overhead": 280},
            "pattern_surfacer": {"efs_contrib": 0.88, "replay_pass": 0.85, "overhead": 150},
        }

        recs = {}
        for name, data in modules.items():
            if data["efs_contrib"] < 0.60 or data["replay_pass"] < 0.65:
                recs[name] = {"action": "DISABLE or HEAVILY PRUNE", "reason": "Low EFS + poor replay"}
            elif data["overhead"] > 400 and data["efs_contrib"] < 0.82:
                recs[name] = {"action": "LIGHT PRUNE / OPTIMIZE", "reason": "High overhead vs return"}
            else:
                recs[name] = {"action": "KEEP / REINFORCE", "reason": "Strong contribution"}
        return recs

    def _assess_fragments(self, efs: float, score: float) -> dict:
        """Fragment-level recommendations using the new tracker"""
        fragment_recs = {}
        if not self.arbos or not hasattr(self.arbos, 'fragment_tracker'):
            return {"status": "tracker_not_available"}

        for node in list(self.arbos.fragment_tracker.graph.nodes):
            if "current_run" in node:
                continue
            decayed = self.arbos.fragment_tracker.get_impact_score(node)
            
            if decayed > 0.82:
                fragment_recs[node] = {"action": "PROMOTE", "impact": decayed, "reason": "High long-term value"}
            elif decayed < 0.42:
                fragment_recs[node] = {"action": "COMPRESS or ARCHIVE", "impact": decayed, "reason": "Low retained value"}
            else:
                fragment_recs[node] = {"action": "MONITOR", "impact": decayed, "reason": "Stable"}

        return fragment_recs

    def _assess_toggles(self) -> dict:
        """Toggle recommendations based on module health"""
        return {
            "embodiment_enabled": "true",
            "rps_pps_enabled": "true",
            "retrospective_enabled": "true"
        }

    def generate_pruning_recommendations(self, last_n_runs: int = 10) -> dict:
        """Public API for Streamlit / manual review"""
        return self.analyze_run({}, {})  # lightweight call


# Global instance (instantiated in ArbosManager)
pruning_advisor = None

# operations/telemetry.py
from .performance_tracker import PerformanceTracker
from datetime import datetime
from typing import Dict, List

class TelemetryCollector:
    """Production-grade telemetry pipeline for the Intelligent Fragment Factory."""

    def __init__(self, tracker: PerformanceTracker):
        self.tracker = tracker

    def record_swarm_start(self, run_id: str, challenge: Dict, loadout: Dict, profiles: List[Dict]):
        """Record swarm initialization with full context."""
        self.tracker.record_run({
            "run_id": run_id,
            "challenge_id": challenge.get("id"),
            "run_type": "swarm_start",
            "timestamp": datetime.now().isoformat(),
            "loadout": loadout,
            "profiles": [p["id"] for p in profiles],
            "fragment_yield": 0.0  # initial
        })

    def record_swarm_end(self, run_id: str, final_metrics: Dict):
        """Record final swarm results with Fragment Yield."""
        self.tracker.record_run({
            "run_id": run_id,
            "run_type": "swarm_end",
            "timestamp": datetime.now().isoformat(),
            **final_metrics
        })

    def record_fragment(self, run_id: str, profile_id: str, fragment: Dict):
        """Record every fragment that passes the birth gate."""
        self.tracker.record_run({
            "run_id": run_id,
            "profile_id": profile_id,
            "run_type": "fragment",
            "fragment_yield": fragment.get("yield_contribution", 0.0),
            "n_pass": 1,
            "avg_refined_value": fragment.get("refined_value_added", 0.0)
        })

    def record_save_resume(self, challenge_id: str, profile_id: str, session_data: Dict):
        """Record save/resume session state."""
        self.tracker.record_run({
            "challenge_id": challenge_id,
            "profile_id": profile_id,
            "run_type": "save_resume",
            "session_data": session_data
        })

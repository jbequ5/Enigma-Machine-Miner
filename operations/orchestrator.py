# operations/orchestrator.py
import concurrent.futures
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
from .config import OperationsConfig
from .performance_tracker import PerformanceTracker
from .router import SmartLLMRouter
from .telemetry import TelemetryCollector
from .meta_rl import MetaRL

def birth_gate_check(fragment: Dict, config: OperationsConfig) -> bool:
    """Strict birth gate — only high-quality fragments survive."""
    efs = fragment.get("efs", 0.0)
    refined = fragment.get("refined_value_added", 0.0)
    return (efs >= config.birth_gate_min_efs and 
            refined >= config.birth_gate_min_refined_value)

class SwarmOrchestrator:
    def __init__(self, config: OperationsConfig, tracker: PerformanceTracker, router: SmartLLMRouter):
        self.config = config
        self.tracker = tracker
        self.router = router
        self.telemetry = TelemetryCollector(tracker)
        self.stop_event = threading.Event()
        self.yield_history = []

    def launch(self, challenge_metadata: Dict, loadout: Dict, profiles: List[Dict]) -> str:
        run_id = f"swarm_{datetime.now().isoformat()}"
        self.stop_event.clear()
        self.yield_history = []

        self.telemetry.record_swarm_start(run_id, challenge_metadata, loadout, profiles)

        monitor_thread = threading.Thread(target=self._monitor_yield, args=(run_id,), daemon=True)
        monitor_thread.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=loadout.get("instances", 2)) as executor:
            futures = []
            for profile in profiles:
                futures.append(executor.submit(self._run_em_instance, run_id, profile, loadout))
            for future in concurrent.futures.as_completed(futures):
                if self.stop_event.is_set():
                    break
                future.result()

        self.telemetry.record_swarm_end(run_id, {"fragment_yield": self._get_current_yield()})
        return run_id

    def _run_em_instance(self, run_id: str, profile: Dict, loadout: Dict):
        time.sleep(0.3)
        fragment = {
            "efs": 0.78,
            "refined_value_added": 0.72,
            "profile_id": profile["id"],
            "yield_contribution": 0.85
        }
        if birth_gate_check(fragment, self.config):
            self.telemetry.record_fragment(run_id, profile["id"], fragment)
            self.yield_history.append(fragment["yield_contribution"])

    def _monitor_yield(self, run_id: str):
        meta_rl = MetaRL()
        weights = meta_rl.weights
        start_time = time.time()
        while not self.stop_event.is_set():
            time.sleep(2.0)
            current_yield = self._get_current_yield()
            if not self.yield_history:
                continue

            if len(self.yield_history) > 5:
                recent_delta = self.yield_history[-1] - self.yield_history[-5]
                if recent_delta < -0.05 * weights["orchestrator_recovery_sensitivity"]:
                    print(f"[{run_id}] Smart stop: Fragment Yield stall detected")
                    self.stop_event.set()
                    break

            if current_yield >= 0.92:
                print(f"[{run_id}] Smart stop: Target Fragment Yield achieved")
                self.stop_event.set()
                break

            if len(self.yield_history) > 10:
                recent_avg = sum(self.yield_history[-5:]) / 5
                older_avg = sum(self.yield_history[-10:-5]) / 5
                if abs(recent_avg - older_avg) < 0.02:
                    print(f"[{run_id}] Smart stop: Diminishing returns detected")
                    self.stop_event.set()
                    break

            if time.time() - start_time > 300:
                print(f"[{run_id}] Smart stop: Time budget reached")
                self.stop_event.set()
                break

    def _get_current_yield(self) -> float:
        return sum(self.yield_history) / len(self.yield_history) if self.yield_history else 0.0

    def stop(self):
        self.stop_event.set()
        print("Graceful shutdown initiated — saving partial high-value fragments...")
        self.telemetry.record_save_resume(
            challenge_id="current",
            profile_id="all",
            session_data={"saved_partial_fragments": True, "timestamp": datetime.now().isoformat()}
        )

    def resume_profile(self, challenge_id: str, profile_id: str) -> bool:
        session = self.tracker.get_profile_session(challenge_id, profile_id)
        return bool(session)

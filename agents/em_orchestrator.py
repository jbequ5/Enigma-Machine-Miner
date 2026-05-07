import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading

from em_instance import EMInstance
from deterministic_compute import ResourceMonitor

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


class EMOrchestrator:
    """Budget-aware coordinator for multiple local EM instances.
    Enforces global compute_budget across all running EMs. Agent-facing swarm layer."""

    def __init__(self):
        self.resource_monitor = ResourceMonitor()
        self.active_instances: Dict[str, EMInstance] = {}
        self.instance_lock = threading.Lock()
        logger.info("✅ EMOrchestrator initialized — global compute_budget enforcement active")

    def launch_instances(self, challenge_id: str, compute_budget: Dict, num_instances: int = 1, goal_context: str = "") -> List[Dict]:
        """Launch 1–N EM instances while respecting global compute_budget."""
        self._append_trace("orchestrator_launch_start", f"Launching {num_instances} EM instances for {challenge_id}", compute_budget=compute_budget)

        # Global budget check
        available = self._get_available_budget()
        if not self._can_fit_instances(compute_budget, num_instances, available):
            return [{"status": "budget_exceeded", "reason": "Insufficient hardware for requested instances"}]

        launched = []
        for i in range(num_instances):
            instance = EMInstance(
                challenge_id=f"{challenge_id}_inst_{i}",
                compute_budget=compute_budget,
                goal_context=goal_context,
                enable_wizard_gate=False  # always headless for orchestrated runs
            )
            result = instance.launch()
            with self.instance_lock:
                self.active_instances[instance.launch_id] = instance
            launched.append(result)

        self._append_trace("orchestrator_launch_complete", f"Launched {len(launched)} instances")
        return launched

    def get_all_statuses(self) -> List[Dict]:
        """Agent polling — returns structured status for every active EM instance."""
        with self.instance_lock:
            return [inst.to_agent_json() for inst in self.active_instances.values()]

    def provide_input_to_instance(self, launch_id: str, input_data: Dict) -> Dict:
        """Mid-run input routing to a specific EM instance."""
        with self.instance_lock:
            instance = self.active_instances.get(launch_id)
            if instance:
                return instance.provide_input(input_data)
        return {"status": "instance_not_found"}

    def shutdown_all(self) -> Dict:
        """Clean global shutdown of all EM instances."""
        with self.instance_lock:
            for launch_id, instance in list(self.active_instances.items()):
                instance.shutdown()
                self.active_instances.pop(launch_id, None)
        self._append_trace("orchestrator_shutdown_complete", "All EM instances shut down")
        return {"status": "shutdown_complete", "instances_closed": "all"}

    def _get_available_budget(self) -> Dict:
        """Real-time hardware availability from ResourceMonitor."""
        return {
            "gpu_count": self.resource_monitor.get_gpu_count() if hasattr(self.resource_monitor, 'get_gpu_count') else 0,
            "cpu_cores": self.resource_monitor.get_cpu_cores() if hasattr(self.resource_monitor, 'get_cpu_cores') else 16,
            "total_ram_gb": self.resource_monitor.get_total_ram_gb() if hasattr(self.resource_monitor, 'get_total_ram_gb') else 64
        }

    def _can_fit_instances(self, per_instance_budget: Dict, num_instances: int, available: Dict) -> bool:
        """Strict budget feasibility check before launch."""
        required_gpu = (per_instance_budget.get("gpu_count", 0) or 0) * num_instances
        required_cpu = (per_instance_budget.get("cpu_cores", 8) or 8) * num_instances
        required_ram = (per_instance_budget.get("total_ram_gb", 32) or 32) * num_instances
        return (required_gpu <= available.get("gpu_count", 0) and
                required_cpu <= available.get("cpu_cores", 16) and
                required_ram <= available.get("total_ram_gb", 64))

    def _append_trace(self, step: str, details: str = "", **kwargs):
        logger.info(f"ORCHESTRATOR_TRACE [{step}] {details[:150]}...")

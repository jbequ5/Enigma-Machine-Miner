import subprocess
import time
import threading
from typing import List, Dict, Any
from .config import load_config
from .router import SmartLLMRouter
from .flight_test import run_flight_test
from .telemetry import log_telemetry

class EMOperationsOrchestrator:
    def __init__(self):
        self.config = load_config()
        self.router = SmartLLMRouter(self.config)
        self.active_instances: List[subprocess.Popen] = []
        self.lock = threading.Lock()

    def recommend_swarm_size(self) -> int:
        """Compute-aware swarm size recommendation."""
        try:
            from sage.resource_monitor import ResourceMonitor
            resources = ResourceMonitor().scan()
            vram_gb = resources.get("total_vram_gb", 8.0)
            estimated_per_instance_gb = 6.0  # conservative default
            return max(1, min(20, int(vram_gb * 0.8 / estimated_per_instance_gb)))
        except Exception:
            return 1  # safe fallback

    def launch_swarm(self, max_instances: int = None):
        """Launch the swarm with smart routing and strategy assignment."""
        N = max_instances or self.recommend_swarm_size()

        # Run ping-only flight test
        flight_results = run_flight_test(self.config)
        log_telemetry({"event": "flight_test", "results": flight_results})

        if not flight_results["success"]:
            print("Flight test failed. Check compute and LLM connectivity.")
            return

        print(f"Launching {N} EM instances with shared config...")

        for i in range(N):
            # Assign different miner input strategy per instance for A/B testing
            strategies = self.config.get("miner_strategies", ["default"])
            strategy = strategies[i % len(strategies)]

            cmd = [
                "python", "-m", "enigma_machine.main",
                "--config", "operations_config.json",
                "--strategy", strategy,
                "--instance-id", str(i)
            ]

            p = subprocess.Popen(cmd)
            with self.lock:
                self.active_instances.append(p)
            print(f"Instance {i} started with strategy '{strategy}'")

    def monitor_and_recover(self):
        """Background monitoring loop with recovery."""
        while True:
            with self.lock:
                for p in self.active_instances[:]:
                    if p.poll() is not None:  # instance died
                        self.active_instances.remove(p)
                        # TODO: restart logic with new strategy/seed if needed
            time.sleep(30)

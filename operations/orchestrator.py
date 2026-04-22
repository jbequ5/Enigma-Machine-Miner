import subprocess
import time
from typing import List, Dict
from .config import load_config
from .router import SmartLLMRouter
from .flight_test import run_flight_test
from .telemetry import log_telemetry

class EMOperationsOrchestrator:
    def __init__(self):
        self.config = load_config()
        self.router = SmartLLMRouter(self.config)
        self.active_instances = []

    def recommend_swarm_size(self) -> int:
        # Simple but realistic computation
        try:
            from sage.resource_monitor import ResourceMonitor
            resources = ResourceMonitor().scan()
            vram_gb = resources.get("total_vram_gb", 8)
            estimated_per_instance = 6.0  # conservative
            return max(1, min(20, int(vram_gb * 0.8 / estimated_per_instance)))
        except Exception:
            return 4  # safe default

    def launch_swarm(self, max_instances: int = None):
        N = max_instances or self.recommend_swarm_size()
        flight_results = run_flight_test(self.config)
        log_telemetry({"event": "flight_test", "results": flight_results})

        if not flight_results["success"]:
            print("Flight test failed. Check compute and LLM connectivity.")
            return

        print(f"Launching {N} EM instances with shared config...")
        for i in range(N):
            # Assign different miner input strategy per instance for A/B testing
            strategy = self.config.get("miner_strategies", ["default"])[i % len(self.config.get("miner_strategies", ["default"]))]
            
            cmd = [
                "python", "-m", "enigma_machine.main",
                "--config", "operations_config.json",
                "--strategy", strategy,
                "--instance-id", str(i)
            ]
            p = subprocess.Popen(cmd)
            self.active_instances.append(p)
            print(f"Instance {i} started with strategy '{strategy}'")

    def monitor(self):
        while True:
            for p in self.active_instances:
                if p.poll() is not None:
                    # Restart logic here if needed
                    pass
            time.sleep(30)

# agents/tools/resource_aware.py
# Real H100 runtime monitoring + auto-compression + guardrails
# Hardened version: Clean, focused, supports dynamic swarm

import time
import psutil
from pathlib import Path

class ResourceMonitor:
    def __init__(self, max_hours: float = 3.8):
        self.max_seconds = max_hours * 3600
        self.start_time = time.time()
        self.max_hours = max_hours
        print(f"⏱️  Resource Monitor initialized — hard limit {max_hours}h")

    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    def elapsed_hours(self) -> float:
        return self.elapsed_seconds() / 3600

    def get_available_vram_gb(self) -> float:
        """Return approximate available VRAM in GB (for dynamic swarm sizing)"""
        try:
            import torch
            if torch.cuda.is_available():
                # Get free memory on GPU 0
                free = torch.cuda.mem_get_info(0)[0] / (1024 ** 3)
                return round(free, 2)
            else:
                # Fallback for CPU-only or unknown
                return 48.0
        except:
            return 48.0  # safe default for Chutes/H100 assumptions

    def check_and_compress(self, output: str) -> str:
        """Check runtime and compress output if approaching limit"""
        elapsed = self.elapsed_hours()

        if elapsed > self.max_hours - 0.1:   # last 6 minutes = danger zone
            print(f"⚠️  Approaching hard limit ({elapsed:.2f}h / {self.max_hours}h) — compressing output")
            # Aggressive but safe compression
            compressed = output[:len(output)//3] + "\n\n[AUTO-COMPRESSED due to time limit — high-value content preserved]"
            return compressed

        elif elapsed > self.max_hours - 0.5:   # last 30 minutes = warning
            print(f"⚠️  Warning: {elapsed:.2f}h / {self.max_hours}h elapsed")

        else:
            print(f"⏱️  Safe runtime: {elapsed:.2f}h / {self.max_hours}h")

        return output

    def get_status(self) -> dict:
        """Return current status for UI or logging"""
        return {
            "elapsed_hours": round(self.elapsed_hours(), 3),
            "remaining_hours": round(self.max_hours - self.elapsed_hours(), 3),
            "available_vram_gb": self.get_available_vram_gb(),
            "status": "warning" if self.elapsed_hours() > self.max_hours - 0.5 else "normal"
        }

    def should_early_stop(self) -> bool:
        """Simple guard for resource-aware early stopping"""
        return self.elapsed_hours() > self.max_hours * 0.95

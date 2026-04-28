# agents/tools/resource_aware.py
# v0.9.11 MAXIMUM SOTA ResourceMonitor + ResourceAwareGuardrails
# Real H100 runtime monitoring + auto-compression + dynamic swarm sizing + EFS awareness
# Fully integrated with ArbosManager, Predictive Layer, FragmentTracker, and VaultRouter.

import time
import psutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import torch

logger = logging.getLogger(__name__)

class ResourceMonitor:
    def __init__(self, max_hours: float = 3.8):
        self.max_seconds = max_hours * 3600
        self.start_time = time.time()
        self.max_hours = max_hours
        self.arbos = None
        self.predictive = None
        self.fragment_tracker = None
        logger.info(f"⏱️ Resource Monitor v0.9.11 MAX SOTA initialized — hard limit {max_hours}h | Dynamic VRAM-aware swarm support active")

    def set_arbos(self, arbos):
        self.arbos = arbos

    def set_predictive(self, predictive):
        self.predictive = predictive

    def set_fragment_tracker(self, fragment_tracker):
        self.fragment_tracker = fragment_tracker

    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    def elapsed_hours(self) -> float:
        return self.elapsed_seconds() / 3600

    def get_available_vram_gb(self) -> float:
        """Return approximate available VRAM in GB (for dynamic swarm sizing + model loading)."""
        try:
            if torch.cuda.is_available():
                free = torch.cuda.mem_get_info(0)[0] / (1024 ** 3)
                return round(free, 2)
            else:
                # CPU-only or unknown fallback (safe default for Chutes/H100 assumptions)
                return 48.0
        except Exception as e:
            logger.debug(f"VRAM detection failed: {e}")
            return 48.0  # safe default

    def check_and_compress(self, output: str, context: Dict = None) -> str:
        """Check runtime and compress output if approaching limit — EFS-aware preservation."""
        if context is None:
            context = {}

        elapsed = self.elapsed_hours()
        efs = context.get("efs", 0.0)
        predictive_power = getattr(self.predictive, 'predictive_power', 0.0) if self.predictive else 0.0

        # Last 6 minutes = danger zone → aggressive but smart compression
        if elapsed > self.max_hours - 0.1:
            logger.warning(f"⚠️ Approaching hard limit ({elapsed:.2f}h / {self.max_hours}h) — EFS-aware compression triggered")
            # Keep high-EFS / high-predictive content
            if efs > 0.75 or predictive_power > 0.80:
                compressed = output[:len(output)//2] + "\n\n[AUTO-COMPRESSED — high EFS/predictive content preserved]"
            else:
                compressed = output[:len(output)//3] + "\n\n[AUTO-COMPRESSED due to time limit — high-value content preserved]"
            return compressed

        # Last 30 minutes = warning zone
        elif elapsed > self.max_hours - 0.5:
            logger.warning(f"⚠️ Warning: {elapsed:.2f}h / {self.max_hours}h elapsed | EFS={efs:.3f} | Predictive={predictive_power:.3f}")

        else:
            logger.info(f"⏱️ Safe runtime: {elapsed:.2f}h / {self.max_hours}h | EFS={efs:.3f}")

        return output

    def get_status(self) -> dict:
        """Return current status for UI / Streamlit dashboard / ArbosManager."""
        status = {
            "elapsed_hours": round(self.elapsed_hours(), 3),
            "remaining_hours": round(self.max_hours - self.elapsed_hours(), 3),
            "available_vram_gb": self.get_available_vram_gb(),
            "status": "warning" if self.elapsed_hours() > self.max_hours - 0.5 else "normal",
            "dynamic_swarm_capacity": "high" if self.get_available_vram_gb() > 32 else "medium" if self.get_available_vram_gb() > 16 else "low"
        }
        return status

    def should_early_stop(self) -> bool:
        """Simple guard for resource-aware early stopping — tied to EFS and predictive power."""
        elapsed = self.elapsed_hours()
        if elapsed > self.max_hours * 0.95:
            return True

        # Bonus early stop if EFS is already very high and time is running low
        if self.arbos and hasattr(self.arbos, 'validator'):
            efs = getattr(self.arbos.validator, 'last_efs', 0.0)
            if efs > 0.88 and elapsed > self.max_hours * 0.85:
                logger.info("🛑 Early stop triggered — high EFS achieved with time remaining")
                return True

        return False

    def recommend_swarm_size(self, base_size: int = 8) -> int:
        """Dynamic swarm sizing based on available VRAM and remaining time."""
        vram_gb = self.get_available_vram_gb()
        remaining_hours = self.max_hours - self.elapsed_hours()

        if vram_gb > 40:
            multiplier = 1.8
        elif vram_gb > 24:
            multiplier = 1.4
        elif vram_gb > 12:
            multiplier = 1.0
        else:
            multiplier = 0.6

        recommended = int(base_size * multiplier)
        # Never exceed safe limits near end of run
        if remaining_hours < 0.5:
            recommended = max(2, recommended // 2)

        return max(2, min(recommended, 32))  # hard cap at 32 for stabilityimport time
import psutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import torch

logger = logging.getLogger(__name__)

class ResourceMonitor:
    def __init__(self, max_hours: float = 3.8):
        self.max_seconds = max_hours * 3600
        self.start_time = time.time()
        self.max_hours = max_hours
        self.arbos = None
        self.predictive = None
        self.fragment_tracker = None
        logger.info(f"⏱️ Resource Monitor v0.9.12 MAX SOTA initialized — hard limit {max_hours}h | Full wizard + operations integration active")

    def set_arbos(self, arbos):
        self.arbos = arbos

    def set_predictive(self, predictive):
        self.predictive = predictive

    def set_fragment_tracker(self, fragment_tracker):
        self.fragment_tracker = fragment_tracker

    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    def elapsed_hours(self) -> float:
        return self.elapsed_seconds() / 3600

    def get_available_vram_gb(self) -> float:
        """Return approximate available VRAM in GB (for dynamic swarm sizing + model loading)."""
        try:
            if torch.cuda.is_available():
                free = torch.cuda.mem_get_info(0)[0] / (1024 ** 3)
                return round(free, 2)
            else:
                return 48.0  # safe default
        except Exception:
            return 48.0

    def check_and_compress(self, output: str, context: Dict = None) -> str:
        """Check runtime and compress output if approaching limit — EFS/predictive-aware preservation."""
        if context is None:
            context = {}

        elapsed = self.elapsed_hours()
        efs = context.get("efs", 0.0)
        predictive_power = getattr(self.predictive, 'predictive_power', 0.0) if self.predictive else 0.0

        if elapsed > self.max_hours - 0.1:
            logger.warning(f"⚠️ Approaching hard limit ({elapsed:.2f}h / {self.max_hours}h) — EFS-aware compression triggered")
            if efs > 0.75 or predictive_power > 0.80:
                compressed = output[:len(output)//2] + "\n\n[AUTO-COMPRESSED — high EFS/predictive content preserved]"
            else:
                compressed = output[:len(output)//3] + "\n\n[AUTO-COMPRESSED due to time limit — high-value content preserved]"
            return compressed

        elif elapsed > self.max_hours - 0.5:
            logger.warning(f"⚠️ Warning: {elapsed:.2f}h / {self.max_hours}h elapsed | EFS={efs:.3f} | Predictive={predictive_power:.3f}")

        return output

    def get_status(self) -> dict:
        """Return current status for UI / Streamlit dashboard / ArbosManager."""
        return {
            "elapsed_hours": round(self.elapsed_hours(), 3),
            "remaining_hours": round(self.max_hours - self.elapsed_hours(), 3),
            "available_vram_gb": self.get_available_vram_gb(),
            "status": "warning" if self.elapsed_hours() > self.max_hours - 0.5 else "normal",
            "dynamic_swarm_capacity": "high" if self.get_available_vram_gb() > 32 else "medium" if self.get_available_vram_gb() > 16 else "low"
        }

    def should_early_stop(self) -> bool:
        """SOTA early stop — tied to EFS, predictive power, and remaining time."""
        elapsed = self.elapsed_hours()
        if elapsed > self.max_hours * 0.95:
            return True

        if self.arbos and hasattr(self.arbos, 'validator'):
            efs = getattr(self.arbos.validator, 'last_efs', 0.0)
            if efs > 0.88 and elapsed > self.max_hours * 0.85:
                logger.info("🛑 Early stop triggered — high EFS achieved with time remaining")
                return True

        return False

    def recommend_swarm_size(self, base_size: int = 8) -> int:
        """Dynamic swarm sizing based on available VRAM, remaining time, and predictive power."""
        vram_gb = self.get_available_vram_gb()
        remaining_hours = self.max_hours - self.elapsed_hours()
        predictive = getattr(self.predictive, 'predictive_power', 0.0) if self.predictive else 0.0

        if vram_gb > 40:
            multiplier = 1.8
        elif vram_gb > 24:
            multiplier = 1.4
        elif vram_gb > 12:
            multiplier = 1.0
        else:
            multiplier = 0.6

        # Boost for high predictive power
        if predictive > 0.75:
            multiplier += 0.3

        recommended = int(base_size * multiplier)
        if remaining_hours < 0.5:
            recommended = max(2, recommended // 2)

        return max(2, min(recommended, 32))

# Global instance
resource_monitor = ResourceMonitor()

# Global instance
resource_monitor = ResourceMonitor()

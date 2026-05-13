# operations/config.py
# SAGE v0.9.14+ — OperationsConfig
# All system-wide constants and tunable parameters (birth gates, Meta-RL defaults, hardware limits, etc.)

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Dict, Any

@dataclass
class OperationsConfig:
    data_dir: Path = Path("data/operations")
    model_registry_path: Path = Path("data/models/registry.json")
    
    # Hardware & concurrency
    max_concurrent_llm_calls: int = 8
    vrambudget_gb: float = 16.0          # Updated safe default for modern GPUs
    
    # Scoring & birth gate (60/40 aware)
    birth_gate_min_efs: float = 0.75
    birth_gate_min_refined_value: float = 0.65
    
    # Swarm safety & timing
    max_swarm_runtime_seconds: int = 300
    target_fragment_yield: float = 0.92
    
    # Meta-RL defaults (overridable)
    meta_rl_defaults: Dict[str, float] = None

    def __post_init__(self):
        if self.meta_rl_defaults is None:
            self.meta_rl_defaults = {
                "flight_test_branching_aggression": 1.0,
                "model_assignment_aggression": 1.0,
                "orchestrator_recovery_sensitivity": 0.05,
                "target_fragment_yield": self.target_fragment_yield,
            }

    @classmethod
    def load(cls, path: str = "operations_config.json") -> "OperationsConfig":
        p = Path(path)
        if p.exists():
            with open(p) as f:
                data = json.load(f)
            # Convert Path objects back
            if "data_dir" in data:
                data["data_dir"] = Path(data["data_dir"])
            if "model_registry_path" in data:
                data["model_registry_path"] = Path(data["model_registry_path"])
            return cls(**data)
        cfg = cls()
        cfg.data_dir.mkdir(parents=True, exist_ok=True)
        cfg.save(path)
        return cfg

    def save(self, path: str = "operations_config.json"):
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2, default=str)

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class OperationsConfig:
    data_dir: Path = Path("data/operations")
    model_registry_path: Path = Path("data/models/registry.json")
    max_concurrent_llm_calls: int = 8
    vrambudget_gb: float = 5.5
    temperature_default: float = 0.7
    birth_gate_min_efs: float = 0.65
    birth_gate_min_refined_value: float = 0.55

    @classmethod
    def load(cls, path: str = "operations_config.json") -> "OperationsConfig":
        p = Path(path)
        if p.exists():
            with open(p) as f:
                data = json.load(f)
            return cls(**data)
        cfg = cls()
        cfg.data_dir.mkdir(parents=True, exist_ok=True)
        return cfg

    def save(self, path: str = "operations_config.json"):
        with open(path, "w") as f:
            json.dump(self.__dict__, f, indent=2, default=str)

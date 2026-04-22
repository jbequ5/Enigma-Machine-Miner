from typing import Dict, List
import math

class SmartLLMRouter:
    def __init__(self, config: Dict):
        self.config = config
        self.model_registry = config.get("model_registry", {})

    def recommend(self, task_type: str, current_n: int, available_vram: float) -> str:
        """Return best model name for this task type and swarm size."""
        base_models = self.config.get("task_type_models", {}).get(task_type, ["claude-3.5"])
        base_model = base_models[0]

        # Automatic downscaling as swarm grows
        downscale_factor = self.config.get("downscale_factor", 0.08)
        effective_size_factor = max(0.3, 1.0 - downscale_factor * (current_n - 1))

        # Simple selection: prefer smaller models as N increases
        if effective_size_factor < 0.6 and len(base_models) > 1:
            return base_models[-1]  # smallest model
        return base_model

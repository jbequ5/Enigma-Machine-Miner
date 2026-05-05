# operations/meta_rl.py (new file)
from .performance_tracker import PerformanceTracker
import json

class MetaRL:
    def run_nightly(self):
        tracker = PerformanceTracker()
        runs = tracker.get_recent_runs()  # new method we can add
        # Compute reward = average Fragment Yield + bonuses
        # Update shared meta-weights.json
        weights = self._optimize_weights(runs)
        with open("data/meta_weights.json", "w") as f:
            json.dump(weights, f, indent=2)
        print(f"Meta-RL updated — new average Fragment Yield: {weights['global_yield']}")

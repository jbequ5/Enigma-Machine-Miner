import json
from datetime import datetime
from pathlib import Path

TELEMETRY_PATH = Path("operations_telemetry.jsonl")

def log_telemetry(entry: Dict):
    entry["timestamp"] = datetime.utcnow().isoformat()
    with open(TELEMETRY_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

import time
from typing import Dict

def run_flight_test(config: Dict) -> Dict:
    """Ping-only flight test: verify compute + LLM connectivity."""
    results = {
        "success": True,
        "compute_ok": True,
        "llm_ping_ok": True,
        "latency_ms": 0.0,
        "estimated_fragments_per_hour": 0,
    }

    # Resource ping
    try:
        from sage.resource_monitor import ResourceMonitor
        monitor = ResourceMonitor()
        resources = monitor.scan()
        results["available_vram_gb"] = resources.get("total_vram_gb", 0)
    except Exception:
        results["compute_ok"] = False
        results["success"] = False

    # LLM ping (dummy call)
    try:
        start = time.time()
        # Replace with your actual LLM ping logic (e.g., simple status call)
        # For now we simulate a fast ping
        time.sleep(0.3)
        results["latency_ms"] = (time.time() - start) * 1000
    except Exception:
        results["llm_ping_ok"] = False
        results["success"] = False

    return results

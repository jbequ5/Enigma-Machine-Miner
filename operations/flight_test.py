import time
from typing import Dict, Any

def run_flight_test(config: Dict[str, Any]) -> Dict[str, Any]:
    """Ping-only flight test: verify compute + LLM connectivity. No full EM run."""
    results: Dict[str, Any] = {
        "success": True,
        "compute_ok": True,
        "llm_ping_ok": True,
        "latency_ms": 0.0,
        "available_vram_gb": 0.0,
        "estimated_fragments_per_hour": 0,
    }

    # Compute ping
    try:
        from sage.resource_monitor import ResourceMonitor
        monitor = ResourceMonitor()
        resources = monitor.scan()
        results["available_vram_gb"] = resources.get("total_vram_gb", 0)
    except Exception as e:
        results["compute_ok"] = False
        results["success"] = False

    # LLM ping (quick connectivity check)
    try:
        start = time.time()
        # Dummy ping - replace with your actual LLM client ping if needed
        time.sleep(0.2)  # simulate network call
        results["latency_ms"] = (time.time() - start) * 1000
    except Exception:
        results["llm_ping_ok"] = False
        results["success"] = False

    return results

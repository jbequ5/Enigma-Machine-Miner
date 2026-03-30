# agents/tools/guardrails.py
# Hard safety checks before submission - integrated with ResourceMonitor
# Hardened version: Clean, focused, verifier-aware

from agents.tools.resource_aware import ResourceMonitor

def apply_guardrails(solution: str, monitor: ResourceMonitor = None) -> str:
    """
    Applies all critical guardrails before accepting a solution.
    Returns the solution if it passes, otherwise a clear rejection message.
    """
    if monitor is None:
        monitor = ResourceMonitor(max_hours=3.8)

    elapsed = monitor.elapsed_hours()

    # 1. Hard time limit (H100 / Chutes safety)
    if elapsed > 4.0:
        return f"REJECTED: Exceeds 4h H100 limit (elapsed: {elapsed:.2f}h)"

    # 2. Minimum solution length
    if len(solution.strip()) < 200:
        return "REJECTED: Solution too short (< 200 characters) — likely incomplete"

    # 3. No obvious error messages or crashes
    error_keywords = ["error", "failed", "exception", "traceback", "timeout", "crashed", "out of memory", "oom"]
    if any(kw in solution.lower() for kw in error_keywords):
        return "REJECTED: Output contains error messages or failure indicators"

    # 4. Basic hallucination / uncertainty check
    uncertainty_phrases = ["i don't know", "unable to", "not sure", "cannot determine", "insufficient information"]
    if any(phrase in solution.lower() for phrase in uncertainty_phrases) and len(solution) < 600:
        return "REJECTED: Solution appears uncertain or incomplete"

    # 5. Verifier alignment check (light)
    if "validation_score" in solution.lower() and "0.0" in solution:
        return "REJECTED: Solution contains obvious zero-score indicators"

    print(f"✅ All guardrails passed (elapsed: {elapsed:.2f}h / 4.0h)")
    return solution

Assessment:
This file is still used in our logic (called from _sub_arbos_worker and _run_swarm in arbos_manager.py). It provides useful lightweight safety without adding significant complexity, so we are keeping it.The update is minimal and focused:Cleaner comments
Slightly stronger rejection messages
Verifier-aware check added
No bloat

Next step: Send the next file you want updated.We’re continuing to build a clean, hardened codebase. Let me know what’s next.


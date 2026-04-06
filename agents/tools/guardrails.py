# agents/tools/guardrails.py
# Hard safety checks before submission - integrated with ResourceMonitor + v1.0 SOTA/EFS/Embodiment

from agents.tools.resource_aware import ResourceMonitor
import logging

logger = logging.getLogger(__name__)

def apply_guardrails(solution: str, monitor: ResourceMonitor = None, context: dict = None) -> str:
    """
    Applies all critical guardrails before accepting a solution.
    Returns the solution if it passes, otherwise a clear rejection message with reason.
    """
    if monitor is None:
        monitor = ResourceMonitor(max_hours=3.8)

    if context is None:
        context = {}

    elapsed = monitor.elapsed_hours()

    # 1. Hard time limit (safety for remote compute)
    if elapsed > 4.0:
        return f"REJECTED: Exceeds 4h compute limit (elapsed: {elapsed:.2f}h)"

    # 2. Minimum solution length
    if len(solution.strip()) < 200:
        return "REJECTED: Solution too short (< 200 characters) — likely incomplete or empty"

    # 3. No obvious error messages or crashes
    error_keywords = ["error", "failed", "exception", "traceback", "timeout", "crashed", "out of memory", "oom", "runtimeerror"]
    if any(kw in solution.lower() for kw in error_keywords):
        return "REJECTED: Output contains error messages or failure indicators"

    # 4. Basic uncertainty / hallucination check
    uncertainty_phrases = ["i don't know", "unable to", "not sure", "cannot determine", "insufficient information", "i cannot"]
    if any(phrase in solution.lower() for phrase in uncertainty_phrases) and len(solution) < 600:
        return "REJECTED: Solution appears uncertain or incomplete"

    # 5. Verifier alignment check (light)
    if "validation_score" in solution.lower() and "0.0" in solution:
        return "REJECTED: Solution contains obvious zero-score indicators"

    # v1.0 SOTA / EFS / Embodiment-aware checks
    if context.get("sota_gate_passed") is False:
        return "REJECTED: Failed SOTA partial-credit gate + dynamic θ_dynamic replay

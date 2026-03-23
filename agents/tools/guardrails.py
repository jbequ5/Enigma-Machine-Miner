# agents/tools/guardrails.py
# Hard safety checks before submission

def apply_guardrails(solution: str, runtime_hours: float):
    """Enforces all subnet rules"""
    if runtime_hours > 4.0:
        return "REJECTED: Exceeds 4h H200 limit"
    if len(solution) < 100:
        return "REJECTED: Solution too short"
    if "error" in solution.lower() or "failed" in solution.lower():
        return "REJECTED: Contains error messages"
    print("✅ All guardrails passed")
    return solution

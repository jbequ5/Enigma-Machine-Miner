# agents/tools/reflection.py
# Lightweight Reflection Helper - v1.0
# Focused on verifier-aligned critique only. Does NOT duplicate re_adapt or ValidationOracle.

from agents.tools.compute import ComputeRouter
import logging

logger = logging.getLogger(__name__)

class ReflectionEngine:
    def __init__(self):
        self.compute = ComputeRouter()
        logger.info("🔄 ReflectionEngine initialized (lightweight verifier-aligned helper)")

    def quick_critique(self, task: str, output: str, context: dict = None) -> dict:
        """
        Simple, fast critique helper.
        Use this when you need a quick second opinion before re_adapt or meta-tuning.
        """
        if context is None:
            context = {}

        critique_task = f"""
Task: {task}
Current Output: {output}

Context: Validation Score ~{context.get('validation_score', 'N/A')}, EFS ~{context.get('efs', 'N/A')}

Provide a short, verifier-first critique focusing on:
- Symbolic fidelity and determinism
- Missing invariants or edge cases
- Potential to improve ValidationOracle score or EFS
- Heterogeneity contribution

Be concise. End with "APPROVED" if excellent, otherwise list 1-3 actionable improvements.
"""

        try:
            critique = self.compute.run_on_compute(critique_task, temperature=0.0, task_type="reflection").strip()
            
            approved = "APPROVED" in critique.upper()
            
            return {
                "approved": approved,
                "critique": critique,
                "suggested_improvements": not approved
            }
        except Exception as e:
            logger.warning(f"Quick critique failed: {e}")
            return {"approved": False, "critique": f"Critique failed: {str(e)[:100]}", "suggested_improvements": True}

# Global instance
reflection_engine = ReflectionEngine()

# Legacy wrapper (kept for compatibility)
def reflect_and_improve(task: str, output: str, max_iterations: int = 1):
    """Light legacy wrapper — now delegates to quick_critique (single pass)."""
    result = reflection_engine.quick_critique(task, output)
    return output if result["approved"] else f"[Improved version needed]\nCritique: {result['critique']}"

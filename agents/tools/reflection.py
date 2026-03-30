# agents/tools/reflection.py
# Full Reflection Pattern - self-critique and iterative improvement
# Hardened version: Uses ComputeRouter + Quasar support + verifier alignment focus

from agents.tools.compute import ComputeRouter

class ReflectionEngine:
    def __init__(self):
        self.compute = ComputeRouter()
        print("🔄 ReflectionEngine initialized (verifier-aligned + Quasar capable)")

    def reflect_and_improve(self, task: str, output: str, max_iterations: int = 3, use_quasar: bool = True):
        """
        Reflection Pattern:
        Critiques → Revises → Stops when APPROVED or max iterations reached.
        """
        current = output
        trace = []

        for i in range(max_iterations):
            critique_task = f"""
Task: {task}
Current Output: {current}

Critique this output on:
- Accuracy
- Completeness
- Logical consistency
- Hallucinations / factual errors
- Clarity and conciseness
- Alignment with original goal and verifier criteria
- Potential to improve validation score

Reply ONLY with "APPROVED" if it is excellent. Otherwise give specific, actionable fixes.
"""

            # Use Quasar for deep reflection when enabled
            task_type = "reflection"
            if use_quasar:
                task_type = "re_adapt"  # routes to Quasar for better long-context critique

            critique_result = self.compute.run_on_compute(
                critique_task, 
                temperature=0.0, 
                task_type=task_type
            )
            critique = critique_result.strip()

            trace.append({"iteration": i + 1, "critique": critique[:500]})

            if "APPROVED" in critique.upper():
                print(f"✅ Reflection approved after {i+1} iterations")
                return current, trace

            # Revise the output
            revise_task = f"""
Improve the following output based on this critique:

Critique: {critique}

Original Output: {current}

Produce a revised, higher-quality version that better aligns with the verifier and task goals.
"""

            revise_result = self.compute.run_on_compute(
                revise_task, 
                temperature=0.3, 
                task_type=task_type
            )
            current = revise_result.strip()

        print(f"⚠️  Reflection reached max iterations ({max_iterations})")
        return current, trace


# Global instance
reflection_engine = ReflectionEngine()

# Legacy compatibility wrapper (your original function signature)
def reflect_and_improve(task: str, output: str, max_iterations: int = 3):
    """Legacy wrapper for backward compatibility."""
    return reflection_engine.reflect_and_improve(task, output, max_iterations)

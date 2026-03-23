# agents/arbos_manager.py
# Main conductor for Enigma Machine - now uses Reflection

from agents.tools.reflection import reflect_and_improve

class ArbosManager:
    def __init__(self, goal_file="goals/killer_base.md"):
        self.goal_file = goal_file
        print(f"✅ Arbos Manager loaded with goal: {goal_file}")

    def run(self, challenge):
        print(f"🔥 Received challenge: {challenge[:100]}...")

        # Placeholder initial output (in real version this would be from planning/tool use)
        initial_output = f"Initial solution attempt for: {challenge}"

        # Use Reflection pattern (from the book)
        final_output, reflection_trace = reflect_and_improve(
            task=challenge,
            output=initial_output,
            llm=lambda x: f"Improved version of: {x}",  # placeholder LLM call
            max_iterations=4
        )

        print("✅ Reflection complete!")
        return {
            "solution": final_output,
            "status": "complete",
            "reflection_trace": reflection_trace
        }

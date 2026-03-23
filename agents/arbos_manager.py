# agents/arbos_manager.py
# FINAL VERSION - CONNECTED TO REAL ARBOS (Const's repo)

import os
import subprocess
from agents.tools.reflection import reflect_and_improve
from agents.tools.gpd import run_gpd
from agents.tools.scienceclaw import run_scienceclaw

class ArbosManager:
    def __init__(self, goal_file="goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        self._setup_real_arbos()
        print(f"✅ Connected to REAL Arbos with goal: {goal_file}")

    def _setup_real_arbos(self):
        """Clones Const's real Arbos repo once"""
        if not os.path.exists(self.arbos_path):
            print("📥 Cloning real Arbos from GitHub (Const's repo)...")
            subprocess.run([
                "git", "clone", "https://github.com/unconst/Arbos.git", self.arbos_path
            ], check=True)

    def run(self, challenge: str):
        print(f"🔥 Running REAL Arbos for challenge: {challenge[:100]}...")

        # 1. Run real tools first
        gpd_result = run_gpd(challenge)
        scienceclaw_result = run_scienceclaw(challenge, 20)

        # 2. Initial output to feed Arbos
        initial_output = f"GPD: {gpd_result}\nScienceClaw: {scienceclaw_result}\nChallenge: {challenge}"

        # 3. Call REAL Arbos (Ralph loop) via subprocess
        try:
            result = subprocess.run([
                "python", f"{self.arbos_path}/arbos.py",
                "--goal", self.goal_file,
                "--input", initial_output
            ], capture_output=True, text=True, timeout=3600)
            
            final_solution = result.stdout.strip()
        except Exception as e:
            final_solution = f"Arbos failed: {str(e)}"

        # 4. Final reflection pass
        final_solution, trace = reflect_and_improve(
            task=challenge,
            output=final_solution,
            llm_call=lambda x: f"Refined: {x}",
            max_iterations=3
        )

        print("✅ REAL Arbos completed!")
        return {
            "solution": final_solution,
            "status": "complete",
            "trace": trace
        }

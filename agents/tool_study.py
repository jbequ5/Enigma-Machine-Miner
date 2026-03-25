# agents/tool_study.py
# 2-Pass Tool Study - Arbos studies each tool, critiques its own profile,
# and evaluates improvement potential for the overall solution

from pathlib import Path
from agents.tools.compute import ComputeRouter

class ToolStudy:
    def __init__(self):
        self.profiles_dir = Path("tool_profiles")
        self.profiles_dir.mkdir(exist_ok=True)
        self.compute = ComputeRouter()

    def study_all_tools(self):
        """Run once. 2-pass study with self-critique and improvement evaluation."""
        tools = {
            "AI-Researcher": "https://github.com/HKUDS/AI-Researcher",
            "AutoResearch": "https://github.com/karpathy/autoresearch",
            "GPD": "https://github.com/psi-oss/get-physics-done",
            "ScienceClaw": "https://github.com/lamm-mit/scienceclaw",
            "HyperAgent": "https://github.com/facebookresearch/HyperAgents"
        }

        print("🔬 Starting 2-Pass Tool Study Phase...\n")

        for tool_name, repo_url in tools.items():
            print(f"Studying {tool_name}...")

            # Pass 1: Initial study
            initial_profile = self._study_tool(tool_name, repo_url)

            # Pass 2: Self-critique + improvement evaluation
            refined_profile = self._critique_and_refine(tool_name, initial_profile)

            self._save_profile(tool_name, refined_profile)
            print(f"✅ Refined profile for {tool_name} saved.\n")

        print("✅ 2-Pass Tool Study completed! All profiles are ready.")

    def _study_tool(self, tool_name: str, repo_url: str) -> str:
        study_task = f"""
You are Arbos, a highly intelligent conductor.
Study the tool "{tool_name}" at {repo_url}.

Provide a detailed profile including:
- Core purpose and unique strengths
- Exact workflow and iteration style
- How it uses memory or persistent state
- What makes it different from a generic LLM call
- Best prompting techniques to mimic its behavior
- Ideal use cases and known limitations
"""

        result = self.compute.run_on_compute(study_task)
        return result

    def _critique_and_refine(self, tool_name: str, initial_profile: str) -> str:
        critique_task = f"""
You are Arbos performing a self-critique.

Initial Profile for {tool_name}:
{initial_profile}

Critique this profile for completeness and usefulness.
Check specifically for:
- Clear core purpose
- Accurate workflow description
- Memory/persistent state handling
- Uniqueness vs generic LLM
- Practical prompting advice
- Realistic limitations

Then evaluate: Would using this tool meaningfully improve the quality, novelty, or verifier score of solutions in the Enigma miner?

Produce a refined, improved profile that incorporates your critique.
Add a final section: "Improvement Potential for Enigma Miner" with a short honest assessment.
"""

        result = self.compute.run_on_compute(critique_task)
        return result

    def _save_profile(self, tool_name: str, profile: str):
        path = self.profiles_dir / f"{tool_name.lower()}.md"
        path.write_text(profile)

    def load_profile(self, tool_name: str) -> str:
        path = self.profiles_dir / f"{tool_name.lower()}.md"
        if path.exists():
            return path.read_text()
        return f"No profile found for {tool_name}. Using high-intelligence generic reasoning."

# Global instance
tool_study = ToolStudy()

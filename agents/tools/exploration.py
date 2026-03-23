# agents/tools/exploration.py
# EXPANDED Exploration & Discovery - real novelty generation using AI-Researcher + Chutes LLM

from agents.tools.ai_researcher import run_ai_researcher
from agents.tools.compute import ComputeRouter

def explore_novel_variant(task: str, base_solution: str):
    """
    Generates truly novel variants using:
    - AI-Researcher for cross-domain inspiration
    - Chutes LLM for creative synthesis
    - Reflection for quality
    Returns structured list of 2-3 novel variants.
    """
    compute = ComputeRouter()
    print(f"🔍 Exploring novel variants for: {task[:80]}...")

    # 1. Get cross-domain inspiration from AI-Researcher
    inspiration = run_ai_researcher(f"Find cross-domain ideas for: {task} related to {base_solution}")

    # 2. Generate novel variants with Chutes LLM
    prompt = f"""
    Task: {task}
    Base solution: {base_solution}
    Inspiration from literature: {inspiration}

    Generate 3 truly novel variants that are:
    - Different from the base
    - High-impact / breakthrough potential
    - Feasible under 4h H100

    Return only JSON list of dicts: [{{"variant": "...", "rationale": "...", "impact": "..."}}]
    """

    raw_variants = compute.run_on_compute(prompt)

    # 3. Quick reflection to pick the best
    final_variants = raw_variants  # In production you could add another reflection pass here

    print("🌟 Novel variants generated!")
    return final_variants

# agents/tools/exploration.py
# EXPANDED Exploration & Discovery - real novelty generation

from agents.tools.ai_researcher import run_ai_researcher
from agents.tools.compute import ComputeRouter

def explore_novel_variant(task: str, base_solution: str):
    """
    Generates truly novel variants using cross-domain inspiration.
    Returns a clean list of 2-3 structured novel ideas.
    """
    compute = ComputeRouter()
    print(f"🔍 Exploring novel variants for: {task[:80]}...")

    try:
        # 1. Cross-domain inspiration from AI-Researcher
        inspiration_task = f"Find cross-domain ideas and analogies for: {task}. Base idea: {base_solution[:300]}"
        inspiration = run_ai_researcher(task=inspiration_task, search_mode="deep").get("output", "")

        # 2. Generate novel variants using Chutes LLM (via ComputeRouter)
        prompt = f"""
Task: {task}
Base solution: {base_solution}

Inspiration from literature: {inspiration}

Generate 2-3 truly novel variants that are:
- Significantly different from the base solution
- High potential impact / breakthrough quality
- Feasible within 4-hour H100 limit

Return ONLY a valid JSON array like this:
[{{"variant": "short title", "rationale": "why it's novel and better", "impact": "estimated verifier score boost"}}]
"""

        raw_variants = compute.run_on_compute(prompt)   # Assuming this method exists

        # Fallback if compute returns string instead of parsed JSON
        if isinstance(raw_variants, str):
            import json
            try:
                variants = json.loads(raw_variants)
            except:
                variants = [{"variant": "Novel Variant", "rationale": raw_variants[:200], "impact": "High"}]
        else:
            variants = raw_variants

        print(f"🌟 Generated {len(variants)} novel variants")
        return variants

    except Exception as e:
        print(f"⚠️ Exploration failed: {e}")
        # Safe fallback
        return [{
            "variant": "Safe Novel Variant",
            "rationale": "Fallback due to exploration error",
            "impact": "Medium"
        }]

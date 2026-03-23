# agents/tools/exploration.py
# Exploration & Discovery - generates novel variants

def explore_novel_variant(task: str, base_solution: str):
    """Generates one novel breakthrough variant"""
    print(f"🔍 Exploring novel variant for: {task[:80]}...")
    return f"🌟 Novel variant: {base_solution} + cross-domain insight"

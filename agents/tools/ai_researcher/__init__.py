import subprocess

def run(task: str, search_mode: str = "deep", **kwargs):
    """
    AI-Researcher is complex (Docker + scripts). We use a simple fallback for now.
    """
    try:
        # Simple fallback using direct LLM call via HyperAgent for now
        from agents.tools.hyperagent import run_hyperagent
        result = run_hyperagent(task=f"Perform research on: {task}", parallel_tasks=3)
        return {
            "success": True,
            "output": result.get("output", "Research completed"),
            "mode_used": search_mode
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

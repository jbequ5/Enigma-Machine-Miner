import subprocess

def run(task: str, search_intensity: str = "high", max_sources: int = 15, **kwargs):
    """Your personal ScienceClaw instance (from lamm-mit/scienceclaw)."""
    try:
        cmd = [
            "npx", "-y", "scienceclaw",
            "--intensity", search_intensity,
            "--max-sources", str(max_sources),
            "--task", task
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.stderr else None,
            "intensity_used": search_intensity,
            "max_sources_used": max_sources
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "ScienceClaw timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}

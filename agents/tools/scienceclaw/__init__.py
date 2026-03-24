import subprocess

def run(task: str, search_intensity: str = "high", max_sources: int = 15, **kwargs):
    """Your personal ScienceClaw instance."""
    try:
        cmd = ["npx", "-y", "scienceclaw", "--intensity", search_intensity, "--max-sources", str(max_sources), "--task", task]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {"success": result.returncode == 0, "output": result.stdout.strip(), "error": result.stderr.strip() if result.stderr else None}
    except Exception as e:
        return {"success": False, "error": str(e)}

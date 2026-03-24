import subprocess

def run(task: str, parallel_tasks: int = 5, **kwargs):
    """Your personal HyperAgent instance."""
    try:
        cmd = ["npx", "-y", "hyperagent", "--parallel", str(parallel_tasks), "--task", task]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {"success": result.returncode == 0, "output": result.stdout.strip(), "error": result.stderr.strip() if result.stderr else None}
    except Exception as e:
        return {"success": False, "error": str(e)}

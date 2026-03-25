# agents/tools/scienceclaw/__init__.py
# Real ScienceClaw integration with automatic setup

import subprocess
from pathlib import Path
import os

def ensure_scienceclaw_installed():
    """One-time automatic setup for ScienceClaw"""
    if Path("/usr/local/bin/scienceclaw-post").exists() or Path("~/.scienceclaw").expanduser().exists():
        return True  # Already installed

    print("🔧 ScienceClaw not found. Running automatic first-time setup...")

    try:
        # Clone if missing
        if not Path("scienceclaw").exists():
            subprocess.run(["git", "clone", "https://github.com/lamm-mit/scienceclaw.git"], check=True)

        os.chdir("scienceclaw")
        subprocess.run(["python3", "-m", "venv", ".venv"], check=True)
        subprocess.run([".venv/bin/pip", "install", "-r", "requirements.txt"], check=True)
        subprocess.run(["./install_scienceclaw_command.sh"], check=True)

        # Quick non-interactive agent setup (requires LLM keys in env)
        subprocess.run([
            "python3", "setup.py", "--quick",
            "--profile", "mixed",
            "--name", "EnigmaMinerAgent"
        ], check=True)

        os.chdir("..")
        print("✅ ScienceClaw setup completed.")
        return True
    except Exception as e:
        print(f"⚠️ ScienceClaw auto-setup failed: {e}")
        print("Please run the setup manually from the scienceclaw folder.")
        return False

def run(task: str, **kwargs):
    """
    Real ScienceClaw call at the end of the loop.
    """
    if not ensure_scienceclaw_installed():
        return {"success": False, "error": "ScienceClaw could not be set up automatically."}

    try:
        result = subprocess.run([
            "scienceclaw-post",
            "--agent", "EnigmaMinerAgent",
            "--topic", task,
            "--community", "mixed"
        ], capture_output=True, text=True, timeout=600)

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip() or result.stderr.strip(),
            "error": result.stderr.strip() if result.returncode != 0 else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# agents/tools/get_physics_done/__init__.py
"""
Real Get Physics Done (psi-oss) integration for Enigma Machine Miner.
This gives each miner their own customizable instance of the AI physicist.
"""

import subprocess
from pathlib import Path
import json

def run(task: str, profile: str = "deep-theory", tier: str = "1", **kwargs):
    """
    Run your personal instance of Get Physics Done.
    
    Parameters:
        task: The physics/research task to solve
        profile: deep-theory, numerical, exploratory, review, paper-writing
        tier: 1 (highest quality), 2, 3 (fastest)
    """
    try:
        # Call the real get-physics-done via npx (works without local install)
        cmd = [
            "npx", "-y", "@psi-oss/get-physics-done",
            "--profile", profile,
            "--tier", tier,
            "--task", task
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        output = {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.stderr else None,
            "profile_used": profile,
            "tier_used": tier,
            "task": task
        }

        return output

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Get Physics Done timed out (took too long)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Optional: Helper to format for GOAL.md
def get_config_summary(config: dict):
    return f"GPD Profile: {config.get('profile', 'deep-theory')}, Tier: {config.get('tier', '1')}"

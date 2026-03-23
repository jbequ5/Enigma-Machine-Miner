# agents/tools/ai_researcher.py
# Real integration with AI-Researcher (HKUDS) - autonomous literature review + idea generation

import subprocess
import os

def run_ai_researcher(task: str):
    """
    Calls the real AI-Researcher repo from HKUDS.
    Clones once if needed, then runs literature review + idea generation.
    """
    repo_path = "tools/ai-researcher"
    
    if not os.path.exists(repo_path):
        print("📥 Cloning AI-Researcher from GitHub (HKUDS)...")
        subprocess.run([
            "git", "clone", "https://github.com/HKUDS/AI-Researcher.git", repo_path
        ], check=True)
    
    print(f"📚 Running AI-Researcher for: {task[:80]}...")
    try:
        result = subprocess.run([
            "python", f"{repo_path}/main.py", "--query", task
        ], capture_output=True, text=True, timeout=600)
        return f"✅ AI-Researcher Result:\n{result.stdout.strip()[:600]}..."
    except Exception as e:
        return f"⚠️ AI-Researcher failed: {str(e)}"

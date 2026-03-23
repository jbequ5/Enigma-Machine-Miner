# agents/tools/ai_researcher.py
# Real integration with AI-Researcher (HKUDS) - autonomous literature review + idea generation

import subprocess
import os

def run_ai_researcher(task: str):
    path = "tools/ai-researcher"
    if not os.path.exists(path):
        print("📥 Cloning real AI-Researcher repo...")
        subprocess.run(["git", "clone", "https://github.com/HKUDS/AI-Researcher.git", path], check=True)
    print(f"📚 Running real AI-Researcher for: {task[:80]}...")
    try:
        result = subprocess.run(["python", f"{path}/main.py", "--query", task], capture_output=True, text=True, timeout=600)
        return f"✅ AI-Researcher Result:\n{result.stdout.strip()[:600]}..."
    except Exception as e:
        return f"⚠️ AI-Researcher failed: {str(e)}"

# agents/tools/gpd.py
# Get Physics Done - derivations & verification

import subprocess
import os

def run_gpd(task: str):
    path = "tools/gpd"
    if not os.path.exists(path):
        print("📥 Cloning real GPD repo...")
        subprocess.run(["git", "clone", "https://github.com/psi-oss/get-physics-done.git", path], check=True)
    print(f"📐 Running real GPD for: {task[:80]}...")
    try:
        result = subprocess.run(["python", f"{path}/gpd.py", task], capture_output=True, text=True, timeout=300)
        return f"✅ GPD Result:\n{result.stdout.strip()[:500]}..."
    except Exception as e:
        return f"⚠️ GPD failed: {str(e)}"

"""
Full integration of karpathy/autoresearch into Enigma Machine Miner.
Uses and updates program.md cumulatively so tools can build on each other.
"""

import subprocess
from pathlib import Path

def run(task: str, depth: str = "medium", iterations: int = 3, program_md_path: str = "program.md", **kwargs):
    """
    Run AutoResearch with full program.md support.
    
    - Reads existing program.md (cumulative context from previous tools)
    - Appends the new task
    - Runs AutoResearch
    - Returns the updated program.md content for the next tool
    """
    program_path = Path(program_md_path)
    
    # Initialize or append to program.md with current context
    if not program_path.exists():
        initial_content = f"# AutoResearch Execution Program\n\n## Original Challenge\n{task}\n\n"
        program_path.write_text(initial_content)
    else:
        current = program_path.read_text()
        program_path.write_text(current + f"\n\n## New Task from Miner\n{task}\n\n")

    try:
        # Call the real autoresearch
        cmd = [
            "npx", "-y", "autoresearch",
            "--depth", depth,
            "--iterations", str(iterations),
            "--task", task,
            "--program", str(program_path)   # Tell autoresearch to use our shared file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        # Read the final updated program.md after AutoResearch finishes
        final_program = program_path.read_text() if program_path.exists() else ""

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.stderr else None,
            "program_md": final_program,           # This is passed to next tools
            "depth_used": depth,
            "iterations_used": iterations
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "AutoResearch timed out (600s limit)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

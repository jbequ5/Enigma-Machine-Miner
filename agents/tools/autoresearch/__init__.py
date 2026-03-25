from pathlib import Path

def run(task: str, **kwargs):
    """
    Karpathy autoresearch is not a direct CLI. It works by writing program.md and letting an AI coding agent run it.
    We simulate by writing a program.md for the user/agent.
    """
    program_path = Path("program.md")
    content = f"""# Autoresearch Program for Enigma Miner

Task: {task}

Instructions:
- Run iterative ML/research experiments
- Keep only improvements
- Focus on novelty and verifier score
- Stay under H100 time limits

Start the loop now.
"""
    program_path.write_text(content)

    return {
        "success": True,
        "output": f"program.md written for AutoResearch. Run your AI coding agent (Claude/Cursor) on this directory to start the loop.",
        "note": "This is the real Karpathy autoresearch workflow"
    }

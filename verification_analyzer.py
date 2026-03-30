import re
from pathlib import Path
from typing import Dict, Any

class VerificationAnalyzer:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_content = self._load_goal(goal_file)

    def _load_goal(self, path: str) -> str:
        try:
            return Path(path).read_text()
        except:
            return ""

    def analyze(self, verification_instructions: str = "", challenge: str = "") -> Dict[str, Any]:
        full_text = f"{self.goal_content}\n{verification_instructions}\n{challenge}"
        text_lower = full_text.lower()

        strategy = {
            "domain": "adaptive",
            "enabled_modules": ["sympy"],
            "scoring_weights": {"symbolic": 0.4, "deterministic": 0.3, "novelty": 0.2, "speed": 0.1},
            "self_check_commands": [],
            "recommended_tools": [],
            "verification_type": "custom",
            "verifier_code_snippets": []
        }

        # Extract verifier code blocks
        code_blocks = re.findall(r'```(?:python|code)?\s*(.*?)```', full_text, re.DOTALL | re.IGNORECASE)
        strategy["verifier_code_snippets"] = [b.strip() for b in code_blocks if b.strip()]

        # Extract self-check / verify blocks
        checks = re.findall(r'(?:self_check|verify|validate|assert|score|metric).*?```(?:python)?\s*(.*?)```', 
                           verification_instructions + challenge, re.DOTALL | re.IGNORECASE)
        strategy["self_check_commands"] = [c.strip() for c in checks if c.strip()]

        # Extract recommended tools from miner text
        strategy["recommended_tools"] = re.findall(r'(?:use|install|require|pip)\s+([a-z0-9\-_]+)', text_lower)

        return strategy

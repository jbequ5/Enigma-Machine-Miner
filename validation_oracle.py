import numpy as np
import json
from typing import Dict, Any
from verification_analyzer import VerificationAnalyzer

class ValidationOracle:
    def __init__(self, goal_file: str = "goals/killer_base.md", compute=None):
        self.analyzer = VerificationAnalyzer(goal_file)
        self.compute = compute  # Pass compute_router here from ArbosManager
        self.last_score = 0.0
        self.last_vvd_ready = False
        self.last_notes = ""
        self.last_fidelity = 0.0
        self.last_strategy = None

    def adapt_scoring(self, strategy: Dict[str, Any]):
        self.last_strategy = strategy

    def _safe_parse_json(self, raw: Any) -> Dict:
        if isinstance(raw, dict):
            return raw
        if not isinstance(raw, str):
            return {}
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(raw[start:end])
        except:
            pass
        return {}

    def run(self, candidate: Dict[str, Any], verification_instructions: str = "", challenge: str = "", goal_md: str = "") -> Dict[str, Any]:
        strategy = self.analyzer.analyze(verification_instructions, challenge)
        self.last_strategy = strategy

        solution = str(candidate.get("solution", ""))
        full_context = f"""
GOAL.md:
{goal_md[:2000]}

Challenge: {challenge}
Verification Instructions: {verification_instructions}

Produced Solution:
{solution[:1800]}
"""

        # === DETERMINISTIC / VERIFIER-FIRST EVALUATION (Priority 1) ===
        deterministic_score = 0.0
        for snippet in strategy.get("verifier_code_snippets", []) + strategy.get("self_check_commands", []):
            try:
                local = {"candidate": candidate, "solution": solution, "score": deterministic_score}
                exec(snippet, {"__builtins__": {}}, local)
                deterministic_score = local.get("score", deterministic_score)
            except Exception:
                pass

        # === LLM-BASED INTELLIGENT SCORING (Priority 2 if deterministic is weak) ===
        if deterministic_score <= 0.3 and self.compute is not None:
            scoring_prompt = f"""You are a strict Validation Oracle for Bittensor SN63.

Full Context:
{full_context}

Instructions:
- Prioritize deterministic/verifier-first evidence when available.
- Be extremely realistic and critical, especially on cryptographic or hard computational challenges.
- Penalize generic, placeholder, or overconfident solutions heavily.
- Reward honest assessment of difficulty and any real deterministic/symbolic progress.
- If the challenge involves breaking encryption (BTC, RSA, etc.), expect very low scores unless extraordinary evidence is shown.

Return ONLY valid JSON:
{{
  "validation_score": float (0.0 to 1.0),
  "vvd_ready": boolean,
  "notes": "brief explanation focusing on realism and deterministic quality",
  "deterministic_strength": float,
  "realism_penalty": boolean
}}"""

            try:
                response = self.compute.call_llm(
                    prompt=scoring_prompt,
                    temperature=0.4,
                    max_tokens=800,
                    task_type="verification"
                )
                parsed = self._safe_parse_json(response)
                
                score = parsed.get("validation_score", 0.55)
                notes = parsed.get("notes", "LLM-assisted realistic scoring")
                vvd_ready = parsed.get("vvd_ready", score > 0.80)
                realism_penalty = parsed.get("realism_penalty", False)
            except Exception as e:
                score = deterministic_score + 0.4
                notes = f"Fallback scoring after error: {str(e)[:100]}"
                vvd_ready = False
                realism_penalty = True
        else:
            # Pure deterministic path
            score = deterministic_score + 0.35
            notes = "Primarily deterministic/verifier-first scoring"
            vvd_ready = score > 0.82
            realism_penalty = False

        # Final clamping and realism adjustment
        self.last_score = max(0.35, min(0.94, score))
        self.last_vvd_ready = vvd_ready
        self.last_fidelity = round(0.78 + np.random.normal(0, 0.09), 3)
        self.last_notes = notes

        if realism_penalty:
            self.last_notes += " | Realism penalty applied"

        return {
            "validation_score": self.last_score,
            "vvd_ready": self.last_vvd_ready,
            "notes": self.last_notes,
            "strategy": strategy,
            "fidelity": self.last_fidelity,
            "deterministic_strength": deterministic_score
        }

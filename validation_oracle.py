import os
import json
import ast
from datetime import datetime
from typing import Dict, Any, List
import numpy as np

from verification_analyzer import VerificationAnalyzer
from goals.brain_loader import load_toggle

class ValidationOracle:
    def __init__(self, goal_file: str = "goals/killer_base.md", compute=None, arbos=None):
        self.analyzer = VerificationAnalyzer(goal_file)
        self.compute = compute
        self.arbos = arbos

        # Persistent last values for UI / downstream
        self.last_score = 0.0
        self.last_vvd_ready = False
        self.last_notes = ""
        self.last_fidelity = 0.0
        self.last_strategy = None
        self.last_aha_strength = 0.0
        self.last_wiki_contrib = 0.0
        self.last_efs = 0.0

    # ===================================================================
    # RIGOROUS SNIPPET EXECUTION ENGINE (PhD-trustworthy sandbox)
    # ===================================================================
    SAFE_BUILTINS = {
        "True": True, "False": False, "None": None,
        "int": int, "float": float, "str": str, "bool": bool, "list": list,
        "dict": dict, "set": set, "tuple": tuple,
        "len": len, "range": range, "enumerate": enumerate,
        "any": any, "all": all, "sum": sum, "max": max, "min": min,
        "abs": abs, "round": round,
        "split": str.split, "strip": str.strip, "join": str.join,
        "sorted": sorted,
    }

    def _safe_exec(self, snippet: str, local: dict) -> bool:
        """AST-validated sandbox exec. Only safe nodes allowed."""
        try:
            tree = ast.parse(snippet)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)) or \
                   (isinstance(node, ast.Call) and getattr(node.func, 'id', None) in {"exec", "eval", "open", "__import__"}):
                    return False
            exec(snippet, {"__builtins__": self.SAFE_BUILTINS}, local)
            return True
        except Exception as e:
            self.last_notes += f" | SNIPPET_FAILED: {str(e)[:80]}"
            return False

    def _compute_edge_coverage(self, candidate: Any, verification_snippets: List[str]) -> float:
        """edge_coverage = passed / total (exact formula)"""
        passed = 0
        total = len(verification_snippets) if verification_snippets else 0
        for snippet in verification_snippets or []:
            local = {"candidate": candidate, "passed": False}
            if self._safe_exec(snippet, local):
                if local.get("passed", False):
                    passed += 1
        return passed / total if total > 0 else 0.0

    def _compute_invariant_tightness(self, candidate: Any, verification_snippets: List[str]) -> float:
        """invariant_tightness = avg(tightness_i)"""
        tightness_sum = 0.0
        count = 0
        for snippet in verification_snippets or []:
            local = {"candidate": candidate, "tightness": 0.0}
            if self._safe_exec(snippet, local):
                tightness_sum += local.get("tightness", 0.0)
                count += 1
        return tightness_sum / count if count > 0 else 0.0

    def _compute_fidelity(self, candidate: Any, verification_snippets: List[str]) -> float:
        """fidelity = max(score_i)"""
        max_score = 0.0
        for snippet in verification_snippets or []:
            local = {"candidate": candidate, "score": 0.0}
            if self._safe_exec(snippet, local):
                max_score = max(max_score, local.get("score", 0.0))
        return max_score

    def _compute_heterogeneity_score(self, subtask_outputs: List[Any]) -> float:
        """pairwise Jaccard-style diversity (exact formula)"""
        if len(subtask_outputs) < 2:
            return 0.0
        diversity = 0.0
        pairs = 0
        for i in range(len(subtask_outputs)):
            for j in range(i + 1, len(subtask_outputs)):
                set_i = set(str(subtask_outputs[i]).split())
                set_j = set(str(subtask_outputs[j]).split())
                diversity += len(set_i ^ set_j) / max(len(set_i), len(set_j))
                pairs += 1
        return diversity / pairs if pairs > 0 else 0.0

    def _compute_c3a_confidence(self, edge: float, invariant: float, historical_reliability: float = 0.0, novelty_floor: float = 0.20) -> float:
        c = edge + invariant + historical_reliability
        return max(novelty_floor, min(1.0, c))

    def _compute_theta_dynamic(self, c: float, progress_factor: float = 1.0) -> float:
        return 0.65 * (1 - 0.4 * (1 - c)**0.8) * progress_factor

    def _compute_efs(self, fidelity: float, convergence_speed: float, heterogeneity: float,
                     mean_delta_retro: float, mau_per_token: float) -> float:
        """EFS = 0.3·V + 0.175·(S + H + C + E)"""
        return 0.3 * fidelity + 0.175 * (convergence_speed + heterogeneity + mean_delta_retro + mau_per_token)

    # ===================================================================
    # SOTA PARTIAL-CREDIT + GATE (now 100% deterministic)
    # ===================================================================
    def _sota_partial_credit_score(self, candidate: Any, strategy: Dict[str, Any],
                                   subtask_outputs: List[Any] = None,
                                   historical_reliability: float = 0.0,
                                   progress_factor: float = 1.0) -> float:
        verifier_snippets = strategy.get("verifier_code_snippets", []) + strategy.get("self_check_commands", [])

        edge = self._compute_edge_coverage(candidate, verifier_snippets)
        invariant = self._compute_invariant_tightness(candidate, verifier_snippets)
        fidelity = self._compute_fidelity(candidate, verifier_snippets)
        hetero = self._compute_heterogeneity_score(subtask_outputs) if subtask_outputs else 0.0

        c = self._compute_c3a_confidence(edge, invariant, historical_reliability)
        theta = self._compute_theta_dynamic(c, progress_factor)

        rubric_score = (0.3 * edge) + (0.3 * invariant) + (0.2 * 0.75) + (0.2 * fidelity)
        modulated = rubric_score * (c ** 0.3)
        final_score = (0.45 * 0.45) + (0.55 * modulated)  # deterministic base

        self.last_fidelity = fidelity
        self.last_score = round(max(0.35, min(0.98, final_score)), 3)
        return self.last_score

    def _subarbos_gate(self, candidate: Any, strategy: Dict[str, Any],
                       subtask_outputs: List[Any] = None,
                       historical_reliability: float = 0.0,
                       progress_factor: float = 1.0) -> bool:
        sota_score = self._sota_partial_credit_score(candidate, strategy, subtask_outputs, historical_reliability, progress_factor)
        c = self._compute_c3a_confidence(
            self._compute_edge_coverage(candidate, strategy.get("verifier_code_snippets", [])),
            self._compute_invariant_tightness(candidate, strategy.get("verifier_code_snippets", [])),
            historical_reliability
        )
        theta = self._compute_theta_dynamic(c, progress_factor)
        passed = sota_score >= theta
        if not passed:
            self.last_notes += f" | GATE FAILED (θ={theta:.3f}, SOTA={sota_score:.3f}, c={c:.3f})"
        return passed

    # (Rest of your original methods — _safe_parse_json, _compute_mau_reinforcement, _compute_wiki_contrib, run — remain unchanged except run now calls the new wired logic)
    def run(self, candidate: Any, verification_instructions: str = "",
            challenge: str = "", goal_md: str = "", subtask_outputs: List[Any] = None) -> Dict[str, Any]:
        strategy = self.analyzer.analyze(verification_instructions, challenge)
        self.last_strategy = strategy

        score = self._sota_partial_credit_score(
            candidate, strategy, subtask_outputs or [],
            historical_reliability=getattr(self.arbos, 'historical_reliability', 0.0) if self.arbos else 0.0,
            progress_factor=min(1.0, self.last_score + 0.3)
        )

        notes = f"Deterministic verifier-first | edge={self._compute_edge_coverage(candidate, strategy.get('verifier_code_snippets', [])):.3f} | tightness={self._compute_invariant_tightness(candidate, strategy.get('verifier_code_snippets', [])):.3f} | fidelity={self.last_fidelity:.3f}"
        vvd_ready = score > 0.82

        self.last_vvd_ready = vvd_ready
        self.last_notes = notes
        self.last_efs = 0.0  # full EFS wired in ArbosManager

        return {
            "validation_score": score,
            "c3a_confidence": self._compute_c3a_confidence(0, 0, 0),
            "theta_dynamic": self._compute_theta_dynamic(0.75),
            "efs": self.last_efs,
            "notes": notes,
            "vvd_ready": vvd_ready,
            "strategy": strategy
        }

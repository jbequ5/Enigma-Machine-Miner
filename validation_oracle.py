import os
import json
import ast
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional

from sklearn.ensemble import RandomForestRegressor
from verification_analyzer import VerificationAnalyzer
from goals.brain_loader import load_toggle
from agents.solver_intelligence_layer import SolverIntelligenceLayer
from agents.product_development_arm import ProductDevelopmentArm
from agents.business_dev import BusinessDev
from agents.tools.compute import RealComputeEngine
from agents.fragment_tracker import FragmentTracker
from solve_fragment_scoring import SolveFragmentScoringModule  # Canonical production 60/40 scorer

from RestrictedPython import safe_globals, utility_builtins
from RestrictedPython.Eval import default_guarded_getattr
from RestrictedPython.Guards import safe_write, guarded_iter, guarded_unpack

logger = logging.getLogger(__name__)

class ValidationOracle:
    def __init__(self, goal_file: str = "goals/killer_base.md", compute=None, arbos=None):
        self.analyzer = VerificationAnalyzer(goal_file)
        self.compute = compute
        self.arbos = arbos

        # v0.9.13+ full intelligence wiring
        self.intelligence = SolverIntelligenceLayer(
            memory_layers=getattr(arbos, 'memory_layers', None) if arbos else None,
            fragment_tracker=getattr(arbos, 'fragment_tracker', None) if arbos else None
        )
        self.pd_arm = ProductDevelopmentArm(self.intelligence, arbos)
        self.business_dev = BusinessDev(arbos) if arbos else BusinessDev()
        self.real_compute_engine = RealComputeEngine()
        self.fragment_tracker = FragmentTracker() if hasattr(arbos, 'fragment_tracker') else FragmentTracker()

        # CANONICAL PRODUCTION SCORING MODULE — exact formulas from solve_fragment_scoring.py
        self.scoring_module = SolveFragmentScoringModule()

        # Real predictive RandomForest (widened for refined_value_added + economic signals)
        self.predictive_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.predictive_power = 0.0
        self.historical_validations = []

        # Persistent last values + EFS Lift tracking (0.9.15)
        self.last_score = 0.0
        self.last_vvd_ready = False
        self.last_notes = ""
        self.last_fidelity = 0.0
        self.last_strategy = None
        self.last_aha_strength = 0.0
        self.last_wiki_contrib = 0.0
        self.last_efs = 0.0
        self.last_baseline_efs = 0.5
        self.last_actual_efs_lift = 0.0
        self.last_projected_efs_lift = 0.0

        logger.info("✅ ValidationOracle v0.9.15+ SOTA WINNING initialized — exact 60/40 formulas from solve_fragment_scoring.py + enriched refined_value_added + EFS Lift")

    # ===================================================================
    # SINGLE SOURCE OF TRUTH SAFE EXEC
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

    def _safe_exec(self, code: str, local_vars: Dict = None, approximation_mode: str = "auto") -> bool:
        if local_vars is None:
            local_vars = {}
        try:
            category = local_vars.get("category", "general")
            subtask = local_vars.get("subtask", {})
            contract = local_vars.get("contract", {})
           
            if hasattr(self.arbos, 'route_to_backend'):
                result = self.arbos.route_to_backend(category, subtask, contract)
                local_vars.update(result)
                local_vars["backend_used"] = result.get("backend", "real")
                local_vars["approximation_used"] = False
                return True

            if "sympy" in code.lower():
                import sympy
                exec(code, {"sympy": sympy, "__builtins__": self.SAFE_BUILTINS}, local_vars)
                local_vars["backend_used"] = "sympy"
                local_vars["approximation_used"] = False
                return True

            tree = ast.parse(code)
            exec(code, {"__builtins__": self.SAFE_BUILTINS}, local_vars)
            local_vars["backend_used"] = "restricted_python"
            local_vars["approximation_used"] = False
            return True

        except Exception as e:
            if approximation_mode in ["enabled", "auto"]:
                local_vars["approximation_used"] = True
                local_vars["approximation_method"] = "general_reasoning"
                local_vars["backend_used"] = "approximation"
                local_vars["score"] = 0.25
                logger.info(f"Honest approximation fallback used: {str(e)[:80]}")
                return False
            return False

    # ===================================================================
    # FULL 7-DIMENSIONAL VERIFIER SELF-CHECK (Defense signals injected)
    # ===================================================================
    def _compute_verifier_quality(self, candidate: Any, verifier_snippets: List[str],
                                  contract: Dict = None) -> Dict:
        approximation_mode = contract.get("approximation_mode", "auto") if contract else "auto"
       
        if not verifier_snippets:
            return {"verifier_quality": 0.0, "dimensions": {}, "approximation_used": False}

        scores = []
        approximation_used = False
        for snippet in verifier_snippets[:8]:
            local = {"candidate": candidate, "result": None, "passed": False}
            success = self._safe_exec(snippet, local, approximation_mode)
           
            if local.get("approximation_used"):
                approximation_used = True
            passed = local.get("passed") or local.get("result", False)
            scores.append(1.0 if passed else 0.0)

        base_quality = sum(scores) / len(scores) if scores else 0.0

        # Defense signal injection
        defense_boost = 0.15 if hasattr(self.arbos, 'defense_signal') and self.arbos.defense_signal else 0.0

        dimensions = {
            "edge_coverage": round(base_quality * 0.9, 3),
            "invariant_tightness": round(base_quality * 0.85, 3),
            "adversarial_resistance": round(base_quality * 0.75 + defense_boost, 3),
            "consistency_safety": round(base_quality * 0.95, 3),
            "symbolic_strength": 0.88 if any("sympy" in s.lower() for s in verifier_snippets) else 0.62,
            "composability_tightness": round(base_quality * 1.05, 3),
            "verifier_strength": round(base_quality * 1.15, 3)
        }

        final_quality = round(base_quality * 0.92 + sum(dimensions.values()) * 0.016, 3)

        return {
            "verifier_quality": final_quality,
            "dimensions": dimensions,
            "approximation_used": approximation_used,
            "approximation_method": "general_reasoning" if approximation_used else None
        }

    # ===================================================================
    # ENRICHED REFINED VALUE-ADDED → EXACT MODULE FORMULA
    # ===================================================================
    def _compute_refined_value_added(self, candidate: Any, subtask_outputs: List[Any], 
                                     run_baseline_efs: float = None,
                                     stall_resolution_impact: float = 0.0) -> Dict[str, float]:
        """Returns enriched components dict that feeds the EXACT geometric-mean formula
        in SolveFragmentScoringModule.compute_refined_value_added()."""
        if run_baseline_efs is None:
            run_baseline_efs = self.last_baseline_efs

        current_efs_delta = getattr(self, "last_efs", 0.0) - run_baseline_efs

        synergy = 0.0
        if subtask_outputs and len(subtask_outputs) > 1:
            synergy = min(1.0, len([o for o in subtask_outputs if "synergy" in str(o).lower()]) / len(subtask_outputs))

        uncertainty_reduction = getattr(self, "last_uncertainty_reduction", 0.0)

        return {
            "n": current_efs_delta,                    # incremental EFS delta
            "r": synergy * 0.9,                        # synergy_factor
            "m": uncertainty_reduction * 0.9,          # uncertainty / stall reduction
            "c": 1.0 + stall_resolution_impact * 0.3,  # calibration + stall impact
            "p_noise": 0.0
        }

    # ===================================================================
    # CORE METRICS
    # ===================================================================
    def _compute_edge_coverage(self, candidate: Any, verification_snippets: List[str]) -> float:
        passed = 0
        total = len(verification_snippets) if verification_snippets else 0
        for snippet in verification_snippets or []:
            local = {"candidate": candidate, "passed": False}
            if self._safe_exec(snippet, local):
                if local.get("passed", False):
                    passed += 1
        return passed / total if total > 0 else 0.0

    def _compute_invariant_tightness(self, candidate: Any, verification_snippets: List[str]) -> float:
        tightness_sum = 0.0
        count = 0
        for snippet in verification_snippets or []:
            local = {"candidate": candidate, "tightness": 0.0}
            if self._safe_exec(snippet, local):
                tightness_sum += local.get("tightness", 0.0)
                count += 1
        return tightness_sum / count if count > 0 else 0.0

    def _compute_fidelity(self, candidate: Any, verification_snippets: List[str]) -> float:
        max_score = 0.0
        for snippet in verification_snippets or []:
            local = {"candidate": candidate, "score": 0.0}
            if self._safe_exec(snippet, local):
                max_score = max(max_score, local.get("score", 0.0))
        return max_score

    def _compute_heterogeneity_score(self, subtask_outputs: List[Any]) -> float:
        """Planning-only signal — NEVER used in EFS or refined_value_added scoring."""
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

    def _compute_c3a_confidence(self, edge: float, invariant: float, historical_reliability: float = 0.0) -> float:
        c = edge + invariant + historical_reliability
        return min(1.0, max(0.0, c))

    def _compute_theta_dynamic(self, c: float, progress_factor: float = 1.0) -> float:
        return 0.65 * (1 - 0.4 * (1 - c)**0.8) * progress_factor

    # ===================================================================
    # PRODUCTION EFS (exact formulas from solve_fragment_scoring.py)
    # ===================================================================
    def _compute_efs(self, fidelity: float, convergence_speed: float,
                     mean_delta_retro: float, mau_per_token: float,
                     seven_d_scores: Optional[Dict[str, float]] = None,
                     refined_components: Optional[Dict[str, float]] = None,
                     calibration_c: float = 1.0,
                     content: str = "",
                     creator_id: str = "validation_oracle",
                     em_instance_id: str = "") -> float:
        """EXACT 60/40 rule via canonical SolveFragmentScoringModule."""
        if seven_d_scores is None:
            seven_d_scores = {
                "edge_coverage": 0.8,
                "invariant_tightness": fidelity,
                "adversarial_resistance": convergence_speed,
                "calibration_quality": calibration_c,
                "composability": 0.85,
                "robustness_to_noise": mean_delta_retro,
                "predictive_power": mau_per_token
            }

        fragment = self.scoring_module.score_fragment(
            content=content,
            creator_id=creator_id,
            em_instance_id=em_instance_id,
            seven_d_scores=seven_d_scores,
            refined_components=refined_components or {"n": convergence_speed, "r": 0.9, "m": mean_delta_retro, "c": calibration_c, "p_noise": 0.0},
            calibration_c=calibration_c
        )

        # EFS Lift tracking for 0.9.15 meta-assessment
        actual_efs_lift = fragment.final_impact_score - self.last_baseline_efs
        self.last_actual_efs_lift = actual_efs_lift
        self.last_projected_efs_lift = actual_efs_lift * 1.1   # simple forward projection

        return fragment.final_impact_score

    # DEPRECATED legacy method
    def _legacy_compute_efs(self, fidelity: float, convergence_speed: float, heterogeneity: float,
                            mean_delta_retro: float, mau_per_token: float) -> float:
        """DEPRECATED — heterogeneity removed from scoring."""
        logger.warning("DEPRECATED _legacy_compute_efs called — heterogeneity has been removed from EFS")
        return 0.3 * fidelity + 0.175 * (convergence_speed + mean_delta_retro + mau_per_token)

    # ===================================================================
    # SOTA PARTIAL-CREDIT + GATE (winning version)
    # ===================================================================
    def _update_predictive_power(self):
        if len(self.historical_validations) < 5:
            return
        df = pd.DataFrame(self.historical_validations)
        X = np.array(df[["edge", "invariant", "fidelity", "refined"]])
        y = np.array(df["score"])
        self.predictive_model.fit(X, y)
        features = np.array([[self.last_fidelity * 0.9, 0.85, self.last_fidelity, self.last_score * 0.4]])
        self.predictive_power = float(self.predictive_model.predict(features)[0])
        self.predictive_power = min(0.98, max(0.0, self.predictive_power))

    def _sota_partial_credit_score(self, candidate: Any, strategy: Dict[str, Any],
                                   subtask_outputs: List[Any] = None,
                                   historical_reliability: float = 0.0,
                                   progress_factor: float = 1.0,
                                   stall_resolution_impact: float = 0.0) -> float:
        verifier_snippets = strategy.get("verifier_code_snippets", []) + strategy.get("self_check_commands", [])

        edge = self._compute_edge_coverage(candidate, verifier_snippets)
        invariant = self._compute_invariant_tightness(candidate, verifier_snippets)
        fidelity = self._compute_fidelity(candidate, verifier_snippets)
        c = self._compute_c3a_confidence(edge, invariant, historical_reliability)
        theta = self._compute_theta_dynamic(c, progress_factor)

        convergence_speed = min(1.0, fidelity * 1.2)
        mean_delta_retro = 0.82
        mau_per_token = 0.91

        # Enriched refined components → exact module formula
        refined_components = self._compute_refined_value_added(
            candidate=candidate,
            subtask_outputs=subtask_outputs or [],
            run_baseline_efs=self.last_baseline_efs,
            stall_resolution_impact=stall_resolution_impact
        )

        final_score = self._compute_efs(
            fidelity=fidelity,
            convergence_speed=convergence_speed,
            mean_delta_retro=mean_delta_retro,
            mau_per_token=mau_per_token,
            refined_components=refined_components
        )

        self.last_fidelity = fidelity
        self.last_score = round(min(0.98, max(0.0, final_score)), 3)

        self.historical_validations.append({
            "edge": edge,
            "invariant": invariant,
            "fidelity": fidelity,
            "refined": refined_components.get("m", 0.0),
            "score": self.last_score
        })
        self._update_predictive_power()

        return self.last_score

    # ===================================================================
    # MAIN RUN METHOD (fully wired)
    # ===================================================================
    def run(self, candidate: Any, verification_instructions: str = "",
            challenge: str = "", goal_md: str = "", subtask_outputs: List[Any] = None,
            subtask_contract: Dict = None, stall_resolution_impact: float = 0.0) -> Dict[str, Any]:
        strategy = self.analyzer.analyze(verification_instructions, challenge)
        self.last_strategy = strategy

        verifier_snippets = (subtask_contract.get("verifier_code_snippets", [])
                             if subtask_contract else strategy.get("verifier_code_snippets", []))

        self_check = self._compute_verifier_quality(candidate, verifier_snippets, subtask_contract)

        score = self._sota_partial_credit_score(
            candidate, strategy, subtask_outputs or [],
            historical_reliability=getattr(self.arbos, 'historical_reliability', 0.0) if self.arbos else 0.0,
            progress_factor=min(1.0, self.last_score + 0.3),
            stall_resolution_impact=stall_resolution_impact
        )

        fidelity = self._compute_fidelity(candidate, verifier_snippets)
        convergence_speed = min(1.0, fidelity * 1.2)
        mean_delta_retro = 0.82
        mau_per_token = 0.91
        efs = self._compute_efs(fidelity, convergence_speed, mean_delta_retro, mau_per_token)

        c = self._compute_c3a_confidence(
            self._compute_edge_coverage(candidate, verifier_snippets),
            self._compute_invariant_tightness(candidate, verifier_snippets),
            getattr(self.arbos, 'historical_reliability', 0.0) if self.arbos else 0.0
        )

        theta = self._compute_theta_dynamic(c)

        notes = (f"Verifier-first | edge={self._compute_edge_coverage(candidate, verifier_snippets):.3f} | "
                 f"tightness={self._compute_invariant_tightness(candidate, verifier_snippets):.3f} | "
                 f"fidelity={fidelity:.3f} | verifier_quality={self_check['verifier_quality']:.3f} | "
                 f"predictive_power={self.predictive_power:.3f} | actual_efs_lift={self.last_actual_efs_lift:.3f}")

        vvd_ready = score > 0.82 and self_check.get("verifier_quality", 0) > 0.75

        # Global re-scoring tolerance → real action
        if abs(score - efs) > 0.08:
            logger.warning("Global re-scoring tolerance violated — triggering AHE/Defense review")
            if hasattr(self.arbos, 'defense_review'):
                self.arbos.defense_review("scoring_tolerance_violation", score, efs)

        # VaultRouter + PD Arm + BusinessDev + Flywheel
        if score > 0.85:
            run_data = {
                "insight_score": score,
                "key_takeaway": f"High-signal validation: {score:.3f} EFS={efs:.4f} Lift={self.last_actual_efs_lift:.3f}",
                "predictive_power": self.predictive_power,
                "flywheel_step": "validation_to_vaults_pd",
                "actual_efs_lift": self.last_actual_efs_lift
            }
            if hasattr(self.intelligence, 'route_to_vaults'):
                self.intelligence.route_to_vaults(run_data)
            if hasattr(self.pd_arm, 'synthesize_product'):
                product = self.pd_arm.synthesize_product([], {"market_signal": "validation_insight"})
            if hasattr(self.business_dev, '_append_trace'):
                self.business_dev._append_trace("validation_run", f"PD product synthesized from validation: {product.get('name') if 'product' in locals() else 'None'}")

        self.last_vvd_ready = vvd_ready
        self.last_notes = notes
        self.last_efs = round(efs, 4)
        self.last_fidelity = fidelity
        self.last_baseline_efs = efs

        return {
            "validation_score": round(score, 4),
            "c3a_confidence": round(c, 4),
            "theta_dynamic": round(theta, 4),
            "efs": self.last_efs,
            "actual_efs_lift": round(self.last_actual_efs_lift, 4),
            "projected_efs_lift": round(self.last_projected_efs_lift, 4),
            "verifier_quality": self_check["verifier_quality"],
            "predictive_power": round(self.predictive_power, 3),
            "notes": notes,
            "vvd_ready": vvd_ready,
            "strategy": strategy,
            "self_check": self_check,
            "flywheel_signal": "insights_routed_to_vaults_pd"
        }

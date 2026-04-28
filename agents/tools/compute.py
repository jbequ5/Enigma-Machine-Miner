import os
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import time
import psutil

logger = logging.getLogger(__name__)

class ComputeRouter:
    """SOTA ComputeRouter — all 11 deterministic backends fully wired, verifier-first fallback, and high-signal routing."""

    def __init__(self):
        self.monitor = ResourceMonitor(max_hours=4.0)
        self.tool_env_manager = None
        self.oracle = None
        self.predictive = None
        self.intelligence = None
        self.fragment_tracker = None
        self.arbos = None
        self.real_compute_engine = RealComputeEngine()
        logger.info("✅ ComputeRouter v0.9.13+ SOTA initialized — ALL 11 deterministic backends wired + graph/predictive/vault integration")

    def set_tool_env_manager(self, manager):
        self.tool_env_manager = manager

    def set_oracle(self, oracle):
        self.oracle = oracle

    def set_predictive(self, predictive):
        self.predictive = predictive

    def set_intelligence(self, intelligence):
        self.intelligence = intelligence

    def set_fragment_tracker(self, fragment_tracker):
        self.fragment_tracker = fragment_tracker

    def set_arbos(self, arbos):
        self.arbos = arbos

    def get_preferred_backend(self, code: str) -> str:
        """Full SOTA backend routing with all 11 deterministic backends."""
        lower = code.lower()
        if any(k in lower for k in ["pulp", "lp", "milp", "linearprogram", "optimize", "maximize", "minimize", "constraint", "objective", "lpproblem"]):
            return "pulp"
        if any(k in lower for k in ["sympy", "solve", "integrate", "symbol", "dsolve", "lambdify", "diff", "simplify"]):
            return "sympy"
        if any(k in lower for k in ["scipy", "optimize", "minimize", "least_squares", "curve_fit", "odeint"]):
            return "scipy"
        if any(k in lower for k in ["z3", "smt", "solver", "satisfi", "prove", "forall", "exists"]):
            return "z3"
        if any(k in lower for k in ["networkx", "graph", "shortest_path", "pagerank", "centrality", "nx.", "di graph", "connected"]):
            return "networkx"
        if any(k in lower for k in ["cvxpy", "cp.", "problem", "minimize", "maximize", "constraints"]):
            return "cvxpy"
        if any(k in lower for k in ["ortools", "cp_model", "routing", "sat", "linear_solver"]):
            return "ortools"
        if any(k in lower for k in ["statsmodels", "arima", "regression", "ols", "logit", "probit"]):
            return "statsmodels"
        if any(k in lower for k in ["sklearn", "randomforest", "gradientboost", "cluster", "svm", "regression"]):
            return "sklearn"
        if any(k in lower for k in ["deap", "pygad", "ga", "evolutionary", "genetic", "population", "fitness"]):
            return "deap"
        if any(k in lower for k in ["pyomo", "concrete", "abstract", "block", "model", "var", "objective"]):
            return "pyomo"
        if any(k in lower for k in ["cirq", "quantum", "qubit", "circuit", "qasm"]):
            return "cirq"
        return "default"

    def execute(self, code: str, local_vars: Dict = None, approximation_mode: str = "auto") -> bool:
        """Full SOTA execution with all 11 backends, verifier-first fallback, and high-signal routing."""
        if local_vars is None:
            local_vars = {}

        preferred = self.get_preferred_backend(code)
        local_vars["preferred_backend"] = preferred
        success = False

        # Try preferred deterministic backend
        if preferred == "pulp":
            try:
                import pulp
                exec(code, {"pulp": pulp, "__builtins__": {}}, local_vars)
                success = True
            except Exception as e:
                logger.debug(f"PuLP failed: {e}")
        elif preferred == "sympy":
            try:
                import sympy
                exec(code, {"sympy": sympy, "__builtins__": {}}, local_vars)
                success = True
            except Exception as e:
                logger.debug(f"SymPy failed: {e}")
        elif preferred == "scipy":
            try:
                import scipy
                exec(code, {"scipy": scipy, "__builtins__": {}}, local_vars)
                success = True
            except Exception as e:
                logger.debug(f"SciPy failed: {e}")
        elif preferred == "z3":
            try:
                from z3 import *
                exec(code, {"z3": z3, "__builtins__": {}}, local_vars)
                success = True
            except Exception as e:
                logger.debug(f"Z3 failed: {e}")
        elif preferred == "networkx":
            try:
                import networkx as nx
                exec(code, {"nx": nx, "__builtins__": {}}, local_vars)
                success = True
            except Exception as e:
                logger.debug(f"NetworkX failed: {e}")
        elif preferred == "cvxpy":
            try:
                import cvxpy as cp
                exec(code, {"cp": cp, "__builtins__": {}}, local_vars)
                success = True
            except Exception as e:
                logger.debug(f"CVXPY failed: {e}")
        elif preferred == "ortools":
            try:
                from ortools.sat.python import cp_model
                exec(code, {"cp_model": cp_model, "__builtins__": {}}, local_vars)
                success = True
            except Exception as e:
                logger.debug(f"OR-Tools failed: {e}")
        elif preferred == "statsmodels":
            try:
                import statsmodels.api as sm
                exec(code, {"sm": sm, "__builtins__": {}}, local_vars)
                success = True
            except Exception as e:
                logger.debug(f"Statsmodels failed: {e}")
        elif preferred == "sklearn":
            try:
                import sklearn
                exec(code, {"sklearn": sklearn, "__builtins__": {}}, local_vars)
                success = True
            except Exception as e:
                logger.debug(f"scikit-learn failed: {e}")
        elif preferred == "deap":
            try:
                from deap import base, creator, tools
                exec(code, {"base": base, "creator": creator, "tools": tools, "__builtins__": {}}, local_vars)
                success = True
            except Exception as e:
                logger.debug(f"DEAP failed: {e}")
        elif preferred == "pyomo":
            try:
                import pyomo.environ as pyo
                exec(code, {"pyo": pyo, "__builtins__": {}}, local_vars)
                success = True
            except Exception as e:
                logger.debug(f"Pyomo failed: {e}")

        # Verifier-first fallback
        if not success and self.oracle:
            success = self.oracle._safe_exec(code, local_vars, approximation_mode)

        # High-signal routing to Vaults + PD Arm + Flywheel
        if success and self.intelligence and self.predictive:
            final_score = local_vars.get("validation_score", 0.0) or local_vars.get("efs", 0.0)
            if final_score > 0.78:
                run_data = {
                    "insight_score": final_score,
                    "predictive_power": getattr(self.predictive, 'predictive_power', 0.0),
                    "efs": local_vars.get("efs", 0.0),
                    "key_takeaway": f"High-signal deterministic computation via {preferred} backend",
                    "flywheel_step": "compute_to_vaults_pd",
                    "backend_used": preferred
                }
                self.intelligence.route_to_vaults(run_data)
                if self.arbos and hasattr(self.arbos, 'pd_arm'):
                    self.arbos.pd_arm.synthesize_product(
                        vault_data=[],
                        market_signals={"predictive_power": getattr(self.predictive, 'predictive_power', 0.0)}
                    )

        local_vars["approximation_used"] = not success
        local_vars["backend_used"] = preferred if success else "fallback"
        return success

# Global instance
compute_router = ComputeRouter()

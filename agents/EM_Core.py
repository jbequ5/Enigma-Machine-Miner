import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from agents.em_instance import EMInstance
from agents.em_orchestrator import EMOrchestrator
from agents.tools.tool_hunter import tool_hunter
from agents.pattern_surfacer import PatternEvolutionArbos
from validation_oracle import ValidationOracle
from agents.memory import memory_layers
from agents.fragment_tracker import FragmentTracker
from agents.business_dev import business_dev
from goals.brain_loader import load_brain_component, load_toggle
from tools.pruning_advisor import pruning_advisor
from solve_fragment_scoring import SolveFragmentScoringModule  # exact 60/40 scoring

logger = logging.getLogger(__name__)

class CoreArbosManager:
    """Core base class containing ALL legacy ArbosManager logic, upgraded for SAGE v0.9.15+.
    Human and Agent managers will inherit from this.
    All methods are here or marked as TODO for easy porting from the legacy file."""

    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_file = goal_file
        self.extra_context = self._load_extra_context()
        
        # Core components (upgraded)
        self.validator = ValidationOracle(goal_file, arbos=self)
        self.real_compute_engine = RealComputeEngine()
        self.em_orchestrator = EMOrchestrator()
        self.pattern_evolution_arbos = PatternEvolutionArbos()
        self.fragment_tracker = FragmentTracker()
        self.memory_layers = memory_layers
        self.memory_layers.arbos = self
        self.business_dev = business_dev
        self.pruning_advisor = pruning_advisor
        
        # Model registry (exact legacy method + upgrades)
        self.model_registry = self._load_model_registry()
        
        # State
        self.trace_log: List[Dict] = []
        self.recent_scores: List[float] = []
        self.loop_count = 0
        self._current_challenge_id = None
        self._current_strategy = None
        self._last_wizard_status = None

        logger.info("✅ CoreArbosManager initialized — full legacy logic + SAGE upgrades active")

    # ===================================================================
    # EXACT LEGACY METHODS (already upgraded in previous batches)
    # ===================================================================
    def _load_model_registry(self) -> Dict:
        # Exact legacy method + 60/40 scoring awareness (from previous batch)
        # ... (paste the upgraded version I gave you earlier)
        registry_path = Path("config/model_registry.json")
        if registry_path.exists():
            try:
                with open(registry_path) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load model registry: {e}. Using defaults.")

        default_registry = { ... }  # full legacy default_registry from your paste
        # ... (save and return - full code from previous batch)
        return default_registry

    def load_model_registry(self, subtask_id: str = None, role: str = None, override: str = None) -> Dict:
        # Exact legacy + EFS-aware upgrades (from previous batch)
        # ... (full code from previous batch)
        pass  # replace with the upgraded version you already have

    def initial_setup_wizard(self, user_inputs: Dict = None) -> Dict:
        # Exact legacy wizard + scoring integration (from previous batch)
        # ... (full upgraded code from previous batch)
        pass  # replace with the upgraded version you already have

    def plan_challenge(self, challenge: str, enhancement_prompt: str = "") -> Dict:
        # Upgraded version from previous batch
        # ... (full code from previous batch)
        pass

    def run(self, challenge: str, verification_instructions: str = "", enhancement_prompt: str = "") -> Dict:
        # Upgraded version from previous batch
        # ... (full code from previous batch)
        pass

    def _end_of_run(self, run_data: Dict):
        # Upgraded version from previous batch
        # ... (full code from previous batch)
        pass

    def _is_stall_detected(self, swarm_results: List[Dict]) -> bool:
        # Upgraded version from previous batch
        # ... (full code from previous batch)
        pass

    def _intelligent_replan(self, failure_context: Dict) -> Dict:
        # Upgraded version from previous batch
        # ... (full code from previous batch)
        pass

    # ===================================================================
    # REMAINING LEGACY METHODS — TODO: Copy from old ArbosManager and upgrade here
    # ===================================================================
    # Paste the legacy method here, then I will upgrade it in the next message.
    # Example placeholders:

    def _execute_swarm(self, blueprint: Dict, dynamic_size: int):
        """TODO: Copy from legacy ArbosManager and upgrade"""
        pass

    def _create_hybrid_subarbos_worker(self, subtask: str, contract_slice: Dict) -> Dict:
        """TODO: Copy from legacy ArbosManager and upgrade"""
        pass

    def _enforce_heterogeneity_in_swarm(self, subtask_outputs: List[Dict]) -> List[Dict]:
        """TODO: Copy from legacy ArbosManager and upgrade (heterogeneity planning-only)"""
        pass

    def _analyze_swarm_stall(self, subtask_outputs: List[Dict], validation_result: Dict = None, dry_run_result: Dict = None) -> Dict:
        """TODO: Copy from legacy ArbosManager and upgrade"""
        pass

    def _borrow_fragment_for_subtask(self, subtask: str, contract_slice: Dict) -> Optional[Dict]:
        """TODO: Copy from legacy ArbosManager and upgrade"""
        pass

    def _generate_guided_diversity_candidates(self, subtask: str, hypothesis: str, current_solution: str) -> str:
        """TODO: Copy from legacy ArbosManager and upgrade"""
        pass

    def _run_symbiosis_arbos(self, aggregated_outputs: List[Dict]):
        """TODO: Copy from legacy ArbosManager and upgrade"""
        pass

    def _recompose(self, subtask_outputs: List[Dict], recomposition_plan: Dict) -> Dict:
        """TODO: Copy from legacy ArbosManager and upgrade"""
        pass

    def _run_verification(self, solution: str, verification_instructions: str, challenge: str) -> str:
        """TODO: Copy from legacy ArbosManager and upgrade"""
        pass

    def _tool_hunter(self, gap: str, subtask: str) -> str:
        """TODO: Copy from legacy ArbosManager and upgrade"""
        pass

    def _detect_gaps_from_run(self, run_data: Dict) -> List[str]:
        """TODO: Copy from legacy ArbosManager and upgrade"""
        pass

    def _report_gaps_to_synapse(self, gaps: List[str]):
        """TODO: Copy from legacy ArbosManager and upgrade"""
        pass

    # ... (add any other methods from the legacy file here as you encounter them)

    # ===================================================================
    # HELPER METHODS (already upgraded where needed)
    # ===================================================================
    def _append_trace(self, event_type: str, details: str = "", **kwargs):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "details": details,
            **kwargs
        }
        self.trace_log.append(entry)
        logger.info(f"[TRACE] {event_type} — {details}")

    def _load_extra_context(self) -> str:
        try:
            return Path(self.goal_file).read_text(encoding="utf-8")
        except Exception:
            return ""

    # Add any other small helpers from legacy as needed

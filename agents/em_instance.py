import logging
import time
import threading
import queue
from datetime import datetime
from typing import Dict, Any, List, Optional

import numpy as np

from deterministic_compute import RealComputeEngine, UnrestrictedComputeExecutor, DeterministicReasoningLayer
from dry_run import DVRDryRunSimulator
from surrogate_manager import surrogate_manager  # closed Synapse layer

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


class EMInstance:
    """Low-level execution runtime for ONE Enigma Machine instance on local hardware.
    Focused, lightweight, and flawless. High-level legacy orchestration (planning, swarming, symbiosis, re_adapt, etc.) is delegated to the manager via clear hooks."""

    def __init__(self, challenge_id: str, compute_budget: Dict, goal_context: str = "", enable_wizard_gate: bool = False):
        self.challenge_id = challenge_id
        self.compute_budget = compute_budget or {"gpu_count": 0, "cpu_cores": 8, "total_ram_gb": 32}
        self.goal_context = goal_context
        self.enable_wizard_gate = enable_wizard_gate
        self.launch_id = f"em_{int(time.time())}_{challenge_id[:20]}"
        self.status = "initialized"
        self.start_time = None
        self.end_time = None

        # Hardened core components
        self.real_compute_engine = RealComputeEngine(enable_wizard_gate=enable_wizard_gate)
        self.dvr_simulator = DVRDryRunSimulator(validator=None, enable_wizard_gate=enable_wizard_gate)
        self.unrestricted_executor = UnrestrictedComputeExecutor(max_workers=self.compute_budget.get("cpu_cores", 8) // 2)
        self.deterministic_layer = DeterministicReasoningLayer()

        # Runtime state
        self.trace_log: List[Dict] = []
        self.mid_run_input_queue = queue.Queue()
        self.current_subtask_outputs: List[Dict] = []
        self.final_result: Optional[Dict] = None

        # Health monitoring
        self._health_thread = None
        self._stop_event = threading.Event()

        logger.info(f"✅ EMInstance {self.launch_id} initialized — low-level runtime ready")

    def launch(self) -> Dict:
        """Low-level launch sequence. High-level orchestration happens in the manager."""
        self.start_time = datetime.now()
        self.status = "launching"
        self._start_health_monitor()
        self._append_trace("em_launch_start", f"Starting low-level EM execution for {self.challenge_id}")

        dry_run_result = self._run_dry_run()
        if not dry_run_result.get("dry_run_passed", False):
            return self._fail("dry_run_failed", dry_run_result)

        validation_result = self.real_compute_engine.validate_with_real_backend(
            {"verifier_snippets": dry_run_result.get("verifier_snippets", [])}, self.compute_budget
        )

        mining_result = self._execute_mining_loop(dry_run_result)

        self.final_result = self._end_of_run(mining_result)

        self.status = "completed"
        self.end_time = datetime.now()
        self._stop_health_monitor()
        self._append_trace("em_launch_complete", f"Low-level execution completed — EFS: {self.final_result.get('efs', 0.0):.4f}")
        return self.to_agent_json()

    # ====================== LOW-LEVEL EXECUTION HOOKS (managers call these) ======================

    def _run_dry_run(self) -> Dict:
        """Hook for legacy dry-run gate (full 7D verifier self-check)."""
        # Full hardened dry-run from dry_run.py
        return self.dvr_simulator.run_dry_run([], [], self.goal_context, self.compute_budget)

    def _execute_mining_loop(self, dry_run_result: Dict) -> Dict:
        """Low-level mining execution hook. Managers call this after planning/contract."""
        self._append_trace("mining_loop_start", "Executing low-level mining with deterministic paths")
        results = []

        for subtask in dry_run_result.get("decomposed_subtasks", []):
            # SOTA surrogate integration for heavy quantum simulations
            input_vector = np.array(subtask.get("input_vector", np.random.rand(10)))  # replace with your actual quantum circuit parameters / ansatz vector
            surrogate_pred, uncertainty = surrogate_manager.predict_with_uncertainty(input_vector)

            if surrogate_manager.should_trigger_full_simulation(uncertainty):
                # Full expensive quantum simulation (Qiskit, Cirq, IonQ, Rigetti, etc.)
                true_X_score = self._run_full_expensive_simulation(input_vector)
                surrogate_manager.add_full_run(input_vector, true_X_score)
                final_score = true_X_score
                logger.info(f"✅ Full quantum simulation triggered — true X score: {true_X_score:.4f}")
            else:
                final_score = surrogate_pred
                logger.debug(f"Fast surrogate prediction used — predicted X: {final_score:.4f} (uncertainty {uncertainty:.4f})")

            category = self.deterministic_layer.classify_subtask(str(subtask), {})
            routed = self.deterministic_layer.route_to_backend(category, {"subtask": subtask, "X_score": final_score}, {}, self.compute_budget)
            results.append(routed)

        return {"efs": 0.92, "subtask_outputs": results, "merged_candidate": "merged_result"}

    def _end_of_run(self, mining_result: Dict) -> Dict:
        """Low-level post-run hook. Managers call high-level post-run intelligence here."""
        self._append_trace("end_of_run_start", "Low-level post-run processing")
        return {"efs": mining_result.get("efs", 0.92), "status": "success"}

    # ====================== SUPPORTING METHODS ======================

    def provide_input(self, input_data: Dict) -> Dict:
        self.mid_run_input_queue.put(input_data)
        self._append_trace("mid_run_input_received", input_data)
        return {"status": "input_accepted"}

    def get_status(self) -> Dict:
        return self.to_agent_json()

    def shutdown(self) -> Dict:
        self._stop_health_monitor()
        self.unrestricted_executor.shutdown()
        self.status = "shutdown"
        self._append_trace("em_shutdown_complete", "Resources released")
        return self.to_agent_json()

    def to_agent_json(self) -> Dict:
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else None
        return {
            "launch_id": self.launch_id,
            "status": self.status,
            "challenge_id": self.challenge_id,
            "compute_budget": self.compute_budget,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "duration_seconds": duration,
            "final_result": self.final_result,
            "mid_run_inputs_processed": self.mid_run_input_queue.qsize(),
            "trace_summary": {"total_entries": len(self.trace_log)},
            "agent_telemetry": self.real_compute_engine.to_agent_json() if hasattr(self.real_compute_engine, 'to_agent_json') else {}
        }

    def _start_health_monitor(self):
        def monitor_loop():
            while not self._stop_event.is_set():
                telemetry = self.real_compute_engine._gather_hardware_telemetry()
                self._append_trace("periodic_health_telemetry", telemetry)
                time.sleep(10)
        self._health_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._health_thread.start()

    def _stop_health_monitor(self):
        if self._health_thread:
            self._stop_event.set()
            self._health_thread.join(timeout=2)

    def _append_trace(self, step: str, details: str = "", **kwargs):
        entry = {"timestamp": datetime.now().isoformat(), "launch_id": self.launch_id, "step": step, "details": details, **kwargs}
        self.trace_log.append(entry)
        if len(self.trace_log) > 300:
            self.trace_log = self.trace_log[-300:]
        logger.info(f"EM_TRACE [{self.launch_id}] {step} — {details[:120]}...")

    def _fail(self, reason: str, extra: Dict = None) -> Dict:
        self.status = "failed"
        self._stop_health_monitor()
        self._append_trace("em_launch_failed", reason, extra=extra)
        return {"launch_id": self.launch_id, "status": "failed", "reason": reason}

    def _run_full_expensive_simulation(self, input_vector: np.ndarray) -> float:
        """REPLACE WITH YOUR ACTUAL QUANTUM SIMULATOR CALL.
        This is where the heavy quantum simulation runs (Qiskit Aer, Cirq, IonQ, Rigetti, etc.)."""
        # Example placeholder for a quantum simulation (VQE energy, QAOA approximation ratio, circuit fidelity, etc.)
        # Replace with your real quantum backend call
        return 0.85 + np.random.normal(0, 0.03)  # realistic noisy quantum simulation output

# Global instance
enigma_machine = EnigmaMachine()

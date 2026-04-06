# agents/history_parse_hunter.py - v0.6 HistoryParseHunter + Retrospective Scoring + Auditing
from agents.video_archiver import VideoArchiver
from agents.validation_oracle import ValidationOracle
import json
from pathlib import Path

class HistoryParseHunter:
    def __init__(self, validation_oracle: ValidationOracle):
        self.video_hunter = VideoArchiver()
        self.oracle = validation_oracle
        self.archive_dir = Path("memdir/archives")
    
    def compute_retrospective_score(self, old_mau: dict, current_brain: dict) -> float:
        """Δ_retro × decay × hetero_bonus × validation_multiplier"""
        delta = self.oracle._compute_delta_retro(old_mau, current_brain)
        decay = 0.92 ** (datetime.now() - old_mau["timestamp"]).days
        hetero_bonus = current_brain.get("heterogeneity_score", 1.0)
        val_mult = old_mau.get("validation_score", 0.5)
        return delta * decay * hetero_bonus * val_mult * 1.8  # retrospective boost
    
    def run_audit_on_mp4_backlog(self) -> dict:
        """Full-system auditing layer"""
        audits = []
        for mp4 in self.archive_dir.glob("*.mv2"):
            data = self.video_hunter.decode_mp4(str(mp4))
            audit = {
                "file": str(mp4),
                "logic_fidelity": self.oracle._sota_partial_credit_score(data),
                "regression_rate": self.oracle._compute_regression_rate(data),
                "gate_success": self.oracle._gate_success_rate(data),
                "efs_impact": self.oracle._compute_efs_impact(data)
            }
            audits.append(audit)
        return {"audits": audits, "summary": "Logic hardening confirmed" if all(a["logic_fidelity"] > 0.85 for a in audits) else "Attention required"}
    
    def trigger_retrospective(self, run_id: str = None):
        # Auto-called on Deep Replan, high-signal runs, or manual button
        pass  # wired into arbos_manager

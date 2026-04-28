import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    import memvid
    MEMVID_AVAILABLE = True
except ImportError:
    MEMVID_AVAILABLE = False
    logger.warning("memvid not installed — using JSON + metadata fallback")

class VideoArchiver:
    """SOTA VideoArchiver — rich archival with oracle metrics, graph snapshot, predictive signals, and full vault integration."""

    ARCHIVE_DIR = Path("memdir/archives")

    def __init__(self):
        self.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ VideoArchiver v0.9.13+ SOTA initialized — archive dir: {self.ARCHIVE_DIR} | memvid: {'available' if MEMVID_AVAILABLE else 'JSON fallback'}")

    def archive_run_to_mp4(self, run_data: dict, run_id: str = None) -> str:
        """High-signal archival with full oracle metrics, contract, Grail context, graph snapshot, predictive signals, and explicit scoring."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = run_id or f"run_{int(datetime.now().timestamp())}"
        out_path = self.ARCHIVE_DIR / f"{run_id}_{timestamp}.mv2"

        frames = [
            {"type": "oracle_metrics", "content": {
                "final_score": run_data.get("final_score", 0.0),
                "efs": run_data.get("efs", 0.0),
                "c3a_confidence": run_data.get("c3a_confidence", 0.0),
                "theta_dynamic": run_data.get("theta_dynamic", 0.0),
                "heterogeneity": run_data.get("heterogeneity_score", 0.0),
                "fidelity": run_data.get("fidelity", 0.0),
                "verifier_quality": run_data.get("verifier_quality", 0.0)
            }},
            {"type": "graph_snapshot", "content": run_data.get("graph_snapshot", {})},
            {"type": "predictive_signals", "content": {
                "predictive_power": run_data.get("predictive_power", 0.0),
                "market_demand_signal": run_data.get("market_demand_signal", 0.0),
                "conversion_forecast": run_data.get("conversion_forecast", 0.0)
            }},
            {"type": "metadata", "content": {
                "run_id": run_id,
                "timestamp": timestamp,
                "loop_count": run_data.get("loop", 0),
                "dry_run_compliant": run_data.get("dry_run_passed", True)
            }}
        ]

        try:
            if MEMVID_AVAILABLE:
                memvid.encode_smart_frames(frames, str(out_path), fps=12, compression="smart")
                logger.info(f"✅ Archived full run {run_id} → {out_path} (Smart Frames .mv2)")
            else:
                fallback_path = self.ARCHIVE_DIR / f"{run_id}_{timestamp}.json"
                fallback_path.write_text(json.dumps(frames, indent=2))
                logger.info(f"✅ Archived run {run_id} → {fallback_path} (JSON fallback)")
                return str(fallback_path)
        except Exception as e:
            logger.error(f"Video archival failed for run {run_id}: {e}")
            fallback_path = self.ARCHIVE_DIR / f"{run_id}_{timestamp}_emergency.json"
            fallback_path.write_text(json.dumps(frames, indent=2))
            return str(fallback_path)

        return str(out_path)

    def decode_mp4(self, archive_path: str) -> dict:
        """VideoHunter decode with full oracle context reconstruction."""
        path = Path(archive_path)
        if not path.exists():
            logger.warning(f"Archive not found: {archive_path}")
            return {"error": "archive_not_found"}

        try:
            if MEMVID_AVAILABLE and path.suffix.lower() in [".mv2", ".mp4"]:
                return memvid.decode_smart_frames(str(path))
            else:
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Decode failed for {archive_path}: {e}")
            return {"error": "decode_failed", "message": str(e)}

    def list_archives(self, limit: int = 20) -> list:
        """List recent archives for UI / audit tab."""
        mv2_files = sorted(self.ARCHIVE_DIR.glob("*.mv2"), reverse=True)
        json_files = sorted(self.ARCHIVE_DIR.glob("*.json"), reverse=True)
        all_files = mv2_files + json_files
        return [str(f) for f in all_files[:limit]]

    def get_archive_summary(self, archive_path: str) -> dict:
        """Quick summary for UI without full decode."""
        try:
            data = self.decode_mp4(archive_path)
            if isinstance(data, dict) and "oracle_metrics" in str(data):
                metrics = data.get("oracle_metrics", {}) if isinstance(data, dict) else {}
                return {
                    "run_id": data.get("metadata", {}).get("run_id", "unknown"),
                    "timestamp": data.get("metadata", {}).get("timestamp"),
                    "final_score": metrics.get("final_score", 0.0),
                    "efs": metrics.get("efs", 0.0),
                    "c3a": metrics.get("c3a_confidence", 0.0),
                    "heterogeneity": metrics.get("heterogeneity", 0.0),
                    "verifier_quality": metrics.get("verifier_quality", 0.0),
                    "predictive_power": data.get("predictive_signals", {}).get("predictive_power", 0.0)
                }
            return {"status": "summary_available", "path": archive_path}
        except:
            return {"status": "summary_failed"}

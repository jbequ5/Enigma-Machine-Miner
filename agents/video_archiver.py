# agents/video_archiver.py - v0.6 VideoArchiver / VideoHunter (Memvid .mv2)
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
    logger.warning("memvid not installed — video archival will use JSON fallback")

class VideoArchiver:
    ARCHIVE_DIR = Path("memdir/archives")
    
    def __init__(self):
        self.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ VideoArchiver initialized — archive dir: {self.ARCHIVE_DIR} | memvid: {'available' if MEMVID_AVAILABLE else 'fallback mode'}")
    
    def archive_run_to_mp4(self, run_data: dict, run_id: str) -> str:
        """Encode MAUs, wiki snapshot, C3A logs, Grail entries, trajectories as Smart Frames .mv2"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = self.ARCHIVE_DIR / f"{run_id}_{timestamp}.mv2"
        
        frames = [
            {"type": "mau_pyramid", "content": run_data.get("mau_pyramid", {})},
            {"type": "wiki_snapshot", "content": run_data.get("wiki_snapshot", {})},
            {"type": "c3a_logs", "content": run_data.get("c3a_logs", [])},
            {"type": "grail_entries", "content": run_data.get("grail", [])},
            {"type": "trajectories", "content": run_data.get("trajectories", [])},
            {"type": "metadata", "content": {
                "run_id": run_id, 
                "timestamp": timestamp, 
                "efs": run_data.get("efs", 0.0),
                "final_score": run_data.get("final_score", 0.0)
            }}
        ]
        
        try:
            if MEMVID_AVAILABLE:
                memvid.encode_smart_frames(frames, str(out_path), fps=12, compression="smart")
                logger.info(f"✅ Archived run {run_id} → {out_path} (Smart Frames .mv2)")
            else:
                # Fallback: save as JSON for compatibility
                fallback_path = self.ARCHIVE_DIR / f"{run_id}_{timestamp}.json"
                fallback_path.write_text(json.dumps(frames, indent=2))
                logger.info(f"✅ Archived run {run_id} → {fallback_path} (JSON fallback)")
                return str(fallback_path)
        except Exception as e:
            logger.error(f"Video archival failed for run {run_id}: {e}")
            # Emergency JSON fallback
            fallback_path = self.ARCHIVE_DIR / f"{run_id}_{timestamp}_fallback.json"
            fallback_path.write_text(json.dumps(frames, indent=2))
            return str(fallback_path)
        
        return str(out_path)
    
    def decode_mp4(self, mp4_path: str) -> dict:
        """VideoHunter on-demand decode for retrospectives"""
        path = Path(mp4_path)
        if not path.exists():
            logger.warning(f"Archive not found: {mp4_path}")
            return {"error": "archive_not_found", "path": str(mp4_path)}
        
        try:
            if MEMVID_AVAILABLE and path.suffix.lower() == ".mv2":
                return memvid.decode_smart_frames(str(path))
            elif path.suffix.lower() == ".json":
                return json.loads(path.read_text(encoding="utf-8"))
            else:
                # Try JSON fallback
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Decode failed for {mp4_path}: {e}")
            return {"error": "decode_failed", "message": str(e), "path": str(mp4_path)}

    def list_archives(self, limit: int = 20) -> list:
        """Helper for audit tab — list recent archives"""
        archives = sorted(self.ARCHIVE_DIR.glob("*.mv2"), reverse=True)
        if not archives and MEMVID_AVAILABLE is False:
            archives = sorted(self.ARCHIVE_DIR.glob("*.json"), reverse=True)
        return [str(a) for a in archives[:limit]]

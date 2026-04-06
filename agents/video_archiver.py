# agents/video_archiver.py - v0.6 VideoArchiver / VideoHunter (Memvid .mv2)
import memvid
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VideoArchiver:
    ARCHIVE_DIR = Path("memdir/archives")
    
    def __init__(self):
        self.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
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
            {"type": "metadata", "content": {"run_id": run_id, "timestamp": timestamp, "efs": run_data.get("efs", 0.0)}}
        ]
        
        memvid.encode_smart_frames(frames, str(out_path), fps=12, compression="smart")
        logger.info(f"✅ Archived run {run_id} → {out_path}")
        return str(out_path)
    
    def decode_mp4(self, mp4_path: str) -> dict:
        """VideoHunter on-demand decode for retrospectives"""
        return memvid.decode_smart_frames(mp4_path)

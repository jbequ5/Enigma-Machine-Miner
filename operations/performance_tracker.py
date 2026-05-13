# operations/performance_tracker.py
# SAGE v0.9.14+ — PerformanceTracker
# Persistent SQLite tracking with full 60/40 scoring, EFS, KAS, and provenance support

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PerformanceTracker:
    def __init__(self, config: "OperationsConfig", db_path: str = "data/operations/performance.db"):
        self.config = config
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                timestamp TEXT,
                challenge_id TEXT,
                profile_id TEXT,
                model_used TEXT,
                internal_branching INTEGER,
                fragment_yield REAL,
                efs REAL DEFAULT 0.0,
                refined_value_added REAL DEFAULT 0.0,
                n_pass INTEGER,
                avg_refined_value REAL,
                s_downstream REAL,
                novelty_factor REAL,
                provenance_integrity REAL,
                kas_signals TEXT,
                session_data TEXT,
                provenance_hash TEXT
            )
        """)
        self.conn.commit()

    def record_run(self, run_data: Dict) -> str:
        run_id = run_data.get("run_id", f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.conn.execute("""
            INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            datetime.now().isoformat(),
            run_data.get("challenge_id"),
            run_data.get("profile_id"),
            run_data.get("model_used"),
            run_data.get("internal_branching"),
            run_data.get("fragment_yield", 0.0),
            run_data.get("efs", 0.0),
            run_data.get("refined_value_added", 0.0),
            run_data.get("n_pass", 0),
            run_data.get("avg_refined_value", 0.0),
            run_data.get("s_downstream", 0.0),
            run_data.get("novelty_factor", 0.0),
            run_data.get("provenance_integrity", 1.0),
            json.dumps(run_data.get("kas_signals", {})),
            json.dumps(run_data.get("session_data", {})),
            run_data.get("provenance_hash", "")
        ))
        self.conn.commit()
        return run_id

    def best_profiles_for_challenge(self, challenge_id: str, limit: int = 5) -> List[Dict]:
        cursor = self.conn.execute("""
            SELECT profile_id, AVG(efs) as efs, AVG(fragment_yield) as yield, 
                   COUNT(*) as runs, AVG(refined_value_added) as refined
            FROM runs 
            WHERE challenge_id = ? 
            GROUP BY profile_id 
            ORDER BY yield DESC LIMIT ?
        """, (challenge_id, limit))
        cols = [col[0] for col in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def get_profile_session(self, challenge_id: str, profile_id: str) -> Optional[Dict]:
        cursor = self.conn.execute("""
            SELECT session_data FROM runs 
            WHERE challenge_id = ? AND profile_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        """, (challenge_id, profile_id))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None

    def get_total_fragments(self) -> int:
        cursor = self.conn.execute("SELECT COUNT(*) FROM runs WHERE run_type = 'fragment'")
        row = cursor.fetchone()
        return row[0] if row else 0

    def get_average_efs(self) -> float:
        cursor = self.conn.execute("SELECT AVG(efs) FROM runs WHERE efs > 0")
        row = cursor.fetchone()
        return round(row[0], 4) if row and row[0] else 0.0

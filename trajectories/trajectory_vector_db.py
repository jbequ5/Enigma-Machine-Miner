import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
from datetime import datetime, timedelta
import logging
import torch
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrajectoryVectorDB:
    def __init__(self, dim: int = 384, max_entries: int = 1200, index_type: str = "HNSW"):
        # Use a stronger but still fast model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dim = dim
        self.max_entries = max_entries
        self.index_type = index_type

        # HNSW = SOTA for approximate nearest neighbor (fast + good recall)
        if index_type == "HNSW":
            self.index = faiss.IndexHNSWFlat(dim, 32)  # 32 = good speed/accuracy balance
            self.index.hnsw.efConstruction = 200
            self.index.hnsw.efSearch = 64
        else:
            self.index = faiss.IndexFlatL2(dim)

        self.trajectories = []  # Full metadata storage
        self.path = Path("trajectories")
        self.meta_path = self.path / "vector_meta.jsonl"
        self.path.mkdir(exist_ok=True)
        
        self.load()
        logger.info(f"✅ TrajectoryVectorDB initialized ({index_type} index | {len(self.trajectories)} entries)")

    def _get_embedding_text(self, traj: dict) -> str:
        """High-signal embedding text — this is crucial for quality."""
        score = traj.get("validation_score", traj.get("local_score", 0.0))
        fidelity = traj.get("fidelity", 0.5)
        hetero = traj.get("heterogeneity_score", 0.0)
        
        return (
            f"Score: {score:.3f} | Fidelity: {fidelity:.3f} | Heterogeneity: {hetero:.3f} | "
            f"Challenge: {traj.get('challenge', '')[:300]} | "
            f"Solution: {str(traj.get('solution', ''))[:1200]} | "
            f"Key Insight: {traj.get('key_insight', '')[:400]}"
        )

    def embed(self, traj: dict) -> np.ndarray:
        text = self._get_embedding_text(traj)
        emb = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return emb.astype('float32')

    def _compute_reinforcement_value(self, traj: dict) -> float:
        """Smart value score for pruning + ranking."""
        score = traj.get("validation_score", traj.get("local_score", 0.0))
        fidelity = traj.get("fidelity", 0.5)
        hetero = traj.get("heterogeneity_score", 0.5)
        age_days = (datetime.now() - datetime.fromisoformat(traj.get("timestamp", "2024-01-01"))) / timedelta(days=1)
        
        # Reinforcement formula (aligned with compression layer)
        value = (score ** 1.6) * (fidelity ** 1.8) * (hetero ** 1.2) * np.exp(-age_days * 0.08)
        return float(value)

    def add(self, traj: dict):
        if not traj:
            return

        emb = self.embed(traj)
        self.index.add(np.array([emb]))
        self.trajectories.append(traj)

        # Smart pruning: keep highest reinforcement value trajectories
        if len(self.trajectories) > self.max_entries:
            self.trajectories.sort(
                key=self._compute_reinforcement_value, 
                reverse=True
            )
            self.trajectories = self.trajectories[:self.max_entries]
            self._rebuild_index()

        # Persistent append
        try:
            with open(self.meta_path, "a", encoding="utf-8") as f:
                copy = traj.copy()
                copy["timestamp"] = datetime.now().isoformat()
                copy["reinforcement_value"] = self._compute_reinforcement_value(traj)
                f.write(json.dumps(copy) + "\n")
        except Exception as e:
            logger.warning(f"Failed to persist trajectory: {e}")

    def add_eggroll(self, traj: dict, perturbation_info: dict = None):
        if perturbation_info:
            traj["eggroll_perturbation"] = perturbation_info
            traj["heterogeneity_score"] = traj.get("heterogeneity_score", 0.0) + 0.15
        self.add(traj)

    def search(self, query_goal: str, k: int = 12, min_score: float = 0.0, 
               min_fidelity: float = 0.0, recency_boost: bool = True):
        """Advanced hybrid search."""
        if not self.trajectories:
            return []

        q_emb = self.model.encode(query_goal, normalize_embeddings=True).astype('float32')
        
        # Oversample for filtering
        D, I = self.index.search(np.array([q_emb]), min(k * 3, len(self.trajectories)))

        results = []
        for idx in I[0]:
            if idx >= len(self.trajectories):
                continue
            traj = self.trajectories[idx]
            
            score = traj.get("validation_score", traj.get("local_score", 0.0))
            fidelity = traj.get("fidelity", 0.0)
            
            if score < min_score or fidelity < min_fidelity:
                continue
                
            results.append(traj)
            if len(results) >= k:
                break

        # Optional recency boost (re-sort)
        if recency_boost and results:
            results.sort(
                key=lambda x: (
                    x.get("validation_score", 0) * 0.6 +
                    x.get("fidelity", 0) * 0.3 +
                    (1.0 / (1 + (datetime.now() - datetime.fromisoformat(x.get("timestamp", "2024-01-01"))).days * 0.1))
                ),
                reverse=True
            )

        return results[:k]

    def _rebuild_index(self):
        """Rebuild index efficiently."""
        self.index.reset()
        if not self.trajectories:
            return
        embeddings = np.array([self.embed(t) for t in self.trajectories])
        self.index.add(embeddings)

    def load(self):
        if not self.meta_path.exists():
            return

        try:
            with open(self.meta_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        traj = json.loads(line)
                        self.trajectories.append(traj)
                        emb = self.embed(traj)
                        self.index.add(np.array([emb]))
        except Exception as e:
            logger.error(f"Error loading TrajectoryVectorDB: {e}")

        logger.info(f"Loaded {len(self.trajectories)} trajectories")

    def clear(self):
        self.index.reset()
        self.trajectories.clear()
        if self.meta_path.exists():
            self.meta_path.unlink()
        logger.info("TrajectoryVectorDB cleared.")

    def get_stats(self):
        """Helpful debugging info."""
        scores = [t.get("validation_score", t.get("local_score", 0)) for t in self.trajectories]
        return {
            "total_entries": len(self.trajectories),
            "avg_score": np.mean(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "index_type": self.index_type
        }

# Global instance
vector_db = TrajectoryVectorDB(max_entries=1200, index_type="HNSW")

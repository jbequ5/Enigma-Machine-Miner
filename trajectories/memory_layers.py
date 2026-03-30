# trajectories/memory_layers.py
# Three-Layer Memory Refinement (short-term + compressed long-term + Vector DB)
# Hardened version: Light compression + tool proposals + verifier-aware

import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MemoryLayers:
    def __init__(self, short_term_limit: int = 40, similarity_threshold: float = 0.92):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.short_term: List[Dict] = []          # Layer 1: raw recent trajectories
        self.long_term_summaries: List[Dict] = [] # Layer 2: LLM-compressed summaries
        self.vector_db = None                     # Layer 3: TrajectoryVectorDB
        self.tool_proposals: List[str] = []       # Lightweight tool suggestions only
        self.short_term_limit = short_term_limit
        self.similarity_threshold = similarity_threshold

    def set_vector_db(self, vector_db):
        self.vector_db = vector_db

    def add_short_term(self, entry: Dict):
        """Add raw entry to short-term layer."""
        self.short_term.append(entry)
        if len(self.short_term) > self.short_term_limit:
            self.short_term.pop(0)  # FIFO

    def add(self, text: str, metadata: dict = None):
        """Convenience method used by ArbosManager."""
        if metadata is None:
            metadata = {}
        entry = {"text": text, "metadata": metadata, "timestamp": str(datetime.datetime.now())}
        self.add_short_term(entry)

    def add_proposals(self, proposals: List[str]):
        """Store tool proposals (suggestions only — no creation)."""
        self.tool_proposals.extend(proposals)
        for p in proposals:
            self.add(f"TOOL PROPOSAL: {p}", {"type": "tool_proposal"})

    def compress_to_long_term(self, recent_entries: List[Dict] = None, arbos=None) -> Dict:
        """Use Arbos to compress recent short-term into one concise summary."""
        if recent_entries is None:
            recent_entries = self.short_term[-15:]  # last 15 by default

        if not recent_entries:
            return {}

        prompt = f"""Compress these recent trajectories into ONE concise, deduplicated summary (max 300 words). 
Focus only on patterns that improved validation_score or novelty.
Output valid JSON: {{"summary": "...", "key_patterns": [...]}}"""

        try:
            compressed = arbos.compute.run_on_compute(prompt, temperature=0.0, task_type="compression")
            summary = json.loads(compressed)
        except:
            summary = {"summary": "Compressed summary unavailable", "key_patterns": []}

        # Deduplicate against existing long-term summaries
        if self.long_term_summaries:
            emb_new = self.model.encode(summary["summary"])
            for old in self.long_term_summaries:
                emb_old = self.model.encode(old["summary"])
                similarity = np.dot(emb_new, emb_old) / (np.linalg.norm(emb_new) * np.linalg.norm(emb_old) + 1e-8)
                if similarity > self.similarity_threshold:
                    return {}  # Duplicate — skip

        self.long_term_summaries.append(summary)
        return summary

    def compress_low_value(self, current_score: float = 0.0):
        """Light threshold-triggered compression — called from re_adapt."""
        # Remove low-value short-term entries
        self.short_term = [entry for entry in self.short_term 
                          if entry.get("metadata", {}).get("local_score", 0.5) > 0.4]

        if len(self.short_term) > 25:
            self.compress_to_long_term()

    def get_total_context_tokens(self) -> int:
        """Rough token estimate for triggering compression."""
        total = 0
        for entry in self.short_term:
            total += len(entry.get("text", "")) // 4
        for entry in self.long_term_summaries:
            total += len(entry.get("summary", "")) // 4
        return total

    def get_context_for_planning(self, query_goal: str, k: int = 8) -> Dict:
        """Layered retrieval for Arbos planning / Adaptation Arbos."""
        short = self.short_term[-10:] if self.short_term else []
        long_summaries = self.long_term_summaries[-5:] if self.long_term_summaries else []
        vector_results = self.vector_db.search(query_goal, k) if self.vector_db else []

        return {
            "short_term": short,
            "long_term_compressed": long_summaries,
            "vector_retrieved": vector_results,
            "tool_proposals": self.tool_proposals[-5:]  # recent proposals
        }

    def clear(self):
        """Clear all layers (useful for testing)."""
        self.short_term.clear()
        self.long_term_summaries.clear()
        self.tool_proposals.clear()
        logger.info("MemoryLayers cleared.")

# Global instance
memory_layers = MemoryLayers()

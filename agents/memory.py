# agents/memory.py - v2.0 MAXIMUM CAPABILITY LongTermMemory + MemoryLayers + ByteRover MAU Pyramid
# Fully verifier-first, EFS/c/θ/heterogeneity/contract-aware, SOTA-gated, and Grail-integrated

from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
import datetime
import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LongTermMemory:
    """ChromaDB backend — preserved but now verifier-first and reinforcement-aware."""
    def __init__(self, db_path="memory_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(name="enigma_memory")

    def add(self, text: str, metadata: dict = None):
        if metadata is None:
            metadata = {}
        metadata["timestamp"] = str(datetime.datetime.now())
        metadata["reinforcement"] = metadata.get("mau_reinforcement", metadata.get("local_score", 0.5) * 0.8)

        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[str(hash(text + str(datetime.datetime.now())))]
        )

    def query(self, query_text: str, n_results: int = 5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results.get('documents', [[]])[0]


class MemoryLayers:
    """Three-layer memory system — fully upgraded v5.1 ByteRover MAU Pyramid + SOTA gating."""
    def __init__(self):
        self.long_term = LongTermMemory()           # Layer 3: Persistent vector DB
        self.short_term: List[Dict] = []            # Layer 1: Recent raw trajectories
        self.long_term_summaries: List[Dict] = []   # Layer 2: Compressed summaries
        self.tool_proposals: List[str] = []

        # v5.1 MAU Pyramid settings
        self.byterover_mau_enabled = False
        self.mau_reinforcement_weight = 1.0
        self.arbos = None  # will be wired from ArbosManager
        
    def compress_low_value_fragment(self, node: str, decayed_score: float):
        """v0.8+ Streamlined per-fragment compression — no poetic/bio fluff.
        Runs only on low-score fragments and produces 1–3 key sentences + provenance."""
        if decayed_score >= 0.42:
            return  # still valuable

        # Simplified prompt — exact as specified in the design
        compress_prompt = f"""Distill this low-signal fragment to 1–3 key sentences + provenance tags only.
Fragment content:
{node[:2000]}

Return ONLY the distilled summary. No extra text."""

        try:
            distilled = self.arbos.harness.call_llm(compress_prompt, temperature=0.2, max_tokens=300)
            # Write back as compressed fragment
            self.arbos._write_fragment(
                challenge_id=self.arbos._current_challenge_id,
                subtask_id="compressed",
                fragment={"id": "compressed", "content": distilled, "type": "compressed"},
                metadata={"original_score": round(decayed_score, 4), "compressed": True}
            )
            logger.info(f"✅ Per-fragment compression applied (score {decayed_score:.3f})")
        except Exception as e:
            logger.debug(f"Compression skipped (safe): {e}")

    def add(self, text: str, metadata: dict = None):
        if metadata is None:
            metadata = {}
        entry = {"text": text, "metadata": metadata, "timestamp": datetime.datetime.now().isoformat()}
        self.short_term.append(entry)
        
        if len(self.short_term) > 40:
            self.compress_to_long_term()

        # ByteRover MAU promotion with SOTA gate
        if self.byterover_mau_enabled and metadata.get("local_score", 0.5) > 0.65:
            self.promote_high_signal(text, metadata)
        else:
            self.long_term.add(text, metadata)

    def promote_high_signal(self, text: str, metadata: dict):
        """SOTA-gated high-signal promotion to permanent memory."""
        if not self.byterover_mau_enabled:
            return

        reinforcement = self._compute_mau_reinforcement(text, metadata)
        
        # SOTA gate — only promote if verifier signal is strong
        if reinforcement > 0.78 and self.arbos and hasattr(self.arbos.validator, '_subarbos_gate'):
            try:
                if self.arbos.validator._subarbos_gate(output=text, theta_dynamic=0.68):
                    metadata["permanent"] = True
                    metadata["mau_reinforcement"] = reinforcement
                    self.long_term.add(text, metadata)
                    logger.info(f"ByteRover + SOTA promoted high-signal MAU (reinforcement: {reinforcement:.3f})")
                else:
                    logger.debug("High-signal MAU rejected by SOTA gate")
            except:
                # Safe fallback
                self.long_term.add(text, metadata)
        else:
            self.long_term.add(text, metadata)

    def _compute_mau_reinforcement(self, text: str, metadata: dict) -> float:
        validation_score = metadata.get("local_score", 0.5)
        fidelity = metadata.get("fidelity", 0.8)
        heterogeneity = metadata.get("heterogeneity_score", 0.7)
        symbolic_coverage = 0.88 if any(k in text.lower() for k in ["sympy", "deterministic", "invariant", "verifier"]) else 0.6
        return validation_score * (fidelity ** 1.5) * symbolic_coverage * heterogeneity

    def add_proposals(self, proposals: List[str]):
        self.tool_proposals.extend(proposals)
        for p in proposals:
            self.add(f"TOOL PROPOSAL: {p}", {"type": "tool_proposal"})

    def compress_to_long_term(self):
        if not self.short_term:
            return
        to_compress = self.short_term[:10]
        self.short_term = self.short_term[10:]

        summary_text = "\n".join([entry["text"][:500] for entry in to_compress])
        summary_entry = {
            "summary": summary_text[:2000],
            "original_count": len(to_compress),
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "compressed_summary"
        }
        self.long_term_summaries.append(summary_entry)
        self.long_term.add(summary_text, {"type": "compressed_summary"})

    def compress_low_value(self, current_score: float = 0.0):
        """SOTA-aware pruning of low-value items."""
        threshold = 0.38 if self.byterover_mau_enabled else 0.45
        self.short_term = [entry for entry in self.short_term 
                          if entry.get("metadata", {}).get("local_score", 0.5) > threshold]
        
        if len(self.short_term) > 25:
            self.compress_to_long_term()

    def get_total_context_tokens(self) -> int:
        total = sum(len(entry["text"]) // 4 for entry in self.short_term)
        total += sum(len(entry["summary"]) // 4 for entry in self.long_term_summaries)
        return total

    def query(self, query_text: str, n_results: int = 5):
        return self.long_term.query(query_text, n_results)

    def get_recent_context(self, max_items: int = 8) -> str:
        recent = self.short_term[-max_items:]
        summaries = self.long_term_summaries[-3:]
        
        context = "RECENT TRAJECTORIES:\n"
        for item in recent:
            context += f"- {item['text'][:300]}...\n"
        
        if summaries:
            context += "\nCOMPRESSED PATTERNS:\n"
            for s in summaries:
                context += f"- {s['summary'][:400]}...\n"
        return context


# Global instances
memory = LongTermMemory()
memory_layers = MemoryLayers()

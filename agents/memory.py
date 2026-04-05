from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
import datetime
import json
from typing import List, Dict, Any

class LongTermMemory:
    """Your original ChromaDB backend - 100% preserved."""
    def __init__(self, db_path="memory_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(name="enigma_memory")

    def add(self, text: str, metadata: dict = None):
        if metadata is None:
            metadata = {}
        metadata["timestamp"] = str(datetime.datetime.now())
        
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
    """Three-layer memory system — fully upgraded to v5.1 ByteRover + MAU Pyramid."""
    def __init__(self):
        self.long_term = LongTermMemory()           # Layer 3: Persistent vector DB
        self.short_term: List[Dict] = []            # Layer 1: Recent raw trajectories
        self.long_term_summaries: List[Dict] = []   # Layer 2: Compressed summaries
        self.tool_proposals: List[str] = []         # Tool suggestions only

        # v5.1 MAU Pyramid settings
        self.byterover_mau_enabled = False          # Will be synced from toggles
        self.mau_reinforcement_weight = 1.0

    def add(self, text: str, metadata: dict = None):
        if metadata is None:
            metadata = {}
        entry = {"text": text, "metadata": metadata, "timestamp": datetime.datetime.now().isoformat()}
        self.short_term.append(entry)
        
        if len(self.short_term) > 40:
            self.compress_to_long_term()

        # v5.1: Add to long-term with MAU scoring if enabled
        if self.byterover_mau_enabled and "local_score" in metadata:
            self._add_with_mau_scoring(text, metadata)
        else:
            self.long_term.add(text, metadata)

    def _add_with_mau_scoring(self, text: str, metadata: dict):
        """Break into MAUs and score with reinforcement formula"""
        # Simple MAU split (paragraphs/sentences)
        maus = [s.strip() for s in text.split("\n\n") if len(s.strip()) > 30]
        
        for mau in maus:
            # Reinforcement scoring from v5.1 diff
            validation_score = metadata.get("local_score", 0.5)
            fidelity = metadata.get("fidelity", 0.8)
            heterogeneity = metadata.get("heterogeneity_score", 0.7)
            symbolic_coverage = 0.85 if any(k in mau.lower() for k in ["sympy", "deterministic", "invariant"]) else 0.6
            
            reinforcement = validation_score * (fidelity ** 1.5) * symbolic_coverage * heterogeneity
            
            mau_metadata = {**metadata, "mau_reinforcement": reinforcement, "type": "mau"}
            self.long_term.add(mau, mau_metadata)

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
        """v5.1 pruning: remove low-reinforcement items"""
        if not self.byterover_mau_enabled:
            self.short_term = [entry for entry in self.short_term 
                              if entry.get("metadata", {}).get("local_score", 0.5) > 0.4]
        else:
            # MAU-aware pruning
            self.short_term = [entry for entry in self.short_term 
                              if entry.get("metadata", {}).get("local_score", 0.5) > 0.35]
        
        if len(self.short_term) > 25:
            self.compress_to_long_term()

    def get_total_context_tokens(self) -> int:
        total = 0
        for entry in self.short_term:
            total += len(entry["text"]) // 4
        for entry in self.long_term_summaries:
            total += len(entry["summary"]) // 4
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

    # ====================== v5.1 MAU Pyramid Promotion ======================
    def promote_high_signal(self, text: str, metadata: dict):
        """Promote high-signal MAUs to permanent wiki locations"""
        if not self.byterover_mau_enabled:
            return
        
        reinforcement = self._compute_mau_reinforcement(text, metadata)
        if reinforcement > 0.75:  # High-signal threshold
            # This would normally call wiki write functions in ArbosManager
            # For now we log and add to long-term with permanent flag
            metadata["permanent"] = True
            metadata["mau_reinforcement"] = reinforcement
            self.long_term.add(text, metadata)
            logger.info(f"ByteRover promoted high-signal MAU (reinforcement: {reinforcement:.3f})")


    def _compute_mau_reinforcement(self, text: str, metadata: dict) -> float:
        validation_score = metadata.get("local_score", 0.5)
        fidelity = metadata.get("fidelity", 0.8)
        heterogeneity = metadata.get("heterogeneity_score", 0.7)
        symbolic_coverage = 0.85 if any(k in text.lower() for k in ["sympy", "deterministic", "invariant"]) else 0.6
        return validation_score * (fidelity ** 1.5) * symbolic_coverage * heterogeneity


# Global instances
memory = LongTermMemory()
memory_layers = MemoryLayers()

# agents/fragment_tracker.py - v0.9.7 MAXIMUM SOTA FragmentTracker + NetworkX Graph Intelligence
# Persistent fragment metadata + NetworkX graph for v0.8+ Wiki Memory Strategy.
# Fully integrated with predictive layer, vault routing, PD Arm synthesis, and Economic Flywheel.

import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Tuple, Any
import networkx as nx
import math

logger = logging.getLogger(__name__)

class FragmentTracker:
    """Persistent fragment metadata + NetworkX graph for v0.9.7 SOTA Wiki Memory Strategy.
    Deep integration with predictive intelligence, vault routing, PD Arm, and Grail promotion."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.metadata_path = Path("goals/knowledge/fragment_metadata.json")
        self._load()

    def _load(self):
        if self.metadata_path.exists():
            try:
                data = json.loads(self.metadata_path.read_text(encoding="utf-8"))
                self.graph = nx.node_link_graph(data.get("graph", {"nodes": [], "links": []}))
                logger.info(f"FragmentTracker loaded {len(self.graph.nodes)} fragments from disk")
            except Exception as e:
                logger.warning(f"FragmentTracker load failed: {e}")
                self.graph = nx.DiGraph()

    def _save(self):
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"graph": nx.node_link_data(self.graph)}
        self.metadata_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def record_fragment(self, frag_id: str, initial_mau: float, challenge_id: str, subtask_id: str, content_preview: str = ""):
        self.graph.add_node(frag_id, 
                            initial_mau=initial_mau,
                            reuse_in_high_efs=0,
                            contract_delta_contrib=0,
                            replay_pass_rate=0.75,
                            last_use=date.today().isoformat(),
                            challenge_id=challenge_id,
                            subtask_id=subtask_id,
                            content_preview=content_preview[:300],
                            predictive_power=0.0,
                            vault_routed=False)
        self._save()

    def record_reuse(self, frag_id: str, efs: float, is_contract_delta: bool = False):
        """Record reuse and optionally mark as contract-related."""
        if self.graph.has_node(frag_id):
            data = self.graph.nodes[frag_id]
            if efs > 0.75:
                data["reuse_in_high_efs"] = data.get("reuse_in_high_efs", 0) + 1
            if is_contract_delta:
                data["contract_delta_contrib"] = data.get("contract_delta_contrib", 0) + 1
            data["last_use"] = date.today().isoformat()
            self.graph.add_edge("current_run", frag_id, weight=efs)
            self._save()

    def get_impact_score(self, frag_id: str) -> float:
        if not self.graph.has_node(frag_id):
            return 0.0
        data = self.graph.nodes[frag_id]
        impact = (0.4 * data.get("initial_mau", 0.65)) + \
                 (0.3 * data.get("reuse_in_high_efs", 0)) + \
                 (0.2 * data.get("contract_delta_contrib", 0)) + \
                 (0.1 * data.get("replay_pass_rate", 0.75))
        
        days = (date.today() - date.fromisoformat(data.get("last_use", "2025-01-01"))).days
        decayed = impact * math.exp(-0.08 * days)
        return round(decayed, 4)

    def query_relevant_fragments(self, query: str, top_k: int = 5, min_score: float = 0.0) -> list:
        """Intelligent graph search for Orchestrator, Synthesis, Symbiosis, ToolHunter, BD, and PD Arm."""
        results = []
        for node in self.graph.nodes:
            data = self.graph.nodes[node]
            preview = data.get("content_preview", "")
            if any(word.lower() in preview.lower() for word in query.lower().split()) or query.lower() in str(data).lower():
                score = self.get_impact_score(node)
                if score >= min_score:
                    results.append({
                        "fragment_id": node,
                        "impact_score": score,
                        "challenge": data.get("challenge_id"),
                        "subtask": data.get("subtask_id"),
                        "preview": preview[:150],
                        "mau": data.get("initial_mau", 0.0),
                        "reuse_in_high_efs": data.get("reuse_in_high_efs", 0),
                        "vault_routed": data.get("vault_routed", False)
                    })
        return sorted(results, key=lambda x: x["impact_score"], reverse=True)[:top_k]

    def cosmic_compress(self, min_utilization: float = 0.35, max_age_days: int = 30, 
                       preserve_grail: bool = True) -> Tuple[int, int]:
        """v0.9+ Advanced Cosmic Compression with multi-criteria scoring, 
        centrality, and community awareness."""
        
        if not self.graph or len(self.graph.nodes) == 0:
            return 0, 0

        to_prune = []
        to_promote = []
        
        # Calculate graph metrics once
        try:
            degree_centrality = nx.degree_centrality(self.graph)
            betweenness = nx.betweenness_centrality(self.graph, k=min(50, len(self.graph.nodes)))
        except:
            degree_centrality = {n: 0.1 for n in self.graph.nodes}
            betweenness = {n: 0.05 for n in self.graph.nodes}

        for node, data in list(self.graph.nodes(data=True)):
            # Skip protected nodes
            if preserve_grail and data.get('in_grail', False):
                continue

            mau = data.get('initial_mau', 0.0)
            impact = self.get_impact_score(node)
            reuse = data.get('reuse_in_high_efs', 0)
            age_days = (date.today() - date.fromisoformat(data.get("last_use", "2025-01-01"))).days
            in_high_efs = data.get('reuse_in_high_efs', 0) > 2

            # Multi-criteria score
            score = (
                0.35 * mau +
                0.25 * impact +
                0.15 * (reuse * 0.1) +           
                0.10 * degree_centrality.get(node, 0.1) +
                0.08 * betweenness.get(node, 0.05) +
                0.07 * (1.0 if in_high_efs else 0.3)
            )

            # Age penalty (Ebbinghaus-style)
            age_factor = max(0.0, 1.0 - (age_days / (max_age_days * 1.5)))
            final_score = score * age_factor

            if final_score < min_utilization and age_days > max_age_days // 2:
                to_prune.append(node)
            elif final_score > 0.82 and not data.get('in_grail', False):
                to_promote.append(node)

        # Execute pruning and promotion
        if to_prune:
            self.graph.remove_nodes_from(to_prune)
            
        for node in to_promote:
            if node in self.graph:
                self.graph.nodes[node]['in_grail'] = True
                self.graph.nodes[node]['promoted_at'] = datetime.now().isoformat()

        logger.info(f"Cosmic Compression: Removed {len(to_prune)} nodes | Promoted {len(to_promote)} invariants")
        
        self._save()
        return len(to_prune), len(to_promote)

    # New SOTA helpers for v0.9.7 integration
    def get_average_heterogeneity(self) -> float:
        """Return average heterogeneity across graph for predictive and meta-tuning layers."""
        if not self.graph.nodes:
            return 0.72
        scores = [data.get("heterogeneity", 0.72) for _, data in self.graph.nodes(data=True)]
        return sum(scores) / len(scores)

    def get_average_freshness(self) -> float:
        """Return average freshness for predictive layer."""
        if not self.graph.nodes:
            return 0.7
        scores = [data.get("freshness_score", 1.0) for _, data in self.graph.nodes(data=True)]
        return sum(scores) / len(scores)

    def add_fragment(self, fragment: Dict):
        """Unified add method used by VaultRouter and other layers."""
        frag_id = fragment.get("fragment_id") or f"frag_{len(self.graph.nodes)+1}"
        self.record_fragment(
            frag_id=frag_id,
            initial_mau=fragment.get("mau_score", 0.75),
            challenge_id=fragment.get("challenge_id", "unknown"),
            subtask_id=fragment.get("subtask_id", "unknown"),
            content_preview=fragment.get("content", "")
        )
        # Mark as vault entry if applicable
        if "vault" in fragment.get("metadata", {}):
            self.graph.nodes[frag_id]["vault_entry"] = True
            self.graph.nodes[frag_id]["vault"] = fragment["metadata"]["vault"]

    def query_relevant_fragments(self, query: str, top_k: int = 5, min_score: float = 0.0) -> list:
        """Public-facing intelligent graph search used by PD Arm, BD, etc."""
        return self.query_relevant_fragments(query, top_k, min_score)  # calls the internal method above

import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any
import networkx as nx
import math

logger = logging.getLogger(__name__)

class FragmentTracker:
    """SOTA Persistent Fragment Tracker with NetworkX graph intelligence.
    Full ByteRover MAU scoring, cosmic compression, provenance, vault routing, and SAGE integration."""

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
                logger.warning(f"FragmentTracker load failed (safe): {e}")
                self.graph = nx.DiGraph()

    def _save(self):
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"graph": nx.node_link_data(self.graph)}
        self.metadata_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def record_fragment(self, frag_id: str, initial_mau: float = 0.75,
                        challenge_id: str = "unknown", subtask_id: str = "unknown",
                        content_preview: str = "", heterogeneity: float = 0.72):
        """Record a new fragment with full metadata for SAGE subsystems."""
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
                            vault_routed=False,
                            heterogeneity=heterogeneity,
                            freshness_score=1.0)
        self._save()

    def record_reuse(self, frag_id: str, efs: float = 0.0, is_contract_delta: bool = False):
        """Record reuse and update impact metrics."""
        if self.graph.has_node(frag_id):
            data = self.graph.nodes[frag_id]
            if efs > 0.75:
                data["reuse_in_high_efs"] = data.get("reuse_in_high_efs", 0) + 1
            if is_contract_delta:
                data["contract_delta_contrib"] = data.get("contract_delta_contrib", 0) + 1
            data["last_use"] = date.today().isoformat()
            data["freshness_score"] = min(1.0, data.get("freshness_score", 1.0) + 0.15)
            self.graph.add_edge("current_run", frag_id, weight=efs)
            self._save()

    def get_impact_score(self, frag_id: str) -> float:
        """ByteRover-style impact score with MAU, reuse, contract contribution, and freshness."""
        if not self.graph.has_node(frag_id):
            return 0.0
        data = self.graph.nodes[frag_id]
        impact = (0.40 * data.get("initial_mau", 0.65)) + \
                 (0.25 * data.get("reuse_in_high_efs", 0)) + \
                 (0.20 * data.get("contract_delta_contrib", 0)) + \
                 (0.10 * data.get("replay_pass_rate", 0.75)) + \
                 (0.05 * data.get("heterogeneity", 0.72))

        # Age decay (Ebbinghaus-inspired)
        days = (date.today() - date.fromisoformat(data.get("last_use", "2025-01-01"))).days
        decayed = impact * math.exp(-0.085 * days)
        return round(max(0.0, decayed), 4)

    def query_relevant_fragments(self, query: str, top_k: int = 8, min_score: float = 0.55) -> List[Dict]:
        """Intelligent graph-based search for Orchestrator, Synthesis, Symbiosis, BD, PD Arm, etc."""
        results = []
        query_lower = query.lower()

        for node in self.graph.nodes:
            data = self.graph.nodes[node]
            preview = data.get("content_preview", "").lower()
            if (any(word in preview for word in query_lower.split()) or 
                query_lower in str(data).lower()):
                
                impact = self.get_impact_score(node)
                if impact >= min_score:
                    results.append({
                        "fragment_id": node,
                        "impact_score": impact,
                        "challenge": data.get("challenge_id"),
                        "subtask": data.get("subtask_id"),
                        "preview": data.get("content_preview", "")[:200],
                        "mau": data.get("initial_mau", 0.0),
                        "reuse_in_high_efs": data.get("reuse_in_high_efs", 0),
                        "heterogeneity": data.get("heterogeneity", 0.72),
                        "freshness_score": data.get("freshness_score", 1.0),
                        "vault_routed": data.get("vault_routed", False)
                    })

        results = sorted(results, key=lambda x: x["impact_score"], reverse=True)
        return results[:top_k]

    def cosmic_compress(self, min_utilization: float = 0.35, max_age_days: int = 30,
                       preserve_grail: bool = True) -> tuple[int, int]:
        """Advanced Cosmic Compression with centrality, community awareness, and MAU decay."""
        if not self.graph or len(self.graph.nodes) == 0:
            return 0, 0

        to_prune = []
        to_promote = []

        try:
            degree_centrality = nx.degree_centrality(self.graph)
            betweenness = nx.betweenness_centrality(self.graph, k=min(50, len(self.graph.nodes)))
        except:
            degree_centrality = {n: 0.1 for n in self.graph.nodes}
            betweenness = {n: 0.05 for n in self.graph.nodes}

        for node, data in list(self.graph.nodes(data=True)):
            if preserve_grail and data.get('in_grail', False):
                continue

            mau = data.get('initial_mau', 0.0)
            impact = self.get_impact_score(node)
            reuse = data.get('reuse_in_high_efs', 0)
            age_days = (date.today() - date.fromisoformat(data.get("last_use", "2025-01-01"))).days
            in_high_efs = reuse > 2

            score = (
                0.35 * mau +
                0.25 * impact +
                0.15 * (reuse * 0.1) +
                0.10 * degree_centrality.get(node, 0.1) +
                0.08 * betweenness.get(node, 0.05) +
                0.07 * (1.0 if in_high_efs else 0.3)
            )

            age_factor = max(0.0, 1.0 - (age_days / (max_age_days * 1.5)))
            final_score = score * age_factor

            if final_score < min_utilization and age_days > max_age_days // 2:
                to_prune.append(node)
            elif final_score > 0.82 and not data.get('in_grail', False):
                to_promote.append(node)

        if to_prune:
            self.graph.remove_nodes_from(to_prune)

        for node in to_promote:
            if node in self.graph:
                self.graph.nodes[node]['in_grail'] = True
                self.graph.nodes[node]['promoted_at'] = datetime.now().isoformat()

        logger.info(f"Cosmic Compression: Removed {len(to_prune)} nodes | Promoted {len(to_promote)} invariants")

        self._save()
        return len(to_prune), len(to_promote)

    def add_fragment(self, fragment: Dict):
        """Unified add method used by VaultRouter, PD Arm, BusinessDev, etc."""
        frag_id = fragment.get("fragment_id") or f"frag_{len(self.graph.nodes)+1}"
        self.record_fragment(
            frag_id=frag_id,
            initial_mau=fragment.get("mau_score", 0.75),
            challenge_id=fragment.get("challenge_id", "unknown"),
            subtask_id=fragment.get("subtask_id", "unknown"),
            content_preview=fragment.get("content", ""),
            heterogeneity=fragment.get("heterogeneity", 0.72)
        )
        if "vault" in fragment.get("metadata", {}):
            self.graph.nodes[frag_id]["vault_entry"] = True
            self.graph.nodes[frag_id]["vault"] = fragment["metadata"]["vault"]

    def get_average_freshness(self) -> float:
        if not self.graph.nodes:
            return 0.75
        scores = [data.get("freshness_score", 1.0) for _, data in self.graph.nodes(data=True)]
        return round(sum(scores) / len(scores), 3)

    def get_average_heterogeneity(self) -> float:
        if not self.graph.nodes:
            return 0.72
        scores = [data.get("heterogeneity", 0.72) for _, data in self.graph.nodes(data=True)]
        return round(sum(scores) / len(scores), 3)

    def mark_vault_routed(self, frag_id: str):
        if self.graph.has_node(frag_id):
            self.graph.nodes[frag_id]["vault_routed"] = True
            self._save()

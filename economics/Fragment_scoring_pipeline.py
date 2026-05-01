# fragment_scoring_pipeline.py
# SAGE v0.9.14 – Locked Economic Scoring & Promotion Module
# Implements the exact latest formulas and pipeline from the last 12 hours of conversation

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
import hashlib

@dataclass
class Fragment:
    fragment_id: str
    content: str
    creator_id: str
    em_instance_id: str
    timestamp: str
    provenance_hash: str
    gap_pain_score: float
    bd_relevance_score: float
    revenue_potential_score: float
    proposal_readiness_score: float
    impact_score: float
    metadata: Dict = None

class FragmentScoringPipeline:
    """Implements the full latest locked economic scoring pipeline."""

    def __init__(self):
        # Tunable thresholds (Meta-RL can adjust)
        self.gap_pain_threshold = 0.65
        self.bd_relevance_threshold = 0.65
        self.revenue_potential_threshold = 0.65
        self.proposal_readiness_threshold = 0.65
        self.synapse_promotion_threshold = 0.82
        self.verifier_floor_efs = 0.72
        self.verifier_floor_7d = 0.68

    def compute_gap_pain_score(self, f: float, s: float, c: float, i: float, vf: float = 1.0, p: float = 0.0) -> float:
        """Gap Pain Score – primary trigger."""
        return (f**0.25 * s**0.30 * c**0.25 * i**0.20) * vf * (1 - p)

    def compute_bd_relevance_score(self, f: float, v: float, k: float, d: float, c: float, vf: float = 1.0, p: float = 0.0) -> float:
        """BD Relevance Score – business-data heavy."""
        return (f**0.20 * v**0.20 * k**0.25 * d**0.20 * c**0.15) * vf * (1 - p)

    def compute_revenue_potential_score(self, r: float, v: float, m: float, o: float, c: float, vf: float = 1.0, p: float = 0.0) -> float:
        """Revenue Potential Score – pre-marketplace adjusted."""
        return (r**0.10 * v**0.30 * m**0.25 * o**0.20 * c**0.15) * vf * (1 - p)

    def compute_proposal_readiness_score(self, k: float, c: float, p: float, v: float, t: float, vf: float = 1.0, n: float = 0.0) -> float:
        """Proposal Readiness Score – business-data heavy."""
        return (k**0.30 * c**0.25 * p**0.20 * v**0.15 * t**0.10) * vf * (1 - n)

    def compute_impact_score(self, g: float, r: float, k: float, d: float, c: float, vf: float = 1.0, n: float = 0.0) -> float:
        """Impact Score – for contributor rewards and vault promotion."""
        return (g**0.30 * r**0.25 * k**0.20 * d**0.15 * c**0.10) * vf * (1 - n)

    def meets_3_of_4_rule(self, gap_pain: float, bd_relevance: float,
                          revenue_potential: float, proposal_readiness: float) -> bool:
        """3-of-4 promotion rule with mandatory Gap Pain + BD Relevance."""
        mandatory = (gap_pain >= self.gap_pain_threshold) and (bd_relevance >= self.bd_relevance_threshold)
        if not mandatory:
            return False
        additional = sum([
            revenue_potential >= self.revenue_potential_threshold,
            proposal_readiness >= self.proposal_readiness_threshold
        ])
        return additional >= 1

    def should_promote_to_synapse_vault(self, gap_pain: float, bd_relevance: float,
                                        revenue_potential: float, proposal_readiness: float) -> bool:
        """Full promotion decision."""
        return self.meets_3_of_4_rule(gap_pain, bd_relevance, revenue_potential, proposal_readiness)

    def score_fragment(self, content: str, creator_id: str, em_instance_id: str,
                       gap_pain_inputs: Dict, bd_inputs: Dict, revenue_inputs: Dict,
                       proposal_inputs: Dict, metadata: Dict = None) -> Fragment:
        """Full scoring pipeline for a new fragment using latest locked formulas."""

        # Compute each score using latest formulas
        gap_pain = self.compute_gap_pain_score(**gap_pain_inputs)
        bd_relevance = self.compute_bd_relevance_score(**bd_inputs)
        revenue_potential = self.compute_revenue_potential_score(**revenue_inputs)
        proposal_readiness = self.compute_proposal_readiness_score(**proposal_inputs)

        # Impact Score
        impact = self.compute_impact_score(
            g=gap_pain,
            r=revenue_potential,
            k=bd_inputs.get("k", 0.0),
            d=bd_inputs.get("d", 0.0),
            c=bd_relevance
        )

        # Provenance
        provenance_str = f"{content}{creator_id}{em_instance_id}{datetime.now().isoformat()}"
        provenance_hash = hashlib.sha256(provenance_str.encode()).hexdigest()

        fragment = Fragment(
            fragment_id=f"frag_{provenance_hash[:12]}",
            content=content,
            creator_id=creator_id,
            em_instance_id=em_instance_id,
            timestamp=datetime.now().isoformat(),
            provenance_hash=provenance_hash,
            gap_pain_score=round(gap_pain, 4),
            bd_relevance_score=round(bd_relevance, 4),
            revenue_potential_score=round(revenue_potential, 4),
            proposal_readiness_score=round(proposal_readiness, 4),
            impact_score=round(impact, 4),
            metadata=metadata or {}
        )

        return fragment

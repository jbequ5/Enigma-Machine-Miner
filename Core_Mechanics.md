# SAGE Core Mechanics Reference

**Single Source of Truth — v0.9.15+ (Locked & Aligned with `solve_fragment_scoring.py`)**  
**All scoring, gating, contribution, and data-flow definitions**

This file is the authoritative reference. Every other document in the SAGE suite links back here for formulas, defaults, and rules. All formulas are implemented exactly in `solve_fragment_scoring.py` and `ValidationOracle`.

## 1. Scoring Foundations (Exact Production Formulas)

**60/40 Final Impact Score** (used everywhere in Solve, ValidationOracle, and downstream)
- **Base EFS** = `compute_7d_geometric_mean(seven_d_scores)` × calibration_c × verifier_floor × r_term  
  (exact weighted geometric mean from `SolveFragmentScoringModule.compute_7d_geometric_mean` + `compute_base_efs`)
- **Refined Value-Added** = geometric mean of (n, r, m, c) × (1.0 - p_noise)  
  (exact from `SolveFragmentScoringModule.compute_refined_value_added`)
- **Final Impact Score** = `0.6 × Base EFS + 0.4 × Refined Value-Added`

**Exact 7D Dimensions & Weights** (from production module):
```python
SEVEN_D_DIMENSIONS = ["edge_coverage", "invariant_tightness", "adversarial_resistance",
                      "calibration_quality", "composability", "robustness_to_noise", "predictive_power"]
SEVEN_D_WEIGHTS = {"edge_coverage": 0.18, "invariant_tightness": 0.20,
                   "adversarial_resistance": 0.15, "calibration_quality": 0.12,
                   "composability": 0.13, "robustness_to_noise": 0.11,
                   "predictive_power": 0.11}

Current Defaults & Hard Floors:
•  verifier_floor_threshold = 0.65
•  final_impact_hard_floor = 0.82 (vault promotion gate)
•  Global re-scoring tolerance = 0.08 (any change > 0.08 flags for AHE/Defense review)
Heterogeneity is planning-only (swarm diversity, guided candidates, _enforce_heterogeneity_in_swarm). It is never used in Base EFS, Refined Value-Added, or Final Impact Score.
EFS Lift (0.9.15 Meta-Assessment):
•  ActualEFSLift = FinalImpactScore_after - FinalImpactScore_before
•  ProjectedEFSLift = learned linear regression on ErrorClusterSize + NoveltyScore
•  Minimum acceptable lift for new expert / objective change = 0.12
θ_dynamic (dynamic calibration factor):

θ_dynamic = 0.65 * (1 - 0.4 * (1 - c)**0.8) * progress_factor

2. Contribution Scoring
ContributionScore (rewards, access tiers, governance priority)

ContributionScore = 0.40 * FinalImpactScore + 0.25 * utilization_EMA + 0.20 * graph_centrality + 0.15 * refined_value_added

•  utilization_EMA: λ = 0.85 exponential moving average
•  graph_centrality: PageRank (damping 0.85) on Strategy graph
•  Re-evaluated globally on every major update with 0.08 tolerance
RewardShare (marketplace / prize revenue)

RewardShare = ContributionScore / Σ(all active contributors’ ContributionScores) × total_pool

3. Key Data Flows & API Contracts
Core Intelligence Pipeline
Solve (gated fragments with exact 60/40 scoring) → Strategy (ranked & enriched) → Defense (adversarial hardening) → Intelligence (Meta-RL + NN Head + distillation) → Synapse (Meta-Agent self-assessment)
Economic Value Pipeline
Raw BD/PD artifacts → Economic (upgrade using Strategy + Defense) → Marketplace → Revenue → larger prize pools → new challenges → Solve
API Contract Stubs (sage-core ↔ sage-intelligence)
Feed Vault Push
POST /feed_vault
Payload includes fragments, provenance, efs_metrics (final_impact_score, base_efs, refined_value_added, actual_efs_lift), run_id
Meta-Weight Pull
GET /meta_weights?version=latest
Response includes global weights, strategy approximations, and 0.9.15 self-assessment decisions
Defense Package Push
POST /defense_package — updated rules, attack vectors, hardened snippets
4. Safety & Anti-Gaming Rules
•  All fragments must pass deterministic gates in Solve + exact 60/40 Final Impact Score floor.
•  Global re-scoring tolerance (0.08) triggers AHE/Defense review or automatic downgrade.
•  High-value artifacts use tiered access + selective encryption.
•  Meta-RL proposals in Intelligence are subject to 0.9.15 self-assessment + EFS Lift gating.
•  Defense Subsystem (AHE) continuously red-teams every layer.
•  Cherry-picking or gaming is penalized via tolerance checks, replay-rate decay, and ContributionScore reduction.
5. Contribution & Reward Principles
•  Every surviving fragment receives immutable provenance via SolveFragmentScoringModule.
•  ContributionScore determines reward share in marketplace revenue and access tier to Synapse.
•  Honest participation is rewarded; gaming is penalized via tolerance checks and decay.
All other documents in the suite reference this Core Mechanics Reference for formulas and rules. No formula should appear in multiple places without linking back here.
Locked as of 2026-05-08 — aligned with solve_fragment_scoring.py and ValidationOracle v0.9.15+

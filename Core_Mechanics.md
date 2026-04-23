# SAGE Core Mechanics Reference

**Single Source of Truth — v0.9.13-FeedbackUpdate1**  
**All scoring, gating, contribution, and data-flow definitions**

This file is the authoritative reference. Every other document in the SAGE suite links back here for formulas, defaults, and rules.

## 1. Scoring Foundations

**60/40 EFS Split** (used in Solve and propagated everywhere)
- **Base EFS** = 0.40·validation_score + 0.20·verifier_7D_average + 0.20·composability_score + 0.20·θ_dynamic
- **Refined Value-Added** = 0.50·historical_EFS_lift + 0.30·calibration_accuracy + 0.20·reuse_multiplier
- **Final EFS** = 0.60·Base EFS + 0.40·Refined Value-Added

**Current Defaults & Ranges**:
- validation_score: 0.0 – 1.0 (typically 0.65–0.95)
- verifier_7D_average: 0.0 – 1.0 (typically 0.60–0.92)
- composability_score: 0.0 – 1.0 (typically 0.70–0.98)
- θ_dynamic: 0.0 – 1.0 (typically 0.75–0.96)
- historical_EFS_lift: -0.15 – +0.25 (realistic range)
- calibration_accuracy: 0.0 – 1.0
- reuse_multiplier: 0.0 – 2.0 (capped at 2.0)

**Example Calculation**:
Fragment with: validation_score=0.88, verifier_7D=0.81, composability=0.92, θ_dynamic=0.89, historical_lift=+0.04, calibration_accuracy=0.76, reuse_multiplier=1.35  
→ Base EFS = (0.40·0.88) + (0.20·0.81) + (0.20·0.92) + (0.20·0.89) = 0.872  
→ Refined Value-Added = (0.50·0.04) + (0.30·0.76) + (0.20·1.35) = 0.542  
→ Final EFS = (0.60·0.872) + (0.40·0.542) = 0.740

**θ_dynamic** (dynamic calibration factor)  
θ_dynamic = 1.0 - (0.6·calibration_error + 0.25·score_variance + 0.15·replan_rate)  
Default ranges: calibration_error 0.02–0.18, score_variance 0.01–0.12, replan_rate 0.0–0.35.

**Global Re-scoring Tolerance**  
Any proposed change (weight tweak, gating rule, ranking adjustment) that would shift a fragment’s Final EFS by more than **0.08** is automatically flagged for review or rejected. This is the primary anti-gaming mechanism.

## 2. Contribution Scoring

**ContributionScore** (used for rewards, access tiers, and governance priority)  
ContributionScore = 0.40·Final EFS + 0.25·utilization_EMA + 0.20·graph_centrality + 0.15·refined_value_added

- utilization_EMA uses λ = 0.85 exponential moving average.
- graph_centrality uses PageRank (damping factor 0.85) on the Strategy graph.
- Score is re-evaluated globally on every major update with the 0.08 tolerance.

**RewardShare** (portion of marketplace or prize revenue)  
RewardShare = ContributionScore / Σ(all active contributors’ ContributionScores) × total_pool

## 3. Key Data Flows & API Contracts

**Core Intelligence Pipeline**  
Solve (gated fragments) → Strategy (ranked & enriched) → Defense (adversarial hardening) → Intelligence (Meta-RL + NN Head + distillation) → Synapse (Meta-Agent)

**Economic Value Pipeline**  
Raw BD/PD artifacts → Economic (upgrade using Strategy + Defense) → Marketplace → Revenue → larger prize pools → new challenges → Solve

**API Contract Stubs** (sage-core ↔ sage-intelligence)

**Feed Vault Push (from core to intelligence)**  
Endpoint: `POST /feed_vault`  
Payload: `{ "fragments": [...], "provenance": {...}, "efs_metrics": {...}, "run_id": str, "timestamp": iso }`  
Requirements: All fragments must pass local Solve gates; signed provenance hash.

**Meta-Weight Pull (from intelligence to core)**  
Endpoint: `GET /meta_weights?version=latest`  
Response: `{ "global_weights": {...}, "strategy_approximations": {...}, "tuning_level": int, "valid_until": iso }`  
Local EM loads these at startup and after each major global update.

**Defense Package Push**  
Endpoint: `POST /defense_package`  
Payload: Updated rules, attack vectors, or hardened snippets. Applied locally by qualified users.

## 4. Safety & Anti-Gaming Rules
- All fragments must pass deterministic gates in Solve (official challenge, EFS floor, replay-rate guard, provenance validation).
- High-value artifacts use tiered access + selective encryption.
- All Meta-RL proposals in Intelligence are subject to global re-scoring tolerance and human/governance gates for major changes.
- Defense Subsystem (AHE) continuously red-teams every layer.
- Cherry-picking or gaming is penalized via tolerance checks, replay-rate decay, and ContributionScore reduction.

## 5. Contribution & Reward Principles
- Every surviving fragment in Solve is immediately credited with immutable provenance.
- ContributionScore determines reward share in marketplace revenue and access tier to Synapse.
- Honest participation is rewarded; cherry-picking or gaming is penalized via tolerance checks and decay.

**All other documents in the suite reference this Core Mechanics Reference for formulas and rules. No formula should appear in multiple places without linking back here.**

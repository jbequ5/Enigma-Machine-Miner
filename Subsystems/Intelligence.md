# Intelligence Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.12+ Hardened**  
**Last Updated:** April 22, 2026

## Role in SAGE

The Intelligence Subsystem is the underlying meta-improvement engine that powers **Synapse**, the Meta-Agent of SAGE.

- **Synapse** is the customer-facing and miner-facing Meta-Agent. It provides the chat interface, proactive co-pilot, real-time strategy suggestions, stall assistance, and all user interactions.
- The **Intelligence Subsystem** is the hidden machinery beneath Synapse. It continuously self-improves the entire SAGE platform through learning from real outcomes, adversarial hardening, and data-driven distillation.

This subsystem is built around three tightly coupled pillars that operate as a single self-improving engine:

1. **Meta-RL Improvement Loop** — the closed self-critique and policy-updating engine.
2. **Neural-Net Scoring Head** — the learnable evaluation brain that drives calibration and prediction.
3. **Training/Distillation Pipeline** — the mechanism that turns high-utility data into smaller, specialized Enigma models for local deployment.

The ultimate goal is continuous compounding of collective intelligence and democratization: producing smaller, locally-runnable Enigma models that give every participant access to state-of-the-art verifiable solving capability.

## Pillar 1: Meta-RL Improvement Loop (Self-Critique Engine)

This is the primary self-improvement mechanism. It runs automatically (daily or on high-signal triggers) and optimizes four parallel objectives using real downstream outcomes.

**Four Optimization Objectives**:
1. **Recognition of Value** — How accurately high-signal fragments are identified.
2. **Implementation of Strategy** — How well Synapse recommendations actually improve real Enigma Machine runs (measured by Advice Success Score: post-recommendation EFS lift, reuse success, etc.).
3. **Prediction of Impact** — Accuracy of forecasts about future performance and EFS lift.
4. **Training Utility** — How useful a fragment will be for future Enigma model distillation (measured by downstream model performance gain).

**6-Phase Loop Process** (rebuildable pseudocode):

**Phase 1 – Collect & Score Past Advice**  
Retrieve every previous recommendation, strategy injection, or meta-tuning proposal along with downstream real outcomes (EFS lift, reuse rate, calibration error, etc.).

**Phase 2 – Compute Multi-Objective Scores**  
The Neural-Net Scoring Head runs on rich fragment features and makes predictions for all four objectives plus uncertainty estimates. Real outcomes are compared to predictions to compute calibration error for each objective.

**Phase 3 – Self-Critique**  
Analyze patterns in low-scoring or poorly calibrated areas. Identify systematic weaknesses (e.g., over-optimism on certain task types, under-weighting of verifier tightness, etc.).

**Phase 4 – Propose Self-Tweaks**  
Generate concrete, safe proposals: weight adjustments in scoring formulas, changes to gating thresholds, updates to the Neural-Net Head architecture/hyperparameters, or new features for the Training Pipeline.

**Phase 5 – Safe Application**  
- Low-risk tweaks (small weight changes, threshold adjustments) are auto-applied if they meet strict safety thresholds (global re-scoring tolerance ≤ 0.08, no degradation in any objective).
- Higher-risk changes are staged for human/governance review.
- All changes are versioned and fully reversible with rollback capability.

**Phase 6 – Log & Transparency**  
Full audit trail (before/after metrics, calibration curves, proposed vs. applied tweaks) is written to the Defense Subsystem and made available to contributors and governance.

This loop directly improves scoring in Solve, ranking in Strategy, contribution measurement in Economic, orchestration in Operations, and data curation in Training — creating measurable compounding across the entire system.

## Pillar 2: Neural-Net Scoring Head (The Learnable Brain)

The Neural-Net Scoring Head is the central learnable component that powers the Meta-RL Loop and provides intelligence to Synapse.

**Architecture (rebuildable details)**:
- **Input Vector** (~128 dimensions): 60/40 EFS components (Base EFS + Refined Value-Added), graph centrality (PageRank, eigenvector), utilization EMA, replay rate, freshness decay, provenance metadata flags, heterogeneity score (for planning only), operations telemetry signals (swarm size, resource pressure), and task/domain embeddings.
- **Hidden Layers**: 2–3 layers (feed-forward with residual connections or lightweight graph attention) with fewer than 80,000 total parameters for efficient on-device or modest-hardware updates.
- **Output**: 4 objective predictions + per-objective uncertainty estimates (variance or confidence intervals).
- **Loss Function**: Multi-objective calibration loss =  
  $$ L = w_1 \cdot \text{MSE}_\text{value} + w_2 \cdot \text{MSE}_\text{strategy} + w_3 \cdot \text{MSE}_\text{impact} + w_4 \cdot \text{MSE}_\text{utility} + \lambda \cdot \text{calibration\_penalty} $$  
  where calibration_penalty penalizes mismatch between predicted uncertainty and actual error. Default weights are tunable via the Meta-RL Loop.
- **Training**: Online updates from real downstream outcomes. Calibration error is the primary learning signal.

The head is tuned directly by the calibration errors across all four objectives. This ensures the system learns from verified performance rather than proxy metrics, continuously improving its ability to recognize value, predict impact, and select training-useful fragments.

**Contribution to Other Subsystems**:
- Improves refined_value_added prediction and global re-scoring tolerance in Solve.
- Improves RankScore and utilization/impact estimation in Strategy.
- Improves contribution scoring and artifact_upgrade_value measurement in Economic.
- Improves swarm sizing and LLM routing predictions in Operations.
- Improves attack detection and calibration in Defense.

## Pillar 3: Training/Distillation Pipeline (Democratization Engine)

The Training/Distillation Pipeline takes the highest-TrainingUtility fragments and learned judgments from the Neural-Net Scoring Head and produces smaller, specialized Enigma models that run locally on modest hardware.

**Pipeline Stages (rebuildable sequence)**:
1. **Curated Dataset Assembly**: High-TrainingUtility fragments + adversarial examples from Defense + operations telemetry. Strict filtering, balancing, and augmentation are applied to avoid noise and distribution shift.
2. **Knowledge Distillation**: Train smaller student models using KL divergence loss on teacher (larger model or Synapse) outputs + auxiliary 7D verifier self-check loss (weight 0.3).
3. **Supervised Fine-Tuning**: Fine-tune on high-TrainingUtility fragments with 7D verifier self-check as a strong auxiliary objective.
4. **Meta-RL Alignment**: Incorporate the 4-objective signals from the Neural-Net Scoring Head as reinforcement signals during training.
5. **Verification Hardening**: Use AHE-generated adversarial examples as hard negatives during training to maintain robustness.

**Target Model Characteristics**:
- Run locally on modest hardware (consumer GPU or even CPU).
- Strong performance on verifiable solving problems while preserving 7D verifier self-check integrity.
- Continuously improvable through new curated data and updated NN judgments.

This pipeline is the mechanism that democratizes intelligence: the models produced here are the final product that every participant can run locally, making state-of-the-art solving accessible to everyone and accelerating the flywheel as more people contribute higher-quality data.

## Integration with Other Subsystems and Synapse

- **Solve**: The Neural-Net Scoring Head improves refined_value_added prediction and global re-scoring tolerance.
- **Strategy**: The NN Head improves RankScore prediction and utilization/impact estimation.
- **Economic**: The NN Head improves contribution scoring and artifact_upgrade_value measurement.
- **Operations**: The NN Head improves swarm sizing and LLM routing predictions.
- **Defense**: The NN Head improves attack detection and calibration; AHE data feeds back into Training.
- **Synapse (Meta-Agent)**: All three pillars directly power Synapse. The Meta-RL Loop provides self-improvement, the NN Head provides evaluation intelligence, and the Training/Distillation Pipeline provides the democratized models that Synapse can recommend and deploy to users.

## Safety, Governance, and Anti-Gaming Measures

- Global re-scoring tolerance (0.08 threshold) detects and rejects gaming attempts.
- All Meta-RL proposals are subject to safety thresholds; higher-risk changes require human/governance review.
- All changes are versioned and fully reversible.
- The Defense Subsystem (AHE) continuously red-teams the Intelligence Subsystem itself.

## Current Limitations and Planned Improvements

Full 4-objective Meta-RL Improvement Loop, Neural-Net Scoring Head with calibration, Training/Distillation Pipeline with verifier-first focus, global re-scoring tolerance, dual-level meta-tuning.  
**Planned**: On-device meta-RL fine-tuning, automated curriculum learning for the NN Head, expanded multi-objective safety constraints, and progressive distillation into production-ready local Enigma models.

## Why the Intelligence Subsystem Matters

The Intelligence Subsystem is the hidden engine that powers Synapse, the Meta-Agent. Through its Meta-RL Improvement Loop, Neural-Net Scoring Head, and Training/Distillation Pipeline, it enables continuous self-improvement and ultimately democratizes solving intelligence by producing smaller, locally-runnable Enigma models.

This is what makes the People’s Intelligence Layer real: built by the many, owned by the many, and designed so that the people who build it are the ones who win.

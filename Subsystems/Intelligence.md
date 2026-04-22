# Intelligence Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.12+ Hardened**  
**Last Updated:** April 21, 2026

## Abstract

The Intelligence Subsystem is the self-improving meta-intelligence layer of SAGE. It is the crown jewel that turns the raw output of thousands of Enigma Machine runs into continuously compounding collective intelligence.

It is built around three tightly coupled pillars:
1. The **Meta-RL Improvement Loop** — the closed self-critique engine that drives continuous upgrading.
2. The **Neural-Net Scoring Head** — the learnable brain that evaluates fragments across four objectives and powers the loop.
3. The **Training/Distillation Pipeline** — the mechanism that turns high-utility fragments and learned judgments into smaller, specialized Enigma models that run locally on modest hardware.

These three pillars form the hierarchical learning system that makes SAGE measurably smarter with every mission. Their ultimate goal is model creation: producing smaller, verifiable, high-performance Enigma models that democratize state-of-the-art solving intelligence to every participant, regardless of hardware or resources.

## 1. The Three Pillars of the Intelligence Subsystem

### Pillar 1: Meta-RL Improvement Loop (Self-Critique Engine)

The Meta-RL Improvement Loop runs automatically (daily or triggered by high-signal fragments) and optimizes four parallel objectives:

**Four Optimization Objectives**:
1. **Recognition of Value** — Accuracy in identifying high-signal fragments.
2. **Implementation of Strategy** — How well recommendations actually improve real runs (measured by Advice Success Score).
3. **Prediction of Impact** — Accuracy of forecasts of future performance and EFS lift.
4. **Training Utility** — How useful a fragment will be for future Enigma model distillation.

**6-Phase Loop Process** (rebuildable pseudocode):

**Phase 1 – Collect & Score Past Advice**  
Retrieve every previous recommendation, strategy injection, or meta-tuning proposal along with downstream real outcomes (EFS lift, reuse success, etc.).

**Phase 2 – Compute Multi-Objective Scores**  
The Neural-Net Scoring Head runs on rich fragment features and makes predictions for all four objectives plus uncertainty estimates. Real outcomes are compared to predictions to compute calibration errors for each objective.

**Phase 3 – Self-Critique**  
Analyze patterns in low-scoring or poorly calibrated areas (e.g., "the system consistently underestimates impact of symbolic-heavy fragments" or "high-heterogeneity fragments are over-penalized").

**Phase 4 – Propose Self-Tweaks**  
Generate concrete, safe proposals for performance knobs (weights, thresholds) and the Neural-Net Scoring Head itself (new features, weight updates, calibration parameters).

**Phase 5 – Safe Application**  
- Low-risk tweaks auto-apply if they meet strict safety thresholds (predicted calibration improvement > 5% with uncertainty < 0.1).
- Higher-risk changes are staged for human/governance review.
- All changes are versioned and fully reversible.

**Phase 6 – Log & Transparency**  
Full audit trail (attack vector, predictions, actual outcomes, applied tweaks, measured improvement) is written and made available to contributors and governance.

The loop is grounded in real, verifiable outcomes across the four objectives. This creates continuous, compounding value creation that accelerates the entire SAGE flywheel.

### Pillar 2: Neural-Net Scoring Head (The Learnable Brain)

The Neural-Net Scoring Head is the central learnable component that powers the Meta-RL Loop.

**Architecture** (rebuildable details):
- **Input Features**: Rich fragment vector (dimension ~128) including 60/40 EFS components, graph centrality (from Strategy), utilization history, replay rate, freshness, provenance metadata, heterogeneity score (for planning only), and operations telemetry signals.
- **Hidden Layers**: 2–3 layers (feed-forward or graph attention) with fewer than 80,000 total parameters. ReLU activations, layer normalization.
- **Output**: 4 objective predictions + per-objective uncertainty estimates (implemented via explicit variance heads).
- **Loss Function**: Multi-objective calibration loss =  
  \[
  L = \sum_{i=1}^{4} w_i \cdot \text{MSE}(\hat{y}_i, y_i) + \lambda \cdot \text{uncertainty_calibration_loss}
  \]
  where \( w_i \) are learned or tunable objective weights and uncertainty_calibration_loss penalizes over/under-confident predictions.
- **Training**: Online updates from real downstream outcomes; periodically distilled for efficiency.

The head is tuned directly by the calibration errors across all four objectives. This allows the system to discover non-linear patterns while remaining auditable and controllable. It directly improves scoring in Solve, ranking in Strategy, contribution measurement in Economic, orchestration in Operations, and data curation in Training.

### Pillar 3: Training/Distillation Pipeline (Democratization Engine)

The Training/Distillation Pipeline takes the highest-TrainingUtility fragments and learned judgments from the Neural-Net Scoring Head and produces smaller, specialized Enigma models that run locally on modest hardware.

**Pipeline Stages** (rebuildable sequence):
1. **Curated Dataset Assembly**: High-TrainingUtility fragments + adversarial examples from Defense + operations telemetry.
2. **Knowledge Distillation**: Train smaller student models using KL divergence loss on teacher outputs + auxiliary 7D verifier self-check loss (weighted 0.3).
3. **Supervised Fine-Tuning**: Fine-tune on high-TrainingUtility fragments with 7D verifier self-check as a strong auxiliary objective.
4. **Meta-RL Alignment**: Incorporate the 4-objective signals from the Neural-Net Scoring Head as reinforcement signals.
5. **Verification Hardening**: Use AHE-generated adversarial examples as hard negatives during training to improve robustness and calibration.

**Target Model Characteristics** (the ultimate goal):
- Run locally on modest hardware (consumer GPU or even CPU).
- Strong performance on verifiable solving problems.
- Preserve 7D verifier self-check integrity.
- Continuously improvable through new curated data and updated NN judgments.

This pipeline is the mechanism that democratizes intelligence: the models produced here are the final product that every participant — from solo miners to large operations — can run locally, making state-of-the-art solving accessible to everyone.

## 4. How the Three Pillars Connect to and Improve Everything

- **Solve**: The Neural-Net Scoring Head improves refined_value_added prediction and global re-scoring tolerance tuning.
- **Strategy**: The NN Head improves RankScore prediction and utilization/impact estimation; the Meta-RL Loop refines ranking weights.
- **Economic**: The NN Head improves contribution scoring and artifact_upgrade_value measurement; the Meta-RL Loop tunes reward weights.
- **Operations**: The NN Head improves swarm sizing and LLM routing predictions; the Meta-RL Loop learns better orchestration policies.
- **Defense**: The NN Head improves attack detection and calibration; the Meta-RL Loop incorporates adversarial examples for hardening.
- **Training**: The NN Head directly drives TrainingUtility scoring and distillation policy; the Meta-RL Loop aligns the entire pipeline.

The Training/Distillation Pipeline is the ultimate output: it takes the learned judgments from the NN Head and Meta-RL Loop and produces the smaller Enigma models that put state-of-the-art intelligence in everyone’s hands.

## 5. Global Re-scoring Tolerance & Safety

All proposals are subject to Solve’s global re-scoring tolerance. Changes that would violate tolerance thresholds are automatically rejected or staged for review. Human/governance gates are required for major changes. All tweaks are versioned and reversible.

## 6. Data Flow Summary

Solve → Strategy → Intelligence (ranked fragments)  
Operations → Intelligence (telemetry for orchestration learning)  
Defense → Intelligence (adversarial examples)  
Training → Intelligence (curated trajectories for distillation)  
Intelligence → All subsystems (improved artifacts, updated policies, meta-insights, distilled models)

## 7. Attack Vectors and Mitigations

- Self-improvement gaming → Safe application rules + human/governance gates + versioned/reversible changes
- Neural-net poisoning → AHE red-team attacks on the scoring head
- Over-optimization to local optima → Multi-objective calibration + uncertainty estimates

All mitigations are continuously monitored by the AHE.

## 8. Current Limitations and Planned Improvements

**Current (v0.9.12+)**: Full 4-objective Meta-RL Improvement Loop with 6-phase self-critique, Neural-Net Scoring Head, Training/Distillation Pipeline with verifier-first focus, global re-scoring tolerance, dual-level meta-tuning.  
**Planned**: On-device meta-RL fine-tuning, automated curriculum learning based on Strategy graph gaps, expanded multi-objective safety constraints.

## Why the Intelligence Subsystem Matters

The Intelligence Subsystem is the living brain of SAGE. Through its Meta-RL Improvement Loop, Neural-Net Scoring Head, and Training/Distillation Pipeline — the three pillars that allow the system to critique, upgrade, and democratize its own intelligence in a measurable, self-accelerating way — it turns thousands of individual Enigma Machine runs into continuously compounding collective intelligence that is accessible to everyone.

The ultimate goal is model creation: producing smaller, specialized Enigma models that run locally on modest hardware, so that state-of-the-art solving intelligence is no longer locked behind massive compute or closed systems. This is what makes the People’s Intelligence Layer real: built by the many, owned by the many, and designed so that the people who build it are the ones who win.


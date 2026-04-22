# Intelligence Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.12+ Hardened**  
**Last Updated:** April 22, 2026

## Role in SAGE
The Intelligence Subsystem is the underlying meta-improvement engine that powers **Synapse**, the Meta-Agent of SAGE.

- **Synapse** is the customer-facing and miner-facing Meta-Agent (chat interface, proactive co-pilot, real-time strategy suggestions).
- The **Intelligence Subsystem** is the hidden machinery beneath Synapse. It continuously self-improves the entire SAGE platform.

It is built around three tightly coupled pillars.

## Pillar 1: Meta-RL Improvement Loop
The closed self-critique engine that optimizes four objectives using real downstream outcomes.

**Four Objectives**:
1. Recognition of Value
2. Implementation of Strategy (measured by Advice Success Score)
3. Prediction of Impact
4. Training Utility

**6-Phase Loop** (pseudocode available on request):
1. Collect past advice + real outcomes
2. Compute multi-objective scores via Neural-Net Scoring Head
3. Self-critique systematic weaknesses
4. Propose safe tweaks
5. Safe application (versioned, reversible, tolerance-checked)
6. Log and transparency

## Pillar 2: Neural-Net Scoring Head
The learnable brain that evaluates fragments and drives the Meta-RL Loop.

**Input Vector** (~128 dimensions):
- 60/40 EFS components
- Graph centrality (PageRank, eigenvector)
- Utilization EMA, replay rate, freshness decay
- Provenance metadata flags
- Heterogeneity score (planning only)
- Operations telemetry signals

**Loss Function**:
$$ L = w_1 \cdot \text{MSE}_\text{value} + w_2 \cdot \text{MSE}_\text{strategy} + w_3 \cdot \text{MSE}_\text{impact} + w_4 \cdot \text{MSE}_\text{utility} + \lambda \cdot \text{calibration\_penalty} $$

Calibration error from real outcomes is the primary learning signal.

## Pillar 3: Training/Distillation Pipeline
The democratization engine that produces smaller, locally-runnable Enigma models.

**Pipeline Stages**:
1. Curated Dataset Assembly (filtering + balancing + augmentation)
2. Knowledge Distillation (KL divergence + 0.3 × 7D verifier self-check loss)
3. Supervised Fine-Tuning
4. Meta-RL Alignment
5. Verification Hardening (AHE adversarial examples as hard negatives)

**Target**: Modest-hardware Enigma models that preserve 7D verifier integrity and improve with new data.

## Integration and Safety
The subsystem improves scoring in Solve, ranking in Strategy, contribution scoring in Economic, orchestration in Operations, and hardening in Defense. All proposals are subject to global re-scoring tolerance (0.08) and human/governance gates for major changes.

## Why It Matters
The Intelligence Subsystem is the engine that makes Synapse continuously smarter and ultimately democratizes solving intelligence through accessible local Enigma models. This is what turns raw solving data into compounding collective capability that benefits the entire community.

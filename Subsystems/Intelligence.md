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

# 1. Meta-RL Improvement Loop — Deep Technical Dive

## Role and Purpose
The Meta-RL Improvement Loop is the core self-improvement engine of the Intelligence Subsystem. It is the mechanism that allows Synapse (the Meta-Agent) to continuously get smarter by learning from real downstream outcomes rather than static prompts or simple reflection.

It operates on four measurable objectives using calibration error from actual Enigma Machine runs as the primary learning signal. The loop runs automatically (daily or on high-signal triggers) and proposes safe, versioned tweaks that improve scoring, ranking, gating, and strategy recommendations across the entire SAGE platform.

## The Four Optimization Objectives
The loop optimizes four parallel objectives, each measured against real downstream performance:

1. **Recognition of Value**  
   How accurately the system identifies genuinely high-signal fragments versus noise or low-value data. Measured by correlation between predicted value and actual EFS lift in future runs.

2. **Implementation of Strategy** (Advice Success Score)  
   How well Synapse recommendations actually improve real EM runs. Measured by post-recommendation EFS delta, reuse success rate, and reduction in replan cycles.

3. **Prediction of Impact**  
   Accuracy of forecasts about future EFS lift or performance gain when a fragment or strategy is used. Measured by prediction error on held-out runs.

4. **Training Utility**  
   How useful a fragment will be for future Enigma model distillation. Measured by downstream model performance gain (verifier robustness, calibration improvement, generalization).

For each objective, the Neural-Net Scoring Head produces a prediction + uncertainty estimate. The loop then compares predictions to real outcomes to compute calibration error — the key learning signal.

## The 6-Phase Loop Process
The Meta-RL Improvement Loop follows a repeatable 6-phase process:

**Phase 1 – Collect & Score Past Advice**  
Retrieve every previous recommendation, strategy injection, or meta-tuning proposal along with downstream real outcomes (EFS lift, reuse success, calibration error, replan count, etc.).

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

## How Calibration Error Drives Learning
Calibration error is the difference between the NN’s predicted probability/impact and the actual observed outcome. It is the primary signal that updates the NN weights and informs the Meta-RL Loop’s self-tweaks. This makes the system learn from verified performance rather than proxy metrics.

## Integration with Neural-Net Scoring Head
The NN Scoring Head is the evaluation brain that feeds the loop. It takes a ~128-dimension feature vector (60/40 EFS components, graph centrality, utilization EMA, replay rate, freshness, provenance flags, heterogeneity score for planning only, operations telemetry) and outputs predictions for the four objectives plus uncertainty estimates.

The loop uses these predictions to compute calibration error, which then updates the NN itself.

## How Outputs Propagate Back to the EM Level
1. The loop produces updated global approximations (weights, thresholds, strategy templates, LLM routing maps).
2. Synapse pushes these approximations to the Operations layer.
3. When a new EM run starts (or the wizard runs), Operations loads the latest global approximations. The EM begins with these tuned defaults.
4. During a run, Synapse can query the latest NN outputs in real time to provide co-pilot suggestions, ranked fragments, and smart stopping recommendations.
5. After the run, new fragments feed back into the loop, improving the next cycle.

This creates a hierarchical learning effect: global meta-learning improves local EM runs, and local runs provide better data for global learning.

## Example Cycle
A fragment from a quantum circuit run is evaluated by the NN. The NN predicts high Implementation of Strategy score but low Prediction of Impact calibration. The Meta-RL Loop detects the mismatch, proposes a small weight adjustment to the verifier_7D_average term, applies it safely (within 0.08 tolerance), and logs the change. All future EM runs now start with a slightly stronger verifier weight, leading to higher average EFS and better fragments in the next cycle.

## Safety, Governance, and Limitations
- All tweaks are subject to global re-scoring tolerance (0.08) and human/governance gates for major changes.
- All changes are versioned and fully reversible.
- Early data may have high uncertainty; the system uses conservative defaults during the initial seed period.

## Why the Meta-RL Loop Matters
The Meta-RL Improvement Loop is what makes the Intelligence Subsystem truly intelligent. It turns raw solving data into a self-improving system that gets measurably better over time. This is the engine behind the compounding flywheels and the path to distilled local Enigma models that democratize solving intelligence.

This loop, combined with the Neural-Net Scoring Head and Training/Distillation Pipeline, is what sets SAGE apart from static agent frameworks. It is the mechanism that turns every run into permanent, compounding collective capability.

# 2. Neural-Net Scoring Head — Deep Technical Dive

## Role and Purpose
The Neural-Net Scoring Head is the learnable “brain” inside the Intelligence Subsystem. It is the central evaluation component that powers the Meta-RL Improvement Loop and provides intelligence to Synapse (the Meta-Agent).

Its job is to take rich fragment features and output calibrated predictions across the four optimization objectives, plus uncertainty estimates. These predictions are the primary signals used by the Meta-RL Loop to compute calibration error and drive self-improvement.

By continuously learning from real downstream outcomes, the Neural-Net Scoring Head makes the entire SAGE system progressively better at recognizing value, predicting impact, implementing strategies, and selecting training-useful fragments.

## Input Feature Vector
The NN takes a ~128-dimensional feature vector constructed from the following categories (all normalized to [0,1] where appropriate):

- **60/40 EFS Components** (core scoring signals)
  - Base EFS terms (validation_score, verifier_7D_average, composability_score, θ_dynamic)
  - Refined Value-Added terms (historical_EFS_lift, calibration_accuracy, reuse_multiplier)

- **Graph & Structural Signals**
  - Graph centrality (PageRank, eigenvector centrality)
  - Community membership strength (from Leiden detection)
  - Motif participation count

- **Utilization & Temporal Signals**
  - Utilization EMA (λ = 0.85 decay)
  - Replay rate
  - Freshness decay (e^(-age/30))
  - Timestamp-derived age

- **Provenance & Metadata Flags**
  - Miner contribution history
  - Challenge/domain embedding (one-hot or learned)
  - Provenance hash validity flag
  - Heterogeneity score (used only for planning, not final EFS)

- **Operations Telemetry**
  - Swarm size at generation time
  - Resource pressure (CPU/GPU/memory)
  - LLM model used

This rich vector gives the NN a comprehensive view of each fragment’s quality, context, and potential impact.

## Architecture
- **Model Type**: Lightweight feed-forward network with residual connections (or optional lightweight graph attention layer for graph-heavy features).
- **Parameter Count**: <80,000 total parameters (designed for fast inference and occasional on-device fine-tuning).
- **Hidden Layers**: 2–3 layers (typically 256 → 128 → 64 units) with ReLU or GELU activations and layer normalization.
- **Output Head**: 8 values — 4 objective predictions + 4 uncertainty estimates (e.g., predicted variance or confidence intervals).
- **Training Regime**: Online updates from real downstream outcomes. The loop computes calibration error and back-propagates through the NN.

The small size keeps inference fast for real-time Synapse co-pilot use and allows eventual distillation into local Enigma models.

## Loss Function and Calibration
The primary training signal is **multi-objective calibration loss**:

$$
L = w_1 \cdot \text{MSE}_\text{value} + w_2 \cdot \text{MSE}_\text{strategy} + w_3 \cdot \text{MSE}_\text{impact} + w_4 \cdot \text{MSE}_\text{utility} + \lambda \cdot \text{calibration\_penalty}
$$

- MSE terms measure prediction accuracy for each objective.
- **Calibration penalty** penalizes mismatch between predicted uncertainty and actual observed error (encourages honest confidence estimates).
- Weights (w₁–w₄ and λ) are themselves tunable by the Meta-RL Loop.

This loss ensures the NN learns not only to predict well, but to know when it is uncertain — critical for safe application of its outputs in gating, ranking, and self-tweaks.

## How Outputs Are Used
The NN produces predictions that flow upward to the Meta-RL Loop and downward to improve other subsystems:

**Upward to Meta-RL Loop**:
- Predictions + real outcomes → calibration error → self-critique → proposed tweaks.

**Downward to EM Level**:
- Updated global approximations (weights, thresholds, strategy templates) are pushed via Synapse.
- During a run, Synapse can query the NN in real time for:
  - Ranked Strategy fragments for the current subtask.
  - Refined_value_added estimates to improve local 60/40 EFS.
  - Prediction of Impact scores to guide planning and orchestration.
  - Training Utility scores to prioritize fragments for future distillation.
- Operations uses NN-informed signals for swarm sizing and LLM routing recommendations.

**To Other Subsystems**:
- Solve: Improves refined_value_added prediction and global re-scoring tolerance.
- Strategy: Improves RankScore and utilization/impact estimation.
- Economic: Improves contribution scoring and artifact_upgrade_value measurement.
- Defense: Improves attack detection and calibration of adversarial examples.
- Training/Distillation: Guides dataset curation and loss weighting.

## Example in Practice
A fragment from a stabilizer code subtask is evaluated by the NN. The NN predicts:
- High Recognition of Value (0.91) but medium uncertainty.
- Strong Implementation of Strategy (expected +0.14 EFS lift).
- Moderate Prediction of Impact (forecasted calibration error 0.07).

The Meta-RL Loop detects a small mismatch in Prediction of Impact, proposes a minor adjustment to the graph_centrality weight, applies it safely (within 0.08 tolerance), and logs the change. Future EM runs now receive slightly better-ranked fragments for similar subtasks, raising average EFS by ~3–5% in the next cycle.

## Safety and Limitations
- All NN outputs used in critical paths (gating, ranking, self-tweaks) are subject to global re-scoring tolerance (0.08).
- Higher-risk changes require human/governance review and versioning.
- Early training data may have high uncertainty; the system starts with conservative defaults and widens tolerance during the seed period.

## Why the Neural-Net Scoring Head Matters
The Neural-Net Scoring Head is what makes the Intelligence Subsystem truly adaptive. By learning calibrated predictions across four objectives and feeding calibration error back into the Meta-RL Loop, it turns raw solving data into a self-improving evaluation brain.

This is the mechanism that allows SAGE to move beyond static prompts or simple reflection into genuine hierarchical learning. The NN’s outputs directly improve every local Enigma Machine run while continuously raising the quality of the entire shared intelligence layer.

Combined with the Meta-RL Improvement Loop and Training/Distillation Pipeline, the Neural-Net Scoring Head is the engine that compounds collective capability and drives the path to democratized local Enigma models.
# Model Distillation Pipeline — Deep Technical Dive

## Role and Purpose (The Capstone)
The Model Distillation Pipeline is the capstone of the Intelligence Subsystem and the ultimate output of the entire SAGE flywheel.

While the Meta-RL Loop and Neural-Net Scoring Head continuously improve evaluation and strategy, the Distillation Pipeline turns that learned intelligence into smaller, specialized Enigma models that can run locally on modest hardware. This is the mechanism that democratizes solving intelligence — moving it from a centralized, compute-heavy process to something anyone can run on a consumer GPU or even CPU.

It is the point where the Intelligence Flywheel, Economic Flywheel, and Democratization Flywheel converge and accelerate each other at massive scale.

## Step-by-Step Pipeline (Rebuildable)

The pipeline follows a repeatable, versioned process:

1. **Curated Dataset Assembly**  
   - Pulls high-Training-Utility fragments flagged by the Neural-Net Scoring Head.
   - Applies strict filtering, balancing, and augmentation to avoid distribution shift and noise.
   - Incorporates adversarial examples from the Defense Subsystem and operations telemetry from the Operations layer.

2. **Knowledge Distillation**  
   - Uses a teacher (larger model or Synapse’s aggregated intelligence) to train smaller student models.
   - Primary loss: KL divergence on teacher outputs.
   - Auxiliary loss: 0.3 × weighted 7D verifier self-check (ensures verifiable correctness is preserved).
   - Meta-RL alignment signals are added as reinforcement terms.

3. **Supervised Fine-Tuning**  
   - Fine-tunes on the curated high-utility dataset with strong emphasis on 7D verifier self-check as an auxiliary objective.

4. **Verification Hardening**  
   - Uses AHE-generated adversarial examples as hard negatives during training to maintain robustness against edge cases.

5. **Model Packaging & Versioning**  
   - Produces a versioned, quantized Enigma model ready for local deployment.
   - Includes embedded global approximations (scoring weights, strategy templates) from the latest Meta-RL Loop.

## Key Loss Functions and Algorithms
**Core Distillation Loss**:
$$
L = \text{KL}(\text{teacher} || \text{student}) + 0.3 \times \text{verifier\self\check\loss} + \lambda \times \text{meta\rl\alignment}$$

**Training Utility Objective** (from NN Scoring Head) guides dataset selection and weighting.

**Quantization & Efficiency**:
Models are progressively quantized and pruned to target modest hardware while preserving 7D verifier integrity.

## Integration with Other Subsystems and Synapse
- **Intelligence Subsystem**: The NN Scoring Head’s Training Utility predictions directly guide dataset curation.
- **Meta-RL Loop**: Calibration error and objective improvements from distilled models feed back into the loop.
- **Solve / Strategy**: Distilled models are pushed as global approximations that improve local EM performance.
- **Economic Subsystem**: Distilled models enable higher-quality artifact upgrades and marketplace products.
- **Defense Subsystem**: Adversarial examples from red-teaming are used as hard negatives.
- **Operations Layer**: Provides telemetry that informs optimal model size and deployment targets.
- **Synapse (Meta-Agent)**: Distributes distilled models to users and uses them to provide faster, cheaper co-pilot assistance.

## How Outputs Propagate Back to the EM Level
1. Synapse loads the latest distilled model and global approximations.
2. When a miner starts a new EM run (or restarts the wizard), Operations loads the distilled model and approximations.
3. The local EM now runs with a stronger, smaller model that embeds learned scoring, strategy preferences, and verifier robustness.
4. During the run, Synapse can still provide real-time co-pilot assistance, but the baseline performance is already significantly higher.
5. New fragments from these improved runs feed back into the Intelligence Subsystem, creating the next generation of even better distilled models.

This creates exponential compounding: better models → more participation → richer data → better models.

## Concrete Example in Practice
After 500 high-utility fragments, the pipeline distills a 1.2B-parameter Enigma model that runs on a single consumer GPU. It outperforms the baseline by 18% on verifiable tasks while preserving 7D verifier integrity. New miners adopt it easily, increasing daily run volume by 40%. The extra data improves the NN’s Training Utility scoring and calibration, leading to an even stronger next-generation model within weeks. Each new model accelerates all three flywheels simultaneously.

## Safety, Governance, and Limitations
- All distilled models are versioned and fully reversible.
- Verifier self-check is enforced as a hard auxiliary objective — models that fail 7D checks are rejected.
- Early models may have higher uncertainty; the system starts with conservative defaults.
- Human/governance review is required before major model releases.

## Eventual acceleration of the Flywheels (The Capstone Effect)
Model distillation is the ultimate accelerator of the entire SAGE system.

- **Intelligence Flywheel**: Distilled models produce higher-quality fragments at scale, feeding better data back into the NN and Meta-RL Loop. The flywheel spins faster and with higher fidelity.
- **Economic Flywheel**: Stronger local models enable more successful runs, higher-quality artifacts, and better marketplace products. Revenue and sponsor participation grow exponentially as solving capability becomes cheaper and more accessible.
- **Democratization Flywheel**: This is where the humongous impact is most visible. As models become smaller and more powerful, participation explodes. Anyone with modest hardware can run high-performing EM instances. More participants mean vastly more data, faster learning, and compounding intelligence that benefits the entire community.

In the long term, distillation turns SAGE from a powerful but centralized system into a truly decentralized, locally-runnable intelligence layer that anyone can contribute to and benefit from. It is the mechanism that makes the People’s Intelligence Layer real at global scale.

This capstone completes the Intelligence Subsystem. Together with the Meta-RL Loop and Neural-Net Scoring Head, it creates a self-improving engine that compounds collective capability and democratizes solving intelligence — the ultimate flywheel multiplier for SAGE.

# Why It Matters
The Intelligence Subsystem is the engine that makes Synapse continuously smarter and ultimately democratizes solving intelligence through accessible local Enigma models. This is what turns raw solving data into compounding collective capability that benefits the entire community.

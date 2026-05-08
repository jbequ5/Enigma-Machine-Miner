# 0.9.15 – Dynamic Meta-Level Self-Assessment (Synapse)

**Version:** 1.0 (10/10 hardened by CC)  
**Date:** 2026-05-07  
**Status:** Executable spec – ready for implementation  
**Purpose:** Turn Synapse into a true self-improving meta-agent that autonomously evolves its own architecture.

## 1. Purpose
The meta-level (Synapse / Intelligence Subsystem) must continuously evaluate its own effectiveness in real time and autonomously decide when to evolve its architecture:
- Create new specialist Process Expert models (MOPE)
- Add, remove, or modify NN objectives
- Re-weight existing objectives
- Adjust data curation or training pipelines

This creates a true self-improving intelligence flywheel that prevents stagnation.

## 2. Trigger Conditions
The self-assessment pass runs:
- Every 24 hours at 02:00 UTC (immediately after the nightly polishing loop)
- Or immediately after any run where `loop_count % 50 == 0`
- Or on-demand via `synapse.trigger_self_assessment()`

## 3. Input Data Sources (All Subsystems)

| Subsystem       | Key Metrics Collected                                      | Purpose |
|-----------------|------------------------------------------------------------|---------|
| IOS             | profile_efs_lift, swarm_size_vs_score, intervention_success_rate, compute_utilization | Detect process steps with poor performance or high resource waste |
| KAS             | hunt_success_rate, novelty_score, gap_relevance_score     | Identify missing knowledge and emerging domains |
| Solve/Strategy  | fragment_efs, refined_value_added, gap_frequency, heterogeneity_index | Detect quality trends and process gaps |
| Defense (RedTeam) | attack_success_rate_per_step, new_vulnerability_score     | Identify hardening needs |
| Economic        | proposal_conversion_rate, gap_to_product_success_rate     | Detect high-value creation opportunities |
| Meta-RL/NN      | calibration_error_history, objective_weight_drift         | Measure how well the current model is learning |

All data is pulled from the Fragment Tracker, Memory Layers, and audit logs.

## 4. Exact Calculations & Formulas

### 4.1 Calibration Error (primary signal)
$$
\text{CalibrationError}_t = \frac{1}{N} \sum_{i=1}^{N} \left| \text{PredictedImpact}_i - \text{ActualEFSLift}_i \right|
$$
- Rolling 7-day average per objective and per process step.
- Threshold: `ERROR_THRESHOLD = 0.18`

### 4.2 Projected EFS Lift (for new expert proposals)
$$
\text{ProjectedEFSLift} = \beta_0 + \beta_1 \cdot \text{ErrorClusterSize} + \beta_2 \cdot \text{NoveltyScore} + \beta_3 \cdot \text{HeterogeneityGain}
$$
- Coefficients learned via simple linear regression on historical data.
- Minimum acceptable lift: `LIFT_THRESHOLD = 0.12`

### 4.3 Heterogeneity Decay
$$
\text{HeterogeneityIndex} = 1 - \frac{\text{SimpsonDominance}}{\text{MaxPossibleDominance}}
$$
- SimpsonDominance = sum of squared fragment-type proportions.
- Decay alert if `HeterogeneityIndex < 0.65` for 3 consecutive days.

### 4.4 Objective Drift
$$
\text{Drift}_j = \left| w_{j,t} - w_{j,t-7} \right| + \left| \text{CalibrationError}_{j,t} - \text{CalibrationError}_{j,t-7} \right|
$$
- Alert if `DRIFT_THRESHOLD = 0.12`

### 4.5 Process-Step Gap Score
$$
\text{GapScore}_{\text{step}} = \frac{\text{CalibrationError}_{\text{step}} \times (1 - \text{ExpertUtilization}_{\text{step}})}{\text{FragmentVolume}_{\text{step}}}
$$

## 5. Decision Logic (Pseudocode – directly implementable)


 # Decision 1: New Process Expert
  for step in PROCESS_STEPS:
        error = metrics[step]["calibration_error_7d"]
        util = metrics[step]["expert_utilization"]
        gap_score = (error * (1 - util)) / max(metrics[step]["fragment_volume"], 1)

    
     if gap_score > 0.25:  # configurable
            projected_lift = predict_efs_lift(step, metrics)
            if projected_lift > LIFT_THRESHOLD:
                decisions.append({
                    "type": "new_expert",
                    "step": step,
                    "projected_lift": projected_lift,
                    "confidence": 1 - error
                })

    # Decision 2: NN Objective Change
    for obj in CURRENT_OBJECTIVES:
        drift = calculate_drift(obj, metrics)
        if drift > DRIFT_THRESHOLD:
            decisions.append({
                "type": "reweight_objective",
                "objective": obj,
                "new_weight": propose_new_weight(obj, metrics)
            })

    # Decision 3: New Objective from Idea Bank
    candidates = score_idea_bank(metrics)  # returns list sorted by projected_lift
    if candidates and candidates[0]["projected_lift"] > CANDIDATE_THRESHOLD:
        decisions.append({
            "type": "add_new_objective",
            "objective": candidates[0]["name"],
            "projected_lift": candidates[0]["projected_lift"]
        })

    # Decision 4: Pipeline Adjustment
    if metrics["heterogeneity_index"] < 0.65:
        decisions.append({"type": "increase_kas_depth", "reason": "heterogeneity_decay"})

    # Execute decisions with safety gates
    for decision in decisions:
        if passes_safety_gate(decision, metrics):
            execute_decision(decision)
        else:
            log_rejected_decision(decision)

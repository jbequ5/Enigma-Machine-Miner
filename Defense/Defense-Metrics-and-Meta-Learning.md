# Defense Metrics & Meta-Learning
**SAGE Defense Subsystem — Deep Technical Specification**  
**v0.9.13+**

### Investor Summary — Why This Matters
Defense Metrics & Meta-Learning is the self-improvement brain of the Defense Subsystem. It defines how the system measures its own effectiveness, tracks hardening progress, and uses Meta-RL to continuously get better at protecting SAGE. In simulations, strong meta-learning in Defense leads to compounding reductions in gaming success (70–85% over time) and measurable improvements in Economic Subsystem integrity and sponsor confidence. For investors, this is what makes Defense not just a static security layer, but a living, evolving guardian that increases platform trustworthiness and long-term value as SAGE scales.

### Core Purpose
This layer defines the metrics, scoring, and Meta-RL feedback loops that allow Defense to evaluate its performance, prioritize improvements, and evolve its strategies over time.

### Key Defense Metrics

**1. Attack Success Rate (ASR)**  
Percentage of generated attacks that successfully bypass current defenses.  
**Target**: ≤ 0.15 on hardened components.

**2. Hardening Effectiveness Score**  
Measures how well fixes resist future attacks while maintaining performance (detailed in reference section).

**3. System-Wide Vulnerability Exposure**  
Aggregated risk score across all major subsystems.

**4. Telemetry Coverage & Quality**  
How complete and actionable the incoming Defense telemetry is.

**5. Flywheel Velocity**  
Rate at which new discoveries lead to cross-subsystem improvements.

### Meta-Learning Loop

**Daily / Cycle Process**:
1. Aggregate metrics from AHE runs, RedTeamVault activity, and local discoveries.
2. Value Prediction NN evaluates which Defense tactics produced the best real-world protection.
3. Main Meta-RL Loop proposes weight and strategy updates (target selection, attack generation, fix validation, etc.).
4. Conservative updates are applied with A/B testing on a subset of targets.
5. Updated policies flow back to AHE, RedTeamVault, and local Defense.

This creates continuous improvement: better metrics → smarter target selection → stronger fixes → better metrics.

### Concrete Example
Meta-RL notices that attacks targeting Economic Impact Score weighting consistently produce high downstream damage.  
It increases prioritization weight for Economic components.  
AHE focuses more resources there, discovers new subtle gaming vectors, and validates stronger fixes.  
Result: Contributor reward integrity improves noticeably, increasing miner trust and participation in the Economic Subsystem.

### Why This Layer Is Critical
- Turns Defense from a static shield into a self-improving system that gets harder to game over time.  
- Ensures resources focus on the highest-leverage vulnerabilities rather than noise.  
- Directly supports Economic fairness, contributor trust, and sponsor confidence.  
- Creates compounding defensibility — the longer SAGE runs, the stronger and more trustworthy it becomes.

**All supporting architecture is covered in [Main Defense Subsystem Overview](../defense/Main-Defense-Overview.md).**

**Economic Impact at a Glance**  
- Target: Continuous reduction in gaming success rate and compounding platform robustness  
- Success Milestone (60 days): Meta-RL-driven improvements visible in ≥ 3 subsystems with measurable Economic integrity gains

---

### Reference: Key Decision Formulas

**1. Hardening Effectiveness Score**  
`Hardening Effectiveness = 0.35 × Post-Fix Attack Resistance + 0.30 × EFS Stability + 0.20 × Performance Overhead + 0.15 × Generalization`  
**Optimizes**: Validates that fixes are robust, low-overhead, and broadly applicable.  
**Meta-RL Tuning**: Refined using long-term stability and Economic performance data.

**2. Overall Defense Health Score**  
`Defense Health Score = 0.40 × (1 - Attack Success Rate) + 0.25 × Hardening Effectiveness + 0.20 × Telemetry Quality + 0.15 × Flywheel Velocity`  
**Optimizes**: Provides a single, holistic view of Defense performance.  
**Meta-RL Tuning**: Primary reward signal for the entire Defense Subsystem.

---


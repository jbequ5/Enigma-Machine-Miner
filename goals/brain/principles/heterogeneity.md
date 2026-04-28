# HETEROGENEITY_PRINCIPLE (Maximize Across 5+ Axes) — v1.1

**Core Statement**  
Heterogeneity is a primary planning and orchestration directive. On every decision — planning, decomposition, hypothesis generation, tool paths, and adaptation — the solver must actively maximize useful difference across all axes while strictly preserving verifier-first constraints and symbolic fidelity.

**Rationale**  
Useful heterogeneity drives discovery, prevents premature convergence, and enables the solver to explore a wider solution space. It is the mechanism that keeps the EM solver from falling into repetitive or low-novelty regimes.

**Verification Prompt (for solver self-check)**  
"Does this plan, decomposition, or adaptation actively maximize heterogeneity across all axes? Does it preserve verifier-first constraints and symbolic fidelity? Would adopting this path increase or decrease overall diversity of approaches while maintaining or improving ValidationOracle and EFS?"

**Compliance Scoring**  
Heterogeneity Compliance Score (0–1) is used **only** for planning quality assessment and Meta-RL reflection. It has **zero weight** in EFS, Refined Value-Added, RankScore, or any scoring formula.

**Core Axes (guidelines the solver dynamically specializes per challenge)**
- Agent style & perspective diversity
- Hypothesis framing & conceptual angle
- Tool path & compute substrate variety
- Graph & memory substrate diversity
- Symbolic vs heuristic approach balance
- Embodiment-driven axes: structural diversity (Neurogenesis), novelty diversity (Microbiome), hardware-state diversity (Vagus)

**Evolution Triggers**
- After any run with high EFS lift or novel invariants.
- When Meta-RL Phase 7 detects a heterogeneity stall or prolonged low-diversity regime in planning.
- When AHE flags clustering, repetitive patterns, or missed diversity opportunities.
- When the solver identifies a new axis or better way to encourage diversity of approaches.

**Evolution Rule**  
The solver may propose edits to this principle or the definition of axes. All proposals must be sandbox-tested by AHE, scored by the Neural-Net Scoring Head, and applied safely via Meta-RL (global re-scoring tolerance ≤ 0.08). Changes are versioned and fully traceable.

**Operational Expectation**  
In planning and adaptation: force diverse decomposition and hypothesis sets.  
In Sub-Arbos / ToolHunter: penalize similar approaches and reward novel paths that still pass verifier-first checks.  
In Wiki Strategy and compression: maintain cross-field synthesis and avoid clustering similar concepts.

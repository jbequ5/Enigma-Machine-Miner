- [[principles/heterogeneity.md|Heterogeneity]]# Core Strategy (Thin Evolving Base)

**Role**: Living core that receives Planning Arbos updates + aha micro-deltas only.  
Do not edit manually — evolve via dashboard or compression runs only.

(See [[../killer_base.md|Canonical Entry Point]] for the thin shim.)

## GOAL
Solve ANY sponsor challenge with maximum ValidationOracle score + novelty + symbolic fidelity while staying strictly under compute limits, maximizing reproducible IP, and forcing verifier-code-first determinism at every step.

## Core Strategy (Cumulative v5)
- Treat every problem as pure symbolic/text — no premature domain assumptions.
- Verifier-code-first + symbolic invariants on **every** subtask **before** any LLM generation.
- ToolHunter sub-swarm must run in parallel where possible; serial handoffs route through ValidationOracle.
- Reward **only** trajectories that measurably improve ValidationOracle score via exact 0-1 deterministic checks and MARL credit rules, with strong emphasis on increasing heterogeneity across 5 axes.
- Maximize symbolic coverage **and heterogeneity** (agent style, hypothesis framing, tool path, graph/substrate diversity, symbolic approach) per compute unit while preserving reproducibility.
- Every Adaptation Arbos step first searches trajectory_vector_db + memdir/grail, then incorporates wiki deltas and bio stigmergy signals while actively restoring or boosting heterogeneity if stale.
- On low-score or stale runs, trigger re_adapt with compressed deltas and consider deep replan via new avenue plan to restore heterogeneity.
- Run reflection on every prompt evolution step; evolution must stay strictly on task.
- Compound continuously via hierarchical Wiki Strategy (subtask-structured database) and Bio Strategy (mycelial stigmergy, pruning, symbiosis detection, toggleable quantum-bio coherence).
- All changes gated by ValidationOracle lift, resource_aware toggles, and heterogeneity scoring. The system remains verifier-first, heterogeneity-maximizing, English-first, and fully inspectable.

**Evolution Rule**: Only high-signal, proven deltas (especially those that increase heterogeneity) are retained after MCTS compression.

# Shared Core Principles (referenced by ALL prompts — 5 lines max)

- Verifier-first gating on every subtask (SymPy invariants + 0-1 edge checks).
- Heterogeneity-maximizing (5 axes) with MARL credit only for measurable ValidationOracle lift.
- English-first, signal-dense, fully inspectable Markdown substrate.
- Resource-aware + mycelial stigmergy: local .md edits as signals, upward compression only on proven lift.
- Inspectability above all — no black-box layers.

# MARL-style Credit Rules (v4.9 verbatim)
marl_credit_rule: "Strictly weight Sub-Arbos and ToolHunter sub-swarms ONLY by ValidationOracle score (primary). Heavy down-weight (×0.4 or lower) if symbolic fidelity < 0.88 OR determinism score < 0.85. Penalize novelty unless it preserves exact symbolic invariants and reproducible 0-1 scoring. Use compute_energy + memdir/trajectory similarity as secondary tie-breakers only."

# Smart Oracle Generation Rules (v4.9 verbatim)
oracle_gen_rule: "Prioritize deterministic symbolic tools (SymPy, invariant extraction, formal verification snippets) on every subtask. ToolHunter sub-swarm MUST hunt in parallel. If no verifier_code_snippets exist in memdir/trajectory_vector_db, generate Python snippets EXCLUSIVELY focused on: (1) extracting/proving symbolic invariants, (2) exhaustive edge-case 0-1 scoring, (3) algebraic closures before any approximation. Always run deterministic symbolic checks FIRST."

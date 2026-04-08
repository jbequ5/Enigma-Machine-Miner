# Tool Recommendation Log – Living Brain Asset (v0.8)

| Tool              | Category                          | Keywords                              | Success Metrics (EFS / Replay Pass) | Compute Cost | Last Used | Notes / Integration Point                  |
|-------------------|-----------------------------------|---------------------------------------|-------------------------------------|--------------|-----------|--------------------------------------------|
| Hypothesis        | Property-Based Testing (PBT)      | probabilistic, invariants, fuzzing    | - / -                               | Low          | -         | Verifier snippets, dry-run gate            |
| RestrictedPython  | Sandboxing / Safe Execution       | verifier snippets, security           | - / -                               | Low          | -         | All exec() calls, sub-arbos validation     |
| gVisor            | Container Sandboxing              | isolation, security                   | - / -                               | Medium       | -         | Advanced RestrictedPython wrapper          |
| Langfuse          | Observability / Tracing           | tracing, metrics, debugging           | - / -                               | Low          | -         | Full swarm + Scientist Mode runs           |
| Spin / Promela    | Model Checking (LTL)              | temporal logic, concurrency           | - / -                               | Medium       | -         | Orchestrator debate, composability         |
| TLA+ / TLC        | Model Checking (Safety/Liveness)  | formal verification, specs            | - / -                               | Medium       | -         | Contract rules, synthesis                  |
| Alloy             | Relational Model Checking         | invariants, relational logic          | - / -                               | Medium       | -         | Composability rules, reassembly plan       |
| AutoQ             | Quantum Model Checking            | quantum circuits, superposition       | - / -                               | High         | -         | Quantum-domain contracts                   |
| Storm / PRISM     | Statistical / Probabilistic Model Checking | probabilistic verification, stochastic | - / -                          | High         | -         | Stochastic protocols, side-channel         |
| SymPy             | Symbolic Execution / Math         | symbolic math, algebra                | - / -                               | Low          | -         | Symbolic verification, invariants          |
| Z3                | SMT Solver / Symbolic Execution   | constraints, satisfiability           | - / -                               | Medium       | -         | Verifier snippets, constraint solving      |
| DoWhy             | Causal Discovery / Inference      | causality, interventions              | - / -                               | Medium       | -         | Causal composability rules                 |
| Cirq              | Quantum Circuit Simulator         | quantum circuits, simulation          | - / -                               | High         | -         | Quantum-domain experiments                 |
| NetworkX          | Graph / Dependency Analysis       | dependency graph, orchestration       | - / -                               | Low          | -         | Orchestrator phase 2, ToolHunter           |

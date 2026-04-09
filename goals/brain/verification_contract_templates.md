# Verifiability Contract Templates – Living Foundation (v0.8)

## Default Standard Template
{
  "artifacts_required": ["final_solution", "verification_proof", "composability_evidence"],
  "composability_rules": ["All subtask outputs must satisfy causal links and contain no contradictions", "Reassembly must preserve all invariants listed in the high-level contract"],
  "dry_run_success_criteria": ["All per-subtask verifier snippets pass on intelligent mock data", "Full composability check passes"],
  "synthesis_guidance": "Critique-first reassembly that explicitly enforces the full contract and reassembly plan"
}

### Novelty & Approximation Handling (New in v0.8+)
- approximation_mode: "enabled" | "disabled" | "auto"          # default: "auto"
- approximation_method_preference: ["sympy", "storm", "monte_carlo", "general_reasoning"]   # ordered list

### Notes
When no real backend/tool exists for a required artifact or verifier, the system will:
- Use the highest-preference available approximation method
- Log the approximation clearly in decision journal and dry-run result
- Still aim for maximum verifier quality under approximation constraints
  
## Evolution Rules (Enforced by Scientist Mode + Pruning Advisor)
- Promotion: Replay pass rate ≥ 0.90 AND EFS contribution ≥ +1.5% AND miner approval
- Every evolved delta must include provenance (e.g., "EVOLVED FROM SCIENTIST MODE – quantum domain – Loop 47" or "DOUBLE_CLICK gap on entropy invariants")
- Pruning: Low-health templates (low EFS or high escalation) are down-weighted by Pruning Advisor

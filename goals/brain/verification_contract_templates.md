# Verifiability Contract Templates – Living Foundation (v0.8)

## Default Standard Template
{
  "artifacts_required": ["final_solution", "verification_proof", "composability_evidence"],
  "composability_rules": ["All subtask outputs must satisfy causal links and contain no contradictions", "Reassembly must preserve all invariants listed in the high-level contract"],
  "dry_run_success_criteria": ["All per-subtask verifier snippets pass on intelligent mock data", "Full composability check passes"],
  "synthesis_guidance": "Critique-first reassembly that explicitly enforces the full contract and reassembly plan"
}

## Evolution Rules (Enforced by Scientist Mode + Pruning Advisor)
- Promotion: Replay pass rate ≥ 0.90 AND EFS contribution ≥ +1.5% AND miner approval
- Every evolved delta must include provenance (e.g., "EVOLVED FROM SCIENTIST MODE – quantum domain – Loop 47" or "DOUBLE_CLICK gap on entropy invariants")
- Pruning: Low-health templates (low EFS or high escalation) are down-weighted by Pruning Advisor

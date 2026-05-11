kas_response = recursive_kas.query_for_process_step(
    process_step="stall_recovery", 
    current_context={
        "content_preview": "Current solver state description...",
        "objective_vector": current_objective_vector,
        "weakest_objective": weakest,
        "stall_reason": "tool_use_loop_failure",
        "stability_score": current_stability_score,
        "domain_tag": current_domain
    }
)

# Use immediately
knowledge = kas_response["knowledge"]
suggested_action = kas_response["suggested_action"]

# After using it, report outcome back (for observability)
recursive_kas.record_outcome_lift(
    process_step="stall_recovery",
    outcome_lift=0.18,  # e.g. combined_score delta
    suggested_action_used=True,
    tool_usage=True
)

# streamlit_app.py
import streamlit as st
from agents.arbos_manager import ArbosManager

st.set_page_config(page_title="Enigma Machine Miner - SN63", layout="wide")
st.title("🧠 Enigma Machine Miner (Bittensor SN63)")
st.markdown("**Arbos-centric solver with Meta Planning + Refinement + Swarm ready**")

# Initialize manager
if "arbos_manager" not in st.session_state:
    st.session_state.arbos_manager = ArbosManager()
manager = st.session_state.arbos_manager

# Input challenge
challenge = st.text_area(
    "Enter SN63 Challenge Description",
    height=150,
    placeholder="e.g., Optimize a peaked circuit for 37+ qubits on Quantum Rings simulator with novel preprocessing for hidden stabilizers..."
)

if st.button("🚀 Generate High-Level Plan", type="primary"):
    if not challenge.strip():
        st.error("Please enter a challenge description.")
    else:
        with st.spinner("Meta Planning Arbos is thinking..."):
            high_level_plan = manager.plan_challenge(challenge)
            st.session_state.high_level_plan = high_level_plan
            st.session_state.challenge = challenge
            st.session_state.stage = "planning_approval"
            st.success("High-level plan generated!")

# ====================== PLAN APPROVAL SCREEN ======================
if st.session_state.get("stage") == "planning_approval":
    plan = st.session_state.high_level_plan
    challenge = st.session_state.challenge

    st.subheader("📋 High-Level Plan from Planning Arbos")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**Goals:** {plan.get('high_level_goals', 'N/A')}")
        
        st.markdown("**Risks & Mitigations**")
        for risk in plan.get("risks_and_mitigations", []):
            st.write(f"- {risk}")

        st.markdown("**Rough Decomposition**")
        for task in plan.get("rough_decomposition", []):
            st.write(f"- {task}")

    with col2:
        st.metric("Suggested Swarm Size", plan.get("suggested_swarm_size", 1))
        st.metric("Compute Ballpark", f"{plan.get('compute_ballpark_minutes', 0)} min")
        st.markdown("**Quality Gate Targets**")
        for k, v in plan.get("quality_gate_targets", {}).items():
            st.write(f"- {k}: {v}/10")

    # Tool hints
    if plan.get("high_level_tool_hints"):
        st.markdown("**High-Level Tool Hints**")
        st.json(plan["high_level_tool_hints"])

    # Miner decision
    st.markdown("---")
    st.subheader("👷 Miner Review & Approval")

    feedback = st.text_area(
        "Feedback / Tweak Request (optional)",
        placeholder="e.g., Emphasize more novelty in quantum preprocessing or reduce swarm size for safety."
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Approve Plan", type="primary"):
            st.session_state.approved_plan = plan
            st.session_state.stage = "refinement"
            st.rerun()

    with col_b:
        if st.button("🔄 Request Tweak"):
            if feedback.strip():
                # Re-run planning with feedback injected (simple way)
                with st.spinner("Re-planning with your feedback..."):
                    tweaked_plan = manager.plan_challenge(
                        f"{challenge}\n\nMINER FEEDBACK: {feedback}"
                    )
                    st.session_state.high_level_plan = tweaked_plan
                    st.rerun()
            else:
                st.warning("Please provide feedback for tweak.")

    with col_c:
        if st.button("❌ Reject & Restart"):
            for key in ["high_level_plan", "stage", "approved_plan"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# ====================== REFINEMENT & EXECUTION ======================
if st.session_state.get("stage") == "refinement":
    approved_plan = st.session_state.approved_plan
    challenge = st.session_state.challenge

    st.subheader("🔧 Refining Plan into Executable Blueprint...")
    with st.spinner("Main Arbos Orchestrator performing refinement..."):
        blueprint = manager._refine_plan(approved_plan, challenge)
        st.session_state.blueprint = blueprint

    st.success("Refinement complete!")
    st.json(blueprint)  # Expandable for debug

    if st.button("▶️ Launch Orchestrator (Swarm Execution)"):
        st.session_state.stage = "execution"
        st.rerun()

# ====================== EXECUTION (Current bridge) ======================
if st.session_state.get("stage") == "execution":
    challenge = st.session_state.challenge
    st.info("Launching full orchestrator (using legacy single-loop bridge for now)...")

    with st.spinner("Running Arbos Primary Solver..."):
        final_solution, tools_used, should_reloop = manager.run(challenge)

    st.subheader("✅ Final Solution")
    st.text_area("Output", final_solution, height=400)

    st.markdown(f"**Tools used:** {tools_used}")
    if should_reloop:
        st.warning("Miner review after loop requested — implement full loop review here if needed.")

    # Final miner review placeholder
    st.markdown("---")
    st.subheader("Final Miner Review")
    final_feedback = st.text_area("Notes before submission (optional)")
    if st.button("📤 Submit to SN63"):
        st.success("Solution packaged and ready for submission! (Implement packaging logic here)")
        # TODO: save final_solution + blueprint + trace to file for submission

# Debug trace (always visible)
if st.session_state.get("trace_log"):
    with st.expander("Debug Trace Log"):
        for entry in st.session_state.trace_log:
            st.write(entry)

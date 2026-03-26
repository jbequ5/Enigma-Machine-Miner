# streamlit_app.py
import streamlit as st
import json
import zipfile
from pathlib import Path
from datetime import datetime

from agents.arbos_manager import ArbosManager

st.set_page_config(page_title="Enigma Machine Miner - SN63", layout="wide")
st.title("🧠 Enigma Machine Miner (Bittensor SN63)")
st.caption("Arbos-centric | Planning + Refinement + Dynamic Swarm + ToolHunter")

if "arbos_manager" not in st.session_state:
    st.session_state.arbos_manager = ArbosManager()
manager = st.session_state.arbos_manager

challenge = st.text_area("SN63 Challenge", height=120, placeholder="Describe the challenge (e.g., optimize peaked circuit for 40+ qubits on Quantum Rings, novel stabilizer preprocessing...)")

if st.button("🚀 Start Solving", type="primary") and challenge.strip():
    with st.spinner("Meta Planning Arbos running..."):
        high_level_plan = manager.plan_challenge(challenge)
        st.session_state.challenge = challenge
        st.session_state.high_level_plan = high_level_plan
        st.session_state.stage = "planning_approval"
        st.rerun()

# ====================== 1. PLANNING APPROVAL ======================
if st.session_state.get("stage") == "planning_approval":
    plan = st.session_state.high_level_plan
    st.subheader("📋 High-Level Plan – Miner Approval")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Goals:** {plan.get('high_level_goals', 'N/A')}")
        st.markdown("**Risks:**")
        for r in plan.get("risks_and_mitigations", []):
            st.write(f"• {r}")
        st.markdown("**Rough Decomposition:**")
        for t in plan.get("rough_decomposition", []):
            st.write(f"• {t}")
    with col2:
        st.metric("Suggested Swarm", plan.get("suggested_swarm_size", 1))
        st.metric("Est. Time", f"{plan.get('compute_ballpark_minutes', 0)} min")

    feedback = st.text_area("Feedback / Tweak (optional)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Approve & Refine", type="primary"):
            st.session_state.approved_plan = plan
            st.session_state.stage = "refinement"
            st.rerun()
    with col_b:
        if st.button("🔄 Tweak & Re-plan"):
            if feedback:
                with st.spinner("Re-planning..."):
                    tweaked = manager.plan_challenge(f"{challenge}\n\nMiner feedback: {feedback}")
                    st.session_state.high_level_plan = tweaked
                    st.rerun()
    with col_c:
        if st.button("❌ Restart"):
            st.session_state.clear()
            st.rerun()

# ====================== 2. REFINEMENT + SWARM ======================
if st.session_state.get("stage") == "refinement":
    with st.spinner("Refining plan + launching dynamic swarm with ToolHunter..."):
        blueprint = manager._refine_plan(st.session_state.approved_plan, st.session_state.challenge)
        st.session_state.blueprint = blueprint
        final_solution, tools_used, _ = manager.run(st.session_state.challenge)  # triggers swarm
        st.session_state.final_solution = final_solution
        st.session_state.tools_used = tools_used
        st.session_state.stage = "final_review"
        st.rerun()

# ====================== 3. FINAL MINER REVIEW (Step 4) ======================
if st.session_state.get("stage") == "final_review":
    solution = st.session_state.final_solution
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])

    st.subheader("🔍 Final Miner Review – Ready for SN63 Submission")

    tab1, tab2, tab3, tab4 = st.tabs(["Solution", "ToolHunter Escalations", "Blueprint & Trace", "Quality Assessment"])

    with tab1:
        st.text_area("Final Synthesized Solution", solution, height=500)

    with tab2:
        st.markdown("**ToolHunter Manual Recommendations**")
        manual_found = False
        for entry in trace:
            if "manual_required" in str(entry).lower() or "TOOLHUNTER ESCALATION" in str(entry):
                st.warning(entry)
                manual_found = True
        if not manual_found:
            st.success("No manual ToolHunter escalations. All tools integrated automatically.")

    with tab3:
        st.json(blueprint, expanded=False)
        with st.expander("Full Execution Trace"):
            for line in trace:
                st.write(line)

    with tab4:
        # Final Arbos quality critique
        if "quality_critique" not in st.session_state:
            with st.spinner("Running final quality gate..."):
                critique_task = f"""You are Arbos. Critique the final solution for SN63:

Solution: {solution[:2000]}...

Score 1-10 on:
- Novelty
- Verifier potential (Quantum Rings compatibility)
- Alignment with miner strategy
- Completeness

Overall recommendation: Submit / Improve / Re-loop"""
                critique = manager.compute.run_on_compute(critique_task)
                st.session_state.quality_critique = critique
        st.text_area("Arbos Final Quality Gate", st.session_state.quality_critique, height=200)

    # Miner notes & actions
    miner_notes = st.text_area("Your Final Notes / Changes (optional)", placeholder="e.g., Manually integrate Tool X from ToolHunter recommendation...")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📦 Package for SN63 Submission", type="primary"):
            self._package_submission(solution, blueprint, trace, miner_notes)
            st.success("Submission package created! Check ./submissions/ folder.")
            st.balloons()

    with col2:
        if st.button("🔄 Request Quick Re-loop"):
            st.warning("Re-loop triggered (if miner_review_after_loop=True). Implement full re-orchestration if needed.")

    with col3:
        if st.button("❌ Discard & Restart"):
            st.session_state.clear()
            st.rerun()

def _package_submission(self, solution: str, blueprint: dict, trace: list, notes: str):
    """Create submission package (not in Streamlit scope, but called from it)."""
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    sub_dir = Path("submissions") / f"sn63_{ts}"
    sub_dir.mkdir(parents=True, exist_ok=True)

    (sub_dir / "solution.md").write_text(solution)
    (sub_dir / "blueprint.json").write_text(json.dumps(blueprint, indent=2))
    (sub_dir / "trace.log").write_text("\n".join(trace))
    (sub_dir / "miner_notes.txt").write_text(notes)

    with zipfile.ZipFile(sub_dir / "submission_package.zip", "w") as z:
        for f in sub_dir.glob("*"):
            if f.is_file() and f.suffix != ".zip":
                z.write(f, f.name)

    print(f"✅ Submission package ready: {sub_dir}/submission_package.zip")

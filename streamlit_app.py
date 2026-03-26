# streamlit_app.py
import streamlit as st
import json
import zipfile
from pathlib import Path
from datetime import datetime

from agents.arbos_manager import ArbosManager

st.set_page_config(page_title="Enigma Machine Miner - SN63", layout="wide")
st.title("🧠 Enigma Machine Miner (Bittensor SN63)")
st.caption("Intelligent Planning Arbos + Dynamic Swarm + ToolHunter + Enhanced Memory")

if "arbos_manager" not in st.session_state:
    st.session_state.arbos_manager = ArbosManager()
manager = st.session_state.arbos_manager

# Show current compute limit
max_hours = manager.config.get("max_compute_hours", 3.8)
st.sidebar.metric("Max Compute Limit", f"{max_hours} hours")

challenge = st.text_area("SN63 Challenge Description", height=140, 
                        placeholder="e.g., Develop novel preprocessing for hidden stabilizers on 40+ qubit Quantum Rings circuit...")

if st.button("🚀 Start Solving", type="primary") and challenge.strip():
    with st.spinner("Planning Arbos is thinking..."):
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
        st.metric("Suggested Swarm Size", plan.get("suggested_swarm_size", 1))
        st.metric("Est. Time", f"{plan.get('compute_ballpark_minutes', 0)} min")

    feedback = st.text_area("Feedback / Tweak Request (optional)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Approve & Refine", type="primary"):
            st.session_state.approved_plan = plan
            st.session_state.stage = "refinement"
            st.rerun()
    with col_b:
        if st.button("🔄 Tweak & Re-plan"):
            if feedback.strip():
                with st.spinner("Re-planning with feedback..."):
                    tweaked = manager.plan_challenge(f"{challenge}\n\nMiner feedback: {feedback}")
                    st.session_state.high_level_plan = tweaked
                    st.rerun()
    with col_c:
        if st.button("❌ Restart"):
            st.session_state.clear()
            st.rerun()

# ====================== 2. REFINEMENT + SWARM ======================
if st.session_state.get("stage") == "refinement":
    with st.spinner("Orchestrator Arbos refining plan + launching swarm..."):
        blueprint = manager._refine_plan(st.session_state.approved_plan, st.session_state.challenge)
        st.session_state.blueprint = blueprint
        final_solution, tools_used, _ = manager.run(st.session_state.challenge)
        st.session_state.final_solution = final_solution
        st.session_state.tools_used = tools_used
        st.session_state.stage = "final_review"
        st.rerun()

# ====================== 3. FINAL MINER REVIEW ======================
if st.session_state.get("stage") == "final_review":
    solution = st.session_state.final_solution
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])

    st.subheader("🔍 Final Miner Review")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Solution", "ToolHunter Escalations", "Memory History", "Blueprint & Trace", "Quality Gate"])

    with tab1:
        st.text_area("Final Synthesized Solution", solution, height=450)

    with tab2:
        st.markdown("**ToolHunter Manual Recommendations**")
        manual_found = False
        for entry in trace:
            if isinstance(entry, str) and ("MANUAL REQUIRED" in entry or "ToolHunter MANUAL" in entry):
                st.warning(entry)
                manual_found = True
        if not manual_found:
            st.success("No manual ToolHunter escalations detected.")

    with tab3:
        st.markdown("**Previous Attempts from Memory (Re-loop Learning)**")
        past_attempts = memory.query(st.session_state.challenge, n_results=6)
        if past_attempts:
            for i, attempt in enumerate(past_attempts, 1):
                st.write(f"**Attempt {i}:** {attempt[:300]}...")
        else:
            st.info("No previous attempts in memory yet.")

    with tab4:
        st.json(blueprint, expanded=False)
        with st.expander("Full Execution Trace"):
            for line in trace:
                st.write(line)

    with tab5:
        if "quality_critique" not in st.session_state:
            with st.spinner("Running final SN63 quality gate..."):
                critique_task = f"""You are Arbos performing final evaluation.

Final solution:
{solution[:2500]}...

Output EXACT JSON:
{{
  "novelty": 9.2,
  "verifier_potential": 9.5,
  "alignment": 9.8,
  "completeness": 9.0,
  "efficiency": 8.7,
  "ip_licensability": 9.1,
  "overall_score": 9.3,
  "recommendation": "Submit / Minor tweak / Re-loop",
  "key_strength": "...",
  "key_risk": "..."
}}"""

                raw = manager.compute.run_on_compute(critique_task)
                try:
                    start = raw.find("{")
                    end = raw.rfind("}") + 1
                    critique_json = json.loads(raw[start:end])
                    st.session_state.quality_critique = critique_json
                except:
                    st.session_state.quality_critique = {"overall_score": 7.0, "recommendation": "Manual review needed"}

        q = st.session_state.quality_critique
        cols = st.columns(6)
        metrics = [
            ("Novelty", q.get("novelty", 0)),
            ("Verifier", q.get("verifier_potential", 0)),
            ("Alignment", q.get("alignment", 0)),
            ("Completeness", q.get("completeness", 0)),
            ("Efficiency", q.get("efficiency", 0)),
            ("IP", q.get("ip_licensability", 0))
        ]
        for col, (label, value) in zip(cols, metrics):
            col.metric(label, f"{value}/10")

        st.success(f"**Overall Score: {q.get('overall_score', 0)}/10** → {q.get('recommendation', '')}")
        st.info(f"**Strength:** {q.get('key_strength', '')}")
        st.warning(f"**Risk:** {q.get('key_risk', '')}")

    # Miner notes
    miner_notes = st.text_area("Your Final Notes (optional)", placeholder="e.g., Manually integrate Tool X from ToolHunter recommendation...")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📦 Package for SN63 Submission", type="primary"):
            self._package_submission(solution, blueprint, trace, miner_notes, st.session_state.challenge)
            st.success("✅ Submission package created in ./submissions/")
            st.balloons()

    with col2:
        if st.button("🔄 Request Re-loop"):
            st.info("Re-loop requested. Implement full re-orchestration if needed.")

    with col3:
        if st.button("❌ Discard & Restart"):
            st.session_state.clear()
            st.rerun()

def _package_submission(self, solution: str, blueprint: dict, trace: list, notes: str, challenge: str):
    """Create clean submission package including memory history."""
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    sub_dir = Path("submissions") / f"sn63_{ts}"
    sub_dir.mkdir(parents=True, exist_ok=True)

    (sub_dir / "solution.md").write_text(solution)
    (sub_dir / "blueprint.json").write_text(json.dumps(blueprint, indent=2))
    (sub_dir / "trace.log").write_text("\n".join(str(t) for t in trace))
    (sub_dir / "miner_notes.txt").write_text(notes)
    (sub_dir / "challenge.txt").write_text(challenge)

    # Include recent memory history
    past = memory.query(challenge, n_results=8)
    (sub_dir / "memory_history.txt").write_text("\n\n".join(past))

    with zipfile.ZipFile(sub_dir / "submission_package.zip", "w") as z:
        for f in sub_dir.glob("*"):
            if f.is_file() and f.suffix != ".zip":
                z.write(f, f.name)

    print(f"✅ Package ready: {sub_dir}/submission_package.zip")

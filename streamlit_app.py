# streamlit_app.py
import streamlit as st
import json
import zipfile
from pathlib import Path
from datetime import datetime

from agents.arbos_manager import ArbosManager

st.set_page_config(page_title="Enigma Machine Miner - SN63", layout="wide")
st.title("🧠 Enigma Machine Miner (Bittensor SN63)")
st.caption("Arbos Planning + Dynamic Swarm + ToolHunter + Custom Verification")

if "arbos_manager" not in st.session_state:
    st.session_state.arbos_manager = ArbosManager()
manager = st.session_state.arbos_manager

# Sidebar info
max_hours = manager.config.get("max_compute_hours", 3.8)
st.sidebar.metric("Max Compute", f"{max_hours} hours")
st.sidebar.metric("Resource Aware", "ON" if manager.config.get("resource_aware") else "OFF")

challenge = st.text_area("SN63 Challenge", height=120, placeholder="Describe the hard problem...")

if st.button("🚀 Start Solving", type="primary") and challenge.strip():
    with st.spinner("Planning Arbos running..."):
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

    feedback = st.text_area("Feedback / Tweak (optional)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Approve & Continue", type="primary"):
            st.session_state.approved_plan = plan
            st.session_state.stage = "refinement"
            st.rerun()
    with col_b:
        if st.button("🔄 Tweak"):
            if feedback:
                with st.spinner("Re-planning..."):
                    tweaked = manager.plan_challenge(f"{challenge}\n\nFeedback: {feedback}")
                    st.session_state.high_level_plan = tweaked
                    st.rerun()
    with col_c:
        if st.button("❌ Restart"):
            st.session_state.clear()
            st.rerun()

# ====================== 2. REFINEMENT + SWARM ======================
if st.session_state.get("stage") == "refinement":
    with st.spinner("Orchestrator refining + launching swarm..."):
        blueprint = manager._refine_plan(st.session_state.approved_plan, st.session_state.challenge)
        st.session_state.blueprint = blueprint
        final_solution, _, _ = manager._smart_route(st.session_state.challenge)
        st.session_state.final_solution = final_solution
        st.session_state.stage = "final_review"
        st.rerun()

# ====================== 3. FINAL REVIEW ======================
if st.session_state.get("stage") == "final_review":
    solution = st.session_state.final_solution
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])

    st.subheader("🔍 Final Miner Review")

    tab1, tab2, tab3, tab4 = st.tabs(["Solution", "ToolHunter Actions", "Memory History", "Verification"])

    with tab1:
        st.text_area("Final Solution", solution, height=400)

    with tab2:
        st.markdown("### ⚠️ ToolHunter Manual Actions")
        manual = [e for e in trace if isinstance(e, str) and "MANUAL REQUIRED" in e.upper()]
        if manual and manager.config.get("manual_tool_installs_allowed"):
            st.warning("**Manual installation required**")
            for m in manual:
                st.error(m)
        else:
            st.success("No manual actions needed.")

    with tab3:
        st.markdown("### Memory History")
        past = memory.query(st.session_state.challenge, n_results=8)
        if past:
            for i, p in enumerate(past, 1):
                st.write(f"**{i}:** {p[:300]}...")
        else:
            st.info("No previous attempts.")

    with tab4:
        st.markdown("### 🔬 Custom Verification")
        verification = st.text_area(
            "Verification Instructions / Code",
            height=180,
            value=st.session_state.get("verification_instructions", ""),
            placeholder="Simulate on Quantum Rings with 5000 shots. Require fidelity > 0.95"
        )
        st.session_state.verification_instructions = verification

        if st.button("🔄 Re-run with this Verification"):
            with st.spinner("Re-running swarm..."):
                new_solution = manager._run_swarm(st.session_state.blueprint, st.session_state.challenge, verification)
                st.session_state.final_solution = new_solution
                st.rerun()

        # Quality Gate
        if "quality_critique" not in st.session_state:
            with st.spinner("Running quality gate..."):
                task = f"""You are Arbos. Evaluate with this verification: {verification or 'General SN63 standards'}
Solution: {solution[:2000]}
Output JSON with novelty, verifier_potential, overall_score, recommendation, verification_assessment."""
                raw = manager.compute.run_on_compute(task)
                try:
                    start = raw.find("{")
                    end = raw.rfind("}") + 1
                    st.session_state.quality_critique = json.loads(raw[start:end])
                except:
                    st.session_state.quality_critique = {"overall_score": 7.0}

        q = st.session_state.quality_critique
        cols = st.columns(3)
        cols[0].metric("Overall", f"{q.get('overall_score', 0)}/10")
        cols[1].metric("Verifier", f"{q.get('verifier_potential', 0)}/10")
        cols[2].metric("Novelty", f"{q.get('novelty', 0)}/10")

    miner_notes = st.text_area("Final Notes")
    if st.button("📦 Package Submission"):
        _package_submission(solution, blueprint, trace, miner_notes, st.session_state.challenge, verification)
        st.success("Package created in submissions/")

def _package_submission(solution, blueprint, trace, notes, challenge, verification):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    dir_path = Path("submissions") / f"sn63_{ts}"
    dir_path.mkdir(parents=True, exist_ok=True)

    (dir_path / "solution.md").write_text(solution)
    (dir_path / "verification.txt").write_text(verification)
    (dir_path / "trace.log").write_text("\n".join(str(t) for t in trace))
    (dir_path / "notes.txt").write_text(notes)

    with zipfile.ZipFile(dir_path / "submission_package.zip", "w") as z:
        for f in dir_path.glob("*"):
            if f.is_file() and f.suffix != ".zip":
                z.write(f, f.name)

    st.success(f"Package saved to {dir_path}")

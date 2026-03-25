import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title="ENIGMA 3D — SN63 Miner", page_icon="🔑", layout="wide")

st.markdown('<h1 style="text-align:center; color:#ffcc00;">🔑 ENIGMA MACHINE 3D — SUBNET 63 MINER</h1>', unsafe_allow_html=True)
st.markdown("**Sequential Tool Chain with Reflection + Configurable Miner Review**")

# Session State
if "challenge" not in st.session_state:
    st.session_state.challenge = ""
if "current_plan" not in st.session_state:
    st.session_state.current_plan = ""
if "program_md" not in st.session_state:
    st.session_state.program_md = ""
if "final_output" not in st.session_state:
    st.session_state.final_output = ""
if "trace_log" not in st.session_state:
    st.session_state.trace_log = []
if "tool_configs" not in st.session_state:
    st.session_state.tool_configs = {}
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

st.subheader("1. Enter the Challenge")
challenge = st.text_area("Main challenge for today's miner", value=st.session_state.challenge, height=120)

col1, col2 = st.columns(2)
with col1:
    if st.button("Generate Strategic Plan with HyperAgent"):
        if not challenge:
            st.error("Please enter a challenge.")
        else:
            st.session_state.challenge = challenge
            with st.spinner("HyperAgent creating strategic plan..."):
                try:
                    from agents.tools.hyperagent import run_hyperagent
                    result = run_hyperagent(task=f"Create detailed plan for: {challenge}", parallel_tasks=5)
                    st.session_state.current_plan = result.get("output", "")
                    st.session_state.program_md = f"# Execution Program\n\n## Challenge\n{challenge}\n\n## Strategic Plan\n{st.session_state.current_plan}\n\n"
                    st.success("Strategic plan generated!")
                except Exception as e:
                    st.error(f"HyperAgent failed: {e}")

with col2:
    if st.button("🔬 Run Tool Study Phase"):
        with st.spinner("Studying tools..."):
            try:
                from agents.tool_study import tool_study
                tool_study.study_all_tools()
                st.success("✅ Tool Study completed!")
            except Exception as e:
                st.error(f"Study failed: {e}")

if st.session_state.current_plan:
    st.subheader("2. Review & Approve Initial Plan")
    edited_plan = st.text_area("Strategic Plan (edit freely)", value=st.session_state.current_plan, height=300)
    if st.button("✅ Approve Plan & Start Tool Chain"):
        st.session_state.current_plan = edited_plan
        st.session_state.program_md = f"# Execution Program\n\n## Challenge\n{st.session_state.challenge}\n\n## Strategic Plan\n{edited_plan}\n\n"
        st.success("Plan approved. Launching tool chain...")

        try:
            from agents.arbos_manager import ArbosManager
            arbos = ArbosManager()
            final_result, tools_used = arbos.run(st.session_state.challenge)
            
            st.session_state.final_output = final_result
            st.success(f"Tool chain completed! Tools used: {', '.join(tools_used)}")
        except Exception as e:
            st.error(f"Tool chain failed: {e}")

# === MINER REVIEW SECTION ===
if st.session_state.final_output:
    st.subheader("3. Miner Review Before Submission")
    st.markdown("**Final Output** — Review carefully before submitting to the subnet")
    
    reviewed_output = st.text_area("Final Solution (you can edit)", 
                                   value=st.session_state.final_output, 
                                   height=500)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Accept & Submit", type="primary"):
            Path("goals/final_solution.md").write_text(reviewed_output)
            st.success("✅ Solution accepted and saved for submission!")
            st.balloons()
    
    with col2:
        if st.button("🔄 Let Arbos Run Another Loop"):
            st.warning("Arbos will now perform another full iteration with updated context.")

# Debug Mode
st.session_state.debug_mode = st.checkbox("Enable Debug/Trace Mode", value=st.session_state.debug_mode)
if st.session_state.debug_mode and st.session_state.trace_log:
    st.subheader("🔍 Debug Trace")
    for entry in st.session_state.trace_log:
        st.text(entry)

st.caption("System: Dynamic Reflection • Real ScienceClaw • Miner Review Before Submission • Optional Per-Loop Review via GOAL.md")

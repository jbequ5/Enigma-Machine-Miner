import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title="ENIGMA 3D — SN63 Miner", page_icon="🔑", layout="wide")

st.markdown('<h1 style="text-align:center; color:#ffcc00;">🔑 ENIGMA MACHINE 3D — SUBNET 63 MINER</h1>', unsafe_allow_html=True)
st.markdown("**Sequential Tool Chain with Reflection & Prompt Redesign After Every Tool**")

if "challenge" not in st.session_state:
    st.session_state.challenge = ""
if "current_plan" not in st.session_state:
    st.session_state.current_plan = ""
if "program_md" not in st.session_state:
    st.session_state.program_md = ""
if "hooked_tools" not in st.session_state:
    st.session_state.hooked_tools = []
if "tool_configs" not in st.session_state:
    st.session_state.tool_configs = {
        "ScienceClaw": {"search_intensity": "high", "max_sources": 15},
        "GPD": {"profile": "deep-theory", "tier": "1"},
        "AI-Researcher": {"search_mode": "deep"},
        "AutoResearch": {"depth": "medium", "iterations": 3},
        "HyperAgent": {"parallel_tasks": 5},
        "Chutes": {"llm_picker": "claude-3-5-sonnet"}
    }

st.subheader("1. Enter the Challenge")
challenge = st.text_area("Main challenge", value=st.session_state.challenge, height=100)

if st.button("Generate Plan with HyperAgent"):
    if not challenge:
        st.error("Please enter a challenge.")
    else:
        st.session_state.challenge = challenge
        with st.spinner("Generating plan..."):
            try:
                from agents.tools.hyperagent import run as run_hyperagent
                cfg = st.session_state.tool_configs.get("HyperAgent", {})
                result = run_hyperagent(task=f"Create detailed plan for: {challenge}", parallel_tasks=cfg.get("parallel_tasks", 5))
                st.session_state.current_plan = result.get("output", "")
                st.session_state.program_md = f"# Execution Program\n\n## Challenge\n{challenge}\n\n## Approved Plan\n{st.session_state.current_plan}\n\n"
                st.success("Plan generated!")
            except Exception as e:
                st.error(f"HyperAgent failed: {e}")

if st.session_state.current_plan:
    st.subheader("2. Review & Edit Plan")
    edited_plan = st.text_area("Plan (edit if needed)", value=st.session_state.current_plan, height=350)
    if st.button("✅ Approve Plan"):
        st.session_state.current_plan = edited_plan
        st.session_state.program_md = f"# Execution Program\n\n## Challenge\n{st.session_state.challenge}\n\n## Approved Plan\n{edited_plan}\n\n"
        st.success("Plan approved.")

# Tool Configurations (example)
st.subheader("3. Personal Tool Configurations")
if st.button("Save AutoResearch"):
    depth = st.selectbox("Depth", ["shallow", "medium", "deep"], key="ar_depth")
    iterations = st.number_input("Iterations", min_value=1, max_value=8, value=3, key="ar_iter")
    st.session_state.tool_configs["AutoResearch"] = {"depth": depth, "iterations": iterations}
    if "AutoResearch" not in st.session_state.hooked_tools:
        st.session_state.hooked_tools.append("AutoResearch")
    st.success("AutoResearch saved")

# Add other tool configs similarly if needed

if st.button("🚀 LAUNCH SEQUENTIAL TOOL CHAIN", type="primary"):
    if not st.session_state.current_plan:
        st.error("Approve a plan first.")
    else:
        Path("goals/GOAL.md").write_text(build_goal_md())
        Path("program.md").write_text(st.session_state.program_md)
        st.success("Tool chain launched with reflection after every tool!")
        st.balloons()

def build_goal_md():
    text = "# Enigma Machine — SN63 Miner Goal\n\n"
    text += f"## Challenge\n{st.session_state.challenge}\n\n"
    text += f"## Approved Plan\n{st.session_state.current_plan}\n\n"
    text += "## Core Settings\nreflection: 4\nplanning: true\nhyper_planning: true\nmulti_agent: true\nswarm_size: 20\nexploration: true\nresource_aware: true\nguardrails: true\n\n"
    text += "## Personal Tool Instances\n"
    for tool, cfg in st.session_state.tool_configs.items():
        if tool in st.session_state.hooked_tools:
            text += f"- {tool}: {json.dumps(cfg)}\n"
    return text

st.text_area("Current program.md", st.session_state.program_md, height=300)

import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title="ENIGMA 3D — SN63 Miner", page_icon="🔑", layout="wide")

st.markdown('<h1 style="text-align:center; color:#ffcc00;">🔑 ENIGMA MACHINE 3D — SUBNET 63 MINER</h1>', unsafe_allow_html=True)

# Session State
if "hooked_tools" not in st.session_state:
    st.session_state.hooked_tools = []
if "tool_configs" not in st.session_state:
    st.session_state.tool_configs = {
        "ScienceClaw": {"search_intensity": "high", "max_sources": 15},
        "GPD": {"profile": "deep-theory", "tier": "1"},
        "AI-Researcher": {"search_mode": "deep"},
        "HyperAgent": {"parallel_tasks": 5},
        "Chutes": {"llm_picker": "claude-3-5-sonnet"}
    }
if "current_plan" not in st.session_state:
    st.session_state.current_plan = ""
if "challenge" not in st.session_state:
    st.session_state.challenge = ""

st.subheader("1. Enter Your Challenge")
challenge = st.text_area("What is the main challenge or task for today's miner?", 
                        value=st.session_state.challenge, height=100)

if st.button("Generate Detailed Plan with HyperAgent"):
    if not challenge:
        st.error("Please enter a challenge first.")
    else:
        st.session_state.challenge = challenge
        with st.spinner("HyperAgent is creating a detailed structured plan..."):
            try:
                from agents.tools.hyperagent import run as run_hyperagent
                cfg = st.session_state.tool_configs.get("HyperAgent", {})
                
                plan_task = f"""Create a detailed execution plan for this challenge: {challenge}

Requirements:
- Break down the challenge into clear steps
- Decide which tools to use (GPD, ScienceClaw, AI-Researcher, HyperAgent, Chutes) and in what order
- For each tool, write a specific, well-crafted prompt that should be sent to it
- Include reasoning for why each tool is chosen

Output format:
1. Overall Strategy
2. Tool Sequence
3. Detailed Prompts for each tool
4. Expected Output from each tool"""

                result = run_hyperagent(
                    task=plan_task,
                    parallel_tasks=cfg.get("parallel_tasks", 5)
                )
                
                st.session_state.current_plan = result.get("output", "No plan generated.")
                st.success("Structured plan generated!")
            except Exception as e:
                st.error(f"Plan generation failed: {e}")

# Show and edit plan
if st.session_state.current_plan:
    st.subheader("2. Review & Edit HyperAgent Plan")
    edited_plan = st.text_area("HyperAgent Plan (edit if needed)", 
                              value=st.session_state.current_plan, height=300)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve Plan & Run Tools"):
            st.session_state.current_plan = edited_plan
            st.success("Plan approved. Running tools with this plan...")
            # Here you would call the full smart_route with the approved plan
            # For now we just show it
            st.info("Tools would now run using this plan (implementation next if you want)")
    with col2:
        if st.button("Regenerate Plan"):
            st.session_state.current_plan = ""
            st.rerun()

# Tool Config Section (same as before, shortened)
st.subheader("3. Configure Your Personal Tool Instances")
# ... (GPD, ScienceClaw, etc. config blocks from previous version)

# Final Launch
if st.button("🚀 LAUNCH FULL MINER", type="primary"):
    if not st.session_state.current_plan:
        st.error("Please generate and approve a plan first.")
    else:
        goal_md = build_goal_md(st.session_state.tool_configs, st.session_state.current_plan)
        Path("goals/GOAL.md").write_text(goal_md)
        st.success("Miner launched with approved plan + your personal tool instances!")
        st.balloons()

def build_goal_md(tool_configs, plan):
    text = "# Enigma Machine — SN63 Miner Goal\n\n"
    text += f"## Approved HyperAgent Plan\n{plan}\n\n"
    text += "## Core Arbos Settings\nreflection: 4\nplanning: true\nhyper_planning: true\nmulti_agent: true\nswarm_size: 20\nexploration: true\nresource_aware: true\nguardrails: true\n\n"
    text += "## Compute + LLM\nchutes: true\ntargon: false\ncelium: true\n"
    text += f"chutes_llm: {tool_configs.get('Chutes', {}).get('llm_picker', 'mixtral')}\n\n"
    text += "## Personal Tool Instances\n"
    for tool, cfg in tool_configs.items():
        text += f"- {tool}: {json.dumps(cfg)}\n"
    return text

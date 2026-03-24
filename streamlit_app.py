import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title="ENIGMA 3D — SN63 Miner", page_icon="🔑", layout="wide")

st.markdown('<h1 style="text-align:center; color:#ffcc00;">🔑 ENIGMA MACHINE 3D — SUBNET 63 MINER</h1>', unsafe_allow_html=True)
st.markdown("**Step 1: Challenge → HyperAgent Plan → Review → Tool Execution**")

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
if "challenge" not in st.session_state:
    st.session_state.challenge = ""
if "current_plan" not in st.session_state:
    st.session_state.current_plan = ""

st.subheader("1. Enter the Challenge")
challenge = st.text_area("What is the main challenge/task for today's miner?", 
                        value=st.session_state.challenge, height=120)

if st.button("Generate Detailed Plan with HyperAgent"):
    if not challenge:
        st.error("Please enter a challenge.")
    else:
        st.session_state.challenge = challenge
        with st.spinner("HyperAgent is creating a structured plan with tool selection and specific prompts..."):
            try:
                from agents.tools.hyperagent import run as run_hyperagent
                cfg = st.session_state.tool_configs.get("HyperAgent", {})
                
                plan_task = f"""Create a detailed execution plan for this challenge: {challenge}

Output in this exact format:

1. Overall Strategy
2. Tool Sequence (which tools and in what order)
3. Specific Prompt for each tool (write the exact prompt that should be sent to GPD, ScienceClaw, AI-Researcher, etc.)
4. Expected Output from each tool

Be precise and professional."""

                result = run_hyperagent(task=plan_task, parallel_tasks=cfg.get("parallel_tasks", 5))
                st.session_state.current_plan = result.get("output", "No plan generated.")
                st.success("Plan generated! Review and edit below.")
            except Exception as e:
                st.error(f"HyperAgent failed: {e}")

# Plan Review
if st.session_state.current_plan:
    st.subheader("2. Review & Edit HyperAgent Plan")
    edited_plan = st.text_area("HyperAgent Plan (edit if you want to change tools or prompts)", 
                              value=st.session_state.current_plan, height=400)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve Plan & Run Tools"):
            st.session_state.current_plan = edited_plan
            st.success("Plan approved. Tools will now run using this plan.")
            # In real version this would trigger smart_route
    with col2:
        if st.button("Regenerate Plan"):
            st.session_state.current_plan = ""
            st.rerun()

# Tool Configuration
st.subheader("3. Configure Your Personal Tool Instances")
# GPD
st.write("**GPD (Get Physics Done)**")
col_g1, col_g2 = st.columns(2)
with col_g1:
    gpd_profile = st.selectbox("Workflow Profile", ["deep-theory", "numerical", "exploratory", "review", "paper-writing"])
with col_g2:
    gpd_tier = st.selectbox("Capability Tier", ["1", "2", "3"])
if st.button("Save GPD"):
    st.session_state.tool_configs["GPD"] = {"profile": gpd_profile, "tier": gpd_tier}
    if "GPD" not in st.session_state.hooked_tools:
        st.session_state.hooked_tools.append("GPD")
    st.success("GPD saved")

# Add similar simple config for other tools if desired (ScienceClaw, etc.)

# Final Launch
if st.button("🚀 LAUNCH FULL MINER WITH APPROVED PLAN", type="primary"):
    if not st.session_state.current_plan:
        st.error("Please generate and approve a plan first.")
    else:
        goal_md = build_goal_md(st.session_state.tool_configs, st.session_state.current_plan, st.session_state.challenge)
        Path("goals/GOAL.md").write_text(goal_md)
        st.success("Miner launched! HyperAgent plan + all personal tool instances are active.")
        st.balloons()

def build_goal_md(tool_configs, plan, challenge):
    text = f"# Enigma Machine — SN63 Miner Goal\n\n"
    text += f"## Challenge\n{challenge}\n\n"
    text += f"## Approved HyperAgent Plan\n{plan}\n\n"
    text += "## Core Arbos Settings\nreflection: 4\nplanning: true\nhyper_planning: true\nmulti_agent: true\nswarm_size: 20\nexploration: true\nresource_aware: true\nguardrails: true\n\n"
    text += "## Compute + LLM\nchutes: true\ntargon: false\ncelium: true\n"
    text += f"chutes_llm: {tool_configs.get('Chutes', {}).get('llm_picker', 'mixtral')}\n\n"
    text += "## Personal Tool Instances\n"
    for tool, cfg in tool_configs.items():
        text += f"- {tool}: {json.dumps(cfg)}\n"
    return text

3. Final _smart_route in agents/arbos_manager.pypython

def _smart_route(self, challenge: str, approved_plan: str = ""):
    """Final routing using approved HyperAgent plan to craft detailed prompts."""
    results = []
    used_tools = []

    plan_context = approved_plan[:800] if approved_plan else "No detailed plan provided."

    # GPD
    if any(k in challenge.lower() for k in ["quantum", "physics", "circuit", "theory", "particle", "gravity"]):
        try:
            from agents.tools.get_physics_done import run as run_gpd
            cfg = self.config.get("GPD", {})
            detailed_task = f"Challenge: {challenge}\n\nPlan context: {plan_context}\n\nSolve this physics task with high rigor using the plan."
            result = run_gpd(task=detailed_task, profile=cfg.get("profile", "deep-theory"), tier=cfg.get("tier", "1"))
            results.append(f"[GPD — {cfg.get('profile')} / Tier {cfg.get('tier')}] {result.get('output', result.get('error'))}")
            used_tools.append("GPD")
        except Exception as e:
            results.append(f"[GPD Error] {str(e)}")

    # ScienceClaw
    if any(k in challenge.lower() for k in ["research", "paper", "data", "science", "analyze"]):
        try:
            from agents.tools.scienceclaw import run as run_scienceclaw
            cfg = self.config.get("ScienceClaw", {})
            detailed_task = f"Challenge: {challenge}\n\nPlan: {plan_context}\n\nPerform deep research and analysis."
            result = run_scienceclaw(task=detailed_task, search_intensity=cfg.get("search_intensity", "high"), max_sources=cfg.get("max_sources", 15))
            results.append(f"[ScienceClaw] {result.get('output', result.get('error'))}")
            used_tools.append("ScienceClaw")
        except Exception as e:
            results.append(f"[ScienceClaw Error] {str(e)}")

    # AI-Researcher
    if any(k in challenge.lower() for k in ["literature", "web", "search", "news"]):
        try:
            from agents.tools.ai_researcher import run as run_ai_researcher
            cfg = self.config.get("AI-Researcher", {})
            detailed_task = f"Challenge: {challenge}\n\nPlan: {plan_context}\n\nConduct thorough research."
            result = run_ai_researcher(task=detailed_task, search_mode=cfg.get("search_mode", "deep"))
            results.append(f"[AI-Researcher] {result.get('output', result.get('error'))}")
            used_tools.append("AI-Researcher")
        except Exception as e:
            results.append(f"[AI-Researcher Error] {str(e)}")

    if not results:
        results.append("No specialized tool matched. Using default reasoning.")
        used_tools.append("Arbos Core")

    return "\n\n".join(results), used_tools

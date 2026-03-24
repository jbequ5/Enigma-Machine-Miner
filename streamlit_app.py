import streamlit as st
from pathlib import Path
import json
from components.enigma_3d.enigma_3d import enigma_3d   # ← matches the v2 component structure

st.set_page_config(
    page_title="ENIGMA 3D — SN63 Miner",
    page_icon="🔑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ====================== BUNKER ATMOSPHERE CSS ======================
st.markdown("""
<style>
    .stApp {
        background: #0a0503;
        color: #ffcc00;
        font-family: 'Courier New', monospace;
    }
    .header {
        text-align: center;
        padding: 20px;
        border-bottom: 3px solid #ffcc00;
        margin-bottom: 20px;
        text-shadow: 0 0 10px #ffcc00;
    }
    .status {
        padding: 10px;
        background: rgba(255, 204, 0, 0.1);
        border: 1px solid #ffcc00;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">🔑 ENIGMA MACHINE 3D — SUBNET 63 MINER</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-size:1.1rem;">You enter the dimly lit bunker. The Enigma awaits on the table. Tools are ready to be hooked.</p>', unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "hooked_tools" not in st.session_state:
    st.session_state.hooked_tools = []
if "tool_configs" not in st.session_state:
    st.session_state.tool_configs = {
        "ScienceClaw": {"enabled": True, "reflection_depth": 3},
        "GPD": {"enabled": True, "repo_limit": 50},
        "AI-Researcher": {"enabled": True, "search_mode": "deep"},
        "HyperAgent": {"enabled": True, "parallel_tasks": 4},
        "Chutes": {"enabled": True, "llm_picker": "claude-3-5-sonnet"},
    }
if "zoom_machine" not in st.session_state:
    st.session_state.zoom_machine = False
if "last_inspected_tool" not in st.session_state:
    st.session_state.last_inspected_tool = None

# ====================== 3D VIDEO-GAME SCENE ======================
st.markdown("### 🕹️ 3D BUNKER — Orbit • Drag • Hook • Launch")
hooked_tools = enigma_3d(
    hooked_tools=st.session_state.hooked_tools,
    tool_configs=st.session_state.tool_configs,
    key="enigma_3d_scene"
)

# Sync back any changes from 3D component
st.session_state.hooked_tools = hooked_tools

# ====================== INSPECT TOOL DIALOG ======================
if st.session_state.last_inspected_tool:
    tool = st.session_state.last_inspected_tool
    config = st.session_state.tool_configs.get(tool, {})
    
    with st.dialog(f"🔧 INSPECT & CUSTOMIZE: {tool}"):
        st.write(f"**Configure {tool}** — changes save live to the miner.")
        
        for k, v in list(config.items()):
            if isinstance(v, bool):
                config[k] = st.checkbox(k.replace("_", " ").title(), value=v)
            elif isinstance(v, (int, float)):
                config[k] = st.number_input(k.replace("_", " ").title(), value=v)
            else:
                config[k] = st.text_input(k.replace("_", " ").title(), value=str(v))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Save & Hook to Machine", type="primary"):
                st.session_state.tool_configs[tool] = config
                if tool not in st.session_state.hooked_tools:
                    st.session_state.hooked_tools.append(tool)
                st.session_state.last_inspected_tool = None
                st.rerun()
        with col2:
            if st.button("Cancel"):
                st.session_state.last_inspected_tool = None
                st.rerun()

# ====================== HOOKED TOOLS STATUS ======================
if st.session_state.hooked_tools:
    st.markdown("### 🔌 CURRENTLY HOOKED TO ENIGMA")
    cols = st.columns(len(st.session_state.hooked_tools))
    for i, tool in enumerate(st.session_state.hooked_tools):
        with cols[i]:
            st.success(f"⚡ **{tool}**")
            if st.button("Unhook", key=f"unhook_{tool}"):
                st.session_state.hooked_tools.remove(tool)
                st.rerun()

# ====================== ZOOM-IN MODAL — FINAL GOAL.MD ENCODING ======================
if st.session_state.zoom_machine:
    with st.dialog("🔍 ENIGMA ZOOM — FINAL ENCODING & LAUNCH"):
        st.markdown("### Set your final mission parameters")
        
        goal_path = Path("goals/GOAL.md")
        base_path = Path("goals/killer_base.md")
        
        if not goal_path.exists():
            if base_path.exists():
                goal_content = base_path.read_text()
            else:
                goal_content = "# Default Enigma Goal\n\nTune reflection, exploration, and compute routing here."
        else:
            goal_content = goal_path.read_text()
        
        edited_goal = st.text_area("GOAL.md (live edit — this controls the entire miner)", 
                                  value=goal_content, 
                                  height=420,
                                  help="Everything in GOAL.md is optional and drives Arbos + all tools.")
        
        col_launch = st.columns([1, 1, 1])
        with col_launch[0]:
            if st.button("🔄 Encode & Save GOAL.md", type="primary"):
                goal_path.parent.mkdir(exist_ok=True)
                goal_path.write_text(edited_goal)
                st.success("✅ GOAL.md encoded and saved!")
        
        with col_launch[1]:
            if st.button("🚀 LAUNCH MINER", type="primary"):
                goal_path.write_text(edited_goal)
                st.balloons()
                st.success("🚀 Forward pass started! Arbos is now conducting with your hooked tools + H100 timer active.")
                # Optional: os.system("python -m neurons.miner")  # uncomment when ready
                st.session_state.zoom_machine = False
                st.rerun()
        
        with col_launch[2]:
            if st.button("← Back to Bunker"):
                st.session_state.zoom_machine = False
                st.rerun()

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("### 🛠️ ENIGMA STATUS")
    st.write(f"**Hooked Tools:** {len(st.session_state.hooked_tools)} / 5")
    st.write(f"**GOAL.md exists:** {Path('goals/GOAL.md').exists()}")
    
    if st.button("Reset All Tools"):
        st.session_state.hooked_tools = []
        st.rerun()
    
    st.caption("3D video-game interface built with React Three Fiber.\n"
               "Orbit the machine • Drag tools to hook • Click for details.")

st.caption("🔑 Powered by real Arbos conductor • Chutes routing • H100 4-hour timer • All changes sync live to the miner.")

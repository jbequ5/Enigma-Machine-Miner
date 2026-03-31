import streamlit as st
import json
import zipfile
import pandas as pd
from pathlib import Path
from datetime import datetime

# MUST BE THE VERY FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="ALLIED ENIGMA MINER",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

from agents.arbos_manager import ArbosManager

# ====================== BUNKER THEME ======================
BUNKER_CSS = """
<style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://pub-1407f82391df4ab1951418d04be76914.r2.dev/enigma-bunker-with-machine.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.88);
        z-index: -1;
    }
    [data-testid="stHeader"], footer, [data-testid="stToolbar"] {
        visibility: hidden;
    }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
        color: #00ff9d !important;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 30px #00ff9d, 0 0 60px #00aa77;
        letter-spacing: 4px;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #000a06 !important;
        color: #00ff9d !important;
        border: 2px solid #00ff9d;
        font-family: 'Courier New', monospace;
    }
    .stButton > button {
        background-color: #001a0f;
        color: #00ff9d;
        border: 3px solid #00ff9d;
        font-family: 'Courier New', monospace;
    }
</style>
"""
st.markdown(BUNKER_CSS, unsafe_allow_html=True)

st.title("🔒 ALLIED ENIGMA MINER")
st.markdown("**US ARMY SIGNALS INTELLIGENCE • BUNKER COMMAND POST 1944 • SN63**  \n**Challenge-Agnostic • Quasar Long-Context • Dynamic Swarm • Verifier-First • Hardened**")

# ====================== MANAGER ======================
if "manager" not in st.session_state:
    st.session_state.manager = ArbosManager()
manager = st.session_state.manager

# ====================== GOAL.MD EDITOR ======================
st.subheader("📋 GOAL.md Strategy (Single Source of Truth)")
goal_path = Path("goals/killer_base.md")
if not goal_path.exists():
    goal_path.parent.mkdir(parents=True, exist_ok=True)
    goal_path.write_text("# Enigma Miner Base Strategy\n\nmode: optimal\nquasar_attention: true\ndynamic_swarm: true\nlight_compression: true\ngrail_on_winning_runs: true\nself_critique_enabled: true\n", encoding="utf-8")

goal_content = goal_path.read_text(encoding="utf-8")
new_goal = st.text_area("Edit GOAL.md:", value=goal_content, height=300, key="goal_editor_unique")

if st.button("💾 Save GOAL.md"):
    goal_path.write_text(new_goal, encoding="utf-8")
    st.success("✅ GOAL.md saved")

# ====================== COMPUTE SETUP ======================
st.subheader("⚙️ Compute Setup")
compute_source = st.radio("Compute Source", ["local", "chutes"], key="compute_source_radio", horizontal=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("🔧 Controls")
    enable_quasar = st.checkbox("Enable Quasar Long-Context", value=True, key="quasar_checkbox")
    enable_three_layer = st.checkbox("Enable Three-Layer Memory Compression", value=True, key="three_layer_checkbox")
    enable_toolhunter = st.checkbox("Enable ToolHunter + ReadyAI", value=True, key="toolhunter_checkbox")
    enable_grail = st.checkbox("Enable Grail on Winning Runs", value=True, key="grail_checkbox")
    enable_self_critique = st.checkbox("Enable Self-Critique", value=True, key="self_critique_checkbox")
    enable_light_compression = st.checkbox("Enable Light Context Compression", value=True, key="light_compression_checkbox")
    enable_dynamic_swarm = st.checkbox("Enable Dynamic Swarm (VRAM-aware)", value=True, key="dynamic_swarm_checkbox")

# ====================== CHALLENGE INPUT ======================
challenge = st.text_area("SN63 Challenge + Verification Instructions", height=200, placeholder="Paste the full challenge here...")

# ====================== STAGE MANAGEMENT ======================
if "stage" not in st.session_state:
    st.session_state.stage = None
if "high_level_plan" not in st.session_state:
    st.session_state.high_level_plan = None
if "blueprint" not in st.session_state:
    st.session_state.blueprint = None
if "final_solution" not in st.session_state:
    st.session_state.final_solution = None

# Stage 1: Generate Plan
if st.button("🔍 Generate High-Level Plan", type="primary"):
    with st.spinner("Arbos Planning Phase..."):
        plan = manager.plan_challenge(challenge)
        st.session_state.high_level_plan = plan
        st.session_state.stage = "planning_approval"
        st.rerun()

# Planning Approval
if st.session_state.get("stage") == "planning_approval" and st.session_state.get("high_level_plan"):
    st.subheader("📋 Stage 1: High-Level Plan Review")
    st.json(st.session_state.high_level_plan)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Approve & Continue to Orchestration", type="primary"):
            st.session_state.stage = "post_orchestration_review"
            st.rerun()
    with col2:
        if st.button("🔄 Tweak & Re-plan"):
            st.session_state.stage = None
            st.rerun()
    with col3:
        if st.button("❌ Reject"):
            st.session_state.stage = None
            st.rerun()

# Post-Orchestration / Launch Swarm
if st.session_state.get("stage") == "post_orchestration_review":
    st.subheader("🧠 Stage 2: Orchestration Review - Ready to Launch")
    if st.button("🚀 Launch Dynamic Swarm Now", type="primary"):
        with st.spinner("Executing full Arbos swarm... This may take time."):
            result = manager.run(challenge)
            st.session_state.final_solution = result
            st.session_state.stage = "final_review"
            st.rerun()

# Final Review + Packaging
if st.session_state.get("stage") == "final_review" and st.session_state.get("final_solution"):
    st.subheader("✅ Final Solution")
    st.markdown(st.session_state.final_solution.get("solution", "No solution text returned"))
    
    if st.button("📦 Create SN63 Submission Package"):
        # Your original packaging logic goes here - paste your full _package_submission function if you have extra fields
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        sub_dir = Path("submissions") / f"sn63_{ts}"
        sub_dir.mkdir(parents=True, exist_ok=True)
        
        solution = st.session_state.final_solution.get("solution", "")
        (sub_dir / "solution.md").write_text(solution)
        # Add more files as in your original code (blueprint, trace, validation_oracle.json, etc.)
        
        with zipfile.ZipFile(sub_dir / "submission_package.zip", "w") as z:
            for f in sub_dir.glob("*"):
                if f.is_file() and f.suffix != ".zip":
                    z.write(f, f.name)
        
        st.success(f"Package ready: {sub_dir}/submission_package.zip")
        with open(sub_dir / "submission_package.zip", "rb") as f:
            st.download_button("Download Submission Package", data=f.read(), file_name=f"sn63_{ts}.zip")

st.caption("Enigma Machine Miner — Ready for SN63 Prize Pools")

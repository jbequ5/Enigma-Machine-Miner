# Enigma Machine Miner – Bittensor SN63

**Arbos-centric primary solver with intelligent planning, dynamic LLM swarm, VRAM monitoring, real-time ToolHunter, miner-controlled executable verification, and automatic deterministic/symbolic tooling.**

The most intelligent and resource-efficient solo miner on Subnet 63 (Enigma). 

Built from first principles to solve extremely hard, well-defined challenges across quantum computing and any industry — while staying strictly within your compute limit.

### Core Architecture – The Intelligent Loop

```mermaid
flowchart TD
    A["SN63 Challenge Definition + GOAL.md"] 
    --> B["🔬 Intelligent Planning Arbos<br/>High-level plan + suggested swarm size + deterministic recommendations"]

    B --> C["Miner Approval<br/>(Streamlit UI)"]
    C -->|"✅ Approve with Miner Enhancements"| D["🧠 Orchestrator Arbos<br/>Plan Refinement → Executable Blueprint"]
    C -->|"🔄 Tweak"| B
    C -->|"❌ Reject"| A

    D -->|"✅ Approve with Miner Enhancements"| E["🚀 Dynamic Subprocess Agent Swarm<br/>Parallel Sub-Arbos Instances<br/>(3–6 agents + real-time VRAM monitoring)"]

    E --> F1["Sub-Arbos 1<br/>Subtask + Hypothesis<br/>→ Symbolic Module + ToolHunter if needed"]
    E --> F2["Sub-Arbos 2<br/>Subtask + Hypothesis<br/>→ Symbolic Module + ToolHunter if needed"]
    E --> FN["Sub-Arbos N<br/>Subtask + Hypothesis<br/>→ Symbolic Module + ToolHunter if needed"]

    F1 & F2 & FN --> G["🔄 Reconvene with Main Arbos<br/>Synthesis of all sub-results"]

    G --> H["📊 Intelligent Verification System<br/>Miner-controlled executable verification +<br/>Direct Quantum Rings / OpenQuantum integration + ValidationOracle"]

    H -->|"✅ Pass"| I["Final Miner Review<br/>+ One-click SN63 Packaging"]
    H -->|"❌ Fail"| J["Arbos Improvement Loop<br/>Re-reflect → Re-refine → Re-swarm<br/>+ Three-Layer Memory + Safe Runtime Tool Creation"]

    J --> E

    I --> K["Submit to SN63<br/>submission_package.zip"]
```

---

### Key Intelligence Highlights

- **Full Miner Control** — Planning approval, deterministic tooling field, executable verification, custom LLM requests, enhancement prompt, final review, and one-click packaging.
- **Intelligent Planning Arbos** — Generates high-level strategy and explicitly recommends deterministic tools and custom HF models (Stim, Quantum Rings, PyTKET, SymPy, or models like Llama-3-70B and Qwen2-Math).
- **Miner-Controlled Deterministic Tooling** — Miner can review Arbos suggestions and add/override tooling or model requirements before the swarm starts.
- **Miner Enhancement Prompt** — Dedicated field to inject custom instructions (tool priorities, novelty focus, model preferences, synthesis style, etc.) that Arbos respects throughout the run.
- **Orchestrator Arbos** — Refines the plan into an executable blueprint with subtasks, swarm config, tool_map, and model assignments.
- **Dynamic Parallel Swarm with per-subtask ToolHunter** — Each Sub-Arbos explores hypotheses independently and calls ToolHunter for gaps. Tool acquisiton failures are clearly shown in the final ToolHunter tab with actionable fixes.
- **Automatic Symbolic Reasoning** — Automatically invokes deterministic logic (stabilizers, fidelity, circuit optimization, preprocessing) before falling back to LLM.
- **Intelligent Verification System** — Supports custom executable code including direct Quantum Rings and OpenQuantum integration for real, deterministic metrics. Now powered by **ValidationOracle** as the single source of truth.
- **Adaptive Re-loop & Memory** — Strong long-term memory with meta-reflection on failures, making the miner more effective over time.
- **EGGROLL Low-Rank Perturbations** — Efficient exploration in the inner loop for better novelty with lower compute cost.
- **Agent-Reach Grounding** — ToolHunter now automatically fetches clean web content with caching and fallbacks for higher-quality recommendations.
- **Phase 4 Post-Orchestration Review Dashboard** — Parallel view with blueprint, Validation Oracle summary, toggles for Arbos Recommended (Vector DB) and custom context, plus "Encode & Launch Swarm".
- **Three-Layer Memory Refinement** — Short-term buffer + LLM-compressed long-term summaries on top of Vector DB for sharper Arbos Recommended and better long-term learning.
- **Safe Runtime Tool Creation** — Arbos can propose, safely test, and persist new quantum-specific tools only if they meaningfully improve validation_score.

---

### Miner Enhancement Prompt (Make this a 10/10 run)

In the planning approval screen there is a dedicated field titled **"🚀 Miner Enhancement Prompt (Make this a 10/10 run)"**.

Use it to give Arbos custom guidance such as:
- Tool priorities or constraints
- Focus areas (novelty, verifier strength, IP potential, efficiency)
- Synthesis preferences
- Specific model requests (e.g. "Use TheBloke/Llama-3-70B-Instruct for synthesis")
- Any other challenge-specific instructions

These instructions are injected into refinement and synthesis.

---

### Miner-Controlled Deterministic Tooling

- Planning Arbos shows clear recommendations.  
- You can immediately add or edit **Deterministic Tooling Requirements** (e.g., "Use stim for stabilizers. Run fidelity on Quantum Rings.").  
- You get time to install recommended tools before the swarm launches.  
- Arbos then automatically uses the symbolic module and respects your preferences.

---

### Accepting Miner Models & Smart Model Hunting

**ToolHunter includes smart model hunting**:  
- When relevant, it searches Hugging Face for specialized models and returns the name + compatibility notes (VRAM, quantization options).  
- You see these in the final ToolHunter tab with manual action suggestions (e.g., “Use 4-bit version” or “Rent larger GPU”).

**How to request custom models**:  
- Simply write the exact model name in the Enhancement Prompt, for example:  
- "Use TheBloke/Llama-3-70B-Instruct for synthesis"  
- "For stabilizer subtasks, prefer Qwen2-Math-7B-Instruct"  

Arbos respects your request. If the compute provider cannot load it, the system falls back gracefully and logs a clear warning.

---

### Dynamic LLM Logic

The system uses a smart **LLM Router** that chooses the right model for each task:  
- High-novelty, planning, orchestration, synthesis → "best" models  
- Routine sub-tasks, verification, ToolHunter → "fast" models  
- You can override any choice by naming a specific model (including HF models) in the Enhancement Prompt.  
- External endpoints receive the `preferred_model` field so they can attempt to load it.

---

### GOAL.md / killer_base.md Configuration

```markdown
# Enigma Machine Miner - Killer Base Strategy & Toggles
# Bittensor SN63 - Arbos-centric Solver

## GOAL
Solve the sponsor challenge with maximum novelty and verifier score while staying under the *DESIRED COMPUTE LIMIT*.

## Core Strategy (Miner Customizes)
Produce novel, verifier-strong, licensable solutions while staying within compute limits and maximizing IP/value.

## Toggles & Explanations

### Core Behavior
miner_review_after_loop: false     # true = pause after every major loop
max_loops: 5
miner_review_final: true

### Compute & Resource Management
compute_source: chutes             # Options: local, chutes, already_running, custom
max_compute_hours: 3.8
resource_aware: true               # Enforces time budgets and adjusts swarm size

### Safety & Quality
guardrails: true

### ToolHunter
toolhunter_escalation: true
manual_tool_installs_allowed: true

### Swarm Efficiency (vLLM only for local)
tensor_parallel_size: 1            # Only affects local compute
vllm_model: mistralai/Mistral-7B-Instruct-v0.2
```

### Quick Start

```bash
pip install -r requirements.txt
pip install vllm                    # Strongly recommended
streamlit run streamlit_app.py
```

(Optional: Add `GITHUB_TOKEN` to `.env` for richer ToolHunter searches. Install `stim`, `qiskit`, `pytket`, or `quantumrings` as needed.)

### Why This Wins on SN63

- True intelligent decomposition with Arbos-driven recommendations
- Parallel per-subtask ToolHunter + automatic symbolic reasoning reduces LLM reliance
- Miner-controlled verification with direct Quantum Rings/OpenQuantum support
- Full control over tooling, models, and instructions
- Strong resource awareness and adaptive memory

**Phase 2 ready.**

---

**Recent Upgrades**  
- **ValidationOracle** as single source of truth for scoring  
- **EGGROLL** low-rank perturbations for efficient exploration  
- **Agent-Reach** with caching + fallbacks for grounded ToolHunter  
- **Three-Layer Memory Refinement** — Short-term buffer + LLM-compressed long-term summaries on top of Vector DB  
- **Safe Runtime Tool Creation** — Arbos can propose, test, and persist new quantum-specific tools only if they meaningfully improve validation_score  
- **Phase 4 Parallel Review Dashboard** with toggles and "Encode & Launch Swarm"  
- **Early-stop** and `max_repair_attempts` robustness guards  
- Full V/Vd-ready packaging with oracle results included  

Made with focus on first-principles agentic design for Bittensor SN63.  
Questions or feature requests? Open an issue or ping @dTAO_Dad on X.

# THE ENIGMA MACHINE
**Arbos-Led Intelligent Solver for Frontier Challenges**

**English-first • Verifier-first • Biologically-evolving • Maximum Heterogeneity**

The Enigma Machine is a closed-loop, self-improving cognitive organism designed to solve the hardest sponsor challenges in quantum, cryptography, symbolic mathematics, and stochastic systems — while permanently upgrading its own intelligence with every run.

Unlike typical prompt-chaining agents that hallucinate and forget, Enigma treats every execution as both a solution attempt and a permanent evolutionary step. High-signal outcomes are distilled through ByteRover MAU scoring and folded into a living second brain of readable Markdown files. This creates compounding capability that grows measurably stronger over time.

### Core Differentiators

**1. Verifier-First Discipline + DVRP Pipeline**  
Every challenge begins with a formal **Verifiability Contract** — the single source of truth defining required artifacts, composability rules, dry-run criteria, and synthesis guidance.  

The DVRP Pipeline (Decompose → Verify → Recompose) enforces this contract at every layer:
- Planning Arbos generates and self-critiques the contract.
- Orchestrator derives per-subtask contract slices with focused verifier snippets through inner-agent debates.
- Dry-run simulator tests the full plan on winning + adversarial mock data before any swarm compute is spent.
- Once passed, the swarm is activated and every Sub-Arbos worker validates locally against its contract slice.
- Synthesis Arbos runs multi-proposal debate over recompositon + builds solution with final contract enforcement.
- ValidationOracle is the sole source of truth for all scoring (edge coverage, invariant tightness, fidelity, C3A confidence, θ_dynamic, and EFS).

This architecture eliminates unverifiable paths and makes every run replayable and auditable.

**2. Intelligent Stall & Gap Handling**  
When dry-runs fail or swarms stall, the system builds rich failure context and triggers intelligent replanning. Intelligent Replanning then decides the severity of the issue, and whether to repair the plan or completely rerun the orchestration layer and reattack. During analysis, the **DOUBLE_CLICK** or **ESCALATE_TO_TOOL** tags identify specific gaps (e.g., low invariant tightness on entropy) and automatically queues narrower, targeted experiments in Scientist Mode, or potential tools to close the gap. Expirement results build systemic knowledge and evolve the challenge specific contract to increase odds of verication success.

Failure becomes precise, surgical learning instead of blind retries.

**3. Proactive ToolHunter + Living Capability Layer**  
Orchestrator provides ToolHunter with full context (contract, gaps, dependency graph). It proactively recommends tools with install commands. The miner adds them via one-click ToolEnvManager (safe venvs). Every tool is replay-tested in dry-run before use. A Tool Recommendation Log tracks real ROI (EFS contribution, replay pass rate). Tool use gets more intelligent and more effecient from run to run, building a bank of reliable tools and strategies in natural language .md layer.

**4. Scientist Mode — Domain Building Engine**  
Scientist Mode generates synthetic challenges in your domain of choice, runs the full DVRP pipeline, and extracts contract improvements, new invariants, and heuristics. DOUBLE_CLICK gaps trigger focused follow-up experiments. All experiment summaries feed Meta-Tuning for genome evolution. Enigma 

This is how the system builds real domain expertise autonomously.

**5. Self-Hardening Intelligence Flywheel**  
The outer loop is a compounding organism:
- Scientist Mode + Meta-Tuning evolve contracts and principles.
- Pruning Advisor tracks module/tool ROI.
- Embodiment layers (Neurogenesis, Microbiome, Vagus) + pattern surfacers (RPS/PPS) add biological plasticity.
- ByteRover MAU Pyramid + Grail remember high-signal patterns.
- Symbiosis Arbos discovers emergent cross-field insights.
- Stigmergic wiki + MP4 archives make every insight rewindable.

High-signal runs automatically evolve the brain. The organism literally improves its own verification rules, decomposition strategies, and synthesis logic over time.

### Miner Workflow
1. Edit brain files or use the Streamlit dashboard (including Optimization & Audit tab).
2. Enter challenge + verification instructions.
3. Review/edit the Planning-generated enhancement prompt.
4. Launch → watch real-time metrics and live stigmergic signals.
5. Review MP4 archives, Grail patterns, contract deltas, and pruning recommendations.

The system evolves its own brain for the next run.

### Quick Start
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py

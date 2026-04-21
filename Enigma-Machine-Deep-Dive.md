# THE ENIGMA MACHINE — Arbos-Inspired Intelligent Solver for Subnet 63

**English-first • Verifier-first • Self-improving • Maximum Heterogeneity • Real Compute Backends**

## Overview and Connection to SAGE

The Enigma Machine is the core solver at the heart of SAGE. It takes well-defined, verifiable challenges from Subnet 63 and produces solutions while generating high-signal fragments that permanently feed the broader SAGE intelligence layer.

Every run is treated as both a solution attempt and a permanent evolutionary step. High-signal outcomes are scored, fragmented with full provenance, and folded into the Solve Subsystem. These fragments flow through the Strategy Subsystem for ranking and enrichment, the Defense Subsystem for red-teaming and hardening, and the Training Subsystem for curation and meta-RL learning. The strongest outputs eventually reach the Economic Subsystem for sponsor proposals and marketplace value.

This tight integration is why SAGE works: the Enigma Machine is not an isolated tool. It is the data engine that powers the entire flywheel.

## 1. Verifier-First Architecture with Living Contract

Every challenge begins with a formal Verifiability Contract — the single source of truth that defines required artifacts, composability rules, dry-run success criteria, and synthesis guidance.

**How it works**:
- The contract is generated and rigorously self-critiqued during planning using deep graph search, bootstrap insights from prior runs, and the latest strategies pulled from the Strategy Subsystem via the Meta-Agent Synapse.
- Orchestrator decomposes the challenge and produces per-subtask contract slices along with executable verifier code snippets.
- These snippets constrain every subsequent step: intelligent dry-run, swarm execution, recomposition, and final validation.
- The contract evolves over time as Synapse’s self-audit loop and the Defense Subsystem identify weak spots and propose validated improvements.

**Why it will work**:
Verification is no longer a post-hoc check. It becomes a proactive constraint that dramatically raises the probability of producing solutions the subnet will actually accept and reward. Because the contract is living and tied to real performance data, it continuously hardens, reducing false positives and wasted compute.

## 2. DVR Pipeline & Intelligent Dry Run Gate

The complete DVR Pipeline (Decompose → Verify → Recompose) enforces the contract at every layer with ruthless determinism.

**How it works**:
- Intelligent mock generation creates high-fidelity winning mocks and adversarial variants that deliberately stress-test rules and invariants.
- Snippet self-validation runs first, followed by a 7D Verifier Self-Check (edge coverage, invariant tightness, adversarial resistance, consistency safety, symbolic strength, composability tightness, and fidelity) before any swarm compute is spent.
- Deterministic composability checking validates that merged subtask outputs satisfy the full contract.

**Why it will work**:
Dry-run gates and composability validation keep wasted compute extremely low. Only high-quality plans proceed to real execution. This efficiency is critical for scaling and for maintaining predictable costs within prize-pool windows.

## 3. Balanced Hybrid Compute with Confidence-Gated Routing

Every subtask is processed by a Balanced Hybrid Worker that prefers deterministic backends when confidence is high, with an explicit, logged fallback to LLM workers otherwise.

**How it works**:
- Confidence is calculated via a multi-signal weighted formula incorporating verifier quality, EFS projections, and historical performance on similar subtasks.
- When the threshold is met, deterministic tools (PuLP, SciPy, SymPy, NetworkX, OR-Tools, etc.) deliver exact results.
- When confidence is insufficient, the system falls back gracefully while preserving exploratory capability and logging the decision for future self-audit.

**Why it will work**:
It maximizes real compute density on optimization-heavy problems while keeping full creative exploration available for frontier challenges. The logged decisions feed Synapse’s self-audit loop, so the system learns when to trust deterministic paths versus when to explore.

## 4. Evolving .md Brain Layer

The brain layer (shared_core.md, principles/*.md, verification_contract_templates.md, constants_tuning.md, etc.) is a living, versioned knowledge store.

**How it works**:
- High-signal runs automatically append targeted evolutionary deltas with provenance and reinforcement scores.
- These files serve as both runtime prompts for the next mission and a permanent, human-readable audit trail.
- Synapse’s self-audit loop and the Defense Subsystem periodically review and refine the brain files based on real performance data and red-team findings.

**Why it will work**:
It creates compounding intelligence that is both machine-readable for the miner and human-auditable for subnet owners and academics. The brain evolves with the system rather than remaining static.

## 5. Actively Scored Fragmented Memory Layer

All outputs are intelligently fragmented (≤50 KB self-contained units) and written to the Strategy Subsystem with ongoing scoring.

**How it works**:
- Each fragment receives utilization, replay, and impact scoring.
- Cosmic Compression periodically prunes low-value fragments while promoting high-signal invariants.
- ByteRover MAU-style reinforcement actively decides whether a fragment is kept, compressed, or promoted to higher layers.

**Why it will work**:
The system remembers what worked, forgets what didn’t, and continuously improves its own knowledge base without unbounded growth. Full provenance ensures every fragment’s contribution is tracked for fair reward.

## 6. Continuous Intelligence Flywheel

The system closes the loop across multiple subsystems in a coherent, self-improving cycle.

**How it works**:
Fresh knowledge from the Solve Subsystem is gathered and integrated in the Strategy Subsystem. Discovered patterns are rigorously mined and tested. Targeted deep-dive experiments (via Scientist Mode) close specific gaps. Automated optimization (including TPE) tunes system constants, verification standards, and core principles. The updated contract, brain files, constants, and memory graph flow back into the next mission. Synapse’s self-audit loop, powered by the Training Subsystem, ensures the entire flywheel improves based on real outcomes.

**Why it will work**:
The miner becomes measurably smarter and more efficient with every mission. The compounding effect is visible in rising EFS trends, better contract quality, and higher solution acceptance rates over time.

## 7. Stall Detection & Intelligent Replanning

When a dry-run fails, a swarm stalls, or performance drops, the system uses rich stall detection and intelligent replanning.

**How it works**:
Early detection analyzes subtask scores, EFS delta, and verifier quality. Rich failure context drives replanning that decides between targeted repair or a new strategy. This happens within the same mission and feeds the self-audit loop and Defense Subsystem.

**Why it will work**:
The system improves in real time, reducing wasted compute and turning problems into learning opportunities rather than dead ends.

## 8. Measurement, Observability & Self-Awareness

**How it works**:
Weighted Hybrid Deterministic-First Score (DFS) quantifies real versus LLM contribution in every run. Pervasive structured tracing, notebook-ready provenance audit logs, and automated tuning provide ongoing self-analysis. Every improvement is tracked for monetization later in the pipeline.

**Why it will work**:
Subnet owners, academics, and contributors can see exactly how the system is improving over time. Transparency builds trust and enables fair reward distribution.

## Smart Stopping and End-of-Run Debriefs

The system includes a Learning Saturation Detector that monitors EFS improvement rate, calibration error trend, replan cycles, red-team findings, and resource pressure. It recommends graceful early stopping when additional runtime would yield diminishing returns, maximizing learning efficiency on local hardware.

After every mission, a comprehensive end-of-run debrief provides deep analysis and actionable Scientist Mode recommendations generated by a lightweight Synapse meta-analysis pass. These recommendations address plateaus or newly surfaced gaps, turning every run into a strategic learning step with one-click experiment execution.

## The Compounding Effect

The real strength of the Enigma Machine lies in how these mechanisms work together in a tightly integrated, self-reinforcing cycle across the five subsystems.

A formal, self-improving verification contract sets the standard from the start. Intelligent pre-execution validation and composability checks ensure only high-quality plans consume real compute. When difficulties arise, the system analyzes failures and adjusts in real time. Deterministic tools are used wherever they add value, while creative exploration remains fully available. Fresh knowledge is gathered and integrated, patterns are discovered and tested, targeted experiments close critical gaps, and core parameters are refined. All of this is filtered through an active memory layer that scores, promotes, and prunes knowledge so that only the highest-signal insights are retained and made immediately usable.

Every mission makes the entire system sharper, more efficient, more reliable, and more creative — feeding Synapse and the broader SAGE flywheel.

**Execution Reality**  
In practice, the full cycle runs efficiently on standard GPU hardware with predictable latency and cost. Dry-run gates, stall detection, and smart stopping keep wasted compute low, while the memory, tuning, and red-teaming layers keep mission costs predictable as the system improves over time. Early testing shows consistent completion within prize-pool windows with measurable gains in solution quality per mission. All solutions will be submitted through miners run by the subnet owners.

## Miner Workflow — Command-Post Experience (0.9.10 Flow)

1. Open the enhanced **Streamlit Command Dashboard**. The system first runs the Initial Setup Wizard, which guides you through compute source selection, smart LLM assignment per task type (optimized for the chosen compute and task requirements), challenge loading (from local or Commons), budget setting, and autonomy mode choice. A full flight test validates the entire configuration before any mission can launch.

2. Once the wizard confirms readiness, enter or select the challenge + verification instructions.

3. Review and optionally edit the Planning-generated contract, per-subtask verifier snippets, and enhancements. Optionally trigger a pre-swarm red-team attack for extra hardening.

4. Launch the mission. Watch live metrics, real-time trace log, ToolHunter recommendations, stigmergic signals, fragment health updates, and Synapse co-pilot assistance.

5. During and after the run, review MP4 archives, contract evolution deltas, fragment scoring and health, pruning recommendations from the advisor, red-team findings, and the comprehensive end-of-run debrief with Scientist Mode recommendations and the impact of any self-audit improvements.

The system continuously evolves its own brain files, constants, and strategies for future runs based on real performance data, red-teaming, and the self-audit loop.

Open the dashboard, complete the setup wizard, enter a frontier challenge, and watch a living cognitive organism solve it while permanently upgrading itself — with real backends, TPE meta-tuning, deep graph memory, sophisticated red teaming, smart stopping, and full observability.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py

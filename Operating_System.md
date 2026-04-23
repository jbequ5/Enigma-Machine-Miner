# Operating System — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.13-FeedbackUpdate1**  
**Last Updated:** April 23, 2026

## Abstract

The Operating System (OS) is the intelligent conductor layer of SAGE. It manages the execution of Enigma Machine (EM) instances at scale — from a single local run to a full swarm of parallel operators — while integrating the existing 0.9.10 full setup UI (wizard) as the primary entry point.

It provides:
- Wizard-first UX for solo miners with shared config for all instances.
- Compute-aware swarm size recommendation and dynamic adjustment.
- Smart LLM router with automatic downscaling as swarm size grows.
- Lightweight ping-only flight test (compute + LLM connectivity verification).
- Per-instance miner input strategy assignment for A/B testing effectiveness at inserted miner points.
- Full API / endpoint support for fully autonomous/headless operation.
- Operations telemetry feed to the Intelligence Subsystem for hierarchical learning.

This subsystem keeps the system dead-simple for a solo miner while delivering SOTA operations intelligence through hierarchical self-improvement. It is the bridge that turns individual EM runs into a scalable data factory feeding the entire SAGE flywheel.

## 1. Integration with Full Setup UI (Wizard)

The existing wizard remains the official human-friendly entry point and is the recommended starting point for all users:

- User runs the wizard once (or loads a saved config).
- Wizard collects global settings (compute sources, API keys, preferred models per task type, default contract queue, telemetry export path, miner input strategy templates, budget limits, autonomy preferences, etc.).
- Output is saved as a single shared `operations_config.json`.
- Every EM instance launched by the Orchestrator inherits this exact config — no per-instance re-setup is required.

**Autonomous Mode**  
The wizard can be fully bypassed via CLI or API for headless/large-scale operation:
```bash
python em_operations.py --autonomous --config operations_config.json --max-instances 24 --strategy-set "quantum_phd,conservative,diversity_max"
```
## 2. EM OS Orchestrator

The central conductor (single process or lightweight distributed swarm) that:

- Loads the shared wizard config.
- Scans live compute via ResourceMonitor (CPU, VRAM, network, thermal headroom).
- Recommends optimal swarm size N based on available resources and historical telemetry.
- Runs the Smart LLM Router with automatic downscaling.
- Performs a lightweight ping-only flight test.
- Assigns different miner input strategies per instance for A/B testing.
- Launches, monitors, recovers, and gracefully shuts down the swarm.
- Collects and forwards rich operations telemetry to the Intelligence Subsystem.

## 3. Smart LLM Router & Downscaling

The router profiles the task queue (via contract analysis and embeddings) and current compute, then recommends LLM size per task type. As swarm size N grows, it automatically downscales to stay within resource limits:

**Effective Model Size** ≈ Base Recommendation × (1 - downscale_factor × (N - 1))

- Base Recommendation is determined by task-type profiling (symbolic-heavy, numeric/optimization, graph-heavy, verification-light, synthesis-heavy) using contract analysis and embedding similarity.
- downscale_factor is learned over time by the Intelligence Subsystem’s Meta-RL Loop.
- Router always respects total available VRAM with an 80% safety margin and falls back gracefully.

**Model Registry** (stored in shared config or `models.json`) includes for each model: name, VRAM requirement, relative capability score, latency estimate, and supported features. The router selects the best fit and logs the choice for later meta-learning.

## 4. Lightweight Flight Test (Ping Only)

Before committing to the full swarm, the Orchestrator performs a pure connectivity and sanity test:

- ResourceMonitor.scan() to verify compute availability and headroom.
- Quick LLM health check (simple ping/status call) for each recommended model to verify connectivity, credentials, and basic rate limits.
- No full EM instance is run during the test.
- Produces a clear availability report and estimated cost-per-fragment summary.

If any ping fails, the Orchestrator re-recommends models and retries. This keeps the wizard fast and reliable.

## 5. Miner Input Strategy Assignment (A/B Testing)

At the specific inserted miner input points (hypothesis refinement, contract choice, synthesis review, etc.), the Orchestrator assigns different strategies to different instances:

- Strategies are stored as prompt templates or decision heuristics in the shared config.
- Examples: “PhD-level quantum physics knowledge injection”, “conservative verification-first”, “aggressive synthesis-first”, “diversity-maximizing with high temperature”.
- Each instance receives one assigned strategy for its entire run.
- All outcomes (EFS lift, fragment quality, stall rate, final solution strength) are logged with the strategy ID.
- This enables direct A/B measurement of which miner input strategies produce the best results.
- Results feed back into the Intelligence Subsystem so Synapse can learn and recommend optimal strategies over time.

## 6. OS Telemetry Collection

Operations data is collected in a dedicated telemetry stream (JSONL or lightweight database) and sent to the Intelligence Subsystem. This telemetry is a critical learning signal.

**Telemetry Schema** (each record includes):

- launch_timestamp, instance_id
- assigned_hardware (GPU ID, VRAM, CPU cores, etc.)
- assigned_model and assigned_miner_input_strategy
- flight_test_results (ping success, latency)
- resource_peaks (VRAM, CPU, duration)
- fragments_produced, final_efs_achieved, stall_count
- estimated_cost_per_fragment

Telemetry is batched and forwarded securely. It becomes additional features/objectives for the Neural-Net Scoring Head and Meta-RL Loop to optimize orchestration policies (swarm sizing, LLM routing, strategy effectiveness, recovery thresholds, etc.).

## 7. Recovery and Dynamic Adjustment

The Orchestrator includes robust recovery logic:

- If an instance stalls (> configurable threshold without progress), it is restarted with a different seed or strategy.
- If total resource usage exceeds safety margins, N is dynamically reduced and instances are rebalanced.
- Circuit-breaker: if > 30% of instances fail, the swarm pauses and alerts the user/Synapse.

## 8. API and Endpoint Options

The Orchestrator exposes simple FastAPI endpoints for headless control and integration:

- `POST /start_swarm` — launch with config and optional overrides
- `GET /status` — current swarm health, telemetry summary, and A/B results
- `POST /stop` — graceful shutdown
- `POST /flight_test` — run on-demand ping test
- `POST /adjust_swarm` — change N or force strategy assignments

## 9. Synapse & Intelligence Connections

- Normal fragments flow: EM → Solve → Strategy → Synapse (unchanged).
- Operations telemetry → dedicated Operations Logger → Intelligence Subsystem (additional learning signal for orchestration policies, swarm sizing, LLM routing, and miner input strategies).
- Updated global approximations, meta-weights, and Defense packages are automatically pulled by the Orchestrator and applied to running swarms.

## 10. Data Flow Summary

Wizard (or API) → Shared Config → Orchestrator (compute scan + router + ping flight test + strategy assignment)  
Orchestrator → EM Instances (parallel, shared config)  
EM Instances → Solve (fragments) + Operations Logger (telemetry)  
Solve → Strategy → Synapse  
OS Logger → Intelligence Subsystem (meta-learning signal)

## 11. Attack Vectors and Mitigations

- Resource exhaustion → ResourceMonitor + safety margins + flight test
- Task queue poisoning → provenance validation on assigned contracts
- Strategy gaming → A/B results validated against actual EFS lift and downstream outcomes
- Telemetry tampering → hashed records with provenance
- All operations are logged with full provenance and can be audited by the Defense Subsystem (AHE).

## 12. Meta-Tuning Interaction

The Intelligence Subsystem’s global Meta-RL loop tunes both inner EM parameters and outer OS parameters (swarm size rules, LLM routing policy, miner input strategy effectiveness, recovery thresholds). Local TPE tuning in each EM instance remains unchanged. This creates a clean hierarchical meta-learning system.

## Why the Operating System Matters

The Operating System turns SAGE from a single-run tool into a scalable, self-improving parallel data factory. By integrating the familiar wizard, adding compute-aware routing with intelligent downscaling, a lightweight ping-only flight test, per-instance miner input strategy assignment for A/B testing, full API support, and a dedicated telemetry feed to the Intelligence Subsystem, it delivers SOTA operations intelligence while remaining dead-simple for a solo miner to run fully autonomously. The hierarchical learning loop (inner EM solving + outer orchestration learning) accelerates the entire SAGE flywheel faster than any individual miner could achieve alone.

This layer is essential for turning SAGE into a true community-scale intelligence engine.


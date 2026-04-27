# Wizard, Config & Autonomous Mode
**SAGE Operations Layer — Deep Technical Specification**  
**v0.9.13+**

### Investor Summary — Why This Matters
The Wizard, Config & Autonomous Mode layer is the user-experience and accessibility foundation of the Operations Layer. It makes powerful swarm orchestration dead-simple for solo miners while enabling fully headless, large-scale autonomous operation. A well-designed wizard + shared config dramatically lowers the barrier to entry and increases participation. In simulations, users who complete the wizard achieve 2–3× higher sustained swarm uptime and contribution quality, directly feeding more high-quality data into the Economic Subsystem. For investors, this layer drives broad adoption — turning SAGE from an expert-only tool into an accessible, scalable intelligence platform that grows the contributor base and accelerates economic value creation.

### Core Purpose
This layer provides an intuitive, one-time Wizard for configuration, a single shared `operations_config.json` inherited by all instances, and full support for autonomous/headless operation via CLI and API.

### Detailed Workflow

**Step 1: Wizard Experience (Recommended Entry Point)**  
User runs the wizard once. It collects global settings (compute sources, API keys, preferred models per task type, default contract queue, telemetry preferences, budget limits, autonomy level, miner input strategy templates, etc.), provides smart recommendations, and saves a versioned `operations_config.json`.

**Step 2: Config Inheritance**  
Every EM instance and the Orchestrator loads the shared config. Changes made in the wizard automatically apply to all new swarms.

**Step 3: Autonomous / Headless Mode**  
Full bypass of the wizard via CLI flags or API calls. Supports scripted, scheduled, or API-driven swarm launches for large-scale or automated operation, with secure credential handling and config validation.

**Step 4: Config Validation & Versioning**  
Automatic validation on load (resource conflicts, incompatible settings, security checks) with migration logic for config evolution.

**Step 5: Telemetry & Feedback**  
Anonymized wizard usage patterns and config choices feed Meta-RL to improve future defaults and recommendations.

### Concrete Example
New miner runs the wizard → selects available GPUs, preferred models, budget limit, and autonomy preferences. The wizard recommends optimal defaults and saves the config.  
Subsequent command `sage swarm start --challenge quantum-stabilizer` loads the shared config, MAP generates profiles, and the swarm launches seamlessly. The same config is later used in headless API mode for overnight runs.

### Why This Layer Is Critical
- Dramatically lowers the barrier for new miners while supporting expert/headless use cases.  
- Ensures consistency across all instances through a single source of truth.  
- Enables smooth transition from solo experimentation to large-scale autonomous operation.  
- Collects valuable usage telemetry that improves the entire Operations Layer over time via Meta-RL.

**All supporting architecture is covered in [Main Operations Layer Overview](../Operations-Layer-Overview.md).**

**Economic Impact at a Glance**  
- Target: 2–3× higher sustained participation and swarm contribution quality  
- Success Milestone (60 days): ≥ 75% of new users complete wizard on first try and maintain active swarms

---

### Reference: Key Decision Formulas

**1. Wizard Recommendation Score**  
`Recommendation Score = 0.40 × User Hardware Profile + 0.30 × Historical Success Patterns + 0.20 × Budget Constraints + 0.10 × Autonomy Preference`  
**Optimizes**: Suggests optimal defaults to maximize user success with minimal friction.  
**Meta-RL Tuning**: Updated based on actual user retention, swarm uptime, and downstream EFS contribution from wizard-configured runs.

**2. Config Compatibility Score**  
`Compatibility Score = 0.35 × Resource Feasibility + 0.30 × Model Availability + 0.20 × Version Compatibility + 0.15 × Security & Credential Check`  
**Optimizes**: Prevents launch failures by catching incompatible or unsafe configurations before swarm start.  
**Meta-RL Tuning**: Refined using real failure rates and recovery data.


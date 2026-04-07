# Enigma-Machine-Miner — Canonical Entry Point (Thin Shim v5.0)

## Verifiability Spec Template (v1.0 — passed to every layer)
```yaml
verifiability_spec:
  artifacts_required: []  # orchestrator fills
  composability_rules: ["no contradictions", "clear interfaces"]
  dry_run_success_criteria:
    edge_coverage: ">= 0.75"
    invariant_tightness: ">= 0.70"
    fidelity: ">= 0.78"
    c3a_confidence: ">= 0.78"
    EFS: ">= 0.65"
  learning_mandate: "full trace to wiki"
**Importance**: Single loader for ALL intelligence layers.  
This is the thin canonical shim. All high-leverage logic lives in `brain/`.  
Edit via **Streamlit Brain Dashboard** only.

[[brain/index.md|→ Full Brain Suite]]

## Core References (auto-loaded)
- **Shared Principles**: [[brain/principles/shared_core.md]]
- **Compression**: [[brain/principles/compression.md]]
- **Wiki Strategy**: [[brain/principles/wiki_strategy.md]]
- **Bio Strategy**: [[brain/principles/bio_strategy.md]]
- **English Evolution**: [[brain/principles/english_evolution.md]]

## Active Toggles
See [[brain/toggles.md]] — brain_depth: "lean" (default)

## Metrics Snapshot
See [[brain/metrics.md]]

---

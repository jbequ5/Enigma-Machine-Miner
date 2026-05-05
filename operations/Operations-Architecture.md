# Intelligent Operating System (IOS) — Fragment Factory Specification
**SAGE Operations Layer — v0.9.13+**

## Core Purpose
The Intelligent Operating System exists for one reason: to be SAGE’s highest-leverage **intelligent fragment factory**. Every decision — profile assembly, calibration flight test, swarm launch, subtask branching, resource allocation, and recovery — must maximize the number and quality of high-signal, provenance-rich fragments that survive strict gates and reach the Strategy and Intelligence layers.

The IOS is not merely an executor of Enigma Machine instances. It is the system that decides *what* becomes a fragment, *when*, *how* it is scored and tracked, and *how* the entire OS learns over time to produce better fragments.

## Non-Negotiable Factory Principles
- Create fewer, but dramatically higher-quality fragments.
- Every fragment must pass a strict verifier-first birth gate at creation time.
- Full immutable provenance and rich metadata are attached at birth.
- The OS must continuously learn (profile-aware yield tracking) which configurations produce the best fragments.
- Save/resume of partial high-value fragments is first-class.
- Calibration flight test must measure fragment yield and quality as the primary metric.

## Factory Metrics the OS Optimizes For
- Number of fragments that pass birth gate per run
- Average refined value-added of surviving fragments
- Profile-specific yield rate (best profiles are learned and preferred)
- Provenance completeness and immutability

## High-Level Factory Flow
1. Challenge or KAS product hunt is selected in the wizard (mandatory first step).
2. KAS-informed profile assembly on the *real* challenge.
3. Profile-aware calibration flight test (empirical measurement of fragment yield per profile on the real challenge and real models).
4. Intelligent load-out recommendation (Conservative / Balanced / Aggressive) with predicted fragment yield.
5. Swarm launch with chosen load-out.
6. During run: early candidacy filter → strict birth gate → rich metadata → fragment creation.
7. Post-run: profile yield statistics updated, partial high-value fragments saved for resume.
8. All surviving fragments routed to shared vaults with full provenance.

## Detailed Factory Mechanisms

### 1. Early Candidacy Filter (right after subtask output)
Fast, lightweight check before full scoring or storage.  
Criteria: preliminary 7D verifier self-check pass rate + quick EFS estimate + KAS novelty/gap signal + deterministic path usage bonus.  
Only candidates that pass move to full fragment creation.

### 2. Strict Birth Gate (at fragment creation)
Every candidate must pass:  
- 7D verifier self-check (geometric mean of 7 dimensions)  
- Base EFS calculation: 0.6 × validation score + 0.4 × refined value-added  
- Refined Value-Added calculation (with noise penalty)  
- Minimum thresholds (e.g., EFS ≥ 0.65, refined value-added ≥ 0.55)  

Only fragments that pass receive immutable cryptographic hash, full provenance, and rich metadata.

### 3. Rich Metadata at Birth
- Challenge ID, subtask ID, timestamp  
- Source profile ID + model used + internal branching size  
- Deterministic fraction  
- 7D scores, Base EFS, Refined Value-Added  
- Provenance hash  
- Gap signals from KAS  
- Utilization/replay counters (initialized at 0)

### 4. Profile-Aware Yield Tracking
The OS records, per profile, per challenge:  
- Total fragments generated  
- % that passed birth gate  
- Average Base EFS and Refined Value-Added  
- % that survived to Strategy/Synapse level  

This data becomes the primary signal for future profile selection and calibration flight test recommendations.

### 5. Save/Resume for Partial High-Value Fragments
After every run (calibration or real mission), the OS saves a profile session state containing:  
- All fragments generated so far  
- Cumulative yield statistics  
- Preferred internal subtask size (self-reported by the EM)  
- Calibration results (if applicable)  

The wizard detects existing sessions and offers “Resume Profile X (already has 4 runs and 87 high-signal fragments)” or start fresh.

### 6. Challenge-Specific Calibration Flight Test (Hardware-Aware, Model-Aware)
- **Stage 1 — Model Profiling**: For each candidate model, run a fast benchmark to build a lookup table (VRAM/RAM usage, throughput, thermal headroom at increasing concurrency).  
- **Stage 2 — KAS-Informed Profile Assembly**: KAS assembles 3–4 meaningful profiles on the *real* challenge.  
- **Stage 3 — Incremental Orchestration Test**: For each profile, run short orchestration with incremental subtask branching (1 → 5).  
- **Stage 4 — Self-Reported Optimal Size**: The EM itself reports its preferred internal subtask size for that profile on this challenge.  
- **Stage 5 — Intelligent Load-Out Recommendations**: Apply hardware limits to generate Conservative / Balanced / Aggressive options with exact predicted numbers: concurrent LLM load, peak VRAM, expected fragment yield, EFS.

## Integration with Rest of SAGE
- Surviving fragments are pushed to shared vaults after the birth gate.  
- Yield statistics feed Meta-RL and Synapse nightly polishing.  
- Save/resume state is stored locally but can be synced to shared vaults for cross-session learning.

This specification turns the IOS into a true intelligent fragment factory. Every component now serves the single goal of producing more and better fragments that fuel the entire SAGE flywheel.

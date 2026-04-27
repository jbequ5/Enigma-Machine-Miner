# Pipeline & Scoring — Economic Subsystem
**SAGE — Shared Agentic Growth Engine**  
**v0.9.13+**  
**Last Updated:** April 27, 2026

### Investor Summary — Why This Matters
The scoring pipeline is the nervous system of the Economic Subsystem. It decides which gaps deserve attention, which drafts get polished, which contributors earn rewards, and which products reach the marketplace. Well-tuned scoring directly correlates with faster revenue, higher participation, and lower risk of low-value work. Early simulations show that Meta-RL improvements to these scorers can increase overall toolkit revenue contribution by 40–65% while cutting wasted polishing compute by more than 50%. This is not theoretical — it is the measurable mechanism that turns collective solving intelligence into predictable economic return.

### Core Purpose
This document centralizes every major scoring formula in the Economic Subsystem. Each score is designed to optimize a specific part of the value-creation funnel while feeding data back into the Meta-RL Loop for continuous improvement.

All scores are normalized 0–1 unless otherwise noted and are updated daily as new data arrives.

---

### 1. Gap Pain Score — Identifying High-Value Problems
**Formula**  
`Gap Pain Score = 0.35 × Frequency + 0.20 × Severity + 0.20 × Commercial Blocking + 0.25 × Intervention Failure Rate / DOUBLE_CLICK`

**What it optimizes**: Prioritizes gaps that are frequent, painful, commercially relevant, and resistant to quick fixes.  
**Why it matters**: High-pain gaps have the strongest correlation with sponsor interest and revenue potential.  
**Meta-RL tuning**: Adjusts component weights based on which combination best predicts downstream monetization.

**Threshold**: ≥ 0.78 triggers Product KAS recommendations to miners.

---

### 2. BD Relevance Score — Market Signal Strength (Lane 1)
**Formula**  
`BD Relevance Score = 0.45 × Sponsor/Chat Frequency + 0.30 × Demand Velocity + 0.15 × Similar Revenue Proxy + 0.10 × Conversion Probability`

**What it optimizes**: Quantifies how commercially promising a gap is based on real sponsor and marketplace signals.  
**Why it matters**: Bridges technical gaps to business demand, ensuring we focus on problems sponsors will actually pay to solve.  
**Meta-RL tuning**: Learns which signals (e.g., chat interventions vs. external searches) are strongest predictors of closed deals.

---

### 3. Revenue Potential Score (Synapse Opportunity Ranker)
**Formula**  
`Revenue Potential Score = 0.40 × BD Demand Velocity + 0.25 × (Gap Pain × Intervention Success) + 0.20 × Market Proxy Strength + 0.15 × Miner Investment Level`

**What it optimizes**: Decides nightly polishing priority and global push-down.  
**Why it matters**: Prevents compute waste on low-potential work and focuses effort on the highest-ROI opportunities.  
**Meta-RL tuning**: Continuously refines weights to maximize actual revenue per polishing cycle.

---

### 4. Proposal Readiness Score (Lane 2 — Business Growth)
**Formula**  
`Proposal Readiness Score = 0.35 × BD Relevance Match + 0.25 × SAGE Technical Strength + 0.20 × Sponsor Fit + 0.15 × Verifiability + 0.05 × Novelty`

**What it optimizes**: Determines when a proposal is ready for sponsor outreach or marketplace listing.  
**Why it matters**: Ensures proposals sent to sponsors are high-quality and likely to close.  
**Meta-RL tuning**: Learns which factors best predict landing rates.

---

### 5. Impact Score (Contributor Pool — 25% of Revenue)
**Formula**  
`Impact Score = 0.40 × Technical Value + 0.30 × Data Quality & Confidence + 0.20 × Uniqueness + 0.10 × Effort`  
(1.5× multiplier for self-funded Product KAS hunts)

**What it optimizes**: Fairly distributes the contributor pool based on real contribution to value.  
**Why it matters**: Creates transparent, merit-based rewards that strongly incentivize high-quality participation.  
**Meta-RL tuning**: Retroactively adjusts scores using real performance data from sales and Health Scores.

---

### 6. Health Score (7-Day Refresher)
**Formula**  
`Health Score = 0.35 × Usage & Adoption + 0.25 × Performance Metrics + 0.20 × Buyer Feedback + 0.15 × Freshness + 0.05 × Compliance`

**What it optimizes**: Monitors live product quality and triggers polishing or de-listing.  
**Why it matters**: Prevents marketplace decay and maintains buyer trust.  
**Meta-RL tuning**: Uses Health Score trajectory to improve polishing tactics.

---

### 7. Synthesis Improvement Score (Polishing Loop)
**Formula**  
`Synthesis Improvement Score = 0.35 × Technical Quality Lift + 0.30 × Verifier Tightness Gain + 0.20 × Composability & Coherence + 0.15 × Revenue Projection Uplift`

**What it optimizes**: Measures how much value the polishing pass added.  
**Why it matters**: Quantifies the effectiveness of the nightly intelligence amplification step.  
**Meta-RL tuning**: Identifies which polishing tactics produce the best outcomes.

---

### 8. Double-Click Confidence Score (Quality Gate)
High-confidence experimental data (Scientist Mode / DOUBLE_CLICK) receives boosted weighting. Low-confidence data is heavily down-weighted or excluded to protect pipeline quality.

### How Meta-RL Interacts with All Scores
- Daily cycle evaluates proposed weight changes using both proxy metrics and real outcomes.
- Value Prediction NN provides economic forecast for each change.
- Updates are conservative (max 8% per day) with A/B testing and human review on major shifts.
- The loop learns high-leverage patterns (e.g., “increasing commercial blocking weight improves Revenue Potential by X%”) and applies them automatically.

**All formulas above are actively tuned by Meta-RL to maximize long-term value creation.**

---

This document serves as the single source of truth for scoring across the Economic Subsystem. It is referenced by the main Economic-Subsystem overview, Polishing Loop, Proposal Creation, and Meta-RL documents.

**Next Steps**  
- All scores feed into the nightly polishing loop and Meta-RL cycle.  
- Success is measured by Pipeline Health Score (composite of the above) trending upward and eventual revenue growth.

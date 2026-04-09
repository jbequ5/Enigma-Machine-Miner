# Memory & System Constants Tuning (v0.8+)
# Managed by Scientist Mode + Meta-Tuning

## Core Memory Constants
decay_k: 0.08                    # Fragment decay rate (Ebbinghaus-style)
high_signal_threshold: 0.78      # Promote fragments above this impact_score
compression_threshold: 0.42      # Compress fragments below this
fragment_max_size_kb: 50         # Automatic splitting threshold
impact_promotion_threshold: 0.78

## EFS Formula Weights
EFS_WEIGHTS:
  V: 0.3                         # Fidelity (V)
  S: 0.175                       # Convergence speed
  H: 0.175                       # Heterogeneity
  C: 0.175                       # Mean Δ_retro
  E: 0.175                       # MAUs per token

## MAU Pyramid Weights
MAU_WEIGHTS:
  validation_score: 0.4
  fidelity: 0.3
  heterogeneity: 0.2
  symbolic_coverage: 0.1

## Pruning & Fragment Utilization Thresholds
pruning_low_value_threshold: 0.42
pruning_high_value_threshold: 0.82
replay_pass_rate_min: 0.65

## Search Spaces for Scientist Mode
search_spaces:
  decay_k: [0.04, 0.06, 0.08, 0.10, 0.12]
  high_signal_threshold: [0.70, 0.75, 0.78, 0.82]
  compression_threshold: [0.35, 0.40, 0.42, 0.45]

## Domain Overrides (example)
quantum:
  decay_k: 0.06
  high_signal_threshold: 0.82

cryptographic:
  decay_k: 0.09
  high_signal_threshold: 0.75

# Last tuned by Scientist Mode: [timestamp]

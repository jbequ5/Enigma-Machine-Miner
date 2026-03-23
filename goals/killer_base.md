GOAL: Solve the sponsor challenge with maximum novelty and verifier score while staying under 3.8h on H100.

# CORE TOGGLES 
# Edit these lines to customize how Arbos behaves. All are optional.

reflection: 4

planning: true

hyper_planning: false

multi_agent: true

swarm_size: 20

exploration: true

resource_aware: true

guardrails: true

# Compute subnets

chutes: true

targon: false

celium: true

# LLM Model Picker for Chutes (new)

chutes_llm: mixtral     # Options: mixtral, llama3, gemma2, qwen2, etc.

# RALPH LOOP STEPS 
- # You can reorder or customize these steps

Steps per Ralph loop:
1. Plan the attack (uses HyperAgent if hyper_planning: true)
2. Execute with smart tool routing (GPD, ScienceClaw, AI-Researcher)
3. Reflect and improve (self-critique loop)
4. Explore one novel variant (if exploration: true)
5. Resource check + compress if needed
6. Final guardrails validation

# Enigma Machine – Agentic Miner Starter Kit for SN63

**The easiest way to build a winning miner for Enigma.**  
Anyone can post capital and an “impossible” problem. Miners compete to solve it in ≤4 hours on a single H200 GPU.

**Powered by Arbos + 8 proven agentic patterns.**  
Everything is **100% optional**. You control everything.

### Two Modes – Choose What Works for You
- **Optimal Mode** → Use the team’s recommended settings (best for beginners)  
- **Self-Built Mode** → Full control: turn features on/off and tune everything

---

### Quickstart (Takes 5 Minutes)

```bash
git clone https://github.com/YOUR-USERNAME/enigma-machine.git
cd enigma-machine
pip install -e .
```

1. Edit `config/miner.yaml` (add your wallet)  
2. Choose mode in `config/arbos.yaml` (`optimal` or `self-built`)  
3. Create or edit a GOAL.md file  
4. Run: `./scripts/run_miner.sh`

---

### How to Customize (Super Simple)

You control the miner by editing **one file**: your GOAL.md.

All settings are optional. Turn anything off if you don’t want it.

### The 8 Core Patterns – All Optional

| Pattern                        | What it does                                      | When to use it                              | One-line toggle in GOAL.md               | Default |
|--------------------------------|---------------------------------------------------|---------------------------------------------|------------------------------------------|---------|
| Reflection                     | Self-critiques and improves output                | Almost always (big quality boost)           | `reflection: 4` (or `false`)             | 3       |
| Planning                       | Breaks challenge into clear steps                 | Most challenges                             | `planning: true` (or `false`)            | true    |
| HyperAgent Planning            | Uses advanced self-improving planning             | Very complex or multi-step challenges       | `hyper_planning: true` (or `false`)      | false   |
| Multi-Agent                    | Runs parallel swarm of agents                     | Discovery & creative problems               | `multi_agent: true` + `swarm_size: 20`   | true    |
| Tool Use                       | Calls GPD, AI-Researcher, etc.                    | Most challenges                             | `tool_use: true` (or `false`)            | true    |
| Resource-Aware                 | Keeps everything under 4h H200                    | Required for prize eligibility              | `resource_aware: true` (or `false`)      | true    |
| Exploration & Discovery        | Creates truly novel solutions                     | Big prize challenges                        | `exploration: true` (or `false`)         | false   |
| Guardrails                     | Safety checks before submission                   | Always recommended                          | `guardrails: true` (or `false`)          | true    |

### Where to Edit (No Mysteries)

| What you want to change               | Where to edit it                          | How to do it                  |
|---------------------------------------|-------------------------------------------|-------------------------------|
| Turn patterns on/off or change numbers| `goals/your_strategy.md`                  | Just edit the text file       |
| Change default values                 | `config/arbos.yaml`                       | One line change               |
| Modify tool behavior                  | `agents/tools/*.py`                       | Edit Python (optional)        |

---

### Killer GOAL.md Template (Copy & Customize)

Copy this into `goals/killer_base.md`:

```markdown
GOAL: Solve the sponsor challenge with maximum novelty and verifier score while staying under 3.8h on H200.

reflection: 4
planning: true
hyper_planning: false          # Turn ON for very hard or multi-step challenges
multi_agent: true
swarm_size: 20
exploration: true
resource_aware: true
guardrails: true

Steps per Ralph loop:
1. Plan the attack (HyperAgent if hyper_planning: true)
2. Execute with smart tool routing
3. Reflect and improve
4. Explore one novel variant
5. Resource check + compress if needed
```

**Pro Tip**: Create multiple GOAL.md files (one for quantum, one for biology, one for speed, etc.) and switch between them.

---

Ready to dominate Enigma?  
Fork the repo, create your first GOAL.md, and start competing.

$TAO 🚀
```

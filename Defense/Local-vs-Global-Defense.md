# Local vs Global Defense
**SAGE Defense Subsystem — Deep Technical Specification**  
**v0.9.13+**

### Investor Summary — Why This Matters
The Local vs Global Defense model is the dual-layer execution strategy that gives SAGE both immediate protection during runs and systematic, network-wide hardening. Local Defense provides fast, real-time red-teaming on every EM instance, while Global Defense coordinates deep analysis and distributes authoritative fixes. In simulations, this hybrid approach reduces successful gaming attempts by 70–85% while keeping runtime overhead low. For investors, this is the mechanism that balances speed, scale, and security — ensuring the Economic Subsystem remains trustworthy and the platform hardens continuously as it grows, building long-term sponsor and participant confidence.

### Core Purpose
This layer defines how Defense operates at two complementary scales: lightweight, fast local execution during individual runs and deep, coordinated global analysis that benefits the entire network.

### Detailed Local vs Global Model

**Global Defense (Centralized, sage-intelligence)**  
- Runs the full Adversarial Hardening Engine on aggregated network data.  
- Maintains the authoritative RedTeamVault.  
- Generates and distributes versioned hardening packages and fixes.  
- Performs deep, long-horizon learning via Meta-RL.

**Local Defense (During EM Runs)**  
- Uses the latest global hardening package for fast, targeted red-teaming at key checkpoints.  
- High-contribution miners can enable deeper local passes.  
- Discovered issues and new attack vectors are securely pushed back to global feed vaults.

**Coordination & Synchronization**  
- Global packages are automatically pulled by the Operations Layer on swarm start.  
- Local discoveries are batched and uploaded via secure, provenance-logged channels.  
- Versioning ensures local instances never use outdated defenses.

### Concrete Example
**During a Quantum Stabilizer Swarm**  
Local Defense detects a subtle verifier ordering attack and blocks it immediately.  
The vector is securely uploaded to global feed vaults.  
Global AHE validates a fix overnight and pushes an updated hardening package.  
All subsequent swarms automatically use the strengthened verifier, preventing recurrence.

### Why This Hybrid Model Is Critical
- Combines instant local protection with comprehensive global learning.  
- Scales effectively for both solo miners and large deployments.  
- Creates a true compounding hardening flywheel where local discoveries strengthen the entire network.  
- Unlike purely centralized or purely local systems, it delivers both responsiveness and depth — essential for Economic integrity and long-term trust.

**All supporting architecture is covered in [Main Defense Subsystem Overview](../defense/Main-Defense-Overview.md).**

**Economic Impact at a Glance**  
- Target: 70–85% reduction in successful gaming vectors with minimal runtime overhead  
- Success Milestone (60 days): ≥ 80% of local discoveries successfully incorporated into global hardening within 24 hours

---

### Reference: Key Decision Formulas

**1. Local vs Global Routing Score**  
`Routing Score = 0.40 × Urgency + 0.30 × Computational Cost + 0.20 × Expected Global Value + 0.10 × Novelty`  
**Optimizes**: Decides whether an attack/finding should be handled locally (fast) or escalated globally (deep).  
**Meta-RL Tuning**: Weights refined based on actual impact on system-wide gaming resistance.

**2. Defense Synchronization Score**  
`Sync Score = 0.35 × Package Freshness + 0.30 × Local Discovery Rate + 0.20 × Global Fix Coverage + 0.15 × Propagation Latency`  
**Optimizes**: Measures how well local and global layers stay aligned.  
**Meta-RL Tuning**: Used to improve package distribution frequency and 

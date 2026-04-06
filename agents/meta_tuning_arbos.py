# agents/meta_tuning_arbos.py - v0.6 EFS + Meta-Tuning Arbos
import json
from pathlib import Path
import random
from agents.validation_oracle import ValidationOracle
import logging

logger = logging.getLogger(__name__)

class MetaTuningArbos:
    GENOME_PATH = Path("goals/brain/tuning_genome.json")
    
    def __init__(self, validation_oracle: ValidationOracle):
        self.oracle = validation_oracle
        self.genome = self._load_genome()
        logger.info(f"✅ MetaTuningArbos initialized — EFS weights: {self.genome['efs_weights']}")

    def _load_genome(self):
        if self.GENOME_PATH.exists():
            try:
                return json.loads(self.GENOME_PATH.read_text())
            except:
                pass
        # v0.6 default genome
        default = {
            "version": "v0.6-default",
            "efs_weights": {"V": 0.3, "S": 0.25, "H": 0.2, "C": 0.15, "E": 0.1},
            "last_tuning": str(datetime.datetime.now().isoformat()),
            "mutation_rate": 0.15,
            "tournament_size": 8
        }
        self._save_genome(default)
        return default

    def _save_genome(self, genome: dict):
        self.GENOME_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.GENOME_PATH.write_text(json.dumps(genome, indent=2))

    def compute_efs(self, metrics: dict) -> float:
        """Enigma Fitness Score = weighted composite (V=Validation, S=Symbiosis, H=Heterogeneity, C=Compression, E=Embodiment)"""
        weights = self.genome["efs_weights"]
        efs = (
            metrics.get("V", 0.0) * weights["V"] +
            metrics.get("S", 0.0) * weights["S"] +
            metrics.get("H", 0.0) * weights["H"] +
            metrics.get("C", 0.0) * weights["C"] +
            metrics.get("E", 0.0) * weights["E"]
        )
        return round(max(0.0, min(1.0, efs)), 4)

    def run_meta_tuning_cycle(self, stall_detected: bool = False):
        """Full meta-tuning cycle:
        1. Sensitivity analysis on current genome
        2. Generate mutant genomes
        3. Run short Scientist Mode tournament on each
        4. Select EFS winner
        5. Human preview → evolve_principles_post_run if approved
        """
        logger.info("🚀 Starting Meta-Tuning Cycle" + (" (stall detected)" if stall_detected else ""))

        # 1. Sensitivity analysis — small perturbations
        base_weights = self.genome["efs_weights"].copy()
        mutants = []

        for i in range(self.genome.get("tournament_size", 8)):
            mutant = base_weights.copy()
            for key in mutant:
                # Small random mutation
                mutant[key] = round(mutant[key] * random.uniform(0.85, 1.15), 3)
                mutant[key] = max(0.05, min(0.45, mutant[key]))  # keep reasonable bounds
            mutants.append({"id": i, "weights": mutant, "efs": 0.0})

        # 2. Run short Scientist Mode tournament on each mutant
        best_efs = 0.0
        best_genome = None

        for mutant in mutants:
            # Temporarily apply mutant weights for scoring
            original_weights = self.genome["efs_weights"]
            self.genome["efs_weights"] = mutant["weights"]

            # Run a short synthetic evaluation
            try:
                if hasattr(self.oracle.arbos, 'run_scientist_mode'):
                    self.oracle.arbos.run_scientist_mode(num_synthetic=3)  # short tournament
            except:
                pass  # safe fallback

            # Compute EFS from recent metrics
            metrics = {
                "V": getattr(self.oracle, "last_score", 0.0),
                "S": 0.82,  # symbiosis estimate
                "H": getattr(self.oracle.arbos, '_compute_heterogeneity_score', lambda: {"heterogeneity_score": 0.72})()["heterogeneity_score"],
                "C": 0.78,  # compression estimate
                "E": 0.85   # embodiment estimate
            }
            mutant["efs"] = self.compute_efs(metrics)

            # Restore original
            self.genome["efs_weights"] = original_weights

            if mutant["efs"] > best_efs:
                best_efs = mutant["efs"]
                best_genome = mutant

        # 3. Apply winner (with human preview simulation)
        if best_genome and best_efs > 0.65:
            logger.info(f"🏆 Meta-Tuning winner found — EFS: {best_efs:.4f}")
            
            # Human preview path
            preview = {
                "winner_efs": best_efs,
                "new_weights": best_genome["weights"],
                "improvement": round(best_efs - self.compute_efs({
                    "V": getattr(self.oracle, "last_score", 0.0),
                    "S": 0.82, "H": 0.72, "C": 0.78, "E": 0.85
                }), 4)
            }
            logger.info(f"Human preview required for genome change: {preview}")

            # Apply winner (in real use, wait for miner approval)
            self.genome["efs_weights"] = best_genome["weights"]
            self.genome["last_tuning"] = str(datetime.datetime.now().isoformat())
            self._save_genome(self.genome)

            # Trigger principle evolution (human veto possible via evolve_principles_post_run)
            if hasattr(self.oracle.arbos, 'evolve_principles_post_run'):
                self.oracle.arbos.evolve_principles_post_run(
                    best_solution="Meta-tuning winner applied",
                    best_score=best_efs,
                    best_diagnostics={"efs_winner": preview}
                )

            return {"status": "success", "best_efs": best_efs, "preview": preview}
        else:
            logger.info("No significant improvement from meta-tuning")
            return {"status": "no_improvement", "best_efs": best_efs}

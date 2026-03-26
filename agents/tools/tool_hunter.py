# agents/tools/tool_hunter.py
# Dynamic Tool Discovery + Safe Integration with Miner Escalation

import os
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List

from agents.memory import memory
from agents.tools.compute import ComputeRouter
from agents.tools.resource_aware import ResourceMonitor


class ToolHunter:
    def __init__(self):
        self.compute = ComputeRouter()
        self.temp_dir = Path(tempfile.gettempdir()) / "toolhunter_cache"
        self.temp_dir.mkdir(exist_ok=True)
        print("🔍 ToolHunter initialized with miner escalation on integration failure")

    def hunt_and_integrate(self, gap_description: str, subtask: str, challenge_context: str = "") -> Dict[str, Any]:
        monitor = ResourceMonitor(max_hours=0.5)

        # ... (search query generation and candidate suggestion steps remain the same as before)

        # Step 3: Decision (same as before)
        decision_task = f"""... [same decision prompt as previous version]"""
        decision = self.compute.run_on_compute(decision_task)
        result = self._parse_json(decision)

        if result.get("chosen_tool") in [None, "none"] or result.get("confidence", 0) < 5:
            return self._create_skip_result(result.get("reason", "Low confidence or no tool"))

        # Step 4: Safe integration attempt with escalation
        integration_attempt = self._attempt_safe_install(result, gap_description, subtask)

        if integration_attempt["success"]:
            memory.add(...)  # same as before
            return {
                "status": "success",
                "tool_name": result["chosen_tool"],
                "integration_code": result.get("integration_code"),
                "patch": result.get("patch"),
                "test_result": integration_attempt["test_output"],
                "miner_action": None
            }
        else:
            # ESCALATION: Recommend manual miner action
            recommendation = self._generate_miner_recommendation(
                result, integration_attempt, gap_description, subtask
            )
            return {
                "status": "manual_required",
                "tool_name": result.get("chosen_tool"),
                "integration_code": result.get("integration_code"),  # partial
                "patch": result.get("patch"),
                "failure_reason": integration_attempt["test_output"],
                "miner_recommendation": recommendation,
                "confidence": result.get("confidence", 5)
            }

    def _generate_miner_recommendation(self, decision: Dict, attempt: Dict, gap: str, subtask: str) -> str:
        """Generate clear, copy-pasteable instructions for the miner."""
        tool = decision.get("chosen_tool", "Unknown tool")
        reason = attempt.get("test_output", "Unknown failure")

        rec = f"""🔧 TOOLHUNTER ESCALATION - Manual Action Recommended

Gap: {gap}
Subtask: {subtask}
Promising Tool: {tool}

Why automated attempt failed: {reason[:300]}

Recommended Manual Steps (run in your miner environment):
1. git clone {tool}   # or pip install if it's a package
2. cd <tool_dir>
3. pip install -e . --no-deps   # or follow the repo's install instructions
4. Test import: python -c "import {tool.split('/')[-1].replace('-','_') or 'module_name'}; print('Success')"

Integration Stub (add to your code or sub-Arbos wrapper):
{decision.get('integration_code', '# Paste the suggested wrapper here')}

Potential Fixes to Try:
- Check CUDA / GPU driver compatibility
- Use --no-deps or install missing system libs (e.g., apt install ...)
- Test in a fresh venv
- Quantum Rings specific: ensure simulator hooks are compatible

Add this tool to long-term memory once working. 
Re-run the challenge after manual integration if it significantly boosts novelty/verifier score."""

        return rec

    # ... (keep _extract_queries, _parse_json, and update _attempt_safe_install to return more detailed failure info)

    def _attempt_safe_install(self, decision: Dict, gap: str, subtask: str) -> Dict[str, Any]:
        # Enhanced with better error capture
        # ... (same logic, but capture more detailed stderr/stdout)
        # On any exception or non-zero return: return {"success": False, "test_output": detailed_error}
        pass  # implement as before but richer logging

# Singleton
tool_hunter = ToolHunter()

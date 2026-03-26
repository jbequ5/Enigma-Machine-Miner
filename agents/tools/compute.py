# agents/tools/compute.py
# ComputeRouter - Smart default to Chutes when no local GPU

import torch
import os
from typing import Any

class ComputeRouter:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.local_compute = self.config.get("local_compute", False)
        self.chutes_enabled = self.config.get("chutes", True)
        
        self.use_local = self._has_local_gpu() and self.local_compute
        
        if self.use_local:
            print("✅ Using LOCAL compute (vLLM)")
        else:
            print("🔄 No local GPU or local_compute=false → Defaulting to Chutes")

    def _has_local_gpu(self):
        try:
            if torch.cuda.is_available():
                print(f"Local GPU detected: {torch.cuda.get_device_name(0)}")
                return True
        except:
            pass
        return False

    def run_on_compute(self, task: str, temperature: float = 0.0) -> str:
        if self.use_local:
            try:
                from agents.arbos_manager import get_vllm_llm
                llm = get_vllm_llm()
                if llm:
                    # Local inference (expand as needed)
                    response = llm.generate(task, max_tokens=2048, temperature=temperature)
                    return response[0].text if hasattr(response[0], 'text') else str(response)
            except Exception as e:
                print(f"Local compute failed: {e}. Falling back to Chutes.")

        # Default / fallback: Chutes
        if self.chutes_enabled:
            print(f"🔄 Routing to Chutes | Task length: {len(task)} chars")
            return self._run_on_chutes(task, temperature)
        else:
            print("⚠️ Chutes disabled and no local compute. Returning placeholder.")
            return "[NO COMPUTE AVAILABLE]"

    def _run_on_chutes(self, task: str, temperature: float = 0.0) -> str:
        """Placeholder for real Chutes integration."""
        # TODO: Add real Chutes SDK call here when you have API keys / hotkey
        # For now it returns a realistic placeholder so the flow works
        return f"[Chutes External Compute]\nTask processed on decentralized GPU.\nTemperature: {temperature}\n(This is a placeholder until full Chutes SDK integration.)"

    # Call this later when you have Chutes credentials
    def set_chutes_credentials(self, hotkey_path: str = None):
        print("Chutes credentials would be set here (hotkey, subtensor, etc.)")

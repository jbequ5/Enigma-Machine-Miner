# agents/tools/compute.py
# ComputeRouter with LLM Router - selects model based on task importance and novelty

import torch
import requests
import time
from typing import Any, Dict

class LLMRouter:
    def __init__(self):
        self.model_preferences = {
            "planning": "best",          # high-level strategy needs strongest model
            "orchestration": "best",
            "subtask": "fast",           # routine sub-tasks can use smaller models
            "synthesis": "best",
            "verification": "fast",
            "toolhunter": "fast"
        }

    def choose_model(self, task_type: str, novelty_level: str = "medium", miner_preference: str = None) -> str:
        """Decide which model to use for this task."""
        if miner_preference:
            return miner_preference

        if novelty_level == "high" or task_type in ["planning", "orchestration", "synthesis"]:
            return "best"   # Claude-3.5, Grok, or largest available fine-tune

        return self.model_preferences.get(task_type, "fast")

class ComputeRouter:
    def __init__(self):
        self.compute_source = None
        self.custom_endpoint = None
        self.use_local = False
        self.llm_router = LLMRouter()
        self.max_retries = 3

    def set_compute_source(self, source: str, endpoint: str = None):
        self.compute_source = source
        self.custom_endpoint = endpoint

        if source == "local":
            self.use_local = torch.cuda.is_available()
            if self.use_local:
                print(f"✅ Using LOCAL GPU: {torch.cuda.get_device_name(0)}")
            else:
                print("⚠️ Local GPU selected but none detected.")
        else:
            self.use_local = False
            if endpoint:
                print(f"✅ Using external compute ({source}) → Endpoint: {endpoint}")
            else:
                print(f"✅ {source} selected — endpoint needed.")

    def run_on_compute(self, task: str, temperature: float = 0.0, task_type: str = "subtask", 
                       novelty_level: str = "medium", miner_preferred_model: str = None) -> str:
        """Main entry point. Now includes smart model selection."""

        preferred_model = self.llm_router.choose_model(task_type, novelty_level, miner_preferred_model)

        if self.use_local:
            try:
                from agents.arbos_manager import get_vllm_llm
                llm = get_vllm_llm()
                if llm:
                    print(f"Using local vLLM model for {task_type} (preferred: {preferred_model})")
                    response = llm.generate(task, max_tokens=2048, temperature=temperature)
                    return response[0].text if hasattr(response[0], 'text') else str(response)
            except Exception as e:
                print(f"Local compute failed: {e}. Falling back.")

        # External compute (Chutes, Already running, Custom)
        if self.custom_endpoint and self.custom_endpoint != "pre_configured":
            print(f"🔄 Routing to external endpoint for {task_type} (preferred model: {preferred_model})")
            return self._call_external_endpoint(task, temperature, preferred_model)

        return f"[COMPUTE NOT CONFIGURED]\nSource: {self.compute_source}\nTask type: {task_type}"

    def _call_external_endpoint(self, task: str, temperature: float = 0.0, preferred_model: str = None) -> str:
        """Real call to any external endpoint (Chutes, custom, already-running)."""
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "task": task,
                    "temperature": temperature,
                    "max_tokens": 2048,
                    "preferred_model": preferred_model   # ← This is the key new field
                }
                response = requests.post(
                    self.custom_endpoint,
                    json=payload,
                    timeout=180,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", data.get("text", str(data)))

            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    return "[Timeout] External endpoint did not respond in time."
                time.sleep(2 ** attempt)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return f"[Endpoint Error] {str(e)}"
                time.sleep(2 ** attempt)

        return "[External Compute Failed] All retries exhausted."

    def get_status(self):
        if self.use_local:
            return f"Local GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}"
        elif self.custom_endpoint:
            return f"Using external endpoint: {self.custom_endpoint}"
        else:
            return "Compute source not configured"

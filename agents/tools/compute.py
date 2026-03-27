# agents/tools/compute.py
# ComputeRouter - Real integration ready for Chutes + other endpoints

import torch
import requests
import time
from typing import Any

class ComputeRouter:
    def __init__(self):
        self.compute_source = None
        self.custom_endpoint = None
        self.use_local = False
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
                print(f"✅ {source} selected — waiting for endpoint...")

    def run_on_compute(self, task: str, temperature: float = 0.0) -> str:
        """Main entry point for all LLM/compute tasks."""

        if self.use_local:
            try:
                from agents.arbos_manager import get_vllm_llm
                llm = get_vllm_llm()
                if llm:
                    response = llm.generate(task, max_tokens=2048, temperature=temperature)
                    return response[0].text if hasattr(response[0], 'text') else str(response)
            except Exception as e:
                print(f"Local compute failed: {e}. Falling back to external.")

        # External compute (Chutes, Already running, Custom)
        if self.custom_endpoint and self.custom_endpoint != "pre_configured":
            print(f"🔄 Sending task to external endpoint: {self.custom_endpoint}")
            return self._call_external_endpoint(task, temperature)

        # No endpoint configured yet
        return f"[COMPUTE NOT CONFIGURED]\n" \
               f"Source: {self.compute_source}\n" \
               f"Please provide a valid endpoint in the Compute Setup screen."

    def _call_external_endpoint(self, task: str, temperature: float = 0.0) -> str:
        """Real HTTP call to Chutes or any custom endpoint."""
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "task": task,
                    "temperature": temperature,
                    "max_tokens": 2048
                }
                response = requests.post(
                    self.custom_endpoint,
                    json=payload,
                    timeout=180,           # 3 minutes timeout
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", data.get("text", str(data)))

            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    return "[Timeout] External endpoint did not respond in time."
                time.sleep(2 ** attempt)  # exponential backoff

            except Exception as e:
                if attempt == self.max_retries - 1:
                    return f"[Endpoint Error] {str(e)}\nMake sure your Chutes endpoint is running and accepts POST requests."
                time.sleep(2 ** attempt)

        return "[External Compute Failed] All retries exhausted."

    def get_status(self):
        if self.use_local:
            return f"Local GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}"
        elif self.custom_endpoint:
            return f"Using external endpoint: {self.custom_endpoint}"
        else:
            return "Compute source not configured"

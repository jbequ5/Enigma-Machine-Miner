# agents/tools/compute.py
# ComputeRouter - Fully supports all compute types chosen in setup screen

import torch
import requests
from typing import Any

class ComputeRouter:
    def __init__(self):
        self.compute_source = None
        self.custom_endpoint = None
        self.use_local = False

    def set_compute_source(self, source: str, endpoint: str = None):
        """Called from Streamlit after miner selects compute source."""
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
                print(f"✅ Using external compute ({source}) with endpoint: {endpoint}")
            else:
                print(f"✅ {source} selected — endpoint needed for live compute.")

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
                print(f"Local compute failed: {e}. Falling back.")

        # Use external endpoint (Chutes, Already running, Custom)
        if self.custom_endpoint and self.custom_endpoint != "pre_configured":
            print(f"🔄 Routing to external endpoint: {self.custom_endpoint}")
            return self._call_external_endpoint(task, temperature)

        # No endpoint provided yet
        return f"[External Compute Placeholder]\n" \
               f"Source: {self.compute_source}\n" \
               f"Task would be sent to your configured endpoint.\n" \
               f"(Please provide a valid endpoint in Compute Setup for live compute.)"

    def _call_external_endpoint(self, task: str, temperature: float = 0.0) -> str:
        """Call the user-provided endpoint."""
        try:
            payload = {
                "task": task,
                "temperature": temperature,
                "max_tokens": 2048
            }
            response = requests.post(
                self.custom_endpoint,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", data.get("text", str(data)))
        except Exception as e:
            return f"[Endpoint Error] Could not reach {self.custom_endpoint}\nError: {str(e)}\n\n" \
                   f"Make sure your endpoint is running and accepts POST requests."

    def get_status(self):
        if self.use_local:
            return f"Local GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}"
        elif self.custom_endpoint:
            return f"Using external endpoint: {self.custom_endpoint}"
        else:
            return "Compute source not configured"

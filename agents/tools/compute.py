# agents/tools/compute.py
# Final version with proactive remote VRAM check + Deep Quasar Attention routing

import torch
import requests
import time
from typing import Any, Dict
import numpy as np
from validation_oracle import ValidationOracle
from trajectories.trajectory_vector_db import vector_db
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def compute_energy(candidate: Dict, validator, rank: int = 8) -> float:
    """Simple but functional energy function used by EGGROLL ranking."""
    base = 1.0
    novelty = candidate.get("novelty_proxy", 0.5)
    score = validator.last_score if hasattr(validator, "last_score") else 0.85
    energy = base + (novelty * 0.4) + (score * 0.6) - (rank * 0.01)
    return max(0.1, energy)
    
class LLMRouter:
    def __init__(self):
        self.model_preferences = {
            "planning": "best", "orchestration": "best", "subtask": "fast",
            "synthesis": "best", "verification": "fast", "toolhunter": "fast"
        }

    def choose_model(self, task_type: str, novelty_level: str = "medium", miner_preference: str = None) -> str:
        if miner_preference:
            return miner_preference
        if novelty_level == "high" or task_type in ["planning", "orchestration", "synthesis"]:
            return "best"
        return self.model_preferences.get(task_type, "fast")

class ComputeRouter:
    def __init__(self):
        self.compute_source = None
        self.custom_endpoint = None
        self.use_local = False
        self.llm_router = LLMRouter()
        self.max_retries = 3
        self.quasar_enabled = False
        self.quasar_llm = None  # Lazy load for Quasar models

    def set_compute_source(self, source: str, endpoint: str = None):
        self.compute_source = source
        self.custom_endpoint = endpoint
        if source == "local":
            self.use_local = torch.cuda.is_available()
        else:
            self.use_local = False

    def enable_quasar(self, enabled: bool = True):
        """Enable deep Quasar Attention routing for long-context critical phases."""
        self.quasar_enabled = enabled
        logger.info(f"Quasar Attention routing {'ENABLED' if enabled else 'DISABLED'}")

    def run_on_compute(self, task: str, temperature: float = 0.0, task_type: str = "subtask", 
                       novelty_level: str = "medium", miner_preferred_model: str = None) -> str:
        preferred_model = self.llm_router.choose_model(task_type, novelty_level, miner_preferred_model)

        # ==================== DEEP QUASAR ROUTING ====================
        if self.quasar_enabled and task_type in ["planning", "orchestration", "adaptation", "re_adapt"]:
            try:
                if self.quasar_llm is None:
                    from vllm import LLM
                    # Use Quasar-10B (or larger if available)
                    model_name = "silx-ai/Quasar-10B"
                    self.quasar_llm = LLM(
                        model=model_name,
                        trust_remote_code=True,
                        gpu_memory_utilization=0.88,
                        max_model_len=32768,   # Quasar handles much larger effectively
                        dtype="float16"
                    )
                    logger.info(f"✅ Quasar Attention model loaded: {model_name}")
                
                from vllm import SamplingParams
                sampling = SamplingParams(temperature=temperature, max_tokens=4096)
                outputs = self.quasar_llm.generate(task, sampling)
                return outputs[0].outputs[0].text.strip()
            except Exception as e:
                logger.warning(f"Quasar routing failed, falling back: {e}")
                # Fall through to normal routing

        # ==================== ORIGINAL LOCAL vLLM PATH ====================
        if self.use_local:
            try:
                from agents.arbos_manager import get_vllm_llm
                llm = get_vllm_llm()
                if llm:
                    response = llm.generate(task, max_tokens=2048, temperature=temperature)
                    return response[0].text if hasattr(response[0], 'text') else str(response)
            except Exception as e:
                logger.warning(f"Local vLLM failed: {e}")

        # ==================== EXTERNAL / CHUTES PATH ====================
        if self.custom_endpoint:
            if miner_preferred_model and not self.use_local:
                quantized = self._try_quantized_version(miner_preferred_model)
                if quantized != miner_preferred_model:
                    print(f"⚡ Using quantized version: {quantized} for hosted compute")
                    preferred_model = quantized
            return self._call_external_endpoint(task, temperature, preferred_model)

        return "[COMPUTE NOT CONFIGURED — Check Chutes / Local setup]"

    def _try_quantized_version(self, model_name: str) -> str:
        quantized_map = {
            "Llama-3-70B": "TheBloke/Llama-3-70B-Instruct-GPTQ-4bit",
            "Llama-3-8B": "TheBloke/Llama-3-8B-Instruct-GPTQ-4bit",
            "Mixtral-8x22B": "TheBloke/Mixtral-8x22B-Instruct-v0.1-GPTQ",
            "Qwen2-72B": "Qwen/Qwen2-72B-Instruct-GPTQ-4bit"
        }
        for key, q_version in quantized_map.items():
            if key.lower() in model_name.lower():
                return q_version
        return model_name

    def _call_external_endpoint(self, task: str, temperature: float = 0.0, preferred_model: str = None) -> str:
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "task": task,
                    "temperature": temperature,
                    "max_tokens": 2048,
                    "preferred_model": preferred_model
                }
                response = requests.post(self.custom_endpoint, json=payload, timeout=180)
                response.raise_for_status()
                data = response.json()
                return data.get("response", str(data))
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return f"[Endpoint Error] {str(e)}"
                time.sleep(2 ** attempt)
        return "[External Compute Failed]"

    def get_status(self):
        """Proactive remote VRAM check (if endpoint supports it)"""
        try:
            if self.custom_endpoint:
                r = requests.get(self.custom_endpoint + "/status", timeout=5)
                if r.status_code == 200:
                    return r.json().get("vram_info", f"Source: {self.compute_source}")
        except:
            pass
        return f"Source: {self.compute_source} | Model routing active | Quasar: {'ON' if self.quasar_enabled else 'OFF'}"

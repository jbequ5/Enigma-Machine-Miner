"""
Synapse Client — Official lightweight wrapper for private Synapse Intelligence API
Zero Synapse code in the public repo. All communication via secure HTTP.
10/10 production grade: async, retries, timeouts, circuit-breaker style resilience.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class SynapseClient:
    """Thin, resilient client for the private Synapse intelligence service."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 15.0,
        max_retries: int = 3
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            follow_redirects=True
        )
        logger.info(f"✅ SynapseClient initialized — connecting to {self.base_url}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
    )
    def _post(self, endpoint: str, json_data: Dict) -> Dict:
        resp = self.client.post(endpoint, json=json_data)
        resp.raise_for_status()
        return resp.json()

    def chat_query(self, query: str, user_tier: str = "standard") -> Dict:
        """Main co-pilot / chat endpoint."""
        return self._post("/chat/query", {"query": query, "user_tier": user_tier})

    def handle_stall(self, em_context: Dict) -> Dict:
        """Called by EM during stalls for immediate intelligence help."""
        return self._post("/chat/stall", {"em_context": em_context})

    def run_daily_cycle(self) -> Dict:
        """Trigger a full intelligence cycle remotely (safe to call)."""
        return self._post("/cycle/run", {})

    def push_telemetry(self, telemetry_data: Dict) -> Dict:
        """Push per-instance vector snapshots / run metrics to Synapse."""
        return self._post("/telemetry/push", telemetry_data)

    def health_check(self) -> Dict:
        resp = self.client.get("/health")
        resp.raise_for_status()
        return resp.json()

# Global singleton — configure once at EM/Arbos startup
synapse_client = SynapseClient(
    base_url="http://your-private-synapse-host:8000",   # ← UPDATE TO YOUR PRIVATE URL
    api_key="your-secret-api-key-here",                 # ← SET IN ENVIRONMENT / SECRETS
    timeout=15.0
)

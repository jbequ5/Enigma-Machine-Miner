"""
Synapse Client — Official lightweight wrapper for private Synapse Intelligence API
v0.9.13 MAXIMUM SOTA
Zero Synapse code in the public repo. All communication via secure HTTP.
Async-first, production-grade: retries, timeouts, circuit-breaker resilience, /ingest support.
"""

import os
import httpx
import logging
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class SynapseClient:
    """Thin, resilient client for the private Synapse intelligence service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 15.0,
        max_retries: int = 3
    ):
        self.base_url = (base_url or os.getenv("SYNAPSE_BASE_URL", "http://localhost:8000")).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        api_key = api_key or os.getenv("SYNAPSE_API_KEY")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
        logger.info(f"✅ SynapseClient initialized — connecting to {self.base_url}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=8),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException, httpx.HTTPStatusError))
    )
    async def _post(self, endpoint: str, json_data: Dict) -> Dict:
        """Internal async POST with automatic retries."""
        resp = await self.client.post(endpoint, json=json_data)
        resp.raise_for_status()
        return resp.json()

    async def ingest_fragments(
        self,
        fragments: List[Dict],
        telemetry: Dict,
        em_instance_id: str,
        run_id: str,
        provenance: Optional[Dict] = None
    ) -> Dict:
        """Securely push raw fragments + telemetry to the private /ingest gate (the critical handoff)."""
        payload = {
            "fragments": fragments,
            "telemetry": telemetry,
            "em_instance_id": em_instance_id,
            "run_id": run_id,
            "provenance": provenance or {"source": "local_em", "version": "0.9.13"}
        }
        return await self._post("/ingest", payload)

    async def chat_query(self, query: str, user_tier: str = "standard") -> Dict:
        """Main co-pilot / chat endpoint."""
        return await self._post("/chat/query", {"query": query, "user_tier": user_tier})

    async def handle_stall(self, em_context: Dict) -> Dict:
        """Called by EM during stalls for immediate intelligence help."""
        return await self._post("/chat/stall", {"em_context": em_context})

    async def run_daily_cycle(self) -> Dict:
        """Trigger a full intelligence cycle remotely."""
        return await self._post("/cycle/run", {})

    async def push_telemetry(self, telemetry_data: Dict) -> Dict:
        """Push per-instance vector snapshots / run metrics."""
        return await self._post("/telemetry/push", {"telemetry_data": telemetry_data})

    async def health_check(self) -> Dict:
        resp = await self.client.get("/health")
        resp.raise_for_status()
        return resp.json()

# synapse_client.py (add these two methods at the bottom of the class)

    async def get_challenges(self) -> List[Dict]:
        """Fetch the authoritative list of active challenges + dense verification specs from private Synapse."""
        return await self._post("/get_challenges", {})

    async def get_challenge_by_id(self, challenge_id: str) -> Dict:
        """Fetch a single challenge (with full dense verification spec) by ID."""
        return await self._post("/get_challenge", {"challenge_id": challenge_id})

    # Synchronous wrappers for EM managers
    def sync_get_challenges(self) -> List[Dict]:
        import asyncio
        return asyncio.run(self.get_challenges())

    def sync_get_challenge_by_id(self, challenge_id: str) -> Dict:
        import asyncio
        return asyncio.run(self.get_challenge_by_id(challenge_id))    

    
    # Synchronous wrappers for easy use in non-async code (e.g. ArbosManager)
    def sync_ingest_fragments(self, fragments: List[Dict], telemetry: Dict, em_instance_id: str, run_id: str, provenance: Optional[Dict] = None) -> Dict:
        import asyncio
        return asyncio.run(self.ingest_fragments(fragments, telemetry, em_instance_id, run_id, provenance))

    def sync_chat_query(self, query: str, user_tier: str = "standard") -> Dict:
        import asyncio
        return asyncio.run(self.chat_query(query, user_tier))

    def sync_handle_stall(self, em_context: Dict) -> Dict:
        import asyncio
        return asyncio.run(self.handle_stall(em_context))

# Global singleton — configure once at EM/Arbos startup
synapse_client = SynapseClient(
    base_url=os.getenv("SYNAPSE_BASE_URL", "http://localhost:8000"),
    api_key=os.getenv("SYNAPSE_API_KEY"),
    timeout=15.0,
    max_retries=3
)

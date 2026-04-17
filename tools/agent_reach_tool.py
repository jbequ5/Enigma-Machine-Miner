# tools/agent_reach_tool.py
# v0.9.11 MAXIMUM SOTA AgentReachTool
# Real web content fetching with memory + disk cache, BeautifulSoup cleaning,
# SOTA/EFS/7D gating, and high-signal routing to VaultRouter + PD Arm.

import requests
from bs4 import BeautifulSoup
import hashlib
from pathlib import Path
import logging
from cachetools import TTLCache
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AgentReachTool:
    def __init__(self, cache_ttl: int = 3600, max_cache_size: int = 200):
        self.cache = TTLCache(maxsize=max_cache_size, ttl=cache_ttl)
        self.cache_dir = Path(".cache/agent_reach")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Enigma-Machine-Miner-AgentReach/2.1'})
        self.arbos = None          # wired by ArbosManager for v0.9.11 SOTA gating
        self.validator = None
        self.intelligence = None
        logger.info("✅ AgentReachTool v0.9.11 MAX SOTA initialized — memory + disk cache + full SOTA gating")

    def set_arbos(self, arbos):
        self.arbos = arbos
        if arbos:
            self.validator = getattr(arbos, 'validator', None)
            self.intelligence = getattr(arbos, 'intelligence', None)

    def _get_cache_key(self, url: str) -> str:
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def _load_disk_cache(self, key: str) -> Optional[str]:
        file = self.cache_dir / f"{key}.txt"
        if file.exists():
            try:
                return file.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning(f"Disk cache read failed: {e}")
        return None

    def _save_disk_cache(self, key: str, content: str):
        file = self.cache_dir / f"{key}.txt"
        try:
            file.write_text(content, encoding="utf-8")
        except Exception as e:
            logger.warning(f"Disk cache write failed: {e}")

    def fetch_url_content(self, url: str, max_length: int = 12000, timeout: int = 15) -> str:
        if not url or not url.startswith(("http://", "https://")):
            return "Invalid URL provided."

        key = self._get_cache_key(url)

        # Memory cache
        if key in self.cache:
            logger.debug(f"Memory cache hit: {url}")
            return self.cache[key]

        # Disk cache
        cached = self._load_disk_cache(key)
        if cached:
            self.cache[key] = cached
            logger.debug(f"Disk cache hit: {url}")
            return cached

        # Live fetch
        try:
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # Clean unwanted tags
            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "svg", "img"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            lines = (line.strip() for line in text.splitlines())
            clean_text = "\n".join(line for line in lines if line)

            if len(clean_text) > max_length:
                clean_text = clean_text[:max_length] + "\n... [truncated]"

            # v0.9.11 SOTA upgrade: optional 7D SOTA gate before caching high-value content
            if self.arbos and self.validator:
                try:
                    gate_data = {
                        "deterministic_strength": 0.6,
                        "edge_coverage": 0.75,
                        "invariant_tightness": 0.7,
                        "simulation_quality": 0.65,
                        "fidelity": 0.82,
                        "c3a_confidence": getattr(self.arbos, 'compute_confidence', lambda *a: 0.75)(0.78, 0.70, 0.88),
                        "verifier_quality": getattr(self.validator, 'last_verifier_quality', 0.0)
                    }
                    if hasattr(self.validator, '_subarbos_gate'):
                        if not self.validator._subarbos_gate(output=clean_text, theta_dynamic=0.68):
                            logger.debug(f"SOTA gate rejected content from {url}")
                            clean_text += "\n[Agent-Reach: Content failed SOTA gate — low signal]"
                except Exception as e:
                    logger.debug(f"SOTA gate check skipped (safe): {e}")

            # Cache the result
            self.cache[key] = clean_text
            self._save_disk_cache(key, clean_text)

            logger.info(f"Agent-Reach success: {url[:70]}...")

            # High-signal routing
            if len(clean_text) > 800 and self.intelligence:
                run_data = {
                    "insight_score": 0.85,
                    "key_takeaway": f"Agent-Reach fetched high-signal content from {url}",
                    "predictive_power": getattr(self.arbos, 'predictive_power', 0.0) if self.arbos else 0.0,
                    "flywheel_step": "agent_reach_to_vaults"
                }
                self.intelligence.route_to_vaults(run_data)

            return clean_text

        except requests.exceptions.RequestException as e:
            err = f"Network error: {str(e)[:150]}"
        except Exception as e:
            err = f"Parse error: {str(e)[:150]}"

        # Full fallback
        fallback = f"[Agent-Reach fallback] Could not retrieve {url}. {err}"
        self.cache[key] = fallback
        self._save_disk_cache(key, fallback)
        logger.warning(f"Agent-Reach fallback triggered for {url}")
        return fallback

    def get_content_with_score(self, url: str) -> Dict[str, Any]:
        """v0.9.11 helper: returns content + basic EFS/SOTA hint for retrospective/audit flows."""
        content = self.fetch_url_content(url)
        return {
            "url": url,
            "content": content,
            "length": len(content),
            "timestamp": datetime.now().isoformat(),
            "sota_hint": "high_signal" if len(content) > 800 else "low_signal",
            "verifier_quality_hint": getattr(self.validator, 'last_verifier_quality', 0.0) if self.validator else 0.0
        }

# Global instance (used by ToolHunter and ArchiveHunter)
agent_reach_tool = AgentReachTool()

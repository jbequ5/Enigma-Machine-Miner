# goals/brain_loader.py — v1.0 Brain Loader (Lean/Rich + Caching)

import os
from typing import Optional
import functools
import logging

logger = logging.getLogger(__name__)

# Small cache for frequently accessed toggles
_toggle_cache = {}

def load_toggle(key: str, default: str = "lean") -> str:
    """Simple toggle parser from brain/toggles.md with light caching"""
    if key in _toggle_cache:
        return _toggle_cache[key]

    try:
        with open("goals/brain/toggles.md", "r", encoding="utf-8") as f:
            content = f.read()
        for line in content.splitlines():
            if line.strip().startswith(f"{key}:"):
                value = line.split(":", 1)[1].strip().strip('"\'')
                _toggle_cache[key] = value
                return value
        _toggle_cache[key] = default
        return default
    except Exception as e:
        logger.debug(f"Toggle load failed for {key}: {e}")
        _toggle_cache[key] = default
        return default

def prune_to_dense_lines(content: str, max_lines: int = 12) -> str:
    """Improved lean-mode pruner: keep header + core content, prioritize high-signal v1.0 terms"""
    lines = content.splitlines()
    if len(lines) <= max_lines:
        return content

    # Key terms that should be preserved in lean mode
    key_terms = [
        "core", "mandate", "rule", "principle", "evolution", "embodiment", 
        "meta-tuning", "retrospective", "SOTA", "EFS", "RPS", "PPS", 
        "heterogeneity", "symbiosis", "mycelial", "neurogenesis", "vagus"
    ]

    dense = []
    for line in lines[:max_lines]:
        dense.append(line)
        if any(term in line.lower() for term in key_terms):
            break  # stop early if we hit a high-signal line

    if len(dense) < max_lines:
        dense.extend(lines[len(dense):max_lines])

    return "\n".join(dense) + "\n... (lean mode — full content available in rich mode)"


@functools.lru_cache(maxsize=128)
def load_brain_component(component_path: str, depth: Optional[str] = None) -> str:
    """Lightweight, reusable brain loader with LRU caching and lean/rich support"""
    if depth is None:
        depth = load_toggle("brain_depth", "lean")

    full_path = f"goals/brain/{component_path}.md"
    if not os.path.exists(full_path):
        # Helpful fallback during brain evolution
        return f"# Missing brain component: {component_path}\n\nThis component will be created automatically on first high-signal run or meta-tuning cycle."

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Error loading brain component {component_path}: {e}")
        return f"# Error loading brain component {component_path}: {e}"

    if depth == "lean":
        content = prune_to_dense_lines(content)

    return content


def clear_brain_cache():
    """Clear caches after major brain updates (call from Streamlit after saving changes)"""
    load_brain_component.cache_clear()
    _toggle_cache.clear()
    logger.info("Brain loader caches cleared")

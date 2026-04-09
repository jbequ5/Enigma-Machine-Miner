# tools/tool_env_manager.py - v0.8+ ToolEnvManager
# Safe ephemeral/persistent venvs + dynamic registration (one-click add from Streamlit)

import subprocess
import venv
import json
import os
import shutil
import time
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ToolEnvManager:
    def __init__(self):
        self.base_path = Path("~/.enigma_tools").expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.envs_dir = Path("tools/envs")
        self.envs_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry_path = Path("tools/env_registry.json")
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict:
        if self.registry_path.exists():
            try:
                return json.loads(self.registry_path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Failed to load env registry: {e}")
        return {}

    def _save_registry(self):
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(json.dumps(self.registry, indent=2), encoding="utf-8")

    def create_or_get_env(self, tool_name: str, persistent: bool = True, 
                         requirements: List[str] = None, install_cmd: str = None) -> Dict[str, Any]:
        """Create or reuse a virtual environment for a tool.
        Returns dict with status and python executable path."""
        key = f"{tool_name}_{'persistent' if persistent else 'ephemeral'}"
        
        # Reuse if exists
        if key in self.registry:
            python_exe = Path(self.registry[key])
            if python_exe.exists():
                logger.info(f"Reusing existing environment for {tool_name}")
                return {"status": "success", "python_exe": str(python_exe), "reused": True}

        # Create new environment
        env_path = self.envs_dir / key
        logger.info(f"Creating new {'persistent' if persistent else 'ephemeral'} environment for {tool_name}")

        try:
            # Create venv
            venv.create(env_path, with_pip=True, clear=True)

            python_exe = env_path / ("bin/python" if os.name != "nt" else "Scripts/python.exe")

            # Install requirements
            if requirements:
                pip_cmd = [str(python_exe), "-m", "pip", "install", "--upgrade"] + requirements
                subprocess.run(pip_cmd, check=True, capture_output=True, text=True)
                logger.info(f"Installed requirements for {tool_name}: {requirements}")

            # Run custom install command if provided
            if install_cmd and install_cmd.strip():
                install_cmd_list = [str(python_exe), "-m", "pip", "install"] + install_cmd.strip().split()
                subprocess.run(install_cmd_list, check=True, capture_output=True, text=True)

            # Register
            self.registry[key] = str(python_exe)
            self._save_registry()

            return {
                "status": "success",
                "python_exe": str(python_exe),
                "reused": False,
                "env_path": str(env_path)
            }

        except Exception as e:
            logger.error(f"Failed to create environment for {tool_name}: {e}")
            return {"status": "error", "error": str(e), "tool_name": tool_name}

    def get_env_python(self, tool_name: str, persistent: bool = True) -> Optional[str]:
        """Convenience method: return python executable path or None on failure."""
        result = self.create_or_get_env(tool_name, persistent=persistent)
        return result.get("python_exe") if result.get("status") == "success" else None

    def cleanup_ephemeral(self, days_old: int = 2):
        """Clean old ephemeral environments."""
        for p in self.envs_dir.glob("*_ephemeral"):
            if p.is_dir():
                try:
                    age_days = (datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)).days
                    if age_days > days_old:
                        shutil.rmtree(p, ignore_errors=True)
                        logger.info(f"Cleaned old ephemeral env: {p}")
                except Exception as e:
                    logger.debug(f"Failed to clean {p}: {e}")

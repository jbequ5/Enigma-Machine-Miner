# tools/tool_env_manager.py - v0.8+ ToolEnvManager
# Safe ephemeral/persistent venvs + dynamic registration (one-click add)

import subprocess
import venv
import json
import os
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolEnvManager:
    def __init__(self):
        self.envs_dir = Path("tools/envs")
        self.envs_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = Path("tools/env_registry.json")
        self._load_registry()

    def _load_registry(self):
        if self.registry_path.exists():
            try:
                self.registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
            except:
                self.registry = {}
        else:
            self.registry = {}

    def _save_registry(self):
        self.registry_path.write_text(json.dumps(self.registry, indent=2), encoding="utf-8")

    def create_or_get_env(self, tool_name: str, persistent: bool = True, requirements: List[str] = None) -> str:
        """Create or retrieve a venv for the tool. Returns path to python executable."""
        key = f"{tool_name}_{'persistent' if persistent else 'ephemeral'}"
        
        if key in self.registry and Path(self.registry[key]).exists():
            logger.info(f"Reusing existing env for {tool_name}")
            return self.registry[key]

        env_path = self.envs_dir / key
        logger.info(f"Creating new {'persistent' if persistent else 'ephemeral'} env for {tool_name} → {env_path}")

        # Create venv
        venv.create(env_path, with_pip=True, clear=True)

        python_exe = env_path / "bin/python" if os.name != "nt" else env_path / "Scripts/python.exe"

        # Install requirements if provided
        if requirements:
            try:
                cmd = [str(python_exe), "-m", "pip", "install", "--upgrade"] + requirements
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                logger.info(f"Installed requirements for {tool_name}: {requirements}")
            except Exception as e:
                logger.warning(f"Failed to install requirements for {tool_name}: {e}")

        # Register
        self.registry[key] = str(python_exe)
        self._save_registry()

        return str(python_exe)

    def get_env_python(self, tool_name: str, persistent: bool = True) -> str:
        """Get python executable path for a tool (creates if missing)."""
        return self.create_or_get_env(tool_name, persistent=persistent)

    def cleanup_ephemeral(self):
        """Optional: clean old ephemeral envs"""
        for p in self.envs_dir.glob("*_ephemeral"):
            if p.is_dir():
                try:
                    # Simple age-based cleanup
                    if (datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)).days > 2:
                        shutil.rmtree(p, ignore_errors=True)
                except:
                    pass

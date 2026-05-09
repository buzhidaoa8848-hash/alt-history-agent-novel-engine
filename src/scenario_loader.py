"""
Scenario Loader

Loads and validates scenario data from YAML, JSON, or Python data files.
Inspired by mirofish-cli's WorkbenchSession + TaskManager pattern.

Supports:
- .yaml / .yml (requires PyYAML)
- .json (stdlib)
- .py (Python data module with SCENARIO_DATA dict)
"""

import json
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class ScenarioValidationError(Exception):
    """Raised when scenario file fails validation."""
    pass


class ScenarioLoader:
    """Loads and validates a scenario definition file."""

    REQUIRED_SCENARIO_KEYS = {"id", "title", "divergence_point", "setting", "agents", "simulation_rounds"}

    def __init__(self, path: str):
        self.path = Path(path)
        self.raw: Dict[str, Any] = {}
        self.data: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load and validate the scenario file."""
        if not self.path.exists():
            raise FileNotFoundError(f"Scenario file not found: {self.path}")

        suffix = self.path.suffix.lower()

        if suffix in ('.yaml', '.yml'):
            self.raw = self._load_yaml()
        elif suffix == '.json':
            self.raw = self._load_json()
        elif suffix == '.py':
            self.raw = self._load_py()
        else:
            raise ValueError(f"Unsupported file format: {suffix}. Use .yaml, .yml, .json, or .py")

        if not self.raw:
            raise ScenarioValidationError("Empty scenario file")

        # Extract scenario data (handle both top-level "scenario" key and flat)
        if "scenario" in self.raw:
            self.data = self.raw["scenario"]
        else:
            self.data = self.raw

        # Validate scenario structure
        missing_scenario = self.REQUIRED_SCENARIO_KEYS - set(self.data.keys())
        if missing_scenario:
            raise ScenarioValidationError(f"Missing scenario keys: {missing_scenario}")

        # Validate agents
        agents = self.data.get("agents", [])
        if len(agents) < 4:
            raise ScenarioValidationError(f"Need at least 4 agents, found {len(agents)}")

        # Validate simulation rounds
        rounds = self.data.get("simulation_rounds", [])
        if len(rounds) < 1:
            raise ScenarioValidationError("Need at least 1 simulation round")

        # Validate output config
        output = self.data.get("output", {})
        if "base_dir" not in output:
            raise ScenarioValidationError("Missing output.base_dir in scenario")

        return self.data

    def _load_yaml(self) -> dict:
        """Load YAML file."""
        try:
            import yaml
        except ImportError:
            print("PyYAML not installed. Trying JSON fallback...")
            json_path = self.path.with_suffix('.json')
            if json_path.exists():
                return self._load_json_at(json_path)
            py_path = self.path.with_suffix('.py')
            if py_path.exists():
                old_path = self.path
                self.path = py_path
                try:
                    return self._load_py()
                finally:
                    self.path = old_path
            raise ImportError("PyYAML is required. Install with: pip install pyyaml")

        with open(self.path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_json(self) -> dict:
        """Load JSON file."""
        return self._load_json_at(self.path)

    def _load_json_at(self, path: Path) -> dict:
        """Load JSON from a specific path."""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_py(self) -> dict:
        """Load Python data file with SCENARIO_DATA."""
        # Add parent directory to path for import
        parent = str(self.path.parent)
        if parent not in sys.path:
            sys.path.insert(0, parent)

        module_name = self.path.stem
        spec = importlib.util.spec_from_file_location(module_name, self.path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load Python module: {self.path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, 'SCENARIO_DATA'):
            raise ValueError(f"Python data file must define SCENARIO_DATA: {self.path}")

        return module.SCENARIO_DATA

    def get_agent_definitions(self) -> List[Dict[str, Any]]:
        """Get the list of agent definitions."""
        return self.data.get("agents", [])

    def get_simulation_rounds(self) -> List[Dict[str, Any]]:
        """Get the list of simulation rounds."""
        return self.data.get("simulation_rounds", [])

    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return self.data.get("output", {})

    def get_setting(self) -> Dict[str, Any]:
        """Get setting information."""
        return self.data.get("setting", {})

    def get_divergence_point(self) -> Dict[str, Any]:
        """Get divergence point information."""
        return self.data.get("divergence_point", {})

    def to_dict(self) -> Dict[str, Any]:
        """Convert full scenario to plain dict for JSON export."""
        return {
            "scenario_id": self.data.get("id", "unknown"),
            "title": self.data.get("title", "Untitled"),
            "description": self.data.get("description", ""),
            "divergence_point": self.get_divergence_point(),
            "setting": self.get_setting(),
            "agent_count": len(self.get_agent_definitions()),
            "round_count": len(self.get_simulation_rounds()),
            "agent_ids": [a.get("id", "unknown") for a in self.get_agent_definitions()],
        }


def load_scenario(path: str) -> ScenarioLoader:
    """Convenience function to load a scenario."""
    loader = ScenarioLoader(path)
    loader.load()
    return loader

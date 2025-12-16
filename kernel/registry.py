from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import yaml


# ---------------------------------------------------------------------------
# AgentSpec
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AgentSpec:
    """
    Immutable specification of an agent loaded from YAML.
    """

    agent_id: str
    role: str
    description: str
    prompt: str

    tools: List[str] = field(default_factory=list)
    limits: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# AgentRegistry
# ---------------------------------------------------------------------------

class AgentRegistry:
    """
    Loads and validates agent specifications from agents/*.yaml
    """

    def __init__(self, agents_dir: Path | None = None):
        self.agents_dir = agents_dir or Path("agents")

        if not self.agents_dir.exists():
            raise RuntimeError(f"Agents directory not found: {self.agents_dir}")

    # ---------------------------------------------------------------------

    def load(self, agent_id: str) -> AgentSpec:
        """
        Load agent specification by ID.
        """
        path = self._agent_path(agent_id)
        data = self._load_yaml(path)

        self._validate_schema(agent_id, data)

        return AgentSpec(
            agent_id=agent_id,
            role=data["role"],
            description=data["description"],
            prompt=data["prompt"],
            tools=data.get("tools", []),
            limits=data.get("limits", {}),
            metadata=data.get("metadata", {}),
        )

    # ---------------------------------------------------------------------

    def list_agents(self) -> List[str]:
        """
        List available agent IDs.
        """
        return sorted(p.stem for p in self.agents_dir.glob("*.yaml"))

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------

    def _agent_path(self, agent_id: str) -> Path:
        path = self.agents_dir / f"{agent_id}.yaml"
        if not path.exists():
            available = ", ".join(self.list_agents())
            raise FileNotFoundError(
                f"Agent '{agent_id}' not found. Available agents: {available}"
            )
        return path

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {path}: {e}")

    def _validate_schema(self, agent_id: str, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise TypeError(f"Agent '{agent_id}' YAML must be a mapping")

        required = ["role", "description", "prompt"]
        missing = [k for k in required if k not in data]

        if missing:
            raise ValueError(
                f"Agent '{agent_id}' missing required fields: {missing}"
            )

        if not isinstance(data.get("tools", []), list):
            raise TypeError("Field 'tools' must be a list")

        if not isinstance(data.get("limits", {}), dict):
            raise TypeError("Field 'limits' must be a mapping")

        if not isinstance(data.get("metadata", {}), dict):
            raise TypeError("Field 'metadata' must be a mapping")

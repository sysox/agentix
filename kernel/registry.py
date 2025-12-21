from pathlib import Path
from typing import Dict

import yaml

from kernel.spec import AgentSpec
from kernel.agent import Agent


class Registry:
    """
    Loads agent specifications from YAML files in agents/.
    Responsible ONLY for AgentSpec lifecycle (not execution).
    """

    def __init__(self, agents_dir: Path = Path("agents")):
        self.agents_dir = agents_dir

    # ------------------------------------------------------------------
    # Low-level loaders (AgentSpec only)
    # ------------------------------------------------------------------

    def load(self, agent_id: str) -> AgentSpec:
        """
        Load an exact agent spec from agents/<agent_id>.yaml
        """
        path = self.agents_dir / f"{agent_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Agent not found: {agent_id}")

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

        return AgentSpec(
            agent_id=agent_id,
            role=data["role"],
            description=data.get("description", ""),
            prompt=data.get("prompt", ""),
            tools=data.get("tools", []),
            limits=data.get("limits", {}),
            metadata=data.get("metadata", {}),
        )

    def load_best(self, agent_id: str) -> AgentSpec:
        """
        Load the latest evolved version if it exists,
        otherwise load the base agent.
        """
        versions = sorted(
            self.agents_dir.glob(f"{agent_id}_v*.yaml"),
            key=lambda p: p.stem,
        )
        if versions:
            return self.load(versions[-1].stem)
        return self.load(agent_id)


# ----------------------------------------------------------------------
# Public convenience API (used by CLI / Supervisor)
# ----------------------------------------------------------------------

def load_agent(agent_id: str) -> Agent:
    """
    Load the best available version of an agent and return a runnable Agent.
    """
    registry = Registry()
    spec = registry.load_best(agent_id)
    return Agent(spec)

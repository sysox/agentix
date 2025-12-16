"""
Agent Registry (Placeholder)

Loads and provides immutable access to agent definitions.

Responsibilities:
- validation
- version handling
"""

import yaml
from pathlib import Path
from kernel.spec import AgentSpec


class AgentRegistry:
    def __init__(self, agents_dir: str = "agents"):
        self.agents_dir = Path(agents_dir)

    def load(self, agent_id: str) -> AgentSpec:
        path = self.agents_dir / f"{agent_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Agent not found: {agent_id}")

        data = yaml.safe_load(path.read_text())
        return AgentSpec(**data)

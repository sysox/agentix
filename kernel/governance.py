import yaml
from pathlib import Path

class Governance:
    def __init__(self, data: dict):
        evo = data.get("evolution", {})
        self.evolution_mode = evo.get("mode", "auto")
        self.allowed_agents = set(evo.get("allowed_agents", []))
        self.blocked_agents = set(evo.get("blocked_agents", []))

    @classmethod
    def load(cls):
        path = Path("governance.yaml")
        if not path.exists():
            return cls({})
        return cls(yaml.safe_load(path.read_text()))

    def is_allowed(self, agent_id: str) -> bool:
        if agent_id in self.blocked_agents:
            return False
        if self.allowed_agents:
            return agent_id in self.allowed_agents
        return True

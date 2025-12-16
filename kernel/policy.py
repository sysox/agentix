from typing import Dict, Any
from pathlib import Path


class EvolutionPolicy:
    """
    Hard constraints for agent evolution.
    """

    def __init__(
        self,
        min_score: float = 0.9,
        max_versions: int = 5,
        min_component: float = 0.7,
    ):
        self.min_score = min_score
        self.max_versions = max_versions
        self.min_component = min_component

    def allow_evolution(
        self,
        agent_id: str,
        evaluation: Dict[str, Any],
        agents_dir: Path = Path("agents"),
    ) -> bool:
        score = evaluation.get("score", 0.0)

        # 1. block if overall performance is already good
        if score >= self.min_score:
            return False

        # 2. block if too many versions exist
        existing = list(agents_dir.glob(f"{agent_id}_v*.yaml"))
        if len(existing) >= self.max_versions:
            return False

        # 3. block if no component is actually weak
        components = evaluation.get("components", {})
        if not any(v < self.min_component for v in components.values()):
            return False

        return True

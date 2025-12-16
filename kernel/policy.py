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
    ):
        self.min_score = min_score
        self.max_versions = max_versions

    def allow_evolution(
        self,
        agent_id: str,
        evaluation: Dict[str, Any],
        agents_dir: Path = Path("agents"),
    ) -> bool:
        score = evaluation.get("score", 0.0)

        # block if performance is already good
        if score >= self.min_score:
            return False

        # block if too many versions exist
        existing = list(agents_dir.glob(f"{agent_id}_v*.yaml"))
        if len(existing) >= self.max_versions:
            return False

        return True

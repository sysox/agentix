from __future__ import annotations

from pathlib import Path
from typing import Optional, Set, Any, Dict

import yaml


class Governance:
    """
    Loads governance.yaml and exposes evolution/autonomy controls.

    Backward compatible:
      - legacy: governance.yaml contains top-level 'evolution: {mode, allowed_agents, blocked_agents}'
      - new: governance.yaml may also contain top-level autonomy settings:
          autonomy_mode: off|propose|auto
          max_cost_usd_per_run: <float|null>
          max_proposals_per_run: <int>
    """

    # Defaults (applied if missing from YAML)
    DEFAULT_AUTONOMY_MODE = "propose"      # off | propose | auto
    DEFAULT_MAX_COST_USD_PER_RUN = None    # type: Optional[float]
    DEFAULT_MAX_PROPOSALS_PER_RUN = 1

    def __init__(self, data: Dict[str, Any]):
        evo = data.get("evolution", {}) or {}

        # legacy evolution controls (still used for allowed/blocked)
        self.evolution_mode: str = evo.get("mode", "propose")  # off | propose | auto
        self.allowed_agents: Set[str] = set(evo.get("allowed_agents", []) or [])
        self.blocked_agents: Set[str] = set(evo.get("blocked_agents", []) or [])

        # new autonomy controls (preferred)
        # If not present, derive from legacy evolution.mode for smooth migration.
        self.autonomy_mode: str = data.get("autonomy_mode") or self._derive_autonomy_mode(self.evolution_mode)
        self.max_cost_usd_per_run: Optional[float] = data.get("max_cost_usd_per_run", self.DEFAULT_MAX_COST_USD_PER_RUN)
        self.max_proposals_per_run: int = int(data.get("max_proposals_per_run", self.DEFAULT_MAX_PROPOSALS_PER_RUN))

        # normalize
        self.autonomy_mode = self.autonomy_mode.strip().lower()
        if self.autonomy_mode not in {"off", "propose", "auto"}:
            # fall back safely
            self.autonomy_mode = self.DEFAULT_AUTONOMY_MODE

        if self.max_proposals_per_run < 0:
            self.max_proposals_per_run = self.DEFAULT_MAX_PROPOSALS_PER_RUN

    @classmethod
    def load(cls) -> "Governance":
        path = Path("governance.yaml")
        if not path.exists():
            return cls({})
        return cls(yaml.safe_load(path.read_text(encoding="utf-8")) or {})

    @staticmethod
    def _derive_autonomy_mode(legacy_mode: str) -> str:
        """
        Map legacy evolution.mode to autonomy_mode.
        """
        m = (legacy_mode or "").strip().lower()
        if m in {"off", "propose", "auto"}:
            return m
        # safest fallback
        return Governance.DEFAULT_AUTONOMY_MODE

    def is_allowed(self, agent_id: str) -> bool:
        """
        Check agent allow/block lists (legacy behavior).
        """
        if agent_id in self.blocked_agents:
            return False
        if self.allowed_agents:
            return agent_id in self.allowed_agents
        return True

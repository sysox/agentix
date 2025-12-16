"""
Evolution placeholder.

Responsible for:
- deciding WHEN to evolve
- deciding HOW to mutate
- calling evolve_agent(...)
"""

from typing import Dict, Any

from kernel.registry import AgentSpec
from kernel.evolve import evolve_agent


class Evolver:
    def __init__(self):
        pass

    def should_evolve(
        self,
        spec: AgentSpec,
        evaluation: Dict[str, Any],
    ) -> bool:
        """
        Decide whether evolution is worth it.
        Placeholder: always False.
        """
        return False

    def propose_mutation(
        self,
        spec: AgentSpec,
        evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Propose mutation.
        Placeholder: empty mutation.
        """
        return {}

    def evolve(
        self,
        spec: AgentSpec,
        evaluation: Dict[str, Any],
    ) -> AgentSpec:
        """
        Execute evolution if allowed.
        """
        if not self.should_evolve(spec, evaluation):
            return spec

        mutation = self.propose_mutation(spec, evaluation)
        return evolve_agent(spec, mutation)

from typing import Dict, Any

from kernel.registry import AgentSpec
from kernel.evolve import evolve_agent
from kernel.mutator import Mutator
from kernel.policy import EvolutionPolicy


class Evolver:
    def __init__(self):
        self.mutator = Mutator()
        self.policy = EvolutionPolicy()

    def evolve(
        self,
        spec: AgentSpec,
        evaluation: Dict[str, Any],
    ) -> AgentSpec:

        if not self.policy.allow_evolution(
            spec.agent_id,
            evaluation,
        ):
            return spec

        mutation = self.mutator.mutate(spec, evaluation)
        return evolve_agent(spec, mutation)

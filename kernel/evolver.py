from typing import Dict, Any

from kernel.registry import AgentSpec
from kernel.evolve import evolve_agent
from kernel.mutator import Mutator
from kernel.policy import EvolutionPolicy
from kernel.pruner import Pruner
from kernel.evolve import base_agent_id
from kernel.evolve import evolve_agent, base_agent_id
from kernel.approval import pause_for_approval


class Evolver:
    def __init__(self):
        self.mutator = Mutator()
        self.policy = EvolutionPolicy()
        self.pruner = Pruner()

    def evolve(self, spec, evaluation, run):
        """
        Perform evolution step.
        MUST pause for approval if a new agent spec is produced.
        """

        if not self.policy.allow_evolution(spec.agent_id, evaluation):
            return spec

        mutation = self.mutator.mutate(spec, evaluation)
        new_spec = evolve_agent(spec, mutation, run)


        # ✅ prune by BASE agent id
        self.pruner.prune(base_agent_id(spec.agent_id))

        # ⛔ IMPORTANT: pause execution AFTER proposal is written
        # evolve_agent(...) is assumed to write *_vX.yaml with status: proposed
        pause_for_approval(run)

        return new_spec


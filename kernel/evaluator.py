from typing import Dict, Any
import os

from kernel.registry import AgentSpec


class Evaluator:
    """
    Evaluates agent outputs and produces fitness signals.
    """

    def __init__(self):
        # env switch for testing evolution
        self.force_fail = os.getenv("AGENTIX_FORCE_EVOLVE") == "1"

    def evaluate(
        self,
        spec: AgentSpec,
        task: Dict[str, Any],
        output: Dict[str, Any],
    ) -> Dict[str, Any]:

        if self.force_fail:
            return {
                "score": 0.0,
                "reasons": ["forced_test"],
            }

        score = 1.0
        reasons = []

        if output.get("response"):
            reasons.append("non_empty_response")
        else:
            score = 0.0
            reasons.append("empty_response")

        # return {
        #     "score": score,
        #     "reasons": reasons,
        # }
        return {
            "score": 0,
            "reasons": reasons,
        }
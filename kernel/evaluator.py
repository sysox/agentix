from typing import Dict, Any

from kernel.registry import AgentSpec


class Evaluator:
    """
    Evaluates agent outputs and produces fitness signals.
    Placeholder: deterministic, schema-stable.
    """

    def evaluate(
        self,
        spec: AgentSpec,
        task: Dict[str, Any],
        output: Dict[str, Any],
    ) -> Dict[str, Any]:
        score = 1.0
        reasons = []

        if "response" in output and output["response"]:
            reasons.append("non_empty_response")
        else:
            score = 0.0
            reasons.append("empty_response")

        return {
            "score": score,
            "reasons": reasons,
        }

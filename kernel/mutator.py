import random
from typing import Dict, Any


class Mutator:
    """
    Produces concrete mutations for agent evolution.
    """

    def mutate(
        self,
        spec,
        evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Return a mutation dict.
        """

        mutation: Dict[str, Any] = {}

        score = evaluation.get("score", 0.0)

        # if score is low, strengthen prompt
        if score < 0.5:
            mutation["prompt"] = (
                spec.prompt
                + "\n\nIMPORTANT:\nBe more explicit and cautious. "
                + "Double-check correctness before responding."
            )

        # small random stylistic variation
        mutation.setdefault("metadata", {})
        mutation["metadata"]["mutation"] = random.choice(
            [
                "prompt_strengthen",
                "prompt_clarify",
                "style_adjust",
            ]
        )

        return mutation

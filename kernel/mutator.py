from typing import Dict, Any
from kernel.registry import AgentSpec


class Mutator:
    """
    Prompt-only mutations based on fitness weaknesses.
    """

    def mutate(
        self,
        spec: AgentSpec,
        evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:

        components = evaluation.get("components", {})
        prompt = spec.prompt.rstrip()

        additions = []

        # --- target weaknesses ---
        if components.get("task_relevance", 1.0) < 0.7:
            additions.append(
                "Focus strictly on the given task. "
                "Do not include unrelated information."
            )

        if components.get("structure", 1.0) < 0.7:
            additions.append(
                "Structure your output clearly using paragraphs or lists."
            )

        if components.get("memory_use", 1.0) < 0.7:
            additions.append(
                "Reuse relevant information from past knowledge when available."
            )

        if not additions:
            return {}  # nothing to mutate

        new_prompt = (
            prompt
            + "\n\n"
            + "EVOLUTION NOTES:\n"
            + "\n".join(f"- {a}" for a in additions)
        )

        return {
            "prompt": new_prompt
        }

from typing import Dict, Any
import re

from kernel.registry import AgentSpec


class Evaluator:
    """
    Deterministic evaluator producing stable fitness scores.
    """

    def evaluate(
        self,
        spec: AgentSpec,
        task: Dict[str, Any],
        output: Dict[str, Any],
    ) -> Dict[str, Any]:

        response = output.get("response", "") or ""
        task_text = task.get("task", "") or ""
        memory = task.get("memory", "") or ""

        reasons = {}
        scores = {}

        # 1. non-empty
        scores["non_empty"] = 1.0 if response.strip() else 0.0
        reasons["non_empty"] = "response present" if scores["non_empty"] else "empty response"

        # 2. task relevance (keyword overlap)
        task_words = set(re.findall(r"\w+", task_text.lower()))
        resp_words = set(re.findall(r"\w+", response.lower()))

        overlap = task_words & resp_words
        scores["task_relevance"] = min(1.0, len(overlap) / max(3, len(task_words)))
        reasons["task_relevance"] = f"{len(overlap)} overlapping keywords"

        # 3. structure (simple heuristic)
        has_paragraphs = "\n\n" in response
        has_list = bool(re.search(r"^\s*[-*]", response, re.MULTILINE))

        scores["structure"] = 1.0 if (has_paragraphs or has_list) else 0.5
        reasons["structure"] = "structured text" if scores["structure"] == 1.0 else "flat text"

        # 4. memory usage (optional bonus)
        if memory and any(line.strip() in response for line in memory.splitlines()[:3]):
            scores["memory_use"] = 1.0
            reasons["memory_use"] = "references past knowledge"
        else:
            scores["memory_use"] = 0.5
            reasons["memory_use"] = "no explicit memory use"

        # final score
        final_score = sum(scores.values()) / len(scores)

        return {
            "score": round(final_score, 3),
            "components": scores,
            "reasons": reasons,
        }

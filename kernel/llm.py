import os
from typing import Optional


class LLM:
    """
    Unified LLM interface.

    Modes:
      - stub    : deterministic, no external calls
      - openai  : real OpenAI backend
    """

    def __init__(self):
        self.mode = os.getenv("AGENTIX_LLM_MODE", "stub")
        self._client: Optional[object] = None

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def complete(self, prompt: str) -> str:
        if self.mode == "stub":
            return self._stub(prompt)
        elif self.mode == "openai":
            return self._openai(prompt)
        else:
            raise ValueError(f"Unknown LLM mode: {self.mode}")

    # ------------------------------------------------------------------
    # stub backend (deterministic)
    # ------------------------------------------------------------------

    def _stub(self, prompt: str) -> str:
        """
        Deterministic stub used for development and testing.
        Includes a hardcoded orchestration plan.
        """

        # Orchestrator shortcut
        if "system orchestrator" in prompt.lower():
            return """PLAN:
steps:
  - agent: summarizer
    purpose: summarize the topic
    output: concise explanation

  - agent: evaluator
    purpose: assess quality
    output: score and reasons

  - agent: reflector
    purpose: suggest improvements
    output: improvement suggestions
"""

        return (
            "[STUB LLM OUTPUT]\n"
            "Task received and processed.\n\n"
            f"Prompt preview:\n{prompt[:200]}"
        )

    # ------------------------------------------------------------------
    # OpenAI backend
    # ------------------------------------------------------------------

    def _openai(self, prompt: str) -> str:
        """
        Real OpenAI backend.
        """

        if self._client is None:
            from openai import OpenAI

            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY not set")

            self._client = OpenAI(api_key=api_key)

        resp = self._client.chat.completions.create(
            model=os.getenv("AGENTIX_OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise, structured, and helpful AI assistant.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
        )

        return resp.choices[0].message.content

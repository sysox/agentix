import os
from typing import Optional


class LLM:
    def __init__(self):
        self.mode = os.getenv("AGENTIX_LLM_MODE", "stub")

    # def complete(self, prompt: str) -> str:
    #     if self.mode == "stub":
    #         return self._stub(prompt)
    #     elif self.mode == "openai":
    #         return self._openai(prompt)
    #     else:
    #         raise ValueError(f"Unknown LLM mode: {self.mode}")
    def complete(self, prompt: str) -> str:
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
        return "[STUB LLM OUTPUT]"

    # ------------------------------------------------------------------

    def _stub(self, prompt: str) -> str:
        return (
            "[STUB LLM OUTPUT]\n"
            "Task received and processed.\n\n"
            f"Prompt preview:\n{prompt[:200]}"
        )

    # ------------------------------------------------------------------

    def _openai(self, prompt: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an autonomous coding agent."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content

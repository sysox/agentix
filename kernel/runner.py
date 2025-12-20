# kernel/runner.py

from kernel.run import Run, RunState
from kernel.pricing import compute_cost_usd
from datetime import datetime


class Runner:
    def __init__(self, agent, run: Run):
        self.agent = agent
        self.run = run

    def execute(self) -> Run:
        try:
            self.run.set_state(RunState.RUNNING)

            # === agent execution ===
            # This is pseudocode – plug into your existing logic

            result = self._run_agent()

            # store artifacts
            for name, value in result.get("artifacts", {}).items():
                self.run.artifacts[name] = value

            self.run.set_state(RunState.COMPLETED)
            return self.run

        except Exception as e:
            self.run.set_state(RunState.FAILED)
            self.run.artifacts["error"] = str(e)
            return self.run

    def _run_agent(self) -> dict:
        """
        Run the agent once and account for cost.
        """

        # Example: single LLM call
        response = self.agent.call_llm(self.run.task)

        input_tokens = response.input_tokens
        output_tokens = response.output_tokens
        model_name = response.model_name

        # exact USD cost
        cost = compute_cost_usd(
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        self.run.cost_usd += cost

        # enforce run-level budget
        if (
            self.run.constraints.max_cost_usd is not None
            and self.run.cost_usd > self.run.constraints.max_cost_usd
        ):
            raise RuntimeError(
                f"Run budget exceeded: "
                f"{self.run.cost_usd:.4f} USD > "
                f"{self.run.constraints.max_cost_usd:.4f} USD"
            )

        return {
            "artifacts": {
                "result": response.text
            }
        }

# kernel/runner.py

from pathlib import Path

from kernel.run import Run, RunState
from kernel.pricing import compute_cost_usd
from kernel.approval import ApprovalRequired
from kernel.action_gate import ActionRequired
from kernel.governance import Governance
from kernel.context import build_project_context
from kernel.run_store import RunStore


class Runner:
    def __init__(self, agent, run: Run):
        self.agent = agent
        self.run = run
        self.store = RunStore()

    def execute(self):
        try:
            self.run.set_state(RunState.RUNNING)

            # ✅ Inject governance run budget if run doesn't have one
            gov = Governance.load()
            if self.run.constraints.max_cost_usd is None and gov.max_cost_usd_per_run is not None:
                self.run.constraints.max_cost_usd = gov.max_cost_usd_per_run

            self._run_agent()

            self.run.set_state(RunState.COMPLETED)
            self.store.save(self.run)
            return self.run

        except ActionRequired as ar:
            # execution paused for system action approval
            self.run.artifacts["pending_action"] = ar.request
            self.run.set_state(RunState.WAITING_FOR_APPROVAL)
            self.store.save(self.run)
            return self.run

        except ApprovalRequired:
            # evolution approval pause
            self.store.save(self.run)
            return self.run

        except Exception as e:
            self.run.set_state(RunState.FAILED)
            self.run.artifacts["error"] = str(e)
            self.store.save(self.run)
            return self.run

    def _run_agent(self) -> dict:
        """
        Run the agent once, pass project context, and account for cost.
        """

        # -----------------------------
        # 🔍 PROJECT INSPECTION (SAFE)
        # -----------------------------
        project_context = build_project_context(
            project_root=Path("."),
            max_depth=3,
        )
        # Debug: verify context is actually being built
        self.run.artifacts["context_files_count"] = len(project_context.get("files", []))

        # -----------------------------
        # 🤖 LLM CALL WITH CONTEXT
        # -----------------------------
        response = self.agent.call_llm(
            task=self.run.task,
            context=project_context,
        )

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

        # store result artifact
        self.run.artifacts["result"] = response.text

        return {"artifacts": {"result": response.text}}

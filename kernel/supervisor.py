from kernel.run import Run, RunState
from kernel.runner import Runner
from proposals import ProposalManager


class Supervisor:
    """
    Human-facing control layer.
    Does NOT evolve, does NOT reason.
    """

    def __init__(self):
        self.proposals = ProposalManager()

    # -------------------------
    # Run control
    # -------------------------

    def start_run(self, agent, run: Run) -> Run:
        runner = Runner(agent, run)
        return runner.execute()

    def can_resume(self, run: Run) -> bool:
        return run.state == RunState.WAITING_FOR_APPROVAL

    # -------------------------
    # Proposal supervision
    # -------------------------

    def list_proposals(self):
        return self.proposals.list_proposals()

    def approve(self, agent_id: str):
        return self.proposals.approve(agent_id)

    def reject(self, agent_id: str):
        return self.proposals.reject(agent_id)

    # -------------------------
    # Action supervision (NEW)
    # -------------------------

    def get_pending_action(self, run: Run):
        """
        Return pending ActionRequest if present.
        This does NOT execute anything.
        """
        return run.artifacts.get("pending_action")

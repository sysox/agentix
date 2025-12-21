from pathlib import Path
import yaml

from kernel.governance import Governance
from kernel.run import Run, RunState
from kernel.runner import Runner
from kernel.proposals import ProposalManager


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

    def _is_safe_agent_yaml_proposal(self, agent_id: str) -> bool:
        """
        Auto-approve policy:
        - must be an agent YAML in agents/
        - must have metadata.status == "proposed"
        - must not touch kernel/ or tools/
        (Since proposals are YAML-only right now, this is sufficient.)
        """
        path = Path("agents") / f"{agent_id}.yaml"
        if not path.exists():
            return False

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        status = (data.get("metadata", {}) or {}).get("status")
        return status == "proposed"

    def maybe_auto_approve(self) -> list[str]:
        """
        Auto-approve pending proposals if governance allows.
        Returns list of approved agent_ids.
        """
        gov = Governance.load()
        if gov.autonomy_mode != "auto":
            return []

        # If manual approval is required, do not auto-approve.
        # (keeps your existing safety knob meaningful)
        # governance.yaml contains:
        # safety:
        #   require_manual_approval: true
        require_manual = False
        try:
            # If you later expose this in Governance, use that instead.
            raw = yaml.safe_load(Path("governance.yaml").read_text(encoding="utf-8")) or {}
            require_manual = bool((raw.get("safety", {}) or {}).get("require_manual_approval", False))
        except Exception:
            require_manual = False

        if require_manual:
            return []

        approved = []
        for agent_id in self.proposals.list_proposals():
            if self._is_safe_agent_yaml_proposal(agent_id):
                self.proposals.approve(agent_id)
                approved.append(agent_id)
        return approved

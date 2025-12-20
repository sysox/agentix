# kernel/approval.py

from kernel.run import RunState


class ApprovalRequired(Exception):
    """Raised to pause execution until human approval."""
    pass


def pause_for_approval(run):
    """
    Put the run into WAITING_FOR_APPROVAL state and stop execution.
    """
    run.set_state(RunState.WAITING_FOR_APPROVAL)
    raise ApprovalRequired()

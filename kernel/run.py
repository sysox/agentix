# kernel/run.py

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import uuid


class RunState(Enum):
    CREATED = "created"
    RUNNING = "running"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


@dataclass
class RunConstraints:
    """
    Constraints under which the run executes.
    """
    max_cost_usd: Optional[float] = None
    allowed_agents: Optional[List[str]] = None
    blocked_agents: Optional[List[str]] = None


@dataclass
class Run:
    """
    A single supervised execution of agentix.
    """
    run_id: str
    task: str
    state: RunState = RunState.CREATED
    constraints: RunConstraints = field(default_factory=RunConstraints)

    cost_usd: float = 0.0
    artifacts: Dict[str, str] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None

    def set_state(self, new_state: RunState) -> None:
        self.state = new_state
        if new_state in {RunState.COMPLETED, RunState.REJECTED, RunState.FAILED}:
            self.finished_at = datetime.utcnow()


def create_run(task: str, constraints: Optional[RunConstraints] = None) -> Run:
    """
    Factory for creating a new Run.
    """
    return Run(
        run_id=str(uuid.uuid4()),
        task=task,
        constraints=constraints or RunConstraints(),
    )

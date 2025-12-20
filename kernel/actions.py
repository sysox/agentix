from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ActionRequest:
    """
    A request for a system-level action.
    This does NOT execute anything.
    """
    action: str               # e.g. read_file, scan_directory, run_command
    payload: Dict[str, Any]   # action-specific parameters
    reason: str               # why the agent needs this
    risk: str                 # low | medium | high

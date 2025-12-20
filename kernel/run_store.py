import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from kernel.run import Run, RunState


def _json_default(obj: Any):
    """
    Safe JSON encoding for dataclasses, enums, datetimes, and unknown objects.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, RunState):
        return obj.value
    if is_dataclass(obj):
        return asdict(obj)
    # For ActionRequest or other small objects stored in artifacts:
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


class RunStore:
    """
    Persists Run objects to disk for auditability and recovery.
    One run = one JSON file in runs/<run_id>.json
    """

    def __init__(self, runs_dir: Path = Path("runs")):
        self.runs_dir = runs_dir
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def save(self, run: Run) -> Path:
        path = self.runs_dir / f"{run.run_id}.json"
        data: Dict[str, Any] = {
            "run_id": run.run_id,
            "task": run.task,
            "state": run.state.value,
            "constraints": asdict(run.constraints),
            "cost_usd": run.cost_usd,
            "artifacts": run.artifacts,
            "created_at": run.created_at,
            "finished_at": run.finished_at,
        }
        path.write_text(json.dumps(data, indent=2, default=_json_default), encoding="utf-8")
        return path

    def load(self, run_id: str) -> Dict[str, Any]:
        path = self.runs_dir / f"{run_id}.json"
        if not path.exists():
            raise FileNotFoundError(path)
        return json.loads(path.read_text(encoding="utf-8"))

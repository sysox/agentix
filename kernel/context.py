"""
Execution Context (Placeholder)

Represents a single execution run.

Contains:
- run identifier
- timestamps
- logs
- artifacts
"""
import json
from pathlib import Path
from datetime import datetime


class ExecutionContext:
    def __init__(self, agent_id: str):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.run_id = f"{agent_id}_{timestamp}"

        self.run_dir = Path("runs") / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.logs = []

    def log(self, message: str):
        self.logs.append(message)

    def write_input(self, data: dict):
        (self.run_dir / "input.json").write_text(
            json.dumps(data, indent=2)
        )

    def write_output(self, data: dict):
        (self.run_dir / "output.json").write_text(
            json.dumps(data, indent=2)
        )

    def finalize(self):
        (self.run_dir / "trace.log").write_text(
            "\n".join(self.logs)
        )

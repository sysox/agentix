import json
from pathlib import Path
from datetime import datetime
import re
from pathlib import Path
from typing import List



def _keywords(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))

class ExecutionContext:
    def __init__(self, agent_id: str):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        self.run_id = f"{agent_id}_{timestamp}"

        self.run_dir = Path("runs") / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.logs = []

        self.knowledge_dir = Path("knowledge")
        self.knowledge_dir.mkdir(exist_ok=True)

        self.used_knowledge = set()

    def log(self, message: str):
        self.logs.append(message)

    def write_input(self, data: dict):
        (self.run_dir / "input.json").write_text(
            json.dumps(data, indent=2)
        )

    def write_prompt(self, prompt: str):
        (self.run_dir / "prompt.txt").write_text(prompt)

    def write_output(self, data: dict):
        (self.run_dir / "output.json").write_text(
            json.dumps(data, indent=2)
        )

    def write_evaluation(self, evaluation: dict):
        (self.run_dir / "evaluation.json").write_text(
            json.dumps(evaluation, indent=2)
        )

    def write_metadata(self, data: dict):
        (self.run_dir / "metadata.json").write_text(
            json.dumps(data, indent=2)
        )

    def write_error(self, error: str):
        self.log(f"ERROR: {error}")
        self.write_output({
            "status": "error",
            "error": error,
        })

    def write_knowledge(self, agent_id: str, text: str):
        path = self.knowledge_dir / f"{self.run_id}_{agent_id}.md"
        path.write_text(text.strip(), encoding="utf-8")

    def load_knowledge(self, task: str, limit: int = 5) -> str:
        """
        Load knowledge entries most relevant to the task.
        """
        if not hasattr(self, "knowledge_dir"):
            return ""

        task_kw = _keywords(task)
        scored = []

        for path in self.knowledge_dir.glob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue

            kw = _keywords(text)
            score = len(task_kw & kw)
            if score > 0:
                scored.append((score, path, text.strip()))

        scored.sort(reverse=True, key=lambda x: x[0])

        chunks = []
        for _, path, text in scored[:limit]:
            chunks.append(f"[{path.name}]\n{text}")

        return "\n\n".join(chunks)

    def finalize(self):
        (self.run_dir / "trace.log").write_text(
            "\n".join(self.logs)
        )

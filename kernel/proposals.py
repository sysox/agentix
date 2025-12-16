from pathlib import Path
import yaml


class ProposalManager:
    def __init__(self, agents_dir: Path = Path("agents")):
        self.agents_dir = agents_dir
        self.archive_dir = agents_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)

    def list_proposals(self):
        proposals = []
        for path in self.agents_dir.glob("*_v*.yaml"):
            data = yaml.safe_load(path.read_text()) or {}
            status = data.get("metadata", {}).get("status")
            if status == "proposed":
                proposals.append(path.stem)
        return sorted(proposals)

    def approve(self, agent_id: str):
        path = self.agents_dir / f"{agent_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(agent_id)

        data = yaml.safe_load(path.read_text())
        data["metadata"].pop("status", None)

        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False)

        return agent_id

    def reject(self, agent_id: str):
        path = self.agents_dir / f"{agent_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(agent_id)

        target = self.archive_dir / path.name
        path.rename(target)

        return agent_id

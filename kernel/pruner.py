from pathlib import Path
from typing import List
import shutil
import yaml


class Pruner:
    """
    Prunes old agent versions based on policy.
    """

    def __init__(
        self,
        keep_last: int = 2,
        agents_dir: Path = Path("agents"),
        archive_dir: Path = Path("agents/archive"),
    ):
        self.keep_last = keep_last
        self.agents_dir = agents_dir
        self.archive_dir = archive_dir
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def prune(self, agent_id: str) -> List[str]:
        """
        Move old agent versions to archive.
        Returns list of archived agent IDs.
        """

        versions = sorted(
            self.agents_dir.glob(f"{agent_id}_v*.yaml"),
            key=self._version_key,
        )

        if len(versions) <= self.keep_last:
            return []

        to_archive = versions[:-self.keep_last]
        archived = []

        for path in to_archive:
            target = self.archive_dir / path.name
            shutil.move(str(path), target)
            archived.append(path.stem)

        return archived

    def _version_key(self, path: Path):
        data = yaml.safe_load(path.read_text())
        version = data.get("metadata", {}).get("version", "0.0")
        try:
            major, minor = map(int, version.split("."))
            return (major, minor)
        except Exception:
            return (0, 0)

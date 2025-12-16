from pathlib import Path
from typing import Set
import time


class MemoryPruner:
    """
    Remove low-value or unused knowledge entries.
    """

    def __init__(
        self,
        max_age_days: int = 7,
        min_keep: int = 5,
    ):
        self.max_age_days = max_age_days
        self.min_keep = min_keep

    def prune(
        self,
        knowledge_dir: Path,
        used_recently: Set[str],
    ) -> None:
        now = time.time()
        files = list(knowledge_dir.glob("*.md"))

        # never prune if too few files
        if len(files) <= self.min_keep:
            return

        for path in files:
            if path.name in used_recently:
                continue

            age_days = (now - path.stat().st_mtime) / 86400
            if age_days > self.max_age_days:
                try:
                    path.unlink()
                except Exception:
                    pass

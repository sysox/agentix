from pathlib import Path
from typing import Dict, List


class ProjectInspector:
    """
    Read-only, bounded inspection of the project directory.
    """

    ALLOWED_EXTENSIONS = {
        ".py", ".md", ".yaml", ".yml", ".toml", ".json"
    }

    MAX_FILE_SIZE = 200_000        # bytes per file
    MAX_TOTAL_BYTES = 1_000_000    # bytes per run

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()

    def scan(self, max_depth: int = 3) -> List[Path]:
        files = []
        for path in self.project_root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in self.ALLOWED_EXTENSIONS:
                continue
            if path.stat().st_size > self.MAX_FILE_SIZE:
                continue
            if self._depth(path) > max_depth:
                continue
            files.append(path)
        return files

    def read(self, files: List[Path]) -> Dict[str, str]:
        total = 0
        out = {}

        for p in files:
            size = p.stat().st_size
            if total + size > self.MAX_TOTAL_BYTES:
                break
            out[str(p)] = p.read_text(encoding="utf-8", errors="ignore")
            total += size

        return out

    def _depth(self, path: Path) -> int:
        return len(path.relative_to(self.project_root).parts)

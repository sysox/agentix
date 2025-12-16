from pathlib import Path
from typing import Optional


class FileSystemTool:
    def read(self, path: str) -> str:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(path)
        return p.read_text(encoding="utf-8")

    def write(self, path: str, content: str, overwrite: bool = True) -> None:
        p = Path(path)
        if p.exists() and not overwrite:
            raise FileExistsError(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

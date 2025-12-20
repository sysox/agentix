from pathlib import Path
from typing import Dict, Any

from kernel.inspector import ProjectInspector


def build_project_context(
    project_root: Path,
    max_depth: int = 3,
) -> Dict[str, Any]:
    """
    Read-only, bounded project context for LLM consumption.
    Safe by design (uses ProjectInspector limits).
    """
    inspector = ProjectInspector(project_root)
    files = inspector.scan(max_depth=max_depth)
    contents = inspector.read(files)

    return {
        "files": list(contents.keys()),
        "contents": contents,
    }

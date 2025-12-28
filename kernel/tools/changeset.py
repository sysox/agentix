from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ReplaceOp:
    op: str
    symbol_id: str
    new_code: str
    expected_sha1: Optional[str] = None
    file: Optional[str] = None          # optional override; else inferred
    write_leaf: bool = True
    leaf_path: Optional[str] = None     # relative


def load_changeset(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(data, dict) or "ops" not in data:
        raise ValueError("Invalid changeset: expected dict with 'ops'")
    return data


def dump_example() -> Dict[str, Any]:
    return {
        "version": "0.1",
        "ops": [
            {
                "op": "replace",
                "symbol_id": "py:function:kernel.policy.allow_action",
                "expected_sha1": None,
                "new_code": "def allow_action(action, ctx):\n    return True\n",
                "write_leaf": True,
                "leaf_path": None,
            }
        ],
    }

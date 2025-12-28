from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml  # type: ignore
except Exception:
    yaml = None  # type: ignore

from .code_edit import (
    parse_symbol_id,
    module_to_path,
    apply_replace_in_file,
    write_leaf,
)
from .changeset import load_changeset


def _load_symbols_yaml(repo_root: Path) -> Optional[Dict[str, Any]]:
    p = repo_root / "desc" / "SYMBOLS.yaml"
    if not p.exists() or yaml is None:
        return None
    data = yaml.safe_load(p.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(data, dict):
        return None
    return data


def _save_symbols_yaml(repo_root: Path, data: Dict[str, Any]) -> None:
    if yaml is None:
        raise RuntimeError("PyYAML not installed; cannot update desc/SYMBOLS.yaml automatically.")
    p = repo_root / "desc" / "SYMBOLS.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _infer_file(repo_root: Path, symbol_id: str, symbols_yaml: Optional[Dict[str, Any]]) -> Path:
    # Prefer desc/SYMBOLS.yaml mapping if present
    if symbols_yaml:
        syms = symbols_yaml.get("symbols", {})
        rec = syms.get(symbol_id)
        if isinstance(rec, dict) and rec.get("file"):
            return repo_root / str(rec["file"])
    sid = parse_symbol_id(symbol_id)
    return repo_root / module_to_path(sid.module)


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply an Agentix ChangeSet to source + desc/leaves.")
    ap.add_argument("changeset", type=str, help="Path to changeset JSON")
    ap.add_argument("--repo-root", type=str, default=".", help="Repo root (default: .)")
    ap.add_argument("--no-update-symbols", action="store_true", help="Do not update desc/SYMBOLS.yaml leaf pointers")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    cs = load_changeset(Path(args.changeset))
    symbols_yaml = _load_symbols_yaml(repo_root)

    reports = []
    for op in cs.get("ops", []):
        if not isinstance(op, dict) or op.get("op") != "replace":
            raise ValueError(f"Unsupported op: {op!r}")

        symbol_id = op["symbol_id"]
        new_code = op["new_code"]
        expected_sha1 = op.get("expected_sha1")
        write_leaf_flag = bool(op.get("write_leaf", True))
        leaf_path = op.get("leaf_path")  # may be None

        file_override = op.get("file")
        if file_override:
            file_path = repo_root / file_override
        else:
            file_path = _infer_file(repo_root, symbol_id, symbols_yaml)

        rep = apply_replace_in_file(
            file_path=file_path,
            symbol_id=symbol_id,
            new_code=new_code,
            expected_sha1=expected_sha1,
            reindent=True,
        )

        if write_leaf_flag:
            rel = write_leaf(repo_root, symbol_id, new_code, leaf_relpath=leaf_path)
            rep["leaf_path"] = rel

            if not args.no_update_symbols and symbols_yaml is not None:
                syms = symbols_yaml.setdefault("symbols", {})
                rec = syms.get(symbol_id)
                if isinstance(rec, dict):
                    rec["leaf"] = rel
                else:
                    syms[symbol_id] = {"leaf": rel}
        reports.append(rep)

    if (not args.no_update_symbols) and symbols_yaml is not None:
        _save_symbols_yaml(repo_root, symbols_yaml)

    out = {"version": cs.get("version", "0.1"), "reports": reports}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

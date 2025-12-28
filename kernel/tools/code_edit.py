from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any


# ============================
# IDs / parsing
# ============================

@dataclass(frozen=True)
class SymbolId:
    """
    Parsed symbol_id.

    Examples:
      py:module:kernel.runner
      py:class:kernel.runner.Runner
      py:function:kernel.policy.allow_action
      py:method:kernel.runner.Runner.execute
    """
    kind: str
    fqname: str  # dotted
    module: str  # dotted module path
    cls: Optional[str] = None
    name: Optional[str] = None


def parse_symbol_id(symbol_id: str) -> SymbolId:
    try:
        prefix, kind, fq = symbol_id.split(":", 2)
    except ValueError as e:
        raise ValueError(f"Invalid symbol_id format: {symbol_id!r}") from e
    if prefix != "py":
        raise ValueError(f"Unsupported symbol_id prefix {prefix!r} (expected 'py')")

    parts = fq.split(".")
    if kind == "module":
        return SymbolId(kind=kind, fqname=fq, module=fq)
    if kind == "class":
        if len(parts) < 2:
            raise ValueError(f"Invalid class fqname: {fq!r}")
        module = ".".join(parts[:-1])
        return SymbolId(kind=kind, fqname=fq, module=module, cls=parts[-1])
    if kind == "function":
        if len(parts) < 2:
            raise ValueError(f"Invalid function fqname: {fq!r}")
        module = ".".join(parts[:-1])
        return SymbolId(kind=kind, fqname=fq, module=module, name=parts[-1])
    if kind == "method":
        if len(parts) < 3:
            raise ValueError(f"Invalid method fqname: {fq!r}")
        module = ".".join(parts[:-2])
        return SymbolId(kind=kind, fqname=fq, module=module, cls=parts[-2], name=parts[-1])

    raise ValueError(f"Unsupported symbol kind: {kind!r}")


def module_to_path(module: str) -> str:
    # We assume kernel.* modules live at kernel/<name>.py
    return module.replace(".", "/") + ".py"


# ============================
# IO helpers
# ============================

def sha1_text(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _write_text(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def _detect_indent(line: str) -> str:
    i = 0
    while i < len(line) and line[i] in (" ", "\t"):
        i += 1
    return line[:i]


def _strip_common_indent(lines: List[str]) -> List[str]:
    """
    Strip common leading indentation across non-empty lines.
    """
    indents: List[int] = []
    for ln in lines:
        if ln.strip() == "":
            continue
        indent = len(_detect_indent(ln).replace("\t", "    "))
        indents.append(indent)
    if not indents:
        return lines
    m = min(indents)
    out: List[str] = []
    for ln in lines:
        if ln.strip() == "":
            out.append("")
        else:
            # remove m spaces (tabs already expanded above only for measuring)
            # for actual removal, remove from original preserving tabs:
            # safest: remove leading whitespace characters until we've removed >= m columns
            removed_cols = 0
            j = 0
            while j < len(ln) and removed_cols < m and ln[j] in (" ", "\t"):
                if ln[j] == "\t":
                    removed_cols += 4
                else:
                    removed_cols += 1
                j += 1
            out.append(ln[j:])
    return out


def reindent_to(code: str, target_indent: str) -> str:
    """
    Normalize `code` by stripping common indent, then prefixing with target_indent.
    """
    raw_lines = code.splitlines()
    stripped = _strip_common_indent(raw_lines)
    out_lines = []
    for ln in stripped:
        if ln == "":
            out_lines.append("")
        else:
            out_lines.append(target_indent + ln)
    return "\n".join(out_lines) + ("\n" if code.endswith("\n") else "")


# ============================
# AST location
# ============================

@dataclass(frozen=True)
class Span:
    start_line: int  # 1-based inclusive
    end_line: int    # 1-based inclusive

    def to_slice(self) -> slice:
        return slice(self.start_line - 1, self.end_line)


def locate_symbol_span(source: str, sid: SymbolId) -> Span:
    """
    Locate the (start_line, end_line) of the symbol in the given source.
    Requires Python 3.8+ end_lineno, which you have (3.12).
    """
    tree = ast.parse(source)

    # module = whole file
    if sid.kind == "module":
        nlines = max(1, len(source.splitlines()))
        return Span(1, nlines)

    def span_of(node: ast.AST, fallback: int) -> Span:
        start = int(getattr(node, "lineno", 0) or fallback)
        end = int(getattr(node, "end_lineno", 0) or start)
        return Span(start, end)

    for node in tree.body:
        if sid.kind == "class" and isinstance(node, ast.ClassDef) and node.name == sid.cls:
            return span_of(node, 1)

        if sid.kind == "function" and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == sid.name:
            return span_of(node, 1)

        if sid.kind == "method" and isinstance(node, ast.ClassDef) and node.name == sid.cls:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == sid.name:
                    return span_of(item, 1)

    raise KeyError(f"Could not locate {sid.kind} {sid.fqname} in AST")


def extract_symbol_code(file_path: Path, symbol_id: str) -> Tuple[str, Span, str]:
    """
    Returns (code_slice_text, span, sha1).
    """
    sid = parse_symbol_id(symbol_id)
    src = _read_text(file_path)
    span = locate_symbol_span(src, sid)
    lines = src.splitlines()
    slice_text = "\n".join(lines[span.start_line - 1 : span.end_line])
    # Preserve trailing newline behavior by checking original file segment
    # (approx: if the original file had a newline at end_line, join above loses it)
    if src.endswith("\n"):
        slice_text += "\n"
    return slice_text, span, sha1_text(slice_text)


# ============================
# Patch operations
# ============================

def apply_replace_in_file(
    file_path: Path,
    symbol_id: str,
    new_code: str,
    expected_sha1: Optional[str] = None,
    reindent: bool = True,
) -> Dict[str, Any]:
    """
    Replace the code for a symbol in-place inside a file.

    Safety:
      - Locates span via AST (not line numbers from a stale map).
      - Optionally checks expected sha1 of the current slice.
      - Reindents new_code to match the original indentation level.

    Returns patch report dict.
    """
    sid = parse_symbol_id(symbol_id)
    src = _read_text(file_path)
    span = locate_symbol_span(src, sid)
    lines = src.splitlines()

    current_slice = "\n".join(lines[span.start_line - 1 : span.end_line])
    # Keep newline behavior consistent with file ending where possible
    if src.endswith("\n"):
        current_slice += "\n"

    cur_sha1 = sha1_text(current_slice)
    if expected_sha1 and expected_sha1 != cur_sha1:
        raise ValueError(
            f"SHA1 mismatch for {symbol_id} in {file_path}. "
            f"expected={expected_sha1} current={cur_sha1}"
        )

    # Determine indentation from first line of current slice
    orig_indent = _detect_indent(lines[span.start_line - 1]) if (span.start_line - 1) < len(lines) else ""
    patched_code = reindent_to(new_code, orig_indent) if reindent else new_code

    # Replace within lines
    patched_lines = lines[: span.start_line - 1] + patched_code.splitlines() + lines[span.end_line :]

    out_text = "\n".join(patched_lines)
    # Preserve trailing newline if original had it OR patched_code ends with newline
    if src.endswith("\n") or patched_code.endswith("\n"):
        out_text += "\n"

    _write_text(file_path, out_text)

    return {
        "op": "replace",
        "file": str(file_path),
        "symbol_id": symbol_id,
        "span": {"start_line": span.start_line, "end_line": span.end_line},
        "old_sha1": cur_sha1,
        "new_sha1": sha1_text(patched_code),
    }


def default_leaf_path(symbol_id: str) -> str:
    """
    Filesystem-safe leaf path, relative to repo root.
    """
    safe = symbol_id.replace(":", "__").replace("/", "_")
    return f"desc/leaves/{safe}.py"


def write_leaf(repo_root: Path, symbol_id: str, code: str, leaf_relpath: Optional[str] = None) -> str:
    leaf_relpath = leaf_relpath or default_leaf_path(symbol_id)
    leaf_path = repo_root / leaf_relpath
    header = f"# symbol_id: {symbol_id}\n"
    content = header + code if code.startswith("#") else header + code
    _write_text(leaf_path, content if content.endswith("\n") else content + "\n")
    return leaf_relpath

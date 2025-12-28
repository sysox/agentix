# ChangeSet automation (MVP)

This directory provides a minimal mechanism to apply code edits **by symbol_id** (not line numbers)
and optionally write/update **leaf code** files for deterministic reconstruction.

## How it works

1. A ChangeSet JSON lists operations targeting `symbol_id` (e.g. `py:method:kernel.runner.Runner.execute`).
2. The tool locates the unit in the target file using Python AST (`lineno/end_lineno`).
3. It optionally checks an `expected_sha1` of the current code slice.
4. It replaces the slice, reindenting the provided code to match existing indentation.
5. Optionally writes `desc/leaves/...` and updates `desc/SYMBOLS.yaml` with the leaf pointer.

## Run

From repo root:

```bash
python3 -m kernel.tools.apply_changeset path/to/changeset.json
```

## ChangeSet format (JSON)

```json
{
  "version": "0.1",
  "ops": [
    {
      "op": "replace",
      "symbol_id": "py:function:kernel.policy.allow_action",
      "expected_sha1": null,
      "new_code": "def allow_action(action, ctx):\n    return True\n",
      "write_leaf": true,
      "leaf_path": null
    }
  ]
}
```

Notes:
- `expected_sha1` is optional but recommended once you start using this routinely.
- `leaf_path` is optional; if omitted, a default path under `desc/leaves/` is used.

## Limitations (MVP)

- Only `replace` is implemented.
- Supports locating modules/classes/functions/methods.
- Constants/assignments and block-level edits are not included yet.

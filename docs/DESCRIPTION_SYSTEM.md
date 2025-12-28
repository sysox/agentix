# Description System (Codemap + Leaves)

This document specifies the **project description system** used to (a) navigate the codebase efficiently,
(b) resume work without loading the entire repository into context, and (c) reconstruct **exact code**
deterministically for selected units.

This is intentionally simple and file-based.

## Goals

### Efficient
- Every described unit has at least:
  - **text description** (`desc_short`)
  - **signature** (for callables) + parameters list
- The description is **progressively loadable**: you can load only the top-level view and pull deeper
  details only when needed.
- Short units should be stored as code leaves when that is smaller/more faithful than prose.

### Complete (selective)
- Deterministic “same code” reconstruction is guaranteed **only** for units that have an attached
  **leaf code file**.
- Reconstruction must not depend on LLM generation (temperature is irrelevant if leaf code is present).

## Non-goals
- Full AST reprint of every file as a single monolith
- A bespoke database for indexing code
- Automatic refactoring (rename/move) without explicit tooling

## Terminology
- **Unit / Symbol**: A named code entity (module, class, function, method, constant).
- **Codemap**: The structured, partial-loadable description (FILES + SYMBOLS + PROJECT).
- **Leaf**: A file containing **exact code** for a unit. Used for deterministic reconstruction.
- **Spine**: The minimal set of modules/units required to understand and modify the main execution flow.

## Storage layout (repo-tracked)

```
desc/
  PROJECT.md         # concise project summary for “resume tomorrow”
  FILES.yaml         # file → purpose/imports/units
  SYMBOLS.yaml       # symbol_id → desc + signature/params + optional leaf pointer
  leaves/            # exact code for selected units (deterministic reconstruction)
```

## Stable identity (symbol_id)

Units are addressed by stable IDs, never by line numbers.

### ID scheme
- Module:   `py:module:<module>`
- Class:    `py:class:<module>.<ClassName>`
- Function: `py:function:<module>.<function_name>`
- Method:   `py:method:<module>.<ClassName>.<method_name>`
- Const:    `py:const:<module>.<NAME>`

Examples:
- `py:module:kernel.runner`
- `py:class:kernel.runner.Runner`
- `py:method:kernel.runner.Runner.execute`
- `py:function:kernel.policy.allow_action`
- `py:const:kernel.pricing.DEFAULT_MODEL`

### Why not line numbers?
Line numbers change whenever code changes. IDs remain stable and allow unambiguous targeting during edits
and discussion.

## Required fields per unit

All units must have a short text description. Callables must have signature + params.

### Minimal unit record (SYMBOLS.yaml)

```yaml
py:method:kernel.runner.Runner.execute:
  kind: method
  file: kernel/runner.py
  signature: "(self, task, ctx) -> Run"
  params:
    - {name: task, type: TaskSpec, desc: ""}
    - {name: ctx,  type: ExecutionContext, desc: ""}
  desc_short: "Executes a supervised agent run step and persists artifacts."
  leaf: null
```

Notes:
- `type` and param `desc` can be empty initially.
- `signature` is required for functions/methods; omit/leave null for modules/classes/constants.

## FILES.yaml structure

FILES.yaml provides the progressive “directory view” and a stable set of entry points for exploration.

```yaml
files:
  kernel/runner.py:
    module: kernel.runner
    purpose: "Run orchestration."
    imports: [...]
    units:
      - id: py:class:kernel.runner.Runner
      - id: py:method:kernel.runner.Runner.execute
      - id: py:method:kernel.runner.Runner._run_agent
```

## Leaves (exact code)

A leaf is a file storing the exact code for a unit. Leaves enable deterministic reconstruction.

### Leaf naming
Use a filesystem-safe name derived from symbol_id, e.g.:
- `desc/leaves/py__method__kernel.runner.Runner.execute.py`

### Leaf format
Leaf files should contain:
- a comment header with `symbol_id` (and optionally `sha1`)
- the exact code block for that unit

Example:

```py
# symbol_id: py:method:kernel.runner.Runner.execute
# sha1: optional
def execute(self, task, ctx) -> "Run":
    ...
```

### Selective completeness
You do **not** need leaves for everything. Start with the spine (core flow), and add leaves for any unit you:
- plan to modify
- use as a stable reference point
- need to reconstruct deterministically

## Progressive loading strategy (how to use this)

Typical “resume tomorrow” process:
1. Load `desc/PROJECT.md` (overview + invariants + main flows).
2. Load only the relevant file entry from `desc/FILES.yaml`.
3. Load the handful of symbols from `desc/SYMBOLS.yaml`.
4. If you need exact behavior, load `desc/leaves/...` for those units.

## Update workflow (manual now; automatable later)

### When code changes
1. Update the source file(s) (`kernel/...`).
2. Update `desc/SYMBOLS.yaml`:
   - if signature/params changed
   - if `desc_short` needs adjustment
3. If the unit is “complete”, update its leaf code file.

Later we will implement a tool to sync leaf ↔ source, but this spec is valid without automation.

## Recommended initial spine

Start storing leaves for these core units first:

- `kernel/runner.py`
  - `py:method:kernel.runner.Runner.execute`
  - `py:method:kernel.runner.Runner._run_agent`
- `kernel/supervisor.py`
  - `py:method:kernel.supervisor.Supervisor.start_run`
  - `py:method:kernel.supervisor.Supervisor.maybe_auto_approve`
- `kernel/agent.py`
  - `py:method:kernel.agent.Agent.call_llm`
- `kernel/llm.py`
  - `py:method:kernel.llm.LLM.complete`
- `kernel/run_store.py`
  - `py:method:kernel.run_store.RunStore.save`
  - `py:method:kernel.run_store.RunStore.load`

This provides deterministic reconstruction for the main execution path.

## Future extensions (optional)
- Add “block map” for exact per-file reconstruction (ordered blocks).
- Add reverse index: symbol → callers/callees.
- Add ChangeSet/apply tooling that patches by symbol_id + expected hash.
- Support non-Python assets (YAML, MD) as units with similar IDs.

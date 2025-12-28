# Agentix — Project Overview

Agentix is a minimal, file-based agent execution + governance kernel. It is designed to be
**understood**, **auditable**, and **reproducible**, with an explicit evolution loop that
creates new agent versions without overwriting old ones.

This file is the canonical entrypoint to the documentation.

## Goals

- **Explicit behavior and interfaces**: agents are defined declaratively (YAML) and executed through a small kernel.
- **Reproducibility**: every run is captured as artifacts on disk (inputs, outputs, traces).
- **Governance-first autonomy**: tool use, approvals, and evolution are constrained by policy.
- **Incremental evolution**: improve agents by creating new versions and pruning/archiving old ones.

## Non-goals

- A complex distributed orchestration platform
- Hidden state or “magic” side channels
- Self-modifying agents without policy gates

(See `docs/DESIGN.md` for deeper rationale.)

## Repository layout

- `agents/` — agent definitions (YAML). Stable identities (e.g., `coder`) with explicit versions.
- `agents/archive/` — archived older agent versions.
- `kernel/` — execution, governance, evolution, persistence, tooling.
- `runs/` — immutable run artifacts (audit + reproducibility).
- `docs/` — documentation set (this file + deep dives).

## Core invariants (the rules)

1. **Immutable runs**  
   Executions produce append-only run artifacts. Runs are not mutated after recording.

2. **Stable identity; explicit versioning**  
   Agent identity is stable; evolution produces versioned artifacts (never overwrites “current history”).

3. **Append-only evolution**  
   Evolution creates a new agent version; pruning archives old versions, never deletes history silently.

4. **Policy-governed autonomy**  
   Tool access, approvals, and evolution are constrained by explicit policy/governance configuration.

5. **No hidden state**  
   State is either explicit in-memory or persisted as files in the repository (`agents/`, `runs/`, `knowledge/`, etc.).

6. **Simple over clever**  
   Prefer clarity and debuggability over abstraction. Keep the kernel small and explicit.

## High-level flows

### Runtime flow (one supervised run)

Typical execution path:

- CLI entrypoint
  → load agent spec (registry)
  → create/load `Run`
  → `Supervisor` starts/continues the run
  → `Runner` executes the agent step(s)
  → `Agent` calls the `LLM`
  → proposals/actions may require approval or be gated by policy
  → persist artifacts to `runs/`

### Evolution flow (one evolution step)

- evaluate current agent output (fitness)
  → propose mutation(s)
  → check evolution policy constraints
  → write new versioned YAML (append-only)
  → optionally prune/archive older versions

## Agent contract (what an “agent” is)

Agents are *data-defined*. A YAML definition typically specifies:
- identity + version
- role/goal/description
- model + pricing configuration
- tool allowlist
- interaction mode (who can talk to user, when approvals are needed)
- evaluation signals (fitness inputs)

Important constraints:
- Agents do not own long-term memory; persistence is managed by the system.
- Agents are not allowed to self-modify directly; evolution is mediated by governance + policies.
- Tool use is constrained and auditable.

See `docs/agent_contract.md` (consider renaming to `AGENT_CONTRACT.md`) for the full contract.

## Where to read next

- `docs/DESIGN.md` — design principles, tradeoffs, non-goals
- `docs/ARCHITECTURE.md` — component responsibilities and detailed flows
- `docs/agent_contract.md` — agent schema + behavioral contract
- `docs/governance.md` — approvals/autonomy, safety rules, policy gates
- `docs/registry.md` — loading agent YAML, spec structure
- `docs/USER_GUIDE.md` — installation and usage examples
- `docs/CONTRIBUTING.md` — development workflow and contribution rules

default load: FILES_SPINE.yaml + SYMBOLS_SPINE.yaml
load FULL only when needed (we’ll add later)
when editing: prefer leaf + ChangeSet by symbol_id

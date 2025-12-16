# Agentix Design Decisions

This document explains *why* Agentix is designed the way it is.

## Core Goals

- Explicit behavior
- Deterministic execution
- Bounded autonomous evolution
- Reproducibility

## Key Design Decisions

### Immutable Runs
Each execution produces an immutable run directory.
This allows perfect reproducibility and debugging.

### Stable Agent Identity
Agent identity (e.g. `coder`) is stable.
Versions are separate artifacts (`coder_vX.Y`).

### Append-Only Evolution
Agents are never overwritten.
Evolution always creates a new version.

### Policy-Governed Autonomy
Evolution is gated by explicit policies:
- score thresholds
- maximum versions
- pruning rules

No agent can evolve itself freely.

### No Hidden State
All state is either:
- on disk (agents/, runs/)
- or explicit in memory

There is no global mutable state.

### Simple Over Clever
The system prefers:
- YAML over databases
- files over services
- clarity over abstraction

## Non-Goals

- Online learning
- Reinforcement learning
- Black-box optimization
- Unbounded self-modification

These can be layered later if desired.

## Summary

Agentix is intentionally minimal.
It is designed to be *understood*, *extended*, and *trusted*.

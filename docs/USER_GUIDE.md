# Agentix User Guide

This guide explains how to *use* Agentix.

## Installation

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.lock
```

## Running an Agent

```bash
python cli.py coder "write hello world"
```

## Inspecting a Run

Each run creates a directory in `runs/`.

Typical files:
- input.json
- output.json
- evaluation.json
- metadata.json
- prompt.txt
- trace.log

Inspect output:
```bash
cat runs/<run_id>/output.json
```

## Controlling Evolution

Evolution depends on evaluator score.

To force evolution (testing only):
```bash
export AGENTIX_FORCE_EVOLVE=1
```

To disable evolution:
- ensure evaluator returns score >= policy threshold

## Agent Versions

List agents:
```bash
ls agents
```

Run a specific version:
```bash
python cli.py coder_v0.10 "task"
```

## Pruning

Pruning runs automatically after evolution.
Older versions are moved to:
```
agents/archive/
```

## Testing

```bash
python test_agentix.py
```

## CI

CI runs tests automatically on push and PR.

## Best Practices

- Do not commit `runs/`
- Do not commit `.venv/`
- Commit after stable milestones
- Keep evaluator simple and explicit

## Troubleshooting

If evolution does not trigger:
- check evaluator score
- check policy thresholds
- verify correct agent ID is used

---

Agentix is designed to be predictable.
If something happens, it should be visible on disk.

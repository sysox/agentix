# Agentix

Agentix is a minimal, autonomous, evolvable agent system written in Python.

It provides a complete lifecycle for agents:
- execution via CLI
- LLM-backed reasoning (stub or real)
- evaluation and fitness scoring
- controlled evolution (mutation + policy)
- automatic pruning and archiving
- full execution tracing
- continuous integration testing

The system is designed to be explicit, reproducible, and bounded.

---

## Architecture Overview

```
CLI
 ↓
Runner ──→ LLM
  │        │
  │        ↓
  │     Response
  │
  ├─→ Evaluator ──→ score
  │
  └─→ Evolver ──→ mutate → version → prune
           │
           └─→ archive
```

---

## Directory Structure

```
agentix/
├── agents/
│   ├── coder.yaml
│   ├── coder_v0.9.yaml
│   ├── coder_v0.10.yaml
│   └── archive/
│       ├── coder_v0.1.yaml
│       ├── coder_v0.2.yaml
│       └── ...
├── kernel/
│   ├── runner.py
│   ├── context.py
│   ├── llm.py
│   ├── evaluator.py
│   ├── evolver.py
│   ├── evolve.py
│   ├── mutator.py
│   ├── policy.py
│   ├── pruner.py
│   ├── registry.py
│   └── tools/
│       ├── base.py
│       └── filesystem.py
├── cli.py
├── test_agentix.py
├── requirements.lock
├── README.md
└── .github/workflows/ci.yml
```

---

## Agents

Agents are defined as YAML files in the `agents/` directory.

Example: `agents/coder.yaml`

```yaml
role: Code generation agent
description: >
  Generates correct, readable, maintainable code.

prompt: |
  You are a senior Python engineer.
  Follow best practices.

tools:
  - filesystem.read
  - filesystem.write

metadata:
  version: 0.0
```

Each evolution creates a new versioned file:

```
coder_v0.1.yaml
coder_v0.2.yaml
coder_v0.3.yaml
```

The base agent (`coder.yaml`) is never modified.

---

## Running an Agent

```bash
python cli.py coder "write hello world"
```

Each run creates an immutable directory under `runs/`:

```
runs/
└── coder_YYYYMMDD_HHMMSS_xxxxxx/
    ├── input.json
    ├── output.json
    ├── evaluation.json
    ├── metadata.json
    ├── prompt.txt
    └── trace.log
```

These directories are runtime artifacts and should not be committed.

---

## LLM Modes

By default, Agentix runs in stub mode.

To enable a real LLM:

```bash
export AGENTIX_LLM_MODE=openai
export OPENAI_API_KEY=sk-...
```

---

## Evaluation

Each run is evaluated by `Evaluator`, producing a fitness signal:

```json
{
  "score": 1.0,
  "reasons": ["non_empty_response"]
}
```

---

## Evolution

Evolution is controlled by:
- Mutator
- EvolutionPolicy
- Evolver
- Pruner

Evolution is append-only and bounded by policy.

---

## Pruning and Archiving

Old agent versions are moved to:

```
agents/archive/
```

Nothing is deleted.

---

## Testing

```bash
python test_agentix.py
```

---

## Git Hygiene

Ignored:
- .venv/
- runs/

Tracked:
- source code
- agent definitions
- CI configuration

---

## Status

Agentix is functionally complete.

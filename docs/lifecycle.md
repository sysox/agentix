# Agent Lifecycle

## Purpose

This document defines the lifecycle of agents in the agentix system.
It describes how agents are created, executed, evaluated, evolved, and retired.

This is a conceptual description without implementation details.

---

## Key Distinction

The system distinguishes between:

- Agent blueprint (persistent definition)
- Agent instance (single execution)

Only agent instances execute.
Only blueprints persist.

---

## Lifecycle Overview

1. Task request is received
2. Kernel selects an agent blueprint
3. Agent instance is created
4. Agent instance executes the task
5. Execution is evaluated
6. Results are harvested
7. Agent instance is destroyed

---

## Creation

Agent instances are created by the kernel based on:
- task type
- available blueprints
- resource constraints
- past evaluation results

Agent instances start with:
- task description
- injected relevant knowledge
- execution limits

---

## Execution

During execution an agent instance may:
- call tools
- read shared knowledge
- produce outputs

Agent instances may not:
- write persistent memory directly
- modify system policies
- spawn new agents

---

## Evaluation

Every execution is evaluated.

Evaluation produces structured metrics describing:
- task success
- resource usage
- reliability
- reuse potential

Evaluation results are stored by the system.

---

## Harvesting

After evaluation:
- useful information is extracted
- knowledge artifacts may be created or updated
- metrics are recorded

Harvesting is explicit and controlled.

---

## Destruction

After harvesting:
- agent instance is terminated
- all ephemeral context is discarded

This is intentional and mandatory.

---

## Evolution

Agent blueprints may evolve based on:
- aggregated evaluation results
- detected inefficiencies
- proposed improvements

Evolution results in a new blueprint version.
Older versions may be archived.

---

## Retirement

Agent blueprints may be retired if:
- consistently low performance
- no longer used
- superseded by better versions

Retirement does not delete knowledge.

---

## Status

This document defines lifecycle version v0.1.
All rules may be refined.

# Architecture

## Purpose

This document defines the conceptual architecture of the agentix system.
It intentionally avoids implementation details.

The goal is to establish clear boundaries, responsibilities, and terminology
before any code is written.

---

## Core Principles

- Agents are execution policies, not autonomous beings
- Agent instances are ephemeral; knowledge is persistent
- Evaluation drives evolution
- Resource constraints are first-class concerns
- Improvement is allowed only when justified by measured benefit

---

## High-Level Components

The system is composed of the following conceptual components:

- Kernel (orchestrator and policy enforcer)
- Agent blueprints (persistent definitions)
- Agent instances (ephemeral executions)
- Knowledge store (compressed, reusable artifacts)
- Evaluation mechanism (scoring and selection)

---

## Kernel

The kernel is responsible for:
- task routing
- agent lifecycle management
- resource enforcement
- permission gating

The kernel is non-evolving by design.

---

## Agents

An agent is defined by:
- a purpose
- a prompt or policy
- a set of tools
- access to shared knowledge

Agents do not own long-term memory.

---

## Agent Instances vs Blueprints

- An agent blueprint is a reusable definition
- An agent instance is a single execution of a blueprint

Agent instances are created, evaluated, and destroyed.

---

## Knowledge

Knowledge is stored separately from agents and consists of:
- summaries
- rules
- code snippets
- decision heuristics

Knowledge must be periodically compressed or discarded.

---

## Evaluation

Every agent execution is evaluated.
Evaluation produces structured scores rather than free-form text.

Evaluation results influence:
- reuse decisions
- blueprint evolution
- agent retirement

---

## Non-Goals

The system explicitly does not aim to:
- train or fine-tune language models
- achieve general intelligence
- allow uncontrolled self-modification

---

## Status

This document defines version v0.1 of the architecture.
All sections are subject to revision.

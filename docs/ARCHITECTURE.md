# Agentix Architecture

This document describes the internal architecture of Agentix.

## Core Flow

CLI → Runner → LLM → Evaluator → Evolver → Pruner

Each component has a single responsibility.

## Key Components

- Runner: orchestrates a single execution
- ExecutionContext: immutable run artifacts
- LLM: stub or real language model interface
- Evaluator: produces fitness score
- Evolver: applies mutation under policy
- Pruner: archives old agent versions

## Design Rules

- No hidden state
- Append-only evolution
- Base agent identity is stable
- Versions are explicit

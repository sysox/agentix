"""
Agent Runner (Placeholder)

Executes exactly one agent once.

Does NOT:
- chain agents
- evaluate results
- retry or loop
"""
from kernel.context import ExecutionContext
from kernel.spec import AgentSpec


def run_agent(
    spec: AgentSpec,
    task: dict,
    context: ExecutionContext
) -> dict:
    context.log(f"Running agent: {spec.id}")
    context.log("Execution stub – no logic implemented")

    return {
        "status": "NOT_IMPLEMENTED",
        "agent": spec.id,
        "version": spec.version,
    }

"""
CLI Entry Point for agentix

Usage:
    python cli.py <agent_id> <task>

Example:
    python cli.py coder "implement agent registry"
"""

import sys
from kernel.registry import AgentRegistry
from kernel.context import ExecutionContext
from kernel.runner import run_agent


def usage() -> None:
    print("Usage: python cli.py <agent_id> <task>")
    sys.exit(1)


def main() -> None:
    # --- parse arguments ---
    if len(sys.argv) < 3:
        usage()

    agent_id = sys.argv[1]
    task_text = " ".join(sys.argv[2:])  # preserve spaces

    # --- load agent spec ---
    registry = AgentRegistry()
    try:
        spec = registry.load(agent_id)
    except Exception as e:
        print(f"[agentix] Failed to load agent '{agent_id}': {e}")
        sys.exit(2)

    # --- create execution context ---
    ctx = ExecutionContext(agent_id=agent_id)

    # --- write input ---
    task = {
        "task": task_text,
    }
    ctx.write_input(task)

    # --- run agent ---
    try:
        output = run_agent(spec, task, ctx)
    except Exception as e:
        ctx.write_error(str(e))
        ctx.finalize()
        print(f"[agentix] Run failed: {e}")
        sys.exit(3)

    # --- write output ---
    ctx.write_output(output)
    ctx.finalize()

    # --- report ---
    print(f"[agentix] Run completed")
    print(f"[agentix] agent_id = {agent_id}")
    print(f"[agentix] run_id   = {ctx.run_id}")


if __name__ == "__main__":
    main()

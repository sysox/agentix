"""
CLI Entry Point (Placeholder)

Future responsibilities:
- load agents
- execute runs
- manage traces
"""
import sys
from kernel.registry import AgentRegistry
from kernel.context import ExecutionContext
from kernel.runner import run_agent


def main():
    if len(sys.argv) < 3:
        print("Usage: python cli.py <agent_id> <task>")
        sys.exit(1)

    agent_id = sys.argv[1]
    task_text = sys.argv[2]

    registry = AgentRegistry()
    spec = registry.load(agent_id)

    ctx = ExecutionContext(agent_id)

    task = {"task": task_text}
    ctx.write_input(task)

    output = run_agent(spec, task, ctx)
    ctx.write_output(output)

    ctx.finalize()

    print(f"Run completed: {ctx.run_id}")


if __name__ == "__main__":
    main()

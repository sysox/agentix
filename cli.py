"""
CLI Entry Point for agentix
"""

import sys

from kernel.registry import AgentRegistry
from kernel.context import ExecutionContext
from kernel.runner import run_agent


def usage() -> None:
    print("Usage: python cli.py <agent_id|orchestrated> <task>")
    sys.exit(1)


def main() -> None:
    if len(sys.argv) < 3:
        usage()

    mode = sys.argv[1]
    task_text = " ".join(sys.argv[2:])

    # --- ORCHESTRATED MODE ---
    if mode == "orchestrated":
        from kernel.orchestration import run_orchestrated_task

        ctx = ExecutionContext(agent_id="orchestrated")
        try:
            run_orchestrated_task(task_text, ctx)
            ctx.finalize()
        except Exception as e:
            ctx.write_error(str(e))
            ctx.finalize()
            print(f"[agentix] Orchestrated run failed: {e}")
            sys.exit(3)

        print("[agentix] Orchestrated run completed")
        print(f"[agentix] run_id = {ctx.run_id}")
        return

    # --- SINGLE AGENT MODE ---
    registry = AgentRegistry()
    try:
        spec = registry.load(mode)
    except Exception as e:
        print(f"[agentix] Failed to load agent '{mode}': {e}")
        sys.exit(2)

    ctx = ExecutionContext(agent_id=mode)

    task = {"task": task_text}
    ctx.write_input(task)

    try:
        output = run_agent(spec, task, ctx)
    except Exception as e:
        ctx.write_error(str(e))
        ctx.finalize()
        print(f"[agentix] Run failed: {e}")
        sys.exit(3)

    ctx.write_output(output)
    ctx.finalize()

    print("[agentix] Run completed")
    print(f"[agentix] agent_id = {mode}")
    print(f"[agentix] run_id   = {ctx.run_id}")


if __name__ == "__main__":
    main()

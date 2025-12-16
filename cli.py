"""
CLI Entry Point for agentix
"""

import sys

from kernel.registry import AgentRegistry
from kernel.context import ExecutionContext
from kernel.runner import run_agent
from kernel.proposals import ProposalManager



def usage():
    print("Usage:")
    print("  python cli.py <agent_id> <task>")
    print("  python cli.py proposals")
    print("  python cli.py approve <agent_id_vX>")
    print("  python cli.py reject <agent_id_vX>")
    sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        usage()

    mode = sys.argv[1]

    # --- proposal management ---
    if mode in {"proposals", "approve", "reject"}:
        pm = ProposalManager()

        if mode == "proposals":
            props = pm.list_proposals()
            if not props:
                print("[agentix] No proposed agents")
            else:
                print("[agentix] Proposed agents:")
                for p in props:
                    print(" ", p)
            return

        if len(sys.argv) != 3:
            usage()

        agent_id = sys.argv[2]

        if mode == "approve":
            pm.approve(agent_id)
            print(f"[agentix] Approved {agent_id}")
            return

        if mode == "reject":
            pm.reject(agent_id)
            print(f"[agentix] Rejected {agent_id}")
            return

    # --- ORCHESTRATED MODE ---
    if mode == "orchestrated":
        if len(sys.argv) < 3:
            usage()

        task_text = " ".join(sys.argv[2:])
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
    if len(sys.argv) < 3:
        usage()

    task_text = " ".join(sys.argv[2:])

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

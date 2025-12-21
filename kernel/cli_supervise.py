import sys

from kernel.run import create_run, RunState
from kernel.supervisor import Supervisor
from kernel.registry import load_agent  # adjust if name differs

import sys
from pathlib import Path

# Ensure repo root is on sys.path when running as a script
ROOT = Path(__file__).resolve().parents[1]  # ../ (repo root)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    supervisor = Supervisor()

    print("agentix supervisor")
    print("------------------")

    run = None  # last run in this session (for 'action' inspection)

    while True:
        cmd = input("> ").strip()

        if cmd in {"exit", "quit"}:
            break

        elif cmd.startswith("run "):
            _, agent_id, *task = cmd.split()
            task = " ".join(task)

            agent = load_agent(agent_id)
            run = create_run(task)

            run = supervisor.start_run(agent, run)
            print(f"run {run.run_id} -> {run.state.value}")

            # ✅ If paused, optionally auto-approve safe YAML proposals (controlled autonomy)
            if run.state == RunState.WAITING_FOR_APPROVAL:
                approved = supervisor.maybe_auto_approve()
                if approved:
                    print("auto-approved:", ", ".join(approved))

        elif cmd == "proposals":
            props = supervisor.list_proposals()
            if not props:
                print("no pending proposals")
            else:
                for p in props:
                    print(" -", p)

        elif cmd == "action":
            if run is None:
                print("no run yet")
                continue
            action = supervisor.get_pending_action(run)
            if not action:
                print("no pending action")
                continue

            print("PENDING ACTION")
            print("--------------")
            print(f"action : {action.action}")
            print(f"risk   : {action.risk}")
            print(f"reason : {action.reason}")
            print("payload:")
            for k, v in action.payload.items():
                print(f"  {k}: {v}")

        elif cmd.startswith("approve "):
            _, agent_id = cmd.split()
            supervisor.approve(agent_id)
            print(f"approved {agent_id}")

        elif cmd.startswith("reject "):
            _, agent_id = cmd.split()
            supervisor.reject(agent_id)
            print(f"rejected {agent_id}")

        else:
            print("commands:")
            print("  run <agent_id> <task>")
            print("  proposals")
            print("  action              # show pending system action (if any)")
            print("  approve <agent_id>")
            print("  reject <agent_id>")
            print("  exit")


if __name__ == "__main__":
    main()

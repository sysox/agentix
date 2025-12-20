import sys

from kernel.run import create_run, RunState
from kernel.supervisor import Supervisor
from kernel.registry import load_agent  # adjust if name differs


def main():
    supervisor = Supervisor()

    print("agentix supervisor")
    print("------------------")

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

        elif cmd == "proposals":
            props = supervisor.list_proposals()
            if not props:
                print("no pending proposals")
            for p in props:
                print(" -", p)

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
            print("  approve <agent_id>")
            print("  reject <agent_id>")
            print("  exit")


if __name__ == "__main__":
    main()

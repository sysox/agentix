from typing import List, Dict
import yaml

from kernel.registry import AgentRegistry
from kernel.runner import run_agent
from kernel.context import ExecutionContext


PLAN_MARKER = "PLAN:"


def extract_plan_yaml(text: str) -> str:
    """
    Extract YAML part after PLAN: marker.
    """
    if PLAN_MARKER not in text:
        raise RuntimeError("Missing PLAN: marker in orchestrator output")

    return text.split(PLAN_MARKER, 1)[1].strip()


def parse_plan_yaml(yaml_text: str) -> List[Dict[str, str]]:
    """
    Parse YAML plan into list of steps.
    """
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        raise RuntimeError(f"Invalid YAML plan: {e}")

    if not isinstance(data, dict) or "steps" not in data:
        raise RuntimeError("Plan YAML must contain 'steps'")

    steps = data["steps"]
    if not isinstance(steps, list):
        raise RuntimeError("'steps' must be a list")

    for step in steps:
        for key in ("agent", "purpose", "output"):
            if key not in step:
                raise RuntimeError(f"Missing '{key}' in step: {step}")

    return steps

def run_orchestrated_task(
    task: str,
    context: ExecutionContext,
) -> None:
    """
    Execute a task using orchestrator + sequential agent execution.
    """

    registry = AgentRegistry()

    # --- 1. Run orchestrator ---
    orch_spec = registry.load("orchestrator")
    orch_output = run_agent(
        orch_spec,
        {"task": task},
        context,
    )

    plan_text = orch_output.get("response", "")
    context.log("Orchestrator output received")

    yaml_text = extract_plan_yaml(plan_text)
    steps = parse_plan_yaml(yaml_text)

    memory_text = context.load_knowledge(task, limit=5)

    # --- 2. Execute steps sequentially ---
    shared_context = f"TASK:\n{task}\n"

    for idx, step in enumerate(steps, start=1):
        agent_id = step["agent"]

        if agent_id == "orchestrator":
            raise RuntimeError("Orchestrator cannot call itself")

        spec = registry.load_best(agent_id)

        step_task = {
            "task": task,
            "purpose": step["purpose"],
            "context": shared_context,
        }

        if memory_text:
            step_task["memory"] = memory_text

        context.log(f"Step {idx}: running {agent_id}")
        output = run_agent(spec, step_task, context)

        response = output.get("response", "")

        if agent_id in ("summarizer", "reflector"):
            context.write_knowledge(agent_id, response)

        shared_context += (
            f"\n\nSTEP {idx} ({agent_id} OUTPUT):\n{response}"
        )
    from kernel.memory import MemoryPruner

    pruner = MemoryPruner()
    pruner.prune(
        context.knowledge_dir,
        context.used_knowledge,
    )
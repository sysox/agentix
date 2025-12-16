from typing import Any, Dict

from kernel.context import ExecutionContext
from kernel.registry import AgentSpec
from kernel.llm import LLM
from kernel.evaluator import Evaluator
from kernel.evolver import Evolver

from pathlib import Path
from kernel.registry import AgentRegistry


def load_latest_agent(agent_id: str) -> AgentSpec:
    reg = AgentRegistry()
    versions = sorted(
        Path("agents").glob(f"{agent_id}_v*.yaml"),
        key=lambda p: p.stem,
    )
    if not versions:
        return reg.load(agent_id)
    return reg.load(versions[-1].stem)

def run_agent(
    spec: AgentSpec,
    task: Dict[str, Any],
    context: ExecutionContext,
) -> Dict[str, Any]:

    context.log(f"Running agent: {spec.agent_id}")

    # prompt
    prompt = _build_prompt(spec, task)
    context.write_prompt(prompt)
    context.log("Prompt written")

    # LLM
    llm = LLM()
    context.log(f"LLM mode: {llm.mode}")

    response = llm.complete(prompt)
    context.log("LLM completed")

    output = {
        "agent_id": spec.agent_id,
        "role": spec.role,
        "task": task,
        "response": response,
    }

    # evaluation
    evaluator = Evaluator()
    evaluation = evaluator.evaluate(spec, task, output)
    context.write_evaluation(evaluation)
    context.log(f"Evaluation score: {evaluation['score']}")

    output["evaluation"] = evaluation

    # evolution hook (CHAINED)
    evolver = Evolver()
    base_spec = load_latest_agent(spec.agent_id)
    evolved_spec = evolver.evolve(base_spec, evaluation)

    metadata = {
        "agent_id": spec.agent_id,
        "evolved_agent": evolved_spec.agent_id
        if evolved_spec.agent_id != spec.agent_id
        else None,
    }
    context.write_metadata(metadata)

    if metadata["evolved_agent"]:
        context.log(f"Evolved agent created: {metadata['evolved_agent']}")

    return output


def _build_prompt(spec: AgentSpec, task: Dict[str, Any]) -> str:
    parts = [spec.prompt, ""]

    if "task" in task:
        parts.append("TASK:")
        parts.append(task["task"])
        parts.append("")

    if "purpose" in task:
        parts.append("PURPOSE:")
        parts.append(task["purpose"])
        parts.append("")

    if "memory" in task:
        parts.append("PAST KNOWLEDGE:")
        parts.append(task["memory"])
        parts.append("")

    if "context" in task:
        parts.append("CURRENT CONTEXT:")
        parts.append(task["context"])

    return "\n".join(parts)

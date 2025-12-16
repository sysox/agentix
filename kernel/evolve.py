from copy import deepcopy
from datetime import datetime
from pathlib import Path
import yaml

from kernel.registry import AgentSpec


def evolve_agent(
    spec: AgentSpec,
    mutation: dict,
    agents_dir: Path = Path("agents"),
) -> AgentSpec:
    """
    Create a new evolved agent spec from an existing one.
    Mutation is a partial override dict.
    """

    data = {
        "role": spec.role,
        "description": spec.description,
        "prompt": spec.prompt,
        "tools": spec.tools,
        "limits": spec.limits,
        "metadata": deepcopy(spec.metadata),
    }

    # update version
    old_version = data["metadata"].get("version", "0.0")
    data["metadata"]["parent"] = spec.agent_id
    data["metadata"]["version"] = bump_version(old_version)
    data["metadata"]["evolved_at"] = datetime.utcnow().isoformat()

    # apply mutation
    deep_update(data, mutation)

    # new agent id
    new_id = f"{spec.agent_id}_v{data['metadata']['version']}"
    path = agents_dir / f"{new_id}.yaml"

    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

    return AgentSpec(
        agent_id=new_id,
        role=data["role"],
        description=data["description"],
        prompt=data["prompt"],
        tools=data.get("tools", []),
        limits=data.get("limits", {}),
        metadata=data.get("metadata", {}),
    )


# ------------------------------------------------------------------

def bump_version(version: str) -> str:
    try:
        major, minor = map(int, version.split("."))
        return f"{major}.{minor + 1}"
    except Exception:
        return "0.1"


def deep_update(target: dict, patch: dict):
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            deep_update(target[k], v)
        else:
            target[k] = v

from copy import deepcopy
from datetime import datetime
from pathlib import Path

import yaml

from kernel.registry import AgentSpec
from kernel.governance import Governance
from kernel.approval import pause_for_approval


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def base_agent_id(agent_id: str) -> str:
    """
    Strip version suffix: coder_v0.3 -> coder
    """
    return agent_id.split("_v")[0]


def bump_version(version: str) -> str:
    try:
        major, minor = map(int, version.split("."))
        return f"{major}.{minor + 1}"
    except Exception:
        return "0.1"


def deep_update(target: dict, patch: dict):
    """
    Recursively update dicts.
    """
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            deep_update(target[k], v)
        else:
            target[k] = v


# ---------------------------------------------------------------------------
# evolution
# ---------------------------------------------------------------------------

def evolve_agent(
    spec: AgentSpec,
    mutation: dict,
    run,                       # 🔴 IMPORTANT: run is required for approval
    agents_dir: Path = Path("agents"),
) -> AgentSpec:
    """
    Create a new evolved agent spec from an existing one.

    - prompt-only mutation (via `mutation`)
    - governance-aware
    - versioned, immutable lineage
    - PAUSES execution if proposal is created
    """

    gov = Governance.load()

    # --- governance: evolution disabled ---
    if gov.evolution_mode == "off":
        return spec

    # --- base data ---
    data = {
        "role": spec.role,
        "description": spec.description,
        "prompt": spec.prompt,
        "tools": spec.tools,
        "limits": spec.limits,
        "metadata": deepcopy(spec.metadata),
    }

    # --- versioning ---
    old_version = data["metadata"].get("version", "0.0")
    new_version = bump_version(old_version)

    data["metadata"]["parent"] = spec.agent_id
    data["metadata"]["version"] = new_version
    data["metadata"]["evolved_at"] = datetime.utcnow().isoformat()

    # --- apply mutation ---
    deep_update(data, mutation)

    # --- governance: proposal mode ---
    is_proposal = False
    if gov.evolution_mode == "propose":
        data["metadata"]["status"] = "proposed"
        is_proposal = True

    # --- write new agent file ---
    base_id = base_agent_id(spec.agent_id)
    new_id = f"{base_id}_v{new_version}"
    path = agents_dir / f"{new_id}.yaml"

    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

    # ⛔ KERNEL ENFORCED STOP (AFTER persistence)
    if is_proposal:
        # Cap number of proposals per run (prevents runaway loops)
        if run.proposal_count >= gov.max_proposals_per_run:
            # If we hit the limit, we still pause, but maybe we should log it?
            # For now, just pausing is safe.
            pause_for_approval(run)

        run.proposal_count += 1
        pause_for_approval(run)

    # --- return new spec (may or may not be auto-selected later) ---
    return AgentSpec(
        agent_id=new_id,
        role=data["role"],
        description=data["description"],
        prompt=data["prompt"],
        tools=data.get("tools", []),
        limits=data.get("limits", {}),
        metadata=data.get("metadata", {}),
    )

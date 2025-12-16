from pydantic import BaseModel
from typing import Dict, List


class AgentSpec(BaseModel):
    id: str
    version: str
    status: str

    role: str
    description: str

    inputs: Dict[str, Dict[str, str]]
    outputs: Dict[str, Dict[str, str]]

    tools: Dict[str, List[str]]
    constraints: Dict[str, str]

    fitness_signals: List[str]

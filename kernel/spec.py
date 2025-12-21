from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional


class AgentSpec(BaseModel):
    agent_id: str
    role: str
    description: str = ""
    prompt: str = ""
    tools: List[str] = Field(default_factory=list)
    limits: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

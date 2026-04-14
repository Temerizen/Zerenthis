from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class AgentResponse:
    agent: str
    prompt: str
    output: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self):
        return asdict(self)


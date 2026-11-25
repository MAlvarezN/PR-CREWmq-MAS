"""Agent registry: load agents and their allow-listed tool surface.

Registry fields follow the LEG prototype in Zhao et al. 2026 (Sec. 2.1):
id, kind, graph_data_class, system_prompt, router_capabilities, tool_names.
"""

import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "registry" / "agents.json"


class AgentRegistry:
    def __init__(self, path=REGISTRY_PATH):
        data = json.loads(Path(path).read_text())
        self._agents = {a["id"]: a for a in data["agents"]}

    def get(self, agent_id: str) -> dict:
        return self._agents[agent_id]

    def ids(self):
        return list(self._agents)

    def tools_of(self, agent_id: str) -> list:
        """Allow-listed tool surface for the runtime to enforce."""
        return self._agents[agent_id]["tool_names"]

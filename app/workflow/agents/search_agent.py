
from typing import Dict, Any
from workflow.agents.agent import Agent
from workflow.state import AgentType

class SearchAgent(Agent):
    def __init__(self, session_id: str):
        super().__init__(
            system_prompt="You are a helpful research paper search agent",
            role=AgentType.SEARCH,
            session_id=session_id
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        return "Search for useful research paper based on user query"

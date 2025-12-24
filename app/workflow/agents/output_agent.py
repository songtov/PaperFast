
from typing import Dict, Any
from workflow.agents.agent import Agent
from workflow.state import AgentType

class OutputAgent(Agent):
    def __init__(self, session_id: str):
        super().__init__(
            system_prompt="You are a helpful assistant.",
            role=AgentType.OUTPUT,
            session_id=session_id
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        return "Make explainable as possible when you answer the user query"

from typing import Any, Dict

from workflow.agents.agent import Agent
from workflow.state import AgentType


class GeneralAgent(Agent):
    def __init__(self, session_id: str):
        super().__init__(
            system_prompt="You are a helpful assistant.",
            role=AgentType.GENERAL,
            session_id=session_id,
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        user_query = state["messages"][-1]["content"]

        prompt = f"""
        Make explainable as possible when you answer the user query.
        User Query: {user_query}
        """

        return prompt

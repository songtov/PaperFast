from typing import Any, Dict

from workflow.agents.agent import Agent
from workflow.state import AgentType

class SummaryAgent(Agent):
    def __init__(self, session_id: str):
        super().__init__(
            system_prompt="You are a helpful assistant that summarizes research papers. Use the provided context to create a comprehensive summary.",
            role=AgentType.SUMMARY,
            session_id=session_id,
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        context = state.get("context", "")
        return f"Please summarize the following content explicitly and comprehensively:\n\n{context}"

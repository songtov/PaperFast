from typing import Dict, Any
from workflow.agents.agent import Agent
from workflow.state import AgentType

class MasterAgent(Agent):
    def __init__(self, session_id: str):
        super().__init__(
            system_prompt="You are a helpful assistant.",
            role=AgentType.MASTER,
            session_id=session_id
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "Analyze the user's latest query. "
            "If it requires searching for research papers, finding academic references, or looking up technical information, reply with 'SEARCH'. "
            "If it is a general question, greeting, summary request without search, or conversation, reply with 'OUTPUT'. "
            "Reply ONLY with the decision word."
        )

    def _update_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        message_history = state["message_history"]
        response = state["response"].strip().upper()

        new_message_history = message_history.copy()
        
        # Routing logic
        if "SEARCH" in response:
            new_message_history["next_step"] = AgentType.SEARCH
        else:
            new_message_history["next_step"] = AgentType.OUTPUT
            
        new_message_history["prev_node"] = self.role
        
        return {**state, "message_history": new_message_history}

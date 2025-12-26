from typing import Dict, Any
from workflow.agents.agent import Agent, AgentState
from workflow.state import AgentType
from pydantic import BaseModel, Field
from utils.config import get_llm
from typing import Literal

class RouteDecision(BaseModel):
    """Decision model for routing the conversation."""

    next_step: Literal[AgentType.OUTPUT, AgentType.SEARCH] = Field(
        description="The next agent to route the conversation to."
    )


class MasterAgent(Agent):
    def __init__(self, session_id: str):
        super().__init__(
            system_prompt="You are a helpful assistant.",
            role=AgentType.MASTER,
            session_id=session_id,
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "Analyze the user's latest query. "
            "If it requires searching for research papers, finding academic references, or looking up technical information, route to SEARCH_AGENT. "
            "If it is a general question, greeting, summary request without search, or conversation, route to OUTPUT_AGENT."
        )

    def _generate_response(self, state: AgentState) -> AgentState:
        messages = state["messages"]

        # Use structured output
        llm = get_llm().with_structured_output(RouteDecision)
        response = llm.invoke(messages)

        # Store the Pydantic model directly in the response field for now,
        # or we could store the string representation.
        # But AgentState.response is typed as str in agent.py (usually).
        # Let's check agent.py again.
        # AgentState defines response: str.
        # So we should probably serialize it or handle it carefully.
        # However, _update_state reads it.
        # Let's store the next_step string in response for compatibility?
        # Or better, let's just return the object and handle type mismatch
        # if Python runtime doesn't enforce it strictly (TypedDict doesn't at runtime).
        # To be safe and clean, let's keep it as an object here effectively
        # but technically we might want to adjust AgentState if we want strict typing.
        # For this refactor, I will return the next_step string as the response
        # so it stays compatible with string-based expectations elsewhere if any
        # (though duplicate check is unique to MasterAgent logic mostly).

        return {**state, "response": response}

    def _update_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        message_history = state["message_history"]
        # response is now a RouteDecision object
        decision: RouteDecision = state["response"]

        new_message_history = message_history.copy()

        # Routing logic using the structured object
        new_message_history["next_step"] = decision.next_step

        new_message_history["prev_node"] = self.role

        return {**state, "message_history": new_message_history}

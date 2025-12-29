from typing import Any, Dict, Literal

from pydantic import BaseModel, Field
from utils.config import get_llm
from workflow.agents.agent import Agent, AgentState
from workflow.state import AgentType


class RouteDecision(BaseModel):
    """Decision model for routing the conversation."""

    next_node: Literal[
        AgentType.GENERAL, AgentType.SEARCH, AgentType.SUMMARY, AgentType.RAG
    ] = Field(description="The next agent to route the conversation to.")


class MasterAgent(Agent):
    def __init__(self, session_id: str):
        super().__init__(
            system_prompt="You are a helpful assistant.",
            role=AgentType.MASTER,
            session_id=session_id,
        )

    def _retrieve_context(self, state: AgentState) -> AgentState:
        # nothing to do...!
        return {**state}

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        rag_enabled = state.get("rag_enabled", False)

        if rag_enabled:
            return (
                "The user has explicitly requested to strictly use RAG (Retrieval-Augmented Generation). "
                "You MUST route the query to one of the following document-aware agents:\n\n"
                "1. **SUMMARY_AGENT**: Choose this if the user asks to summarize, explain, or get the 'main idea' of the currently selected PDF(s) *as a whole*. "
                "Examples: 'Summarize this paper', 'What is the main conclusion?', 'Tell me about this document'.\n\n"
                "2. **RAG_AGENT**: Choose this when the user asks specific questions about details *within* the selected PDF(s), or asks general questions "
                "that should be answered using the document context. "
                "Examples: 'What does the paper say about transformer architecture?', 'Find the section on experiments', 'Tell me about NAT'.\n\n"
                "**DO NOT** choose SEARCH_AGENT or GENERAL_AGENT. They are DISABLED in this mode.\n"
                "DEFAULT to RAG_AGENT if unsure."
            )

        base_prompt = (
            "Analyze the user's latest query and route to the most appropriate agent:\n\n"
            "1. **SEARCH_AGENT**: Choose this ONLY if the user explicitly asks to *search* or *find* NEW research papers, arxiv papers, "
            "or academic literature. Ideally for queries like 'find papers on X', 'search for Y'.\n\n"
            "2. **SUMMARY_AGENT**: Choose this if the user asks to summarize, explain, or get the 'main idea' of the currently selected PDF(s) *as a whole*. "
            "Examples: 'Summarize this paper', 'What is the main conclusion?', 'Tell me about this document'. "
            "Use this for high-level understanding of the document content.\n\n"
            "3. **GENERAL_AGENT**: Helper for everything else. Use this for general conversational queries, questions about current events, "
            "web searches (non-academic), weather, or technical questions unrelated to finding new papers. Also use this if the user "
            "asks to 'summarize' but clearly means a general concept rather than a specific document context.\n\n"
            "4. **RAG_AGENT**: Use this when the user asks specific questions about details *within* the selected PDF(s). "
            "Examples: 'What does the paper say about transformer architecture?', 'Find the section on experiments', 'What is the value of alpha used?'. "
            "If the user wants to retrieve specific facts, figures, or sections from the PDF, route here.\n\n"
            "DEFAULT to GENERAL_AGENT if unsure."
        )
        return base_prompt

    def _generate_response(self, state: AgentState) -> AgentState:
        messages = state["messages"]

        # Use structured output
        llm = get_llm().with_structured_output(RouteDecision)
        response = llm.invoke(messages)

        return {**state, "response": response}

    def _update_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        root_state = state["root_state"]
        # response is now a RouteDecision object
        decision: RouteDecision = state["response"]

        new_root_state = root_state.copy()

        # Routing logic using the structured object
        new_root_state["next_node"] = decision.next_node

        new_root_state["prev_node"] = self.role

        return {**state, "root_state": new_root_state}

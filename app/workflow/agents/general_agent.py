import asyncio
from typing import Any, Dict

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_mcp_adapters.client import MultiServerMCPClient
from langfuse.langchain import CallbackHandler
from utils.config import get_llm
from workflow.agents.agent import Agent, AgentState
from workflow.state import AgentType, RootState


class GeneralAgent(Agent):
    def __init__(self, session_id: str, k: int = 5):
        super().__init__(
            system_prompt="You are a helpful assistant. You can specific tools to answer the user query.",
            role=AgentType.GENERAL,
            session_id=session_id,
            k=k,
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        user_query = self._get_latest_user_query(state)
        context = state.get("context", "")

        prompt = f"User query: {user_query}\n\nIf user query is in Korean, answer in Korean.\n\n"
        prompt += "Answer the user query using the available tools if necessary."
        if context:
            prompt += f"\n\nHere is the full text or context from the selected documents. Use this to answer the user's question, especially if they ask for a summary:\n{context}"
        return prompt

    async def _generate_response(self, state: AgentState) -> AgentState:
        client = MultiServerMCPClient(
            {
                "exa": {
                    "transport": "http",
                    "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,get_code_context_exa",
                }
            }
        )

        # Load tools from the client
        try:
            tools = await client.get_tools()
        except Exception as e:
            # Fallback or error handling if tools fail to load
            print(f"Failed to load MCP tools: {e}")
            return {
                **state,
                "response": "Sorry, I encountered an error while initializing the general tools.",
            }

        # Create and run a react agent with the tools
        model = get_llm()
        agent = create_agent(
            model,
            tools,
            system_prompt=self.system_prompt,
            middleware=[
                SummarizationMiddleware(
                    model=model,
                    trigger=("fraction", 0.6),
                    keep=("fraction", 0.5),
                )
            ],
        )

        # Use the messages prepared by _prepare_messages
        messages = state["messages"]

        # Invoke the agent
        agent_response = await agent.ainvoke({"messages": messages})

        # Extract the last message content
        response_content = agent_response["messages"][-1].content

        return {**state, "response": response_content}

    def run(self, state: RootState) -> RootState:
        # Override run to handle async execution since _generate_response is async
        agent_state = AgentState(root_state=state, context="", messages=[], response="")

        langfuse_handler = CallbackHandler()

        # Use ainvoke because the graph contains async nodes (_generate_response)
        result = asyncio.run(
            self.graph.ainvoke(
                agent_state,
                config={"callbacks": [langfuse_handler], "session_id": self.session_id},
            )
        )

        return result["root_state"]

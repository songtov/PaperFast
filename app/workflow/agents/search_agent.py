import asyncio
import os
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langfuse.langchain import CallbackHandler
from langgraph.prebuilt import create_react_agent
from utils.config import get_llm
from workflow.agents.agent import Agent, AgentState
from workflow.state import AgentType, RootState


class SearchAgent(Agent):
    def __init__(self, session_id: str):
        super().__init__(
            system_prompt="You are a helpful research paper search agent. Search for useful research paper based on user query.",
            role=AgentType.SEARCH,
            session_id=session_id,
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        return "Search for useful research paper based on user query"

    async def _generate_response(self, state: AgentState) -> AgentState:
        # Define storage path for papers (using a temp dir or project dir)
        storage_path = os.path.join(os.getcwd(), "data", "papers")
        os.makedirs(storage_path, exist_ok=True)

        client = MultiServerMCPClient(
            {
                "arxiv": {
                    "transport": "stdio",
                    "command": "uv",
                    "args": [
                        "tool",
                        "run",
                        "arxiv-mcp-server",
                        "--storage-path",
                        storage_path,
                    ],
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
                "response": "Sorry, I encountered an error while initializing the search tools.",
            }

        # Create and run a react agent with the tools
        model = get_llm()
        agent = create_react_agent(model, tools)

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

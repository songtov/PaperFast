from typing import Dict, Any
from workflow.agents.agent import Agent
from workflow.state import AgentType, RootState
from utils.config import get_llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


class SearchAgent(Agent):
    def __init__(self, session_id: str):
        super().__init__(
            system_prompt="You are a helpful research paper search agent. Search for useful research paper based on user query.",
            role=AgentType.SEARCH,
            session_id=session_id,
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        return "Search for useful research paper based on user query"

    def run(self, state: RootState) -> RootState:
        return asyncio.run(self._run(state))

    async def _run(self, state: RootState) -> RootState:
        # Define storage path for papers (using a temp dir or project dir)
        import os

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
        tools = await client.get_tools()

        # Create and run a react agent with the tools
        model = get_llm()
        agent = create_react_agent(model, tools)

        # Prepare messages
        messages = [SystemMessage(content=self.system_prompt)]
        for msg in state["messages"]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant" or msg["role"] == self.role:
                messages.append(AIMessage(content=msg["content"]))

        # Invoke the agent
        agent_response = await agent.ainvoke({"messages": messages})
        print(agent_response)

        # Extract the last message content
        response_content = agent_response["messages"][-1].content

        # Update state
        new_state = state.copy()
        new_messages = list(new_state.get("messages", []))
        new_messages.append({"role": self.role, "content": response_content})
        new_state["messages"] = new_messages
        new_state["prev_node"] = self.role

        return new_state

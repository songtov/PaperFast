from workflow.agents.master_agent import MasterAgent
from workflow.state import CustomState, AgentType
from langgraph.graph import StateGraph

def create_workflow():
    workflow = StateGraph(CustomState)

    master_agent = MasterAgent()

    workflow.add_node(AgentType.MASTER, master_agent.run())

    return workflow.compile()
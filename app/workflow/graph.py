from workflow.agents.master_agent import MasterAgent
from workflow.state import CustomState, AgentType
from langgraph.graph import StateGraph, END

def create_workflow():
    workflow = StateGraph(CustomState)

    master_agent = MasterAgent()

    workflow.add_node(AgentType.MASTER, master_agent.run)
    workflow.set_entry_point(AgentType.MASTER)
    workflow.add_edge(AgentType.MASTER, END)

    return workflow.compile()
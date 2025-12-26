from workflow.agents.master_agent import MasterAgent
from workflow.agents.output_agent import OutputAgent
from workflow.agents.search_agent import SearchAgent
from workflow.state import RootState, AgentType
from langgraph.graph import StateGraph, END


def create_workflow(session_id: str = ""):
    workflow = StateGraph(RootState)

    master_agent = MasterAgent(session_id=session_id)
    output_agent = OutputAgent(session_id=session_id)
    search_agent = SearchAgent(session_id=session_id)

    workflow.add_node(AgentType.MASTER, master_agent.run)
    workflow.add_node(AgentType.OUTPUT, output_agent.run)
    workflow.add_node(AgentType.SEARCH, search_agent.run)

    workflow.set_entry_point(AgentType.MASTER)

    def route_master(state: RootState):
        return state.get("next_step", AgentType.OUTPUT)

    workflow.add_conditional_edges(
        AgentType.MASTER,
        route_master,
        {AgentType.SEARCH: AgentType.SEARCH, AgentType.OUTPUT: AgentType.OUTPUT},
    )

    workflow.add_edge(AgentType.SEARCH, END)
    workflow.add_edge(AgentType.OUTPUT, END)

    return workflow.compile()


if __name__ == "__main__":
    graph = create_workflow()

    graph_image = graph.get_graph().draw_mermaid_png()

    output_path = "workflow.png"
    with open(output_path, "wb") as f:
        f.write(graph_image)

    print(f"Workflow graph saved to {output_path}")

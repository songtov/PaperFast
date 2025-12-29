from langgraph.graph import END, StateGraph
from workflow.agents.general_agent import GeneralAgent
from workflow.agents.master_agent import MasterAgent
from workflow.agents.search_agent import SearchAgent
from workflow.agents.summary_agent import SummaryAgent
from workflow.state import AgentType, RootState


def create_workflow(session_id: str = ""):
    workflow = StateGraph(RootState)

    master_agent = MasterAgent(session_id=session_id)
    general_agent = GeneralAgent(session_id=session_id)
    search_agent = SearchAgent(session_id=session_id)
    summary_agent = SummaryAgent(session_id=session_id)

    workflow.add_node(AgentType.MASTER, master_agent.run)
    workflow.add_node(AgentType.GENERAL, general_agent.run)
    workflow.add_node(AgentType.SEARCH, search_agent.run)
    workflow.add_node(AgentType.SUMMARY, summary_agent.run)

    workflow.set_entry_point(AgentType.MASTER)

    def route_master(state: RootState):
        return state.get("next_node", AgentType.GENERAL)

    workflow.add_conditional_edges(
        AgentType.MASTER,
        route_master,
        {
            AgentType.SEARCH: AgentType.SEARCH,
            AgentType.GENERAL: AgentType.GENERAL,
            AgentType.SUMMARY: AgentType.SUMMARY,
        },
    )

    workflow.add_edge(AgentType.SEARCH, END)
    workflow.add_edge(AgentType.GENERAL, END)
    workflow.add_edge(AgentType.SUMMARY, END)

    return workflow.compile()


if __name__ == "__main__":
    graph = create_workflow()

    graph_image = graph.get_graph().draw_mermaid_png()

    output_path = "workflow.png"
    with open(output_path, "wb") as f:
        f.write(graph_image)

    print(f"Workflow graph saved to {output_path}")

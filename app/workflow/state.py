from typing import TypedDict, List, Dict

class AgentType:
    MASTER = "MASTER_AGENT"


class CustomState(TypedDict):
    messages: List[Dict]
    prev_node: str
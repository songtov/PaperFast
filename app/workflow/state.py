from typing import TypedDict, List, Dict, Annotated
import operator

class AgentType:
    MASTER = "MASTER_AGENT"
    OUTPUT = "OUTPUT_AGENT"
    SEARCH = "SEARCH_AGENT"


def last_write_wins(old: str, new: str) -> str:
    return new

class CustomState(TypedDict):
    messages: Annotated[List[Dict], operator.add]
    prev_node: Annotated[str, last_write_wins]
    next_step: Annotated[str, last_write_wins]
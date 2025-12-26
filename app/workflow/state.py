from typing import TypedDict, List, Dict, Annotated


from enum import StrEnum

class AgentType(StrEnum):
    MASTER = "MASTER_AGENT"
    OUTPUT = "OUTPUT_AGENT"
    SEARCH = "SEARCH_AGENT"


def last_write_wins(old: str, new: str) -> str:
    return new


def replace_messages(old: List[Dict], new: List[Dict]) -> List[Dict]:
    """Replace messages list instead of concatenating to avoid duplicates"""
    return new if new else old


class CustomState(TypedDict):
    messages: Annotated[List[Dict], replace_messages]
    prev_node: Annotated[str, last_write_wins]
    next_step: Annotated[str, last_write_wins]

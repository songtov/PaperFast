from typing import Annotated, Dict, List, TypedDict


class AgentType:
    MASTER = "MASTER_AGENT"
    GENERAL = "GENERAL_AGENT"
    SEARCH = "SEARCH_AGENT"
    SUMMARY = "SUMMARY_AGENT"


def last_write_wins(old: str, new: str) -> str:
    return new


def replace_messages(old: List[Dict], new: List[Dict]) -> List[Dict]:
    """Replace messages list instead of concatenating to avoid duplicates"""
    return new if new else old


class RootState(TypedDict):
    messages: Annotated[List[Dict], replace_messages]
    prev_node: Annotated[str, last_write_wins]
    next_node: Annotated[str, last_write_wins]

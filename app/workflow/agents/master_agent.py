from typing import Dict, Any
from workflow.agents.agent import Agent
from workflow.state import AgentType

class MasterAgent(Agent):
    def __init__(self):
        super().__init__(
            system_prompt="You are a helpful assistant.",
            role=AgentType.MASTER
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        # In this simple version, we just return the last user message or a prompt based on history.
        # But looking at Agent._prepare_messages, it constructs messages from history.
        # And then calls _create_prompt to append a final HumanMessage.
        # If the user just typed something, it's in st.session_state.messages (in main.py),
        # but in agent.py 'state["debate_state"]["messages"]' is used?
        
        # Let's re-read agent.py carefully.
        # agent.py: 
        #   debate_state = state["debate_state"] (Wait, AgentState def has message_history, context, messages, response. Where is debate_state coming from? Ah, looking at AgentState definition again.)
        
        # AgentState definition in agent.py:
        # class AgentState(TypedDict):
        #     message_history: Dict[str, Any] 
        #     context: str
        #     messages: List[BaseMessage]
        #     response: str

        # But in _prepare_messages:
        #   debate_state = state["debate_state"]
        # This looks like a bug or mismatch in agent.py vs my understanding.
        # Let's grep "debate_state" in agent.py.
        # line 54: debate_state = state["debate_state"]
        # But AgentState top definition doesn't have debate_state.
        
        # In run():
        #   agent_state = AgentState(message_history=state, ...)
        # So 'state' passed to run() is put into 'message_history'.
        
        # So inside _prepare_messages, state is AgentState.
        # state["message_history"] holds the external state.
        
        # Wait, line 54 says `state["debate_state"]`. This key MUST exist in AgentState for this to work.
        # But AgentState definition at line 11-16 does NOT have it.
        # Only message_history, context, messages, response.
        
        # This implies `agent.py` might be broken or I misunderstood TypedDict in LangGraph/Python (it doesn't enforce keys at runtime but access will fail if missing).
        # However, checking `run` method lines 111-113:
        # agent_state = AgentState(message_history=state, ...)
        # It does NOT set debate_state. 
        
        # IF agent.py is indeed broken, I should fix it or work around it.
        # BUT the user said "Implement MasterAgent ... using agent.py".
        # Maybe I should assume `agent.py` is correct and I just missed something?
        # Or maybe I should check if `AgentState` inherits from something else? No.
        
        # Let's look at `agent.py` again.
        # Line 54: debate_state = state["debate_state"]
        # This will KeyError if "debate_state" is not in the dict.
        # And it's not initialized in `run`.
        
        # HYPOTHESIS: The `AgentState` definition in `agent.py` is missing `debate_state` OR `message_history` is meant to be used.
        # In `_prepare_messages`:
        # `debate_state = state["debate_state"]`
        # `context = state["context"]`
        
        # In `run(self, state: AgentState)`: (annotation says AgentState but it's likely CustomState from outside)
        # `agent_state = AgentState(message_history=state, ...)`
        
        # It seems `agent.py` might have been copied from a "Debate" example where `debate_state` was the key.
        # Here we have `message_history`.
        # I should probably FIX `agent.py` to use `message_history` instead of `debate_state`, OR alias it.
        
        # But strictly I should implement `master_agent.py`. If I modify `agent.py` it might be out of scope, but if it's broken I must.
        # Let's verify `agent.py` content again.
        
        # Line 11 is `class AgentState(TypedDict):`
        # Line 13 `message_history: Dict[str, Any]`
        
        # Line 54 `debate_state = state["debate_state"]`
        
        # Yes, `agent.py` seems BUGGY. It tries to access `debate_state` but puts input into `message_history`.
        
        # Action: I will implement MasterAgent, AND I will fix `agent.py` to use `message_history`.
        
        # But first, `_create_prompt`.
        # It receives `state: Dict[str, Any]`.
        # In `_prepare_messages`, it calls `self._create_prompt({**debate_state, "context": context})`.
        # So `_create_prompt` receives the flattened state.
        
        return "Please answer the user's question based on the history."

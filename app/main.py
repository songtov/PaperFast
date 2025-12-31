import uuid

import streamlit as st
from components.sidebar import render_sidebar
from database.repository import message_repository
from database.session import db_session
from langfuse.langchain import CallbackHandler
from utils.state_manager import init_session_state
from workflow.graph import create_workflow
from workflow.state import AgentType, RootState


def process_message_chunk(chunk, current_status):
    """Process streaming chunks from workflow execution

    Args:
        chunk: The chunk from workflow.stream()
        current_status: Dict to track current agent status context

    Returns:
        tuple: (agent_name, subgraph_step, response_text)
    """
    if not chunk or len(chunk) < 2:
        return None, None, None

    node_tuple = chunk[0]
    node_data = chunk[1]

    # Map agent types to display names and emojis
    agent_display = {
        AgentType.MASTER: ("🧠 Master Agent", "라우팅 중..."),
        AgentType.GENERAL: ("💬 General Agent", "답변 생성 중..."),
        AgentType.SEARCH: ("🔍 Search Agent", "논문 검색 중..."),
        AgentType.SUMMARY: ("📝 Summary Agent", "논문 요약 중..."),
        AgentType.RAG: ("📚 RAG Agent", "데이터베이스 검색 중..."),
    }

    # Map subgraph step names to Korean
    step_display = {
        "retrieve_context": "📥 컨텍스트 검색",
        "prepare_messages": "📝 메시지 준비",
        "generate_response": "🤖 응답 생성",
        "update_state": "✅ 상태 업데이트",
    }

    # Handle subgraph chunks: (('AGENT_NAME:id',), {'step_name': {...}})
    if node_tuple and len(node_tuple) > 0 and isinstance(node_tuple[0], str):
        # Extract agent name from 'AGENT_NAME:id' format
        agent_full_name = node_tuple[0].split(":")[0]

        # Update current agent
        if agent_full_name in agent_display:
            current_status["agent"] = agent_full_name
            current_status["emoji_name"], current_status["status_text"] = agent_display[
                agent_full_name
            ]

        # Extract subgraph step information
        subgraph_step = None
        if isinstance(node_data, dict):
            for step_name, step_data in node_data.items():
                # Track the current step
                if step_name in step_display:
                    subgraph_step = step_display[step_name]

                # Check if this chunk contains a response in 'update_state' step
                if step_name == "update_state" and isinstance(step_data, dict):
                    response = step_data.get("response")
                    if response and isinstance(response, str):
                        return agent_full_name, subgraph_step, response

        return agent_full_name, subgraph_step, None

    # Handle final chunks: ((), {'AGENT_NAME': {...}})
    elif not node_tuple or node_tuple == ():
        if isinstance(node_data, dict):
            for agent_name, agent_state in node_data.items():
                if isinstance(agent_state, dict) and "messages" in agent_state:
                    messages = agent_state["messages"]
                    if messages and isinstance(messages, list) and len(messages) > 0:
                        last_msg = messages[-1]
                        if isinstance(last_msg, dict) and "content" in last_msg:
                            return agent_name, None, last_msg["content"]

    return current_status.get("agent"), None, None


def invoke_workflow():
    """Execute the workflow and display agent status with subgraph steps

    Returns:
        The final response text
    """
    session_id = str(uuid.uuid4())

    workflow = create_workflow(session_id=session_id)

    # Get rag_enabled from session state, default to False
    rag_enabled = st.session_state.get("rag_enabled", False)

    initial_state: RootState = {
        "messages": st.session_state.messages,
        "prev_node": "",
        "rag_enabled": rag_enabled,
    }

    langfuse_handler = CallbackHandler()
    final_response = None
    current_status = {}
    status_obj = None
    step_placeholder = None

    for chunk in workflow.stream(
        initial_state,
        config={
            "callbacks": [langfuse_handler],
            "metadata": {"session_id": session_id},
        },
        subgraphs=True,
        stream_mode="updates",
    ):
        # Process each chunk
        agent_name, subgraph_step, response = process_message_chunk(chunk, current_status)

        # Update status display
        if current_status.get("agent") and current_status.get("emoji_name"):
            emoji_name = current_status["emoji_name"]
            status_text = current_status["status_text"]

            # Create or update status
            if status_obj:
                status_obj.update(
                    label=f"{emoji_name} - {status_text}", state="running"
                )
            else:
                status_obj = st.status(
                    f"{emoji_name} - {status_text}", state="running", expanded=True
                )
                # Create placeholder inside status for subgraph steps
                with status_obj:
                    step_placeholder = st.empty()

        # Display subgraph step inside the status
        if subgraph_step and step_placeholder:
            with step_placeholder:
                st.write(subgraph_step)

        # Track final response
        if response:
            final_response = response

    # Mark final status as complete
    if status_obj:
        status_obj.update(state="complete", expanded=False)

    # Return the final response
    if final_response:
        return final_response

    return "응답을 생성하지 못했습니다."


def render_ui():
    # 페이지 설정
    st.set_page_config(page_title="PaperFast", page_icon="🤖")

    # 제목 및 소개
    st.title("🤖 PaperFast")
    st.markdown(
        """
        ### 프로젝트 소개
        이 애플리케이션은 AI 에이전트들(논문 탐색, 논문 요약, 논문 데이터베이스화)을 사용하여
        논문을 공부할 때 도움을 주는 애플리케이션입니다.
        """
    )

    render_sidebar()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("어떤 논문이 궁금하신가요?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            # Invoke workflow with agent status display
            full_response = invoke_workflow()
            # Display final response
            st.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

        # Save or update messages to database
        try:
            # Pass current_conversation_id to update existing conversation
            # Returns the conversation ID (new or existing)
            conversation_id = message_repository.save(
                messages=st.session_state.messages,
                message_id=st.session_state.current_conversation_id,
            )
            # Update session state with the conversation ID
            st.session_state.current_conversation_id = conversation_id

            # Rerun to refresh sidebar with updated conversation list
            st.rerun()
        except Exception as e:
            st.error(f"메시지 저장 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    init_session_state()

    db_session.initialize()

    render_ui()

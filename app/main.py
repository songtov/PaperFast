import uuid

import streamlit as st
from components.sidebar import render_sidebar
from database.repository import message_repository
from database.session import db_session
from langfuse.langchain import CallbackHandler
from utils.state_manager import init_session_state
from workflow.graph import create_workflow
from workflow.state import RootState


def invoke_workflow():
    session_id = str(uuid.uuid4())

    workflow = create_workflow(session_id=session_id)

    # Get rag_enabled from session state, default to False
    rag_enabled = st.session_state.get("rag_enabled", False)

    initial_state: RootState = {
        "messages": st.session_state.messages,
        "prev_node": "",
        "rag_enabled": rag_enabled,
    }

    with st.spinner("로딩 중..."):
        langfuse_handler = CallbackHandler()
        result = workflow.invoke(
            initial_state,
            config={
                "callbacks": [langfuse_handler],
                "metadata": {"session_id": session_id},
            },
        )

    # For debugging
    # st.info(result)

    return result["messages"][-1]["content"]


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
            message_placeholder = st.empty()
            full_response = invoke_workflow()
            message_placeholder.markdown(full_response)

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

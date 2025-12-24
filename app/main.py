import streamlit as st
from utils.state_manager import init_session_state, reset_session_state
from components.sidebar import render_sidebar

def invoke_workflow():
    return "이것은 모의 응답입니다. 실제 LLM이 연결되면 여기에 답변이 표시됩니다."


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
        st.session_state.messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    init_session_state()

    render_ui()
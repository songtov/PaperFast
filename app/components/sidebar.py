import streamlit as st
from typing import Dict, Any


def render_input_form():
    with st.form("input_form", border=False):
        st.text_input(
            label="질문을 입력해주세요.",
            placeholder="질문을 입력해주세요.",
            key="question",
        )

        st.form_submit_button(
            "질문하기",
            on_click=lambda: st.session_state.update({"app_mode": "chat"}),
        )

        # # RAG 기능 활성화 옵션
        # st.checkbox(
        #     "RAG 활성화",
        #     value=True,
        #     help="외부 지식을 검색하여 토론에 활용합니다.",
        #     key="ui_enable_rag",
        # )




def render_history_ui():
    pass


def render_sidebar() -> Dict[str, Any]:
    with st.sidebar:
        tab1, tab2 = st.tabs(["새 대화", "대화 이력"])

        with tab1:
            render_input_form()

        with tab2:
            render_history_ui()
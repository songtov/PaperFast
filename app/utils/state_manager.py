import streamlit as st


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "app_mode" not in st.session_state:
        reset_session_state()
    
    if "uploaded_pdfs" not in st.session_state:
        st.session_state.uploaded_pdfs = []


def reset_session_state():
    st.session_state.app_mode = False

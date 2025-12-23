import streamlit as st


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

    # render_sidebar()

    # current_mode = st.session_state.get("app_mode")

    # if current_mode == "debate":
    #     start_debate()
    # elif current_mode == "results":
    #     display_debate_results()



if __name__ == "__main__":
    render_ui()
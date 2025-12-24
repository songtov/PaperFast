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


def render_artifacts_ui():

    # 현재 추가된 PDF 목록 표시
    st.markdown("### 현재 추가된 PDF")

    if len(st.session_state.uploaded_pdfs) == 0:
        st.info("📄 아직 추가된 PDF가 없습니다.")
    else:
        for idx, pdf in enumerate(st.session_state.uploaded_pdfs):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"**{pdf['name']}**")
                st.caption(f"크기: {pdf['size']:,} bytes")

            with col2:
                if st.button("삭제", key=f"delete_pdf_{idx}"):
                    st.session_state.uploaded_pdfs.pop(idx)
                    st.rerun()

        st.info(f"총 {len(st.session_state.uploaded_pdfs)}개의 PDF가 추가되었습니다.")

    # PDF 업로드 섹션
    st.markdown("### PDF 추가")
    uploaded_file = st.file_uploader(
        "PDF 파일을 선택하세요",
        type=["pdf"],
        key="pdf_uploader",
        help="논문 PDF 파일을 업로드할 수 있습니다.",
    )

    if uploaded_file is not None:
        # 파일이 업로드되었을 때
        if st.button("PDF 추가", key="add_pdf_button"):
            # 중복 체크
            file_exists = any(
                pdf["name"] == uploaded_file.name
                for pdf in st.session_state.uploaded_pdfs
            )

            if not file_exists:
                # PDF 정보를 세션 상태에 저장
                pdf_info = {
                    "name": uploaded_file.name,
                    "size": uploaded_file.size,
                    "data": uploaded_file.read(),
                    "type": uploaded_file.type,
                }
                st.session_state.uploaded_pdfs.append(pdf_info)
                st.success(f"✅ '{uploaded_file.name}' 추가되었습니다!")
                st.rerun()
            else:
                st.warning(f"⚠️ '{uploaded_file.name}' 이미 추가된 파일입니다.")


def render_sidebar() -> Dict[str, Any]:
    with st.sidebar:
        tab1, tab2, tab3 = st.tabs(["새 대화", "대화 이력", "아티팩트"])

        with tab1:
            render_input_form()

        with tab2:
            render_history_ui()

        with tab3:
            render_artifacts_ui()

from typing import Any, Dict

import streamlit as st


def render_history_ui():
    pass


import os

DATA_DIR = "data/papers"
os.makedirs(DATA_DIR, exist_ok=True)


def render_artifacts_ui():
    st.markdown("### 현재 추가된 아티팩트")

    # Initialize selected_pdfs in session_state if not present
    if "selected_pdfs" not in st.session_state:
        st.session_state.selected_pdfs = []

    # List PDF files in the data directory
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        st.info("📄 PDF 파일을 업로드하여 아티팩트로 추가할 수 있습니다.")
    else:
        st.write("RAG 검색에 사용할 파일을 선택하세요:")
        for pdf_file in pdf_files:
            file_path = os.path.join(DATA_DIR, pdf_file)
            size = os.path.getsize(file_path)

            # Checkbox for selection
            is_selected = st.checkbox(
                f"{pdf_file} ({size / 1024:.1f} KB)",
                value=pdf_file in st.session_state.selected_pdfs,
                key=f"select_{pdf_file}",
            )

            if is_selected and pdf_file not in st.session_state.selected_pdfs:
                st.session_state.selected_pdfs.append(pdf_file)
            elif not is_selected and pdf_file in st.session_state.selected_pdfs:
                st.session_state.selected_pdfs.remove(pdf_file)

        st.info(f"선택된 파일: {len(st.session_state.selected_pdfs)}개")

    # PDF 업로드 섹션
    st.markdown("### PDF 추가")
    uploaded_file = st.file_uploader(
        "PDF 파일을 선택하세요",
        type=["pdf"],
        key="pdf_uploader",
        help="논문 PDF 파일을 업로드할 수 있습니다.",
    )

    if uploaded_file is not None:
        if st.button("PDF 추가", key="add_pdf_button"):
            file_path = os.path.join(DATA_DIR, uploaded_file.name)
            if os.path.exists(file_path):
                st.warning(f"⚠️ '{uploaded_file.name}' 이미 존재하는 파일입니다.")
            else:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())
                st.success(f"✅ '{uploaded_file.name}' 저장되었습니다!")
                st.rerun()


def render_sidebar() -> Dict[str, Any]:
    with st.sidebar:
        tab1, tab2 = st.tabs(["아티팩트", "대화 이력"])

        with tab1:
            render_artifacts_ui()

        with tab2:
            render_history_ui()

import os
from typing import Any, Dict

import streamlit as st
from retrieval.vector_store import (
    add_pdfs_to_vector_store,
    delete_document_from_vector_store,
    rebuild_index,
    rename_document_in_vector_store,
)

DATA_DIR = "app/storage/raw"
os.makedirs(DATA_DIR, exist_ok=True)


def render_history_ui():
    pass


def rename_file(old_path: str, new_name_key: str):
    new_name = st.session_state[new_name_key]
    if not new_name.lower().endswith(".pdf"):
        new_name += ".pdf"

    if new_name == os.path.basename(old_path):
        return

    new_path = os.path.join(DATA_DIR, new_name)

    if os.path.exists(new_path):
        st.toast(f"⚠️ '{new_name}' 이미 존재하는 파일입니다.", icon="⚠️")
        return

    try:
        empty_space = st.empty()
        with empty_space.container():
            with st.status(f"'{new_name}'으로 변경 및 색인 업데이트 중..."):
                os.rename(old_path, new_path)
                # Use optimized rename
                rename_document_in_vector_store(old_path, new_path)
        empty_space.empty()
        st.toast(f"'{new_name}' 변경되었습니다!", icon="✅")
    except Exception as e:
        st.toast(f"오류: {e}", icon="❌")


def delete_file(path: str, filename: str):
    try:
        with st.spinner(f"'{filename}' 삭제 및 색인 정리 중..."):
            os.remove(path)
            # Use optimized delete
            delete_document_from_vector_store(filename)

        st.toast(f"'{filename}' 삭제되었습니다!", icon="✅")
    except Exception as e:
        st.toast(f"오류: {e}", icon="❌")


def render_artifacts_ui():
    st.markdown("### VectorDB 추가된 PDF")

    # List PDF files in the data directory
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        st.info("📄 PDF 파일을 업로드하여 추가할 수 있습니다.")
    else:
        st.write("저장된 파일 목록:")

        # Grid layout for better spacing
        for pdf_file in pdf_files:
            file_path = os.path.join(DATA_DIR, pdf_file)
            size = os.path.getsize(file_path)

            # Create columns for layout
            col1, col2 = st.columns([0.8, 0.2])

            with col1:
                # Just display filename
                st.write(f"📄 {pdf_file}")
                st.caption(f"{size / (1024 * 1024):.2f} MB")

            with col2:
                # Management Menu
                with st.popover("⋮", use_container_width=True):
                    st.write("관리")

                    # Download
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="다운로드",
                            data=f,
                            file_name=pdf_file,
                            mime="application/pdf",
                            key=f"btn_download_{pdf_file}",
                            use_container_width=True,
                        )

                    # Rename
                    rename_key = f"rename_{pdf_file}"
                    st.text_input("새 이름", value=pdf_file, key=rename_key)
                    st.button(
                        "이름 변경",
                        key=f"btn_rename_{pdf_file}",
                        on_click=rename_file,
                        args=(file_path, rename_key),
                        use_container_width=True,
                    )

                    # Delete
                    st.button(
                        "삭제",
                        key=f"btn_delete_{pdf_file}",
                        type="primary",
                        on_click=delete_file,
                        args=(file_path, pdf_file),
                        use_container_width=True,
                    )

        st.info(f"총 파일: {len(pdf_files)}개")

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

                # Update Vector Store
                with st.spinner("임베딩 처리 중..."):
                    add_pdfs_to_vector_store([file_path])

                st.success(f"✅ '{uploaded_file.name}' 저장 및 색인 완료!")
                st.rerun()


def render_sidebar() -> Dict[str, Any]:
    with st.sidebar:
        tab1, tab2 = st.tabs(["PDF", "대화 이력"])

        with tab1:
            render_artifacts_ui()

        with tab2:
            render_history_ui()

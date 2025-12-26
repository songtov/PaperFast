import streamlit as st
import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Any, Dict, Optional, List
from utils.config import get_embeddings


@st.cache_resource
def get_pdf_vector_store(pdf_paths: List[str]) -> Optional[FAISS]:
    if not pdf_paths:
        return None

    documents = []
    for path in pdf_paths:
        if os.path.exists(path):
            try:
                loader = PyPDFLoader(path)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading {path}: {e}")

    if not documents:
        return None

    # Text splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    splits = text_splitter.split_documents(documents)

    try:
        return FAISS.from_documents(splits, get_embeddings())
    except Exception as e:
        print(f"Vector DB 생성 중 오류 발생: {str(e)}")
        return None


def search_pdfs(query: str, pdf_paths: List[str], k: int = 5) -> List[Dict[str, Any]]:
    # Create vector store from selected PDFs
    vector_store = get_pdf_vector_store(pdf_paths)
    if not vector_store:
        return []
    try:
        # Perform similarity search
        return vector_store.similarity_search(query, k=k)
    except Exception as e:
        print(f"검색 중 오류 발생: {str(e)}")
        return []

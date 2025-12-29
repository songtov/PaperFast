import os
import shutil
from typing import Any, Dict, List, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.config import get_embeddings

VECTOR_STORE_PATH = "app/storage/vector_store"
RAW_DATA_PATH = "app/storage/raw"
INDEX_NAME = "index"


def get_vector_store() -> Optional[FAISS]:
    """Load the existing vector store from disk if it exists."""
    if os.path.exists(os.path.join(VECTOR_STORE_PATH, f"{INDEX_NAME}.faiss")):
        try:
            return FAISS.load_local(
                VECTOR_STORE_PATH,
                get_embeddings(),
                allow_dangerous_deserialization=True,
            )
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return None
    return None


def add_pdfs_to_vector_store(pdf_paths: List[str]):
    """Add new PDFs to the persistent vector store."""
    if not pdf_paths:
        return

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
        return

    # Text splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    splits = text_splitter.split_documents(documents)

    vector_store = get_vector_store()

    if vector_store:
        vector_store.add_documents(splits)
    else:
        try:
            vector_store = FAISS.from_documents(splits, get_embeddings())
        except Exception as e:
            print(f"Error creating new vector store: {e}")
            return

    try:
        vector_store.save_local(VECTOR_STORE_PATH, index_name=INDEX_NAME)
        print(f"Vector store saved to {VECTOR_STORE_PATH}")
    except Exception as e:
        print(f"Error saving vector store: {e}")


def rebuild_index():
    """Rebuild the entire index from the raw data directory.
    Useful when files are deleted or checking consistency.
    """
    if not os.path.exists(RAW_DATA_PATH):
        return

    # Clear existing vector store
    if os.path.exists(VECTOR_STORE_PATH):
        try:
            shutil.rmtree(VECTOR_STORE_PATH)
            os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
        except Exception as e:
            print(f"Error clearing vector store directory: {e}")

    pdf_files = [
        os.path.join(RAW_DATA_PATH, f)
        for f in os.listdir(RAW_DATA_PATH)
        if f.lower().endswith(".pdf")
    ]

    if pdf_files:
        add_pdfs_to_vector_store(pdf_files)


def delete_document_from_vector_store(filename: str):
    """Delete a specific document from the vector store by filename."""
    vector_store = get_vector_store()
    if not vector_store:
        return

    # In LangChain FAISS, docstore stores documents with IDs.
    # index_to_docstore_id maps index ID to docstore ID.
    # We need to find ids where metadata source matches.

    ids_to_delete = []

    # helper to check if source matches
    # source in metadata might be absolute path or just filename depending on how we saved it.
    # We should handle both cases or ensure we pass what matches.

    for doc_id, doc in vector_store.docstore._dict.items():
        source = doc.metadata.get("source", "")
        # Check if source matches filename or ends with filename
        if source == filename or source.endswith(f"/{filename}"):
            ids_to_delete.append(doc_id)

    if not ids_to_delete:
        print(f"No documents found for {filename}")
        return

    try:
        vector_store.delete(ids_to_delete)
        vector_store.save_local(VECTOR_STORE_PATH, index_name=INDEX_NAME)
        print(f"Deleted {len(ids_to_delete)} chunks for {filename}")
    except Exception as e:
        print(f"Error deleting document {filename}: {e}")


def rename_document_in_vector_store(old_path: str, new_path: str):
    """Rename a document by deleting the old one and adding the new one."""
    # 1. Delete old chunks
    old_filename = os.path.basename(old_path)
    delete_document_from_vector_store(old_filename)

    # 2. Add new file
    if os.path.exists(new_path):
        add_pdfs_to_vector_store([new_path])


def search_pdfs(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search within the persistent vector store."""
    vector_store = get_vector_store()
    if not vector_store:
        return []
    try:
        return vector_store.similarity_search(query, k=k)
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []


def get_all_documents() -> List[Document]:
    """Retrieve all documents from the vector store."""
    vector_store = get_vector_store()
    if not vector_store:
        return []

    return list(vector_store.docstore._dict.values())

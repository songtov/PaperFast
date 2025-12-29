from typing import Any, Dict

import os
from workflow.agents.agent import Agent
from workflow.state import AgentType
from retrieval.vector_store import search_pdfs

class SummaryAgent(Agent):
    def __init__(self, session_id: str):
        super().__init__(
            system_prompt="You are a helpful assistant that summarizes research papers. Use the provided context to create a comprehensive summary. if user query is in Korean answer in Korean",
            role=AgentType.SUMMARY,
            session_id=session_id,
        )
    
        # 자료 검색
    def _retrieve_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        root_state = state["root_state"]

        # Extract query from last user message
        messages = root_state["messages"]
        last_human_msg = next(
            (m for m in reversed(messages) if m["role"] == "user"), None
        )
        query = last_human_msg["content"] if last_human_msg else ""

        # RAG Search on persistent Vector Store
        # We search across all indexed documents.
        print(query)
        docs = search_pdfs(query, k=self.k)

        # 컨텍스트 포맷팅
        context = self._format_context(docs)

        # 상태 업데이트
        return {**state, "context": context}

    # 검색 결과로 Context 생성
    def _format_context(self, docs: list) -> str:
        context = ""
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown")
            section = doc.metadata.get("section", "")
            context += f"[문서 {i + 1}] 출처: {os.path.basename(source)}"
            if section:
                context += f", 섹션: {section}"
            context += f"\n{doc.page_content}\n\n"
        return context

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        context = state.get("context", "")
        return f"Please summarize the following content explicitly and comprehensively:\n\n{context}"

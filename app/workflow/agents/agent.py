import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langfuse.langchain import CallbackHandler
from langgraph.graph import END, StateGraph
from retrieval.vector_store import search_pdfs
from utils.config import get_llm
from workflow.state import RootState


# 에이전트 내부 상태 타입 정의
class AgentState(TypedDict):
    root_state: RootState  # 전체 토론 상태
    context: str  # 검색된 컨텍스트
    messages: List[BaseMessage]  # LLM에 전달할 메시지
    response: str  # LLM 응답


# 에이전트 추상 클래스 정의
class Agent(ABC):
    def __init__(
        self, system_prompt: str, role: str, session_id: str = None, k: int = 5
    ):
        self.system_prompt = system_prompt
        self.role = role
        self.k = k
        self._setup_graph()  # 그래프 설정
        self.session_id = session_id  # langfuse 세션 ID

    def _setup_graph(self):
        # 그래프 생성
        workflow = StateGraph(AgentState)

        # 노드 추가
        workflow.add_node("retrieve_context", self._retrieve_context)  # 자료 검색
        workflow.add_node("prepare_messages", self._prepare_messages)  # 메시지 준비
        workflow.add_node("generate_response", self._generate_response)  # 응답 생성
        workflow.add_node("update_state", self._update_state)  # 상태 업데이트

        # 엣지 추가 - 순차 실행 흐름
        workflow.add_edge("retrieve_context", "prepare_messages")
        workflow.add_edge("prepare_messages", "generate_response")
        workflow.add_edge("generate_response", "update_state")

        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("update_state", END)

        # 그래프 컴파일
        self.graph = workflow.compile()

    def _retrieve_context(self, state: AgentState) -> AgentState:
        # Nothing
        return {**state}

    # # 자료 검색
    # def _retrieve_context(self, state: AgentState) -> AgentState:
    #     root_state = state["root_state"]

    #     # Extract query from last user message
    #     messages = root_state["messages"]
    #     last_human_msg = next(
    #         (m for m in reversed(messages) if m["role"] == "user"), None
    #     )
    #     query = last_human_msg["content"] if last_human_msg else ""

    #     # RAG Search on persistent Vector Store
    #     # We search across all indexed documents.
    #     docs = search_pdfs(query, k=self.k)

    #     # 컨텍스트 포맷팅
    #     context = self._format_context(docs)

    #     # 상태 업데이트
    #     return {**state, "context": context}

    # # 검색 결과로 Context 생성
    # def _format_context(self, docs: list) -> str:
    #     context = ""
    #     for i, doc in enumerate(docs):
    #         source = doc.metadata.get("source", "Unknown")
    #         section = doc.metadata.get("section", "")
    #         context += f"[문서 {i + 1}] 출처: {os.path.basename(source)}"
    #         if section:
    #             context += f", 섹션: {section}"
    #         context += f"\n{doc.page_content}\n\n"
    #     return context

    # 프롬프트 메시지 준비
    def _prepare_messages(self, state: AgentState) -> AgentState:
        root_state = state["root_state"]
        context = state["context"]

        # 시스템 프롬프트로 시작
        messages = [SystemMessage(content=self.system_prompt)]

        # 기존 대화 기록 추가
        for message in root_state["messages"]:
            if message["role"] == "assistant":
                messages.append(AIMessage(content=message["content"]))
            elif message["role"] == "user":
                messages.append(HumanMessage(content=message["content"]))
            else:
                messages.append(
                    HumanMessage(content=f"{message['role']}: {message['content']}")
                )

        # 프롬프트 생성 (검색된 컨텍스트 포함)
        prompt = self._create_prompt({**root_state, "context": context})
        messages.append(HumanMessage(content=prompt))

        # 상태 업데이트
        return {**state, "messages": messages}

    # 프롬프트 생성 - 하위 클래스에서 구현 필요
    @abstractmethod
    def _create_prompt(self, state: Dict[str, Any]) -> str:
        pass

    # LLM 호출
    def _generate_response(self, state: AgentState) -> AgentState:
        messages = state["messages"]
        response = get_llm().invoke(messages)

        return {**state, "response": response.content}

    # 상태 업데이트
    def _update_state(self, state: AgentState) -> AgentState:
        root_state = state["root_state"]
        response = state["response"]

        # 상태 복사 및 업데이트
        new_root_state = root_state.copy()

        # 에이전트 응답 추가
        # Create a new list to avoid mutating the shared session state
        new_messages = list(new_root_state["messages"])
        new_messages.append({"role": self.role, "content": response})
        new_root_state["messages"] = new_messages

        # 이전 노드 정보 업데이트
        new_root_state["prev_node"] = self.role

        # 상태 업데이트
        return {**state, "root_state": new_root_state}

    # 토론 실행
    def run(self, state: RootState) -> RootState:
        # 초기 에이전트 상태 구성
        agent_state = AgentState(root_state=state, context="", messages=[], response="")

        # 내부 그래프 실행
        try:
            langfuse_handler = CallbackHandler()
            result = self.graph.invoke(
                agent_state,
                config={"callbacks": [langfuse_handler], "session_id": self.session_id},
            )
        except Exception as e:
            # Fallback if Langfuse fails or is not configured
            print(f"Warning: Langfuse callback failed or disabled: {e}")
            result = self.graph.invoke(
                agent_state,
                config={"session_id": self.session_id},
            )

        # 최종 상태 반환
        return result["root_state"]

    def visualize(self):
        return self.graph.get_graph().draw_mermaid_png()


if __name__ == "__main__":

    class DummyAgent(Agent):
        def _create_prompt(self, state: Dict[str, Any]) -> str:
            return "dummy_prompt"

    try:
        agent = DummyAgent(system_prompt="test", role="test_role")
        png_data = agent.visualize()
        with open("agent_visualization.png", "wb") as f:
            f.write(png_data)
        print("Visualization saved to agent_visualization.png")
    except Exception as e:
        print(f"Error: {e}")

from __future__ import annotations

from time import perf_counter

from langgraph.graph import END, StateGraph

from app.graph.conversation_state import ConversationState
from app.services.evidence_formatter import build_evidence_items


def build_rag_graph(retrieve_fn, answer_fn):
    workflow = StateGraph(ConversationState)

    def retrieve(state: ConversationState) -> ConversationState:
        chunks = retrieve_fn(state["question"])
        return {**state, "retrieved_chunks": chunks}

    def answer(state: ConversationState) -> ConversationState:
        started = perf_counter()
        answer_text, status = answer_fn(
            state["question"],
            state.get("history", []),
            state.get("retrieved_chunks", []),
        )
        evidence = build_evidence_items(state.get("retrieved_chunks", [])) if status == "answered" else []
        return {
            **state,
            "answer": answer_text,
            "status": status,
            "evidence": evidence,
            "processing_ms": int((perf_counter() - started) * 1000),
        }

    workflow.add_node("retrieve", retrieve)
    workflow.add_node("answer", answer)
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "answer")
    workflow.add_edge("answer", END)
    return workflow.compile()

from typing import TypedDict, List, Any

from langgraph.graph import StateGraph, START, END

from src.config import TOP_K
from src.generator import generate_answer
from src.retriever import calculate_confidence, retrieve

class AgentState(TypedDict, total=False):
    question: str
    top_k: int
    context: List[dict]
    retrieved_chunks: List[dict]
    confidence_score: float
    answer: str

def retrieve_node(state: AgentState):
    matches = retrieve(
        query=state["question"],
        top_k=state.get("top_k", TOP_K),
    )
    return {
        "context": matches,
        "retrieved_chunks": matches,
        "confidence_score": calculate_confidence(matches),
    }

def generate_node(state: AgentState):
    answer = generate_answer(
        question=state["question"],
        matches=state.get("context", []),
    )
    return {"answer": answer}

workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

rag_graph = workflow.compile()
def run_rag(question: str, top_k: int = TOP_K):
    result = rag_graph.invoke({
        "question": question,
        "top_k": top_k,
    })

    return result
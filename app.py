from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.graph import rag_graph

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Appening RAG AI Chatbot",
    description="Grounded RAG chatbot using Groq, FastEmbed, Pinecone and LangGraph.",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=2,
        description="Question to ask about the indexed knowledge source.",
    )
    top_k: int = Field(default=5, ge=1, le=10)


@app.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        result = rag_graph.invoke({
            "question": request.query,
            "top_k": request.top_k,
            "context": [],
            "answer": "",
            "confidence_score": 0.0,
            "retrieved_chunks": [],
        })

        return {
            "answer": result["answer"],
            "retrieved_chunks": result["retrieved_chunks"],
            "confidence_score": result["confidence_score"],
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/style.css")
def style():
    return FileResponse(FRONTEND_DIR / "style.css")


@app.get("/script.js")
def script():
    return FileResponse(FRONTEND_DIR / "script.js")
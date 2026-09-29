import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# API KEYS
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")

# =========================
# Pinecone
# =========================

PINECONE_INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME",
    "appening-rag-index"
)

PINECONE_CLOUD = os.getenv(
    "PINECONE_CLOUD",
    "aws"
)

PINECONE_REGION = os.getenv(
    "PINECONE_REGION",
    "us-east-1"
)

# =========================
# Embedding Model
# =========================

# FastEmbed local model
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5"
)

# BGE-small-en-v1.5 produces 384-dimensional vectors
EMBEDDING_DIMENSION = 384

# =========================
# Groq LLM
# =========================

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# =========================
# RAG settings
# =========================

CHUNK_SIZE = int(
    os.getenv("CHUNK_SIZE", "1000")
)

CHUNK_OVERLAP = int(
    os.getenv("CHUNK_OVERLAP", "200")
)

TOP_K = int(
    os.getenv("TOP_K", "5")
)

MIN_RELEVANCE_SCORE = float(
    os.getenv("MIN_RELEVANCE_SCORE", "0.35")
)


def validate_keys():

    missing = []

    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")

    if not PINECONE_API_KEY:
        missing.append("PINECONE_API_KEY")

    if missing:

        raise RuntimeError(
            "Missing environment variables: "
            + ", ".join(missing)
            + ". Copy .env.example to .env and add your API keys."
        )
from pinecone import Pinecone
from fastembed import TextEmbedding

from src.config import (
    EMBEDDING_MODEL,
    MIN_RELEVANCE_SCORE,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    TOP_K,
    validate_keys,
)


# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

embedding_model = TextEmbedding(
    model_name=EMBEDDING_MODEL
)


# ==========================================
# RETRIEVE
# ==========================================

def retrieve(
    query: str,
    top_k: int = TOP_K
):

    validate_keys()

    # ------------------------------
    # Create query embedding
    # ------------------------------

    query_embedding = list(
        embedding_model.query_embed(
            query
        )
    )[0]

    # ------------------------------
    # Connect to Pinecone
    # ------------------------------

    pinecone_client = Pinecone(
        api_key=PINECONE_API_KEY
    )

    index = pinecone_client.Index(
        PINECONE_INDEX_NAME
    )

    # ------------------------------
    # Search
    # ------------------------------

    response = index.query(

        vector=query_embedding.tolist(),

        top_k=top_k,

        include_metadata=True

    )

    matches = []

    for match in response.matches:

        metadata = (
            match.metadata or {}
        )

        score = float(
            match.score or 0.0
        )

        matches.append({

            "id": match.id,

            "score": round(
                score,
                4
            ),

            "page": metadata.get(
                "page"
            ),

            "chunk_number":
                metadata.get(
                    "chunk_number"
                ),

            "source": metadata.get(
                "source"
            ),

            "text": metadata.get(
                "text",
                ""
            )

        })

    return matches


# ==========================================
# CONFIDENCE SCORE
# ==========================================

def calculate_confidence(
    matches
):

    if not matches:

        return 0.0

    top_scores = [

        max(
            0.0,
            min(
                1.0,
                item["score"]
            )
        )

        for item in matches[:3]

    ]

    weighted = sum(

        score *
        (len(top_scores) - i)

        for i, score in enumerate(
            top_scores
        )

    )

    denominator = sum(
        range(
            1,
            len(top_scores) + 1
        )
    )

    return round(
        weighted / denominator,
        4
    )


# ==========================================
# CHECK RELEVANCE
# ==========================================

def has_relevant_context(
    matches
):

    return (

        bool(matches)

        and

        matches[0]["score"]
        >= MIN_RELEVANCE_SCORE

    )
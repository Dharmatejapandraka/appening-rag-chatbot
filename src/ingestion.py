import argparse
import hashlib
from pathlib import Path
from typing import List, Dict

from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader
from fastembed import TextEmbedding

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
    PINECONE_API_KEY,
    PINECONE_CLOUD,
    PINECONE_INDEX_NAME,
    PINECONE_REGION,
    validate_keys,
)


# ==========================================
# LOAD PDF
# ==========================================

def load_pdf(pdf_path: str) -> List[Dict]:

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text() or ""

        text = " ".join(text.split())

        if text:

            pages.append({
                "page": page_number,
                "text": text
            })

    return pages


# ==========================================
# TEXT CHUNKING
# ==========================================

def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
):

    if overlap >= chunk_size:

        raise ValueError(
            "CHUNK_OVERLAP must be smaller than CHUNK_SIZE."
        )

    chunks = []

    start = 0

    while start < len(text):

        end = min(
            start + chunk_size,
            len(text)
        )

        chunk = text[start:end].strip()

        if chunk:

            chunks.append(chunk)

        if end >= len(text):

            break

        start = end - overlap

    return chunks


# ==========================================
# CREATE CHUNKS
# ==========================================

def create_chunks(
    pages: List[Dict]
):

    records = []

    for page in pages:

        chunks = split_text(
            page["text"]
        )

        for chunk_number, chunk in enumerate(
            chunks
        ):

            records.append({

                "text": chunk,

                "page": page["page"],

                "chunk_number": chunk_number

            })

    return records


# ==========================================
# PINECONE INDEX
# ==========================================

def get_or_create_index(
    pc: Pinecone
):

    existing_indexes = pc.list_indexes().names()

    if PINECONE_INDEX_NAME not in existing_indexes:

        print(
            f"Creating Pinecone index: "
            f"{PINECONE_INDEX_NAME}"
        )

        pc.create_index(

            name=PINECONE_INDEX_NAME,

            dimension=EMBEDDING_DIMENSION,

            metric="cosine",

            spec=ServerlessSpec(

                cloud=PINECONE_CLOUD,

                region=PINECONE_REGION

            )
        )

    return pc.Index(
        PINECONE_INDEX_NAME
    )


# ==========================================
# MAIN INGESTION
# ==========================================

def ingest(pdf_path: str):

    validate_keys()

    path = Path(pdf_path)

    if not path.exists():

        raise FileNotFoundError(
            f"PDF not found: {path}"
        )

    print("\nReading PDF...")

    pages = load_pdf(
        str(path)
    )

    print(
        f"Pages extracted: {len(pages)}"
    )

    records = create_chunks(
        pages
    )

    print(
        f"Chunks created: {len(records)}"
    )

    if not records:

        raise RuntimeError(
            "No text could be extracted from the PDF."
        )

    # ======================================
    # LOAD LOCAL EMBEDDING MODEL
    # ======================================

    print("\nLoading FastEmbed model...")

    embedding_model = TextEmbedding(
        model_name=EMBEDDING_MODEL
    )

    print(
        f"Embedding model: {EMBEDDING_MODEL}"
    )

    # ======================================
    # GENERATE EMBEDDINGS
    # ======================================

    texts = [
        record["text"]
        for record in records
    ]

    print("\nGenerating embeddings...")

    embeddings = list(
        embedding_model.passage_embed(
            texts
        )
    )

    print(
        f"Embeddings generated: "
        f"{len(embeddings)}"
    )

    # ======================================
    # CONNECT PINECONE
    # ======================================

    print("\nConnecting to Pinecone...")

    pinecone_client = Pinecone(
        api_key=PINECONE_API_KEY
    )

    index = get_or_create_index(
        pinecone_client
    )

    # ======================================
    # CREATE VECTOR RECORDS
    # ======================================

    vectors = []

    for record, embedding in zip(
        records,
        embeddings
    ):

        raw_id = (
            f"{record['page']}-"
            f"{record['chunk_number']}-"
            f"{record['text'][:50]}"
        )

        vector_id = hashlib.sha1(
            raw_id.encode("utf-8")
        ).hexdigest()

        vectors.append({

            "id": vector_id,

            "values": embedding.tolist(),

            "metadata": {

                "text": record["text"],

                "page": record["page"],

                "chunk_number":
                    record["chunk_number"],

                "source": path.name

            }

        })

    # ======================================
    # UPLOAD TO PINECONE
    # ======================================

    batch_size = 100

    print("\nUploading vectors...")

    for start in range(
        0,
        len(vectors),
        batch_size
    ):

        batch = vectors[
            start:start + batch_size
        ]

        index.upsert(
            vectors=batch
        )

        uploaded = min(
            start + batch_size,
            len(vectors)
        )

        print(
            f"Uploaded "
            f"{uploaded}/{len(vectors)}"
        )

    print("\n================================")
    print("INGESTION COMPLETE")
    print("================================")

    print(
        f"Index: {PINECONE_INDEX_NAME}"
    )

    print(
        f"Vectors: {len(vectors)}"
    )

    print(
        f"Dimension: {EMBEDDING_DIMENSION}"
    )


# ==========================================
# COMMAND LINE
# ==========================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Ingest Agentic AI eBook "
            "into Pinecone."
        )
    )

    parser.add_argument(

        "--pdf",

        default=(
            "data/"
            "Ebook-Agentic-AI.pdf"
        ),

        help="Path to the PDF file."

    )

    args = parser.parse_args()

    ingest(
        args.pdf
    )
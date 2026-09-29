import os

from openai import OpenAI

from src.config import (
    GROQ_API_KEY,
    GROQ_BASE_URL,
    GROQ_MODEL
)

from src.retriever import (
    has_relevant_context
)


# ==========================================
# GROQ CLIENT
# ==========================================

client = OpenAI(

    api_key=GROQ_API_KEY,

    base_url=GROQ_BASE_URL

)


# ==========================================
# SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """

You are a strict document-grounded
question answering assistant.

Your ONLY source of factual information
is the CONTEXT supplied by the application.

Do NOT use outside knowledge.

Do NOT use general knowledge.

Do NOT make assumptions.

Do NOT invent information.

Rules:

1. Answer ONLY using the provided CONTEXT.

2. If the CONTEXT does not contain enough
information to answer the question, say:

"I don't have enough information in the
provided document to answer that."

3. Never invent facts, names, dates,
definitions, examples, or citations.

4. Keep the answer concise but useful.

5. If the question is unrelated to the
document, refuse to answer it.

"""


# ==========================================
# GENERATE ANSWER
# ==========================================

def generate_answer(
    question: str,
    matches: list
):

    # --------------------------------------
    # Check relevance
    # --------------------------------------

    if not has_relevant_context(
        matches
    ):

        return (
            "I don't have enough information "
            "in the provided document to "
            "answer that."
        )

    # --------------------------------------
    # Build context
    # --------------------------------------

    context_parts = []

    for i, item in enumerate(
        matches,
        start=1
    ):

        context_parts.append(

            f"[Context {i} | "
            f"Page {item.get('page')} | "
            f"Score {item.get('score')}]\n"
            f"{item.get('text', '')}"

        )

    context = "\n\n".join(
        context_parts
    )

    # --------------------------------------
    # User prompt
    # --------------------------------------

    user_prompt = f"""

CONTEXT:

{context}


QUESTION:

{question}


Answer the QUESTION using ONLY
the CONTEXT above.

If the answer is not present in
the CONTEXT, say:

"I don't have enough information in
the provided document to answer that."

"""

    # --------------------------------------
    # GROQ REQUEST
    # --------------------------------------

    response = client.chat.completions.create(

        model=GROQ_MODEL,

        messages=[

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": user_prompt
            }

        ],

        temperature=0.1

    )

    return (
        response
        .choices[0]
        .message
        .content
        .strip()
    )
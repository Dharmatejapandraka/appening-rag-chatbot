# Architecture

```text
                    Agentic AI eBook PDF
                             |
                             v
                    src/ingestion.py
                             |
                +------------+------------+
                |                         |
           PyPDF extraction        Chunking 1000/200
                |                         |
                +------------+------------+
                             |
                             v
                  OpenAI text-embedding-3-small
                             |
                             v
                         Pinecone
                    (1536 dimensions)
                             |
                             |
User --> POST /chat --> LangGraph
                          |
                          v
                     retrieve node
                          |
                          v
                    top-k Pinecone
                       matches
                          |
                          v
                    generate node
                          |
                          v
                  OpenAI gpt-4o-mini
                          |
                          v
                  Grounded answer
                          +
                  Retrieved chunks
                          +
                  Relevance score
```

## Grounding design

The generation prompt explicitly instructs the model to use only retrieved context.

A minimum retrieval relevance threshold is also applied before generation. If the top Pinecone match is below the configured threshold, the API returns a document-insufficient response.

This is intended to reduce unsupported answers. It is not a formal guarantee of factual correctness.

# Appening RAG AI Chatbot

A document-grounded Retrieval-Augmented Generation (RAG) chatbot built for the Appening technical assessment.

## Architecture

PDF -> text extraction -> chunking -> OpenAI embeddings -> Pinecone
-> LangGraph retrieval node -> LangGraph generation node -> FastAPI

The `/chat` endpoint returns:

- `answer`
- `retrieved_chunks`
- `confidence_score`

The application is designed to answer only from the indexed Agentic AI eBook. For unrelated questions, it should refuse instead of using outside knowledge.

## Technology

- Python 3.13
- FastAPI
- LangGraph
- Pinecone
- OpenAI `text-embedding-3-small`
- OpenAI `gpt-4o-mini`
- PyPDF
- python-dotenv

## Project structure

```text
appening-rag-chatbot/
├── app.py
├── requirements.txt
├── render.yaml
├── .python-version
├── .env.example
├── .gitignore
├── README.md
├── data/
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── ingestion.py
│   ├── retriever.py
│   ├── generator.py
│   └── graph.py
└── tests/
    └── test_health.py
```

## 1. Prerequisites

Install:

- Python 3.10+
- Git
- VS Code

You also need:

- OpenAI API key
- Pinecone API key

## 2. Create virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again.

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## 4. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Then put your real keys into `.env`.

Never commit `.env` to GitHub.

## 5. Download the Agentic AI eBook

Download the PDF from the assessment's supplied Google Drive link.

Save it exactly as:

```text
data/Ebook-Agentic-AI.pdf
```

Do not commit the PDF if it is not yours to redistribute.

## 6. Create the Pinecone index and ingest the PDF

From the project root:

```powershell
python -m src.ingestion --pdf data/Ebook-Agentic-AI.pdf
```

The ingestion script:

1. Reads the PDF.
2. Extracts page text.
3. Splits text into overlapping chunks.
4. Creates OpenAI embeddings.
5. Creates the Pinecone index if it does not exist.
6. Uploads vectors and metadata.

The index uses dimension 1536 for `text-embedding-3-small`.

## 7. Run the API locally

```powershell
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Use the Swagger UI to test `/chat`.

Example request:

```json
{
  "query": "What is Agentic AI according to the eBook?",
  "top_k": 5
}
```

## 8. Example response

```json
{
  "answer": "Answer grounded in the retrieved document context...",
  "retrieved_chunks": [
    {
      "id": "example",
      "score": 0.82,
      "page": 4,
      "chunk_number": 0,
      "source": "Ebook-Agentic-AI.pdf",
      "text": "..."
    }
  ],
  "confidence_score": 0.81
}
```

`confidence_score` is a retrieval relevance indicator derived from Pinecone similarity scores. It is not a calibrated probability.

## 9. Required benchmark tests

Test at least these questions:

1. What is Agentic AI according to the eBook?
2. How do AI agents differ from traditional automation systems?
3. What are the core components of an Agentic Architecture?
4. What role does memory play in Agentic AI workflows?
5. Who won the 2022 FIFA World Cup?

The fifth question is an intentional grounding test. The application should not answer from general knowledge if the indexed document does not contain the answer.

Record the responses/screenshots for your assessment evidence.

## 10. Run automated tests

```powershell
pytest
```

The included tests verify the basic API routes. RAG quality should be verified with the benchmark questions after ingestion.

## 11. GitHub

Create a public GitHub repository, then:

```powershell
git init
git add .
git commit -m "Initial RAG chatbot implementation"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Do not upload `.env` or API keys.

## 12. Deploy to Render

This repository includes `render.yaml`.

### Dashboard method

1. Push the project to GitHub.
2. Open Render.
3. Create a new Web Service.
4. Connect the GitHub repository.
5. Select the repository.
6. Use Python runtime.
7. Add:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
8. Deploy.

The included Render configuration uses:

```text
Build Command:
pip install -r requirements.txt

Start Command:
uvicorn app:app --host 0.0.0.0 --port $PORT
```

After deployment, open:

```text
https://YOUR-SERVICE.onrender.com/docs
```

## Important: ingestion before deployment

The deployed Render service needs access to the same Pinecone index.

Recommended workflow:

1. Create Pinecone index.
2. Run ingestion locally once.
3. Confirm vectors are visible in Pinecone.
4. Deploy the FastAPI application to Render.
5. Add the same OpenAI and Pinecone API keys to Render.
6. Test `/docs` and `/chat`.

The PDF itself does not need to be stored inside the Render application when Pinecone already contains the vectors and metadata.

## Security

Never put API keys in:

- Python files
- README
- GitHub commits
- screenshots
- frontend code

Use `.env` locally and Render Environment Variables in production.

## Assessment deliverables

Recommended final GitHub repository contents:

- Working Python RAG implementation
- README with setup and execution commands
- `requirements.txt`
- LangGraph workflow
- Pinecone retrieval
- OpenAI embeddings and generation
- FastAPI `/chat` endpoint
- Retrieved context in API output
- Retrieval confidence/relevance score
- Benchmark query evidence

Do not include private API keys or the PDF unless redistribution is permitted.

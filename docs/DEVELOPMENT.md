# Local Development Setup

This guide is a target setup checklist. Commands should be run and
verified one stage at a time.

## 1. Prerequisites

-   macOS on Apple Silicon
-   Python 3.12
-   Homebrew
-   PostgreSQL 18
-   pgvector extension available to PostgreSQL
-   Ollama
-   Node.js LTS and npm
-   Git

Check versions:

``` bash
python3 --version
brew --version
psql --version
node --version
npm --version
ollama --version
```

## 2. Project folders

From the repository root:

``` bash
mkdir -p backend frontend docs
```

## 3. Python virtual environment

``` bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python --version
which python
```

The selected Python should resolve to `backend/.venv/bin/python`. A
Conda `(base)` marker may remain in the prompt; the important check is
`which python`. Do not commit `.venv`.

Upgrade pip:

``` bash
python -m pip install --upgrade pip
```

Install application dependencies in stages after the initial project
structure is reviewed. Pin tested versions in the project dependency
file.

## 4. PostgreSQL and pgvector

Check service:

``` bash
brew services list
psql -d postgres -c "SELECT version();"
```

Check extension availability:

``` bash
psql -d postgres -c "SELECT name, default_version FROM pg_available_extensions WHERE name = 'vector';"
```

Create the application database if it does not already exist:

``` bash
createdb local_ai_workbench
```

Enable pgvector in that database:

``` bash
psql -d local_ai_workbench -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -d local_ai_workbench -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

If `createdb` reports that the database already exists, do not delete
it; continue by checking the extension.

## 5. Ollama

Check server:

``` bash
curl http://localhost:11434/api/version
ollama list
ollama ps
```

The chat model currently planned is `llama3.2`. Pull it if needed:

``` bash
ollama pull llama3.2
```

Candidate embedding model:

``` bash
ollama pull nomic-embed-text
```

Before defining the vector column, call the embedding endpoint and
inspect the returned vector length. Model names and published dimensions
are not a substitute for checking the installed model response.

## 6. Frontend

Create the Vite app from the repository root when ready:

``` bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
```

Follow prompts if the directory is not empty. Do not overwrite existing
work without checking it first.

## 7. Environment variables

Create `backend/.env` from `.env.example`. Example keys:

``` dotenv
DATABASE_URL=postgresql+psycopg://localhost:5432/local_ai_workbench
OLLAMA_BASE_URL=http://localhost:11434
CHAT_MODEL=llama3.2
EMBEDDING_MODEL=nomic-embed-text
MAX_UPLOAD_BYTES=10485760
CHUNK_SIZE=1200
CHUNK_OVERLAP=150
RETRIEVAL_TOP_K=5
MODEL_TIMEOUT_SECONDS=120
MAX_GENERATION_TOKENS=700
LOG_LEVEL=INFO
```

These values are starting points, not calibrated production settings.
Confirm database authentication works on the local machine. Never commit
`.env`.

## 8. Run the application

The eventual local workflow will use separate terminals: 1. PostgreSQL
and Ollama services 2. FastAPI API 3. Ingestion worker 4. Vite frontend

Exact commands should be added to the README after the entrypoints are
implemented.

## 9. Verify each milestone

-   Python environment points to `backend/.venv`.
-   PostgreSQL accepts connections.
-   `vector` extension is enabled in the application database.
-   Ollama health endpoint responds.
-   Chat and embedding models are available.
-   API health endpoint works.
-   A document can be uploaded, processed, and queried.
-   Tests pass from a clean checkout.

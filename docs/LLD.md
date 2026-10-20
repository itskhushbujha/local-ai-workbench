# Low-Level Design (LLD)

## 1. Suggested backend layout

``` text
backend/
├── app/
│   ├── main.py
│   ├── api/v1/
│   │   ├── health.py
│   │   ├── conversations.py
│   │   ├── chat.py
│   │   ├── documents.py
│   │   └── jobs.py
│   ├── core/
│   │   ├── config.py
│   │   ├── errors.py
│   │   └── logging.py
│   ├── db/
│   │   ├── session.py
│   │   └── models.py
│   ├── schemas/
│   │   ├── chat.py
│   │   ├── documents.py
│   │   ├── conversations.py
│   │   └── jobs.py
│   ├── repositories/
│   │   ├── conversation_repo.py
│   │   ├── document_repo.py
│   │   ├── chunk_repo.py
│   │   └── job_repo.py
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── ingestion_service.py
│   │   ├── retrieval_service.py
│   │   └── extraction_service.py
│   ├── integrations/ollama/
│   │   └── client.py
│   └── worker/
│       ├── main.py
│       └── ingestion_worker.py
├── tests/
├── alembic/
├── alembic.ini
├── pyproject.toml
└── .env.example
```

## 2. Layer responsibilities

-   **API route:** parse and validate HTTP input, call a service,
    translate result into HTTP/SSE.
-   **Schema:** request/response validation; do not use ORM objects as
    public response contracts.
-   **Service:** orchestrate business operations and transaction
    boundaries.
-   **Repository:** perform focused persistence operations.
-   **Integration client:** wrap Ollama or other external processes
    behind a small interface.
-   **Worker:** claim jobs and call ingestion services; no HTTP-specific
    logic.

Avoid putting SQL, prompt construction, and HTTP handling in one
function.

## 3. Chat state machine

``` text
pending -> streaming -> completed
                    \-> failed
```

Only a fully persisted final answer is `completed`. A disconnected
stream can be recorded as failed or interrupted according to the chosen
policy. The client should reload conversation history to learn the
persisted state.

## 4. Document state machine

``` text
queued -> processing -> ready
                    \-> queued (retry)
                    \-> failed (retry limit reached)
```

A document is searchable only when `ready`. Never expose partial chunks
from an unfinished ingestion as a ready document.

## 5. Job claim and recovery

Claim one eligible job in a short transaction using
`SELECT ... FOR UPDATE SKIP LOCKED`. Set status to processing, increment
attempts, and set `lease_expires_at`. Commit before parsing or calling
the embedding model.

A periodic recovery path should find expired leases. It may requeue jobs
below the retry cap and fail jobs at the cap. A worker must verify that
its claim/attempt is still current before committing output, so an
expired worker cannot overwrite a newer attempt.

## 6. Embedding and chunking

-   Extract text with page boundaries when possible.
-   Normalize whitespace without destroying meaningful structure.
-   Split by paragraph/sentence first, then enforce a token/character
    ceiling.
-   Use a small overlap to preserve context across boundaries.
-   Store `chunk_index`, page number, text, embedding model name, and
    embedding vector.
-   Batch embeddings conservatively on an 8 GB machine.
-   Record the embedding model/version with each vector.
-   If the embedding model changes dimensions or behavior, re-embed the
    corpus rather than mixing incompatible vectors.

**Important:** run an actual embedding request and inspect the returned
vector length before defining `vector(D)` in a migration. Do not infer
the dimension only from a model name.

## 7. Retrieval and citation rules

-   Embed the question using the same embedding model used for stored
    chunks.
-   Restrict the SQL query to the requested document scope.
-   Rank by cosine distance (`<=>`) initially.
-   Apply top-k and a calibrated relevance threshold.
-   Do not invent citation IDs or page numbers.
-   Citation IDs must be among the chunks returned for this exact
    request.
-   The UI should render a citation from stored metadata, not from
    arbitrary model-generated fields.
-   When evidence is weak or absent, state that limitation and ask for a
    better source or narrower question.

## 8. Streaming contract

Use SSE with named event types: - `message_start` - `token` -
`citations` - `done` - `error`

Do not hold a DB transaction open while streaming. `done` is sent only
after the final answer and citations are committed. If the client
disconnects, the server should stop unnecessary work where possible and
ensure message status remains accurate.

## 9. Configuration

Keep environment-specific settings in typed configuration: -
`DATABASE_URL` - `OLLAMA_BASE_URL` - `CHAT_MODEL` - `EMBEDDING_MODEL` -
`MAX_UPLOAD_BYTES` - `CHUNK_SIZE` - `CHUNK_OVERLAP` -
`RETRIEVAL_TOP_K` - `RETRIEVAL_MIN_SCORE` or calibrated distance
threshold - `MODEL_TIMEOUT_SECONDS` - `MAX_GENERATION_TOKENS` -
`LOG_LEVEL`

Provide safe defaults for local development. Never store API keys or
passwords in source control.

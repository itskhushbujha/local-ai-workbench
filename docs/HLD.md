# High-Level Design (HLD)

## 1. System context

The application is a local modular monolith with two backend processes:
the HTTP API and an ingestion worker. Both use the same application
modules and PostgreSQL database. Ollama serves local chat and embedding
models.

``` text
[React + TypeScript UI]
          |
       HTTP / SSE
          |
     [FastAPI API] ----------- [Ollama: chat model]
          |                    [Ollama: embedding model]
          |
   [PostgreSQL + pgvector]
          ^
          |
 [Background ingestion worker]
```

## 2. Major components

### Frontend

Responsible for conversation and document UI, upload progress/status,
SSE parsing, citations, and clear error states. It does not connect
directly to PostgreSQL or Ollama.

### FastAPI API

Validates requests, authenticates/authorizes resources if multi-user
support is added later, invokes services, returns typed responses, and
streams chat events. Routes should not contain complex SQL, prompts, or
model orchestration.

### Application services

-   **Chat service:** persists messages, builds context, invokes
    generation, handles completion/failure.
-   **Retrieval service:** embeds query, searches scoped chunks, applies
    thresholds and limits.
-   **Document service:** validates upload, stores original bytes and
    creates job atomically.
-   **Ingestion service:** extracts text, chunks content, embeds
    batches, stores chunks.
-   **Extraction service:** requests structured output and validates it
    against Pydantic schemas.

### Repositories

Encapsulate database operations for conversations, messages, documents,
chunks, citations, and jobs.

### Ingestion worker

Claims jobs using PostgreSQL row locking, processes them outside the
claim transaction, and marks success or failure. A lease and retry cap
enable recovery after crashes.

### Ollama integration

A small client wrapper handles health checks, model calls, timeouts,
response parsing, and error translation. The application must not assume
that a model is always available.

## 3. Key flows

### Document ingestion

1.  Validate extension, MIME type, size, and file signature where
    feasible.
2.  Compute SHA-256 content hash.
3.  In one transaction, insert document bytes and an ingestion job.
4.  Return `202 Accepted`.
5.  Worker claims job and commits the claim/lease.
6.  Worker extracts text and chunks it with page metadata.
7.  Worker embeds bounded batches.
8.  In a transaction, replace/insert chunks and mark document `ready`,
    job `succeeded`.
9.  On error, record a sanitized code, increment attempt count, retry
    within a cap, then mark failed.

### Chat with retrieval

1.  Validate conversation and document scope.
2.  Persist user message and pending assistant message.
3.  Retrieve relevant chunks, scoped to selected documents.
4.  Build a prompt that labels retrieved content as untrusted evidence.
5.  Call Ollama without holding a database transaction open.
6.  Stream tokens/events to the client.
7.  Validate citations against actual retrieved chunk IDs and scope.
8.  Commit final answer, citations, and completed status atomically.
9.  If generation fails, mark assistant message failed; never mark
    partial output completed.

## 4. Deployment topology

Local development initially runs: - PostgreSQL as a Homebrew service. -
Ollama as a local service. - FastAPI API in one terminal. - Ingestion
worker in another terminal. - Vite frontend in another terminal.

Docker and Redis are intentionally deferred to reduce memory and setup
complexity on an 8 GB Apple Silicon machine.

## 5. Cross-cutting concerns

-   Configuration from environment variables and `.env` (never commit
    secrets).
-   Structured logs with request ID, job ID, duration, and status.
-   Explicit timeouts for model calls.
-   Bounded request bodies, text lengths, chunk sizes, top-k retrieval,
    and generation tokens.
-   Database migrations through Alembic.
-   Health/readiness checks for PostgreSQL and Ollama.
-   Unit tests around deterministic logic and integration tests for
    PostgreSQL/pgvector.

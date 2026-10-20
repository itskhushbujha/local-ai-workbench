# Implementation Roadmap

Build incrementally. Each milestone should end with a verified, working
state before the next begins.

## Milestone 1 --- Foundation

-   Create repository folders and Git ignore rules.
-   Create and activate Python virtual environment.
-   Add typed settings and `.env.example`.
-   Connect SQLAlchemy to PostgreSQL.
-   Add Alembic and first migration.
-   Add `/health`.
-   Add basic tests and structured logging.
-   Verify pgvector in the project database.
-   Probe embedding output dimensions before vector migration.

**Exit criteria:** API starts, database connection is verified,
migrations work from an empty database, tests pass.

## Milestone 2 --- Conversations and local chat

-   Add conversation/message tables and schemas.
-   Implement conversation CRUD.
-   Add Ollama client wrapper.
-   Implement message persistence and SSE.
-   Handle timeouts, model unavailable, and disconnects.
-   Add UI for conversations and streaming response.

**Exit criteria:** local chat persists history and never marks partial
output as completed.

## Milestone 3 --- Document ingestion

-   Add document and job models.
-   Implement upload validation and byte storage.
-   Implement PostgreSQL-backed worker queue with lease/retry.
-   Extract PDF/TXT text and page metadata.
-   Chunk text and generate embeddings in bounded batches.
-   Store chunks and mark documents ready/failed.
-   Add upload and job-status UI.

**Exit criteria:** a test PDF and TXT can reach ready state, and a
failed job is recoverable.

## Milestone 4 --- Retrieval-augmented Q&A

-   Embed user query.
-   Implement scope-restricted vector retrieval.
-   Tune top-k and threshold on a small corpus.
-   Add prompt assembly with untrusted-evidence delimiters.
-   Validate citation IDs against retrieved chunks.
-   Persist citations and show source references in the UI.
-   Implement insufficient-evidence behavior.

**Exit criteria:** answerable questions cite supporting sources;
unanswerable questions abstain appropriately.

## Milestone 5 --- Structured extraction and controlled tools

-   Define a few useful Pydantic schemas.
-   Generate structured output and validate it.
-   Add bounded repair/retry behavior.
-   Add only explicit allowlisted tools with strict input validation.
-   Add tests for malicious or malformed inputs.

**Exit criteria:** invalid outputs fail safely and no arbitrary code
execution is possible.

## Milestone 6 --- Evaluation and portfolio release

-   Add a small repeatable evaluation set.
-   Report retrieval recall@k, citation coverage, abstention quality,
    and latency.
-   Add request/job correlation IDs and sanitized logs.
-   Improve loading/error/accessibility states.
-   Write a demo script and known-limitations section.
-   Capture screenshots and explain architectural trade-offs.

**Exit criteria:** a clean checkout can reproduce the demo and test
suite; claims are supported by measured results.

# Testing and Evaluation Plan

## 1. Testing layers

### Unit tests

Test deterministic logic without Ollama or a real database: - Upload
type and size validation - Text normalization and chunk boundaries -
Citation ID validation - Pydantic structured-output validation - Error
mapping - Configuration validation - Job retry policy and state
transitions

### Integration tests

Use a dedicated test database with pgvector: - Alembic migrations from
an empty database - Conversation/message persistence - Document upload
and job creation in one transaction - Job claim with concurrent
workers - Ingestion success/failure state changes - Scoped vector
retrieval - Citation foreign keys and snapshots - Soft-delete and purge
behavior

### API tests

Use FastAPI's test client: - Health and dependency degradation - Invalid
IDs and missing resources - Upload rejection cases - Correct
`202 Accepted` response - SSE event sequence and error behavior - Stream
disconnect does not falsely mark a message completed

### Frontend tests

As the UI grows: - Upload states and errors - SSE event parsing -
Conversation history rendering - Citation display - Accessible keyboard
interactions

## 2. Evaluation dataset

Maintain a small version-controlled JSONL or YAML set of questions over
a known document corpus. Each case should include: - question - selected
document IDs or logical scope - expected supporting chunk/document -
expected answer facts - whether the correct behavior is to abstain -
optional acceptable answer variants

Do not use only questions the system can easily answer. Include
unanswerable and ambiguous questions.

## 3. Core metrics

-   **Retrieval recall@k:** whether a known relevant chunk appears in
    the top k.
-   **Citation precision:** whether cited passages actually support the
    claims they accompany.
-   **Citation coverage:** proportion of source-dependent claims
    supported by citations.
-   **Abstention quality:** whether the system declines to answer when
    evidence is insufficient.
-   **Latency:** upload-to-ready, retrieval time, time to first token,
    total generation time.
-   **Reliability:** job failure rate, retries, model timeout rate,
    malformed structured-output rate.
-   **Resource use:** memory pressure and model load behavior on the
    target Mac.

## 4. Failure scenarios to test

-   Ollama is stopped.
-   PostgreSQL is unavailable.
-   The embedding model is missing.
-   A PDF has no extractable text.
-   A file exceeds the upload limit.
-   A job worker crashes after claiming a job.
-   A lease expires while an old worker is still running.
-   A model returns malformed structured JSON.
-   Retrieval returns no results.
-   Retrieval returns relevant chunks from a document outside the
    requested scope.
-   A citation refers to a chunk not returned by retrieval.
-   A client disconnects during SSE.
-   The same file is uploaded twice.

## 5. Definition of done

A feature is not done merely because the happy path works. It should
have: - Typed request and response contracts - Tests for at least one
important failure path - Sanitized error behavior - Useful logs -
Documentation updated - A manual verification procedure

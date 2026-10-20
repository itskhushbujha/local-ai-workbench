# Database Design

## 1. Technology

PostgreSQL 18 with the pgvector extension. SQLAlchemy 2.x and Psycopg 3
provide application access; Alembic manages schema changes.

## 2. Core tables

### `conversations`

-   `id UUID PRIMARY KEY`
-   `title TEXT NOT NULL`
-   `created_at TIMESTAMPTZ NOT NULL`
-   `updated_at TIMESTAMPTZ NOT NULL`

### `messages`

-   `id UUID PRIMARY KEY`
-   `conversation_id UUID NOT NULL REFERENCES conversations(id)`
-   `role TEXT NOT NULL` --- constrained to `user` or `assistant` in v1
-   `content TEXT NOT NULL`
-   `status TEXT NOT NULL` --- e.g. `pending`, `streaming`, `completed`,
    `failed`
-   `model_name TEXT NULL`
-   `error_code TEXT NULL`
-   `created_at TIMESTAMPTZ NOT NULL`
-   `completed_at TIMESTAMPTZ NULL`

Indexes: `(conversation_id, created_at)`.

### `documents`

-   `id UUID PRIMARY KEY`
-   `filename TEXT NOT NULL`
-   `media_type TEXT NOT NULL`
-   `file_size_bytes BIGINT NOT NULL`
-   `content_hash TEXT NOT NULL`
-   `original_file BYTEA NOT NULL`
-   `status TEXT NOT NULL` --- `queued`, `processing`, `ready`,
    `failed`, `deleted`
-   `error_code TEXT NULL`
-   `created_at TIMESTAMPTZ NOT NULL`
-   `updated_at TIMESTAMPTZ NOT NULL`
-   `deleted_at TIMESTAMPTZ NULL`

The original bytes live in PostgreSQL as required for this project.
Enforce a configurable upload limit to prevent oversized database rows
and memory pressure.

### `ingestion_jobs`

-   `id UUID PRIMARY KEY`
-   `document_id UUID NOT NULL REFERENCES documents(id)`
-   `status TEXT NOT NULL`
-   `attempt_count INTEGER NOT NULL DEFAULT 0`
-   `lease_expires_at TIMESTAMPTZ NULL`
-   `error_code TEXT NULL`
-   `error_message TEXT NULL` --- sanitized, no secrets
-   `created_at TIMESTAMPTZ NOT NULL`
-   `updated_at TIMESTAMPTZ NOT NULL`
-   `completed_at TIMESTAMPTZ NULL`

Indexes should support finding queued jobs and expired leases.

### `document_chunks`

-   `id UUID PRIMARY KEY`
-   `document_id UUID NOT NULL REFERENCES documents(id)`
-   `chunk_index INTEGER NOT NULL`
-   `content TEXT NOT NULL`
-   `page_number INTEGER NULL`
-   `embedding VECTOR(D) NOT NULL`
-   `embedding_model TEXT NOT NULL`
-   `created_at TIMESTAMPTZ NOT NULL`

Constraint: unique `(document_id, chunk_index)`. `D` is a placeholder
and must be replaced only after measuring the selected embedding model's
actual vector length.

### `message_citations`

-   `message_id UUID NOT NULL REFERENCES messages(id)`
-   `chunk_id UUID NOT NULL REFERENCES document_chunks(id)`
-   `citation_order INTEGER NOT NULL`
-   `quote TEXT NULL`
-   `filename_snapshot TEXT NULL`
-   `page_number_snapshot INTEGER NULL`
-   Primary key `(message_id, citation_order)`

Citation snapshots can preserve useful historical display after a
document is soft-deleted or permanently purged.

### `message_document_scopes`

-   `message_id UUID NOT NULL REFERENCES messages(id)`
-   `document_id UUID NOT NULL REFERENCES documents(id)`
-   Primary key `(message_id, document_id)`

This records which documents were in scope for a response, useful for
reproducibility and auditability.

## 3. Relationships

``` text
conversations 1 --- N messages
documents     1 --- N ingestion_jobs
documents     1 --- N document_chunks
messages      1 --- N message_citations
document_chunks 1 --- N message_citations
messages      N --- N documents (via message_document_scopes)
```

## 4. Transaction boundaries

-   **Upload:** insert document and ingestion job in the same
    transaction.
-   **Claim job:** lock and update one job in a short transaction, then
    commit.
-   **Process job:** do file parsing and model calls outside a long
    database transaction.
-   **Finish ingestion:** store chunks and mark document/job status in
    one transaction.
-   **Start chat:** persist user and pending assistant messages
    together.
-   **Finish chat:** persist final answer, citations, and completed
    status together.
-   **Failure:** mark message/job/document with explicit failed status
    and a sanitized code.

Never hold a transaction open while waiting for Ollama generation or
embedding calls.

## 5. Retrieval query

Use cosine distance initially, conceptually:

``` sql
SELECT id, document_id, content, page_number,
       embedding <=> :query_embedding AS distance
FROM document_chunks
WHERE document_id = ANY(:document_ids)
ORDER BY embedding <=> :query_embedding
LIMIT :top_k;
```

The real implementation must handle empty document scope,
deleted/not-ready documents, valid vector adaptation, and calibrated
distance thresholds. Verify the exact pgvector SQLAlchemy integration
before relying on this illustrative query.

## 6. Indexing strategy

Start with ordinary indexes and measure performance before adding
approximate-nearest-neighbor indexes. For a small local corpus, an ANN
index may not be necessary. If adding HNSW/IVFFlat later, benchmark
recall and latency against exact search.

## 7. Data lifecycle

-   Soft-delete by default so users can remove documents from future
    retrieval without breaking all historical UI.
-   Provide an explicit purge path to remove bytes, chunks, and related
    records according to the retention policy.
-   Avoid cascading away citation metadata if historical answers must
    remain understandable.
-   Keep migrations as the source of truth; do not rely on ad hoc manual
    schema edits in the application.

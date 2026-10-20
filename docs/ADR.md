# Architecture Decision Records (ADR)

This file records the key choices and their rationale. Revisit decisions
when evidence changes.

## ADR-001: Local-first inference through Ollama

**Status:** Accepted

**Decision:** Use Ollama to serve chat and embedding models locally.

**Why:** Simple local model lifecycle, local HTTP interface, and no
mandatory hosted AI dependency.

**Trade-offs:** Model availability and performance depend on machine
memory and hardware. Model output is not guaranteed correct.

## ADR-002: React + TypeScript + Vite frontend

**Status:** Accepted

**Decision:** Use a standard React/TypeScript frontend.

**Why:** Good portfolio value, broad ecosystem, and clear separation
between UI and API.

**Trade-offs:** More setup than a single-file Python UI.

## ADR-003: FastAPI backend

**Status:** Accepted

**Decision:** Use Python 3.12 and FastAPI with Pydantic schemas.

**Why:** Typed API contracts, async support, OpenAPI documentation, and
natural integration with Python document/AI libraries.

## ADR-004: PostgreSQL + pgvector

**Status:** Accepted

**Decision:** Store application state and vector embeddings in
PostgreSQL.

**Why:** One durable database and transactional coordination for app
data and background jobs.

**Trade-offs:** Vector dimension must match the embedding model;
indexing and retrieval thresholds require evaluation.

## ADR-005: Store original document bytes in PostgreSQL

**Status:** Accepted for v1

**Decision:** Store uploaded PDF/TXT bytes in a `BYTEA` column.

**Why:** Keeps the initial system self-contained and transactional.

**Trade-offs:** Database growth and memory use; mitigate with strict
upload limits and explicit retention.

## ADR-006: Background ingestion with PostgreSQL queue

**Status:** Accepted

**Decision:** Use a separate worker process and a PostgreSQL-backed job
queue with leases and bounded retries.

**Why:** Avoids blocking upload requests and avoids an extra Redis
dependency.

**Trade-offs:** Requires careful stale-lease recovery and concurrency
tests.

## ADR-007: SSE for chat streaming

**Status:** Accepted

**Decision:** Use Server-Sent Events for server-to-browser chat output.

**Why:** Simple one-way event stream over HTTP, suitable for token
streaming.

**Trade-offs:** No built-in replay guarantee; persisted history is the
recovery path.

## ADR-008: Single-user local application initially

**Status:** Accepted for v1

**Decision:** Focus on a local single-user workflow before implementing
authentication and multi-user authorization.

**Why:** Keeps the first release focused.

**Trade-offs:** Do not expose the service to untrusted networks until
authentication, authorization, and deployment hardening are implemented.

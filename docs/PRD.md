# Product Requirements Document (PRD)

**Product:** Local AI Intelligence Workbench\
**Version:** 1.2 --- implementation-oriented baseline\
**Status:** Proposed specification

## 1. Problem statement

People need a private, understandable way to chat with a local model and
ask questions about their own documents. A useful answer must
distinguish what the sources support from what the model merely guesses.

## 2. Product vision

Build a portfolio-quality, local-first AI workbench that demonstrates
practical AI application engineering: model integration,
retrieval-augmented generation (RAG), data modeling, asynchronous work,
validation, observability, evaluation, and a polished user interface.

## 3. Goals

1.  Chat with a model served by Ollama on the local machine.
2.  Persist conversations and messages.
3.  Upload PDF and TXT documents.
4.  Process documents in a background worker.
5.  Retrieve semantically relevant document passages using embeddings
    and pgvector.
6.  Produce answers with citations that refer to stored chunks and
    document metadata.
7.  Clearly indicate when evidence is insufficient.
8.  Validate structured extraction output against a schema.
9.  Expose only explicitly allowlisted tools with validated inputs.
10. Include tests, evaluation cases, logs, metrics, and reproducible
    setup instructions.

## 4. Non-goals

-   Training or fine-tuning a foundation model.
-   Guaranteeing factual correctness.
-   Running arbitrary generated code or unrestricted agents.
-   Sending document content to cloud AI APIs by default.
-   Supporting every document format in the first release.
-   Multi-user enterprise authentication or complex distributed
    deployment in v1.
-   Requiring Kubernetes, Redis, or Docker for local development.

## 5. Target user and primary journeys

### Journey A: local chat

1.  User opens the app.
2.  User creates or opens a conversation.
3.  User sends a message.
4.  API stores the user message and a pending assistant message.
5.  API calls the local model and streams response events.
6.  API stores the completed answer and status.

### Journey B: document Q&A

1.  User uploads a PDF or TXT file.
2.  API validates the file and stores the original bytes plus an
    ingestion job.
3.  API returns an accepted response with document and job IDs.
4.  Background worker extracts text, chunks it, embeds chunks, and
    stores them.
5.  UI shows processing state and then readiness or failure.
6.  User asks a question scoped to selected documents.
7.  Retrieval returns relevant chunks; the model answers using that
    evidence.
8.  The UI displays citations linked to the source document and page
    where available.

### Journey C: structured extraction

1.  User selects an extraction schema or template.
2.  The application retrieves relevant source text.
3.  The model proposes structured data.
4.  Pydantic validates the result.
5.  Invalid results are retried in a bounded way or returned as
    validation failures; never silently accept malformed data.

## 6. Functional requirements

### P0 --- first usable release

-   Health endpoint reports application and dependency state.
-   Create, list, and retrieve conversations.
-   Persist user and assistant messages with status.
-   Local chat via Ollama.
-   Stream chat using Server-Sent Events (SSE).
-   Upload PDF/TXT with configurable size limit.
-   Store original bytes in PostgreSQL `BYTEA`.
-   Process uploads asynchronously.
-   Extract text, preserve page numbers when possible, and chunk text.
-   Generate local embeddings and store them in pgvector.
-   Retrieve chunks by semantic similarity, restricted to the selected
    document scope.
-   Display citations derived from retrieved chunk IDs and metadata.
-   Return a clear insufficient-evidence response when retrieval is weak
    or empty.
-   Support document status, job status, and retry-safe ingestion.
-   Include backend tests, setup documentation, and useful error
    responses.

### P1 --- quality and portfolio readiness

-   Schema-validated structured extraction.
-   Small allowlist of safe tools, such as calculator or document
    metadata lookup.
-   Evaluation dataset and repeatable evaluation runner.
-   Metrics for request latency, model latency, retrieval results,
    citation coverage, and failures.
-   Better document management and explicit permanent deletion.
-   Frontend tests and accessibility checks.
-   Screenshots and a short demo walkthrough.

## 7. Non-functional requirements

-   **Local-first:** inference and embeddings run locally by default.
-   **Resource-aware:** bounded input, chunk, and batch sizes.
-   **Reliability:** job retries are bounded; stale jobs can be
    recovered.
-   **Data integrity:** file storage and job creation are transactional.
-   **Maintainability:** API routes stay thin; business logic belongs in
    services.
-   **Testability:** external dependencies are wrapped behind
    interfaces.
-   **Safety:** validate uploads, constrain retrieval scope, validate
    model outputs, and never execute arbitrary model-generated code.
-   **Observability:** log request/job IDs, durations, statuses, and
    sanitized errors.
-   **Honesty:** do not invent citations; distinguish model output from
    retrieved evidence.

## 8. UX principles

-   Show clear document states: `queued`, `processing`, `ready`,
    `failed`.
-   Show useful error messages without exposing stack traces or secrets.
-   Show citations with filename, page number when known, and a short
    supporting quote.
-   Allow users to see which documents are in scope for a question.
-   Make it easy to retry a failed ingestion.
-   Make incomplete or interrupted answers visibly different from
    completed answers.

## 9. Success criteria

-   A clean local setup can run the API, worker, frontend, PostgreSQL,
    and Ollama.
-   A PDF and TXT can be uploaded and reach `ready`.
-   A question about a document returns at least one relevant citation
    when evidence exists.
-   An unsupported question produces an insufficient-evidence response
    rather than fabricated source claims.
-   A disconnected or failed stream does not leave a partial answer
    marked completed.
-   Tests cover validation, job claiming/recovery, retrieval scope,
    citations, and failure paths.
-   The README explains limitations and demonstrates the app clearly.

## 10. Risks and mitigations

  -----------------------------------------------------------------------
  Risk                                Mitigation
  ----------------------------------- -----------------------------------
  8 GB memory pressure                Use quantized models, one model at
                                      a time where practical, small
                                      batches

  Wrong vector dimension              Probe actual embedding output
                                      before migration

  Hallucinated citations              Construct citations only from
                                      retrieved chunk records

  Stuck ingestion jobs                Leases, bounded retries, stale-job
                                      recovery

  Duplicate ingestion                 Content hash and idempotency policy

  Prompt injection in documents       Treat retrieved content as
                                      untrusted data; no
                                      instruction-following tools from
                                      document text

  PostgreSQL/pgvector mismatch        Verify extension and migration in
                                      the target database

  Model response failure              Persist explicit failed status and
                                      sanitized error code
  -----------------------------------------------------------------------

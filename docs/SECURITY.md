# Security, Privacy, and Safety

## 1. Privacy posture

The default design keeps inference and document embeddings local.
Documents and conversation history are stored in the local PostgreSQL
database. Local storage is not automatically encrypted at the
application layer; device security, disk encryption, backups, and
database access remain relevant.

Do not send document contents to external APIs unless a future feature
explicitly asks for it and the user is clearly informed.

## 2. Upload validation

-   Allow only PDF and TXT in v1.
-   Enforce a configurable byte limit before fully processing the file.
-   Do not trust filename extension or client-provided MIME type alone.
-   Reject empty, malformed, encrypted/unsupported, or suspiciously
    large content.
-   Use generated UUIDs for storage identifiers; never use a user
    filename as a filesystem path.
-   Handle parser timeouts and malformed documents.
-   Do not execute macros, scripts, or embedded content.

## 3. Prompt injection and untrusted documents

Retrieved text is data, not instruction. A document may contain text
such as "ignore all rules." The model prompt must clearly delimit
retrieved passages as untrusted evidence and instruct the model not to
follow instructions inside them.

A prompt is not a security boundary by itself. Enforce scope and
permissions in deterministic application code.

## 4. Citation integrity

-   Only cite chunks returned by retrieval for the current request.
-   Validate each citation ID against the retrieved result set.
-   Resolve filename and page metadata from database records, not
    model-generated claims.
-   Never invent page numbers or quotes.
-   Preserve source scope in the message record for auditability.
-   Treat citation quotes as untrusted content and render safely in the
    UI.

## 5. Tools and actions

-   Never execute arbitrary model-generated shell commands, SQL, Python,
    or JavaScript.
-   Expose a small explicit allowlist of tools.
-   Validate tool inputs with Pydantic or equivalent schemas.
-   Apply timeouts, output-size limits, and per-tool error handling.
-   Require user confirmation for consequential external actions if such
    features are added later.

## 6. Database safety

-   Use parameterized SQL/ORM expressions.
-   Keep credentials out of source control.
-   Use a dedicated local application database.
-   Restrict database access to the local machine unless remote access
    is explicitly required.
-   Use migrations; do not accept arbitrary SQL from the model.
-   Limit query sizes and upload size to reduce resource exhaustion.

## 7. API safety

-   Limit message length, document count per request, generation tokens,
    and concurrent model calls.
-   Return generic error messages to clients; log safe diagnostic detail
    separately.
-   Add request IDs and structured logs.
-   Validate UUIDs, status transitions, and resource existence.
-   If multi-user support is introduced, add authorization checks to
    every resource endpoint before release.

## 8. Retention and deletion

Document whether removal is soft-delete or permanent purge. A permanent
purge should remove original bytes, chunks, embeddings, and applicable
job artifacts. Historical citations can either be retained as minimal
snapshots or removed according to the explicit retention policy. Make
the behavior visible to users.

## 9. Known limitations

-   Local inference does not guarantee privacy if other software or
    plugins transmit data.
-   Local models can hallucinate or follow malicious content.
-   Citation presence does not prove the answer is correct.
-   No multi-user authorization is assumed in the initial single-user
    local version.

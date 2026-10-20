# API Specification

**Base path:** `/api/v1`\
**Transport:** JSON over HTTP; chat uses Server-Sent Events (SSE).\
**IDs:** UUID strings.

The contracts below are the intended API. They must be implemented and
tested before being treated as live behavior.

## 1. Health

### `GET /health`

Returns application and dependency status.

Example:

``` json
{
  "status": "ok",
  "dependencies": {
    "database": "ok",
    "ollama": "ok"
  }
}
```

A dependency may be `degraded` or `unavailable`; do not return `ok` if a
required dependency is down.

## 2. Conversations

### `POST /api/v1/conversations`

Request:

``` json
{ "title": "Research notes" }
```

Response: `201 Created`

``` json
{
  "id": "uuid",
  "title": "Research notes",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z"
}
```

### `GET /api/v1/conversations`

Returns a paginated list, newest updated first.

### `GET /api/v1/conversations/{conversation_id}`

Returns one conversation or `404`.

### `GET /api/v1/conversations/{conversation_id}/messages`

Returns persisted messages ordered by creation time.

## 3. Chat stream

### `POST /api/v1/conversations/{conversation_id}/messages`

Request:

``` json
{
  "content": "What are the main findings?",
  "document_ids": ["uuid"],
  "stream": true
}
```

Response content type: `text/event-stream`.

Example event sequence:

``` text
event: message_start
data: {"message_id":"uuid","status":"streaming"}

event: token
data: {"text":"The"}

event: token
data: {"text":" report"}

event: citations
data: {"items":[{"chunk_id":"uuid","document_id":"uuid","filename":"report.pdf","page_number":3,"quote":"..."}]}

event: done
data: {"message_id":"uuid","status":"completed"}
```

If the error occurs before streaming starts, return a normal HTTP error.
Once streaming begins, emit an `error` event if possible. Never emit
`done` for an incomplete answer.

### Error envelope

``` json
{
  "error": {
    "code": "MODEL_UNAVAILABLE",
    "message": "The local model service is unavailable.",
    "request_id": "uuid"
  }
}
```

Do not expose stack traces, SQL, prompts containing sensitive content,
or environment secrets.

## 4. Documents

### `POST /api/v1/documents`

Multipart upload with a `file` field. Accept PDF and TXT only in v1.
Enforce size limits and validate actual content as far as practical.

Response: `202 Accepted`

``` json
{
  "document_id": "uuid",
  "job_id": "uuid",
  "status": "queued"
}
```

### `GET /api/v1/documents`

List document metadata and statuses. Do not return original file bytes.

### `GET /api/v1/documents/{document_id}`

Return metadata, status, and a safe error code if failed.

### `DELETE /api/v1/documents/{document_id}`

Default behavior should soft-delete/archive a document and remove it
from new retrieval. Permanent deletion is a separate explicit operation
or policy. Preserve historical citation display via stored citation
snapshots if required.

## 5. Jobs

### `GET /api/v1/jobs/{job_id}`

Returns:

``` json
{
  "id": "uuid",
  "document_id": "uuid",
  "status": "processing",
  "attempt_count": 1,
  "error_code": null,
  "created_at": "2026-01-01T12:00:00Z",
  "completed_at": null
}
```

## 6. Status codes

-   `200` successful read
-   `201` resource created
-   `202` accepted for asynchronous processing
-   `400` malformed request
-   `404` resource not found
-   `413` upload too large
-   `415` unsupported media type
-   `422` schema/validation error
-   `429` rate or concurrency limit reached, if implemented
-   `500` unexpected application error
-   `503` required dependency unavailable

## 7. API implementation rules

-   Validate all inputs using Pydantic.
-   Use explicit response schemas.
-   Limit message length, upload size, document scope size, and
    generation length.
-   Validate conversation/document ownership if multi-user support is
    later added.
-   Keep route handlers thin.
-   Add request IDs to logs and error responses.
-   Document pagination and sort behavior when implementing list
    endpoints.

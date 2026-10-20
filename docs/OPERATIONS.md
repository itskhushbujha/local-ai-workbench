# Operations and Troubleshooting

## 1. Service checks

### PostgreSQL

``` bash
brew services list
psql -d local_ai_workbench -c "SELECT 1;"
psql -d local_ai_workbench -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

### Ollama

``` bash
curl http://localhost:11434/api/version
ollama list
ollama ps
```

If the API responds but the model is missing, pull the configured model.
Avoid loading multiple large models simultaneously on an 8 GB machine.

## 2. Common problems

### `psql` cannot connect

-   Check whether the PostgreSQL Homebrew service is started.
-   Confirm the target database exists.
-   Check the connection URL and local authentication method.
-   Do not delete or recreate a database as a first troubleshooting
    step.

### `vector` extension is unavailable

-   Confirm pgvector is installed for the PostgreSQL version being used.
-   Check `pg_available_extensions` on the same PostgreSQL server.
-   Enable the extension in the application database, not only in the
    default `postgres` database.

### Ollama model not found

-   Compare the configured model name with `ollama list`.
-   Pull the model if needed.
-   Verify Ollama is responding at the configured base URL.

### High memory pressure

-   Use a smaller quantized model.
-   Reduce context and generation limits.
-   Keep embedding batches small.
-   Avoid concurrent ingestion and large chat generation.
-   Inspect `ollama ps` to see loaded models.

### Document remains processing

-   Inspect the job status, attempt count, lease expiry, and sanitized
    error code.
-   Confirm the worker process is running.
-   Verify the PDF has extractable text.
-   Ensure expired leases are recovered and retries are bounded.

### No relevant retrieval results

-   Confirm the document is `ready`.
-   Confirm the query uses the same embedding model as indexed chunks.
-   Verify vector dimensions and embedding model version.
-   Inspect the top results and distance values.
-   Recalibrate threshold and top-k using the evaluation set.

### Citations look wrong

-   Confirm citation IDs are validated against retrieved chunk IDs.
-   Confirm the SQL query restricts results to selected documents.
-   Resolve filename and page number from stored records.
-   Never trust model-generated citation metadata.

## 3. Logging

Log: - request ID and job ID - operation and status - elapsed time -
dependency/model name - retry count - safe error code

Do not log: - passwords, tokens, or secrets - full document contents by
default - complete prompts containing sensitive user data - raw stack
traces in client responses

## 4. Backups and deletion

A local database may contain original files, conversations, and derived
embeddings. Document a backup policy before relying on it for important
data. Test restoration, not only backup creation. Ensure purge behavior
covers original bytes and derived chunks.

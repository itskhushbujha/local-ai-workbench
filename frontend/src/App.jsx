import { useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  async function sendMessage(event) {
    event.preventDefault();

    const text = question.trim();
    if (!text || loading) return;

    setQuestion("");
    setError("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: text }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail ?? `Request failed (${response.status})`);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer ?? "No answer returned.",
          sources: data.sources ?? [],
        },
      ]);
    } catch (err) {
      setError(
        `${err.message}. Check that the backend and Ollama are running.`,
      );
    } finally {
      setLoading(false);
    }
  }

  async function uploadDocument(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    const allowedExtensions = [".pdf", ".txt"];
    const fileName = file.name.toLowerCase();

    if (!allowedExtensions.some((ext) => fileName.endsWith(ext))) {
      setError("Please select a PDF or TXT file.");
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("File size must be 10 MB or less.");
      event.target.value = "";
      return;
    }

    setUploading(true);
    setUploadMessage("");
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail ?? `Upload failed (${response.status})`);
      }

      setUploadMessage(
        `${file.name} uploaded successfully. ${
          data.status === "processed"
            ? "Your document is ready for questions."
            : "Document processing may still be in progress."
        }`,
      );
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  return (
    <main className="app">
      <header className="header">
        <div className="logo">✦</div>

        <div>
          <h1>Local AI</h1>
          <p>Your private AI assistant</p>
        </div>

        <div className="local-badge">
          <span className="status-dot" />
          Local
        </div>
      </header>

      <section className="workspace">
        <div className="workspace-heading">
          <h2>Document assistant</h2>
          <p>Upload your documents and ask questions about them.</p>
        </div>

        <div className="upload-panel">
          <div className="upload-icon">↑</div>

          <div className="upload-details">
            <h3>Upload a document</h3>
            <p>PDF or TXT · Maximum file size: 10 MB</p>
          </div>

          <button
            type="button"
            className="upload-button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Choose file"}
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,application/pdf,text/plain"
            onChange={uploadDocument}
            hidden
          />
        </div>

        {uploadMessage && (
          <div className="notice success" role="status">
            <span>✓</span>
            <p>{uploadMessage}</p>
          </div>
        )}

        {error && (
          <div className="notice error" role="alert">
            <p>{error}</p>
            <button
              type="button"
              onClick={() => setError("")}
              aria-label="Dismiss error"
            >
              ×
            </button>
          </div>
        )}

        <div className="chat-panel">
          <div className="chat-heading">
            <div>
              <h3>Chat</h3>
              <p>Ask anything about your documents</p>
            </div>

            {messages.length > 0 && (
              <button
                type="button"
                className="clear-button"
                onClick={() => setMessages([])}
              >
                Clear chat
              </button>
            )}
          </div>

          <div className="chat-messages" aria-live="polite">
            {messages.length === 0 ? (
              <div className="welcome">
                <div className="welcome-icon">✦</div>
                <h2>What would you like to know?</h2>
                <p>Upload a document, then ask a question to get started.</p>

                <div className="suggestion">"Summarize my document"</div>
                <div className="suggestion">"What are the main points?"</div>
              </div>
            ) : (
              messages.map((message, index) => (
                <article className={`message ${message.role}`} key={index}>
                  <div className="message-role">
                    {message.role === "user" ? "You" : "Local AI"}
                  </div>

                  <div className="message-text">{message.content}</div>

                  {message.sources?.length > 0 && (
                    <div className="sources">
                      <h4>Sources</h4>

                      {message.sources.map((source, sourceIndex) => (
                        <div className="source" key={sourceIndex}>
                          <strong>{source.filename ?? "Document"}</strong>

                          {source.content && <p>{source.content}</p>}
                        </div>
                      ))}
                    </div>
                  )}
                </article>
              ))
            )}

            {loading && (
              <div className="thinking" role="status">
                <span className="thinking-dot" />
                <span className="thinking-dot" />
                <span className="thinking-dot" />
                <span>Thinking...</span>
              </div>
            )}
          </div>

          <form className="composer" onSubmit={sendMessage}>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a question..."
              rows={1}
              disabled={loading}
              aria-label="Your question"
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey &&
                  !event.nativeEvent.isComposing
                ) {
                  event.preventDefault();
                  event.currentTarget.form.requestSubmit();
                }
              }}
            />

            <button
              type="submit"
              className="send-button"
              disabled={!question.trim() || loading}
              aria-label="Send message"
            >
              ↑
            </button>
          </form>

          <p className="chat-footer">
            Your questions are processed by your local AI backend.
          </p>
        </div>
      </section>
    </main>
  );
}

export default App;

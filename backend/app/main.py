from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, conversations, documents

app = FastAPI(
    title="Local AI Intelligence Workbench",
    version="0.1.0",
)

# Allow the React frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Local AI Intelligence Workbench API is running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Register application routes.
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(conversations.router)

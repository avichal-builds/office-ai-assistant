
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.office_assistant import ask_office_assistant

app = FastAPI(
    title="Office AI Assistant API",
    description="Local AI-powered Office Assistant",
    version="1.0.0"
)

# Allow our local frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "Office AI Assistant API is running"
    }


@app.post("/api/chat")
def chat(request: ChatRequest):

    answer = ask_office_assistant(request.question)

    return {
        "success": True,
        "question": request.question,
        "answer": answer
    }

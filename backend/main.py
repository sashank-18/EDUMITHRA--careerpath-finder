from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from routes import auth, curriculum, quiz, chatbot, progress, automation
from config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Learning Platform API",
    description="Intelligent learning platform powered by Groq LLM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(curriculum.router, prefix="/api/curriculum", tags=["Curriculum"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])
app.include_router(chatbot.router, prefix="/api/chat", tags=["Chatbot"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(automation.router, prefix="/api/automation", tags=["Automation"])

@app.get("/")
def root():
    return {"message": "AI Learning Platform API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

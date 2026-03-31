from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Cognify API",
    description="Intelligent quiz generation from any input content",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.routers import upload, quiz
app.include_router(upload.router, prefix="/api/v1", tags=["File Upload"])
app.include_router(quiz.router, prefix="/api/v1", tags=["Quiz Generation"])


@app.get("/")
def root():
    return {"message": "Cognify API is running", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
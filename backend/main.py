from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.database import connect_db, close_db

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

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

from backend.routers import upload, quiz, evaluate, sessions, adaptive
app.include_router(upload.router, prefix="/api/v1", tags=["File Upload"])
app.include_router(quiz.router, prefix="/api/v1", tags=["Quiz Generation"])
app.include_router(evaluate.router, prefix="/api/v1", tags=["Evaluation"])
app.include_router(sessions.router, prefix="/api/v1", tags=["Sessions"])
app.include_router(adaptive.router, prefix="/api/v1", tags=["Adaptive Learning"])


@app.get("/")
def root():
    return {"message": "Cognify API is running", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
"""
Sessions Router
Handles quiz session storage and retrieval.
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional

from backend.database import quiz_sessions, user_performance

router = APIRouter()


class SaveSessionRequest(BaseModel):
    quiz_id: str
    questions: List[Dict]
    answers: List[Dict]
    score: float
    percentage: float
    grade: str
    topic: Optional[str] = "General"


class PerformanceRequest(BaseModel):
    session_id: str
    question_type: str
    difficulty: str
    is_correct: bool


@router.post("/sessions/save")
async def save_session(payload: SaveSessionRequest):
    """Save a completed quiz session to MongoDB."""
    try:
        session = {
            "session_id": str(uuid.uuid4()),
            "quiz_id": payload.quiz_id,
            "topic": payload.topic,
            "questions": payload.questions,
            "answers": payload.answers,
            "score": payload.score,
            "percentage": payload.percentage,
            "grade": payload.grade,
            "created_at": datetime.utcnow().isoformat(),
        }
        await quiz_sessions.insert_one(session)
        session.pop("_id", None)

        return JSONResponse(content={
            "message": "Session saved successfully!",
            "session_id": session["session_id"],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save session: {str(e)}")


@router.get("/sessions/history")
async def get_history():
    """Get all past quiz sessions."""
    try:
        sessions = await quiz_sessions.find(
            {}, {"_id": 0}
        ).sort("created_at", -1).limit(20).to_list(20)

        return JSONResponse(content={
            "total": len(sessions),
            "sessions": sessions,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@router.get("/sessions/stats")
async def get_stats():
    """Get overall performance statistics."""
    try:
        all_sessions = await quiz_sessions.find({}, {"_id": 0}).to_list(1000)

        if not all_sessions:
            return JSONResponse(content={
                "total_quizzes": 0,
                "average_score": 0,
                "best_score": 0,
                "total_questions_attempted": 0,
            })

        total_quizzes = len(all_sessions)
        avg_score = sum(s["percentage"] for s in all_sessions) / total_quizzes
        best_score = max(s["percentage"] for s in all_sessions)
        total_questions = sum(len(s.get("questions", [])) for s in all_sessions)

        # Grade distribution
        grades = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for s in all_sessions:
            grade = s.get("grade", "F")
            if grade in grades:
                grades[grade] += 1

        return JSONResponse(content={
            "total_quizzes": total_quizzes,
            "average_score": round(avg_score, 1),
            "best_score": round(best_score, 1),
            "total_questions_attempted": total_questions,
            "grade_distribution": grades,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")


@router.delete("/sessions/clear")
async def clear_sessions():
    """Clear all sessions (for testing)."""
    try:
        await quiz_sessions.delete_many({})
        return JSONResponse(content={"message": "All sessions cleared!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear sessions: {str(e)}")
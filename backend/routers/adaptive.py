"""
Adaptive Learning Router
Handles performance tracking and difficulty recommendations.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from backend.services.adaptive import AdaptiveEngine

router = APIRouter()


class PerformanceRecord(BaseModel):
    session_id: str
    question_type: str
    difficulty: str
    is_correct: bool
    topic: Optional[str] = "General"


@router.post("/adaptive/record")
async def record_performance(payload: PerformanceRecord):
    """Record a single answer performance."""
    try:
        await AdaptiveEngine.record_performance(
            session_id=payload.session_id,
            question_type=payload.question_type,
            difficulty=payload.difficulty,
            is_correct=payload.is_correct,
            topic=payload.topic,
        )
        return JSONResponse(content={"message": "Performance recorded!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record: {str(e)}")


@router.get("/adaptive/summary")
async def get_summary():
    """Get performance summary and difficulty recommendation."""
    try:
        summary = await AdaptiveEngine.get_performance_summary()
        return JSONResponse(content=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}")


@router.get("/adaptive/weak-areas")
async def get_weak_areas():
    """Get weak areas where user needs improvement."""
    try:
        weak_areas = await AdaptiveEngine.get_weak_areas()
        return JSONResponse(content={"weak_areas": weak_areas})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weak areas: {str(e)}")


@router.get("/adaptive/recommend")
async def get_recommendation():
    """Get next quiz difficulty recommendation."""
    try:
        summary = await AdaptiveEngine.get_performance_summary()
        weak_areas = await AdaptiveEngine.get_weak_areas()

        return JSONResponse(content={
            "recommended_difficulty": summary["recommended_difficulty"],
            "overall_accuracy": summary["overall_accuracy"],
            "weak_areas": weak_areas,
            "message": f"Based on your performance, we recommend {summary['recommended_difficulty']} difficulty questions.",
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation: {str(e)}")
"""
Quiz Router
Handles quiz generation endpoints with custom question counts.
"""

import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from backend.services.preprocessor import TextPreprocessor
from backend.services.quiz_generator import QuizGenerator

router = APIRouter()


class TextInput(BaseModel):
    content: str
    mcq_count: Optional[int] = 5
    tf_count: Optional[int] = 5
    fill_count: Optional[int] = 5


@router.post("/quiz/generate")
async def generate_quiz(payload: TextInput):
    """Generate a complete quiz from input text with custom question counts."""
    try:
        if len(payload.content.split()) < 50:
            raise HTTPException(
                status_code=422,
                detail="Content too short. Please provide at least 50 words.",
            )

        processed = TextPreprocessor.process(payload.content)
        quiz = QuizGenerator.generate_all(
            processed,
            mcq_count=payload.mcq_count,
            tf_count=payload.tf_count,
            fill_count=payload.fill_count,
        )

        return JSONResponse(
            content={
                "quiz_id": str(uuid.uuid4()),
                "status": "generated",
                "total_questions": quiz["total_questions"],
                "breakdown": {
                    "mcq": quiz["mcq_count"],
                    "true_false": quiz["true_false_count"],
                    "fill_blank": quiz["fill_blank_count"],
                },
                "questions": quiz["questions"],
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


@router.get("/quiz/sample")
async def sample_quiz():
    """Returns a sample quiz for testing purposes."""
    sample_text = """
    Machine learning is a subset of artificial intelligence that enables systems to learn
    from data and improve their performance over time without being explicitly programmed.
    Supervised learning involves training a model on labeled data where the correct answers
    are provided. Unsupervised learning finds hidden patterns in data without labeled responses.
    Neural networks are computing systems inspired by biological neural networks in the brain.
    Deep learning uses multiple layers of neural networks to learn complex representations of data.
    """

    processed = TextPreprocessor.process(sample_text)
    quiz = QuizGenerator.generate_all(processed, mcq_count=3, tf_count=3, fill_count=3)

    return JSONResponse(
        content={
            "quiz_id": str(uuid.uuid4()),
            "status": "generated",
            "total_questions": quiz["total_questions"],
            "questions": quiz["questions"],
        }
    )
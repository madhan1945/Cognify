"""
Quiz Router
Handles quiz generation endpoints.
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
    num_questions: Optional[int] = 10
    question_types: Optional[list] = ["mcq", "true_false", "fill_blank", "short_answer"]


@router.post("/quiz/generate")
async def generate_quiz(payload: TextInput):
    """Generate a complete quiz from input text."""
    try:
        if len(payload.content.split()) < 50:
            raise HTTPException(
                status_code=422,
                detail="Content too short. Please provide at least 50 words.",
            )

        processed = TextPreprocessor.process(payload.content)
        mcqs = QuizGenerator.generate_mcq_rule_based(processed["sentences"], processed["keywords"])
        true_false = QuizGenerator.generate_truefalse(processed["sentences"])
        fill_blanks = QuizGenerator.generate_fill_blanks(processed["sentences"], processed["keywords"])
        all_questions = mcqs + true_false + fill_blanks

        return JSONResponse(
            content={
                "quiz_id": str(uuid.uuid4()),
                "status": "generated",
                "total_questions": len(all_questions),
                "breakdown": {
                    "mcq": len(mcqs),
                    "true_false": len(true_false),
                    "fill_blank": len(fill_blanks),
                },
                "questions": all_questions,
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
    mcqs = QuizGenerator.generate_mcq_rule_based(processed["sentences"], processed["keywords"])
    true_false = QuizGenerator.generate_truefalse(processed["sentences"])
    fill_blanks = QuizGenerator.generate_fill_blanks(processed["sentences"], processed["keywords"])
    all_questions = mcqs + true_false + fill_blanks

    return JSONResponse(
        content={
            "quiz_id": str(uuid.uuid4()),
            "status": "generated",
            "total_questions": len(all_questions),
            "questions": all_questions,
        }
    )
"""
Evaluation Router
Handles answer evaluation endpoints.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict

from backend.services.evaluator import AnswerEvaluator

router = APIRouter()


class AnswerSubmission(BaseModel):
    question_type: str
    user_answer: str
    correct_answer: str


class QuizSubmission(BaseModel):
    answers: List[Dict]


@router.post("/evaluate/answer")
async def evaluate_answer(payload: AnswerSubmission):
    """Evaluate a single answer."""
    try:
        result = AnswerEvaluator.evaluate(
            payload.user_answer,
            payload.correct_answer,
            payload.question_type,
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/evaluate/quiz")
async def evaluate_quiz(payload: QuizSubmission):
    """
    Evaluate all answers in a quiz.
    Returns score, breakdown, and per-question feedback.
    """
    try:
        results = []
        total_score = 0.0

        for answer in payload.answers:
            result = AnswerEvaluator.evaluate(
                answer.get("user_answer", ""),
                answer.get("correct_answer", ""),
                answer.get("question_type", "mcq"),
            )
            results.append({
                "question": answer.get("question", ""),
                "user_answer": answer.get("user_answer", ""),
                "correct_answer": answer.get("correct_answer", ""),
                "is_correct": result["is_correct"],
                "score": result["score"],
                "feedback": result["feedback"],
            })
            total_score += result["score"]

        total = len(results)
        correct = sum(1 for r in results if r["is_correct"])
        percentage = round((correct / total) * 100, 1) if total > 0 else 0

        return JSONResponse(content={
            "total_questions": total,
            "correct_answers": correct,
            "percentage": percentage,
            "grade": AnswerEvaluator.get_grade(percentage),
            "results": results,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
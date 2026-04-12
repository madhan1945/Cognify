"""
Cognify Backend Test Suite
Tests all major endpoints and services.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

SAMPLE_TEXT = """
Photosynthesis is the process by which plants use sunlight water and carbon dioxide
to produce oxygen and energy in the form of sugar. This process takes place in the
chloroplasts of plant cells. Chlorophyll is the green pigment in plants that absorbs
sunlight. The light reactions of photosynthesis occur in the thylakoid membranes and
produce ATP and NADPH. The Calvin cycle occurs in the stroma of the chloroplast and
uses ATP and NADPH to fix carbon dioxide into glucose. Cellular respiration is the
process by which cells break down glucose to release energy in the form of ATP.
Mitochondria are the organelles where cellular respiration takes place.
"""


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ── Health & Root ─────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_root(client):
    res = await client.get("/")
    assert res.status_code == 200
    assert res.json()["message"] == "Cognify API is running"


@pytest.mark.anyio
async def test_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


# ── Quiz Generation ───────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_generate_quiz(client):
    res = await client.post("/api/v1/quiz/generate", json={
        "content": SAMPLE_TEXT,
        "mcq_count": 3,
        "tf_count": 3,
        "fill_count": 3,
    })
    assert res.status_code == 200
    data = res.json()
    assert "questions" in data
    assert data["total_questions"] > 0


@pytest.mark.anyio
async def test_generate_quiz_short_text(client):
    res = await client.post("/api/v1/quiz/generate", json={"content": "Too short text."})
    assert res.status_code == 422


@pytest.mark.anyio
async def test_sample_quiz(client):
    res = await client.get("/api/v1/quiz/sample")
    assert res.status_code == 200
    data = res.json()
    assert "questions" in data


# ── Answer Evaluation ─────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_evaluate_correct_mcq(client):
    res = await client.post("/api/v1/evaluate/answer", json={
        "question_type": "mcq",
        "user_answer": "photosynthesis",
        "correct_answer": "photosynthesis",
    })
    assert res.status_code == 200
    assert res.json()["is_correct"] == True


@pytest.mark.anyio
async def test_evaluate_wrong_mcq(client):
    res = await client.post("/api/v1/evaluate/answer", json={
        "question_type": "mcq",
        "user_answer": "respiration",
        "correct_answer": "photosynthesis",
    })
    assert res.status_code == 200
    assert res.json()["is_correct"] == False


@pytest.mark.anyio
async def test_evaluate_truefalse(client):
    res = await client.post("/api/v1/evaluate/answer", json={
        "question_type": "true_false",
        "user_answer": "True",
        "correct_answer": "True",
    })
    assert res.status_code == 200
    assert res.json()["is_correct"] == True


@pytest.mark.anyio
async def test_evaluate_fill_blank_fuzzy(client):
    res = await client.post("/api/v1/evaluate/answer", json={
        "question_type": "fill_blank",
        "user_answer": "chlorophyl",
        "correct_answer": "chlorophyll",
    })
    assert res.status_code == 200
    assert res.json()["score"] > 0.7


# ── Sessions ──────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_save_session(client):
    res = await client.post("/api/v1/sessions/save", json={
        "quiz_id": "test-quiz-123",
        "questions": [],
        "answers": [],
        "score": 8.0,
        "percentage": 80.0,
        "grade": "B",
        "topic": "Test",
    })
    assert res.status_code == 200
    assert "session_id" in res.json()


@pytest.mark.anyio
async def test_get_history(client):
    res = await client.get("/api/v1/sessions/history")
    assert res.status_code == 200
    assert "sessions" in res.json()


@pytest.mark.anyio
async def test_get_stats(client):
    res = await client.get("/api/v1/sessions/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_quizzes" in data
    assert "average_score" in data


# ── Adaptive Learning ─────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_record_performance(client):
    res = await client.post("/api/v1/adaptive/record", json={
        "session_id": "test-session-123",
        "question_type": "mcq",
        "difficulty": "medium",
        "is_correct": True,
        "topic": "Test",
    })
    assert res.status_code == 200


@pytest.mark.anyio
async def test_get_summary(client):
    res = await client.get("/api/v1/adaptive/summary")
    assert res.status_code == 200
    data = res.json()
    assert "recommended_difficulty" in data


@pytest.mark.anyio
async def test_get_recommendation(client):
    res = await client.get("/api/v1/adaptive/recommend")
    assert res.status_code == 200
    data = res.json()
    assert "recommended_difficulty" in data
    assert "message" in data


# ── Preprocessor Service ──────────────────────────────────────────────────────

def test_preprocessor():
    from backend.services.preprocessor import TextPreprocessor
    result = TextPreprocessor.process(SAMPLE_TEXT)
    assert "sentences" in result
    assert "keywords" in result
    assert len(result["sentences"]) > 0
    assert len(result["keywords"]) > 0


def test_clean_text():
    from backend.services.preprocessor import TextPreprocessor
    dirty = "Hello   World\n\n\nPage 1 of 5\nhttps://example.com test"
    clean = TextPreprocessor.clean_text(dirty)
    assert "Page" not in clean
    assert "https" not in clean


# ── Evaluator Service ─────────────────────────────────────────────────────────

def test_exact_match():
    from backend.services.evaluator import AnswerEvaluator
    assert AnswerEvaluator.exact_match("Photosynthesis", "photosynthesis") == True
    assert AnswerEvaluator.exact_match("wrong", "photosynthesis") == False


def test_fuzzy_match():
    from backend.services.evaluator import AnswerEvaluator
    score = AnswerEvaluator.fuzzy_match("chlorophyl", "chlorophyll")
    assert score > 0.8


def test_get_grade():
    from backend.services.evaluator import AnswerEvaluator
    assert AnswerEvaluator.get_grade(95) == "A"
    assert AnswerEvaluator.get_grade(85) == "B"
    assert AnswerEvaluator.get_grade(45) == "F"
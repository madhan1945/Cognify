"""
Adaptive Learning Engine
Tracks user performance and adjusts quiz difficulty dynamically.
"""

from typing import Dict, List
from backend.database import user_performance
from datetime import datetime


class AdaptiveEngine:

    @staticmethod
    async def record_performance(
        session_id: str,
        question_type: str,
        difficulty: str,
        is_correct: bool,
        topic: str = "General"
    ):
        """Record a single answer's performance to MongoDB."""
        record = {
            "session_id": session_id,
            "question_type": question_type,
            "difficulty": difficulty,
            "is_correct": is_correct,
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await user_performance.insert_one(record)

    @staticmethod
    async def get_performance_summary() -> Dict:
        """Get overall performance breakdown by difficulty and type."""
        records = await user_performance.find({}, {"_id": 0}).to_list(1000)

        if not records:
            return {
                "total_answered": 0,
                "overall_accuracy": 0,
                "by_difficulty": {},
                "by_type": {},
                "recommended_difficulty": "medium",
            }

        total = len(records)
        correct = sum(1 for r in records if r["is_correct"])
        overall_accuracy = round((correct / total) * 100, 1)

        # By difficulty
        by_difficulty = {}
        for diff in ["easy", "medium", "hard"]:
            diff_records = [r for r in records if r["difficulty"] == diff]
            if diff_records:
                diff_correct = sum(1 for r in diff_records if r["is_correct"])
                by_difficulty[diff] = {
                    "total": len(diff_records),
                    "correct": diff_correct,
                    "accuracy": round((diff_correct / len(diff_records)) * 100, 1),
                }

        # By type
        by_type = {}
        for qtype in ["mcq", "true_false", "fill_blank"]:
            type_records = [r for r in records if r["question_type"] == qtype]
            if type_records:
                type_correct = sum(1 for r in type_records if r["is_correct"])
                by_type[qtype] = {
                    "total": len(type_records),
                    "correct": type_correct,
                    "accuracy": round((type_correct / len(type_records)) * 100, 1),
                }

        # Recommend next difficulty
        recommended = AdaptiveEngine.recommend_difficulty(by_difficulty, overall_accuracy)

        return {
            "total_answered": total,
            "overall_accuracy": overall_accuracy,
            "by_difficulty": by_difficulty,
            "by_type": by_type,
            "recommended_difficulty": recommended,
        }

    @staticmethod
    def recommend_difficulty(by_difficulty: Dict, overall_accuracy: float) -> str:
        """
        Recommend next difficulty based on performance:
        - Above 80% accuracy → increase difficulty
        - Below 50% accuracy → decrease difficulty
        - Between 50-80% → stay same
        """
        if overall_accuracy >= 80:
            # User is doing well — push harder
            if "hard" not in by_difficulty:
                return "hard"
            hard_acc = by_difficulty.get("hard", {}).get("accuracy", 0)
            if hard_acc >= 70:
                return "hard"
            return "medium"
        elif overall_accuracy < 50:
            # User is struggling — ease up
            if "easy" not in by_difficulty:
                return "easy"
            easy_acc = by_difficulty.get("easy", {}).get("accuracy", 0)
            if easy_acc < 60:
                return "easy"
            return "medium"
        else:
            return "medium"

    @staticmethod
    async def get_weak_areas() -> List[Dict]:
        """Identify topics and question types where user struggles most."""
        records = await user_performance.find({}, {"_id": 0}).to_list(1000)

        if not records:
            return []

        weak_areas = []

        # Check each difficulty
        for diff in ["easy", "medium", "hard"]:
            diff_records = [r for r in records if r["difficulty"] == diff]
            if len(diff_records) >= 3:
                accuracy = sum(1 for r in diff_records if r["is_correct"]) / len(diff_records) * 100
                if accuracy < 60:
                    weak_areas.append({
                        "area": f"{diff.capitalize()} questions",
                        "accuracy": round(accuracy, 1),
                        "suggestion": f"Practice more {diff} level questions",
                    })

        # Check each type
        for qtype in ["mcq", "true_false", "fill_blank"]:
            type_records = [r for r in records if r["question_type"] == qtype]
            if len(type_records) >= 3:
                accuracy = sum(1 for r in type_records if r["is_correct"]) / len(type_records) * 100
                if accuracy < 60:
                    weak_areas.append({
                        "area": f"{qtype.replace('_', ' ').title()} questions",
                        "accuracy": round(accuracy, 1),
                        "suggestion": f"Focus on improving {qtype.replace('_', ' ')} accuracy",
                    })

        return weak_areas
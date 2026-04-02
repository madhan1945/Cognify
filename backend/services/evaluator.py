"""
Answer Evaluation Service
Evaluates user answers using exact match + semantic similarity.
"""

import re
from typing import Dict
from difflib import SequenceMatcher
import nltk
from nltk.corpus import wordnet

nltk.download('wordnet', quiet=True)


class AnswerEvaluator:

    @staticmethod
    def normalize(text: str) -> str:
        """Normalize text for comparison."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    @staticmethod
    def get_grade(percentage: float) -> str:
        """Return letter grade based on percentage."""
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
            
    @staticmethod
    def exact_match(user_answer: str, correct_answer: str) -> bool:
        """Check if answers match exactly after normalization."""
        return AnswerEvaluator.normalize(user_answer) == AnswerEvaluator.normalize(correct_answer)

    @staticmethod
    def fuzzy_match(user_answer: str, correct_answer: str) -> float:
        """Fuzzy string matching score (0-1)."""
        a = AnswerEvaluator.normalize(user_answer)
        b = AnswerEvaluator.normalize(correct_answer)
        return SequenceMatcher(None, a, b).ratio()

    @staticmethod
    def wordnet_similarity(word1: str, word2: str) -> float:
        """Semantic similarity using WordNet."""
        try:
            syns1 = wordnet.synsets(word1.replace(" ", "_"))
            syns2 = wordnet.synsets(word2.replace(" ", "_"))

            if not syns1 or not syns2:
                return 0.0

            max_sim = 0.0
            for s1 in syns1[:3]:
                for s2 in syns2[:3]:
                    sim = s1.wup_similarity(s2)
                    if sim and sim > max_sim:
                        max_sim = sim
            return max_sim
        except Exception:
            return 0.0

    @staticmethod
    def evaluate(user_answer: str, correct_answer: str, question_type: str) -> Dict:
        """
        Main evaluation method.
        Returns score, feedback, and whether the answer is correct.
        """
        if not user_answer or not user_answer.strip():
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "No answer provided.",
                "method": "none",
            }

        # MCQ and True/False — exact match only
        if question_type in ("mcq", "true_false"):
            correct = AnswerEvaluator.exact_match(user_answer, correct_answer)
            return {
                "is_correct": correct,
                "score": 1.0 if correct else 0.0,
                "feedback": "Correct!" if correct else f"Incorrect. The correct answer is: {correct_answer}",
                "method": "exact_match",
            }

        # Fill in blank — fuzzy + wordnet
        if question_type == "fill_blank":
            fuzzy = AnswerEvaluator.fuzzy_match(user_answer, correct_answer)
            semantic = AnswerEvaluator.wordnet_similarity(user_answer, correct_answer)
            score = max(fuzzy, semantic)
            is_correct = score >= 0.7

            if is_correct:
                feedback = "Correct!" if score >= 0.9 else "Mostly correct!"
            else:
                feedback = f"Incorrect. Expected: {correct_answer}"

            return {
                "is_correct": is_correct,
                "score": round(score, 2),
                "feedback": feedback,
                "method": "fuzzy+wordnet",
            }

        # Short answer — fuzzy match
        if question_type == "short_answer":
            fuzzy = AnswerEvaluator.fuzzy_match(user_answer, correct_answer)
            is_correct = fuzzy >= 0.6
            return {
                "is_correct": is_correct,
                "score": round(fuzzy, 2),
                "feedback": "Good answer!" if is_correct else f"Expected something like: {correct_answer}",
                "method": "fuzzy_match",
            }

        return {
            "is_correct": False,
            "score": 0.0,
            "feedback": "Unable to evaluate.",
            "method": "none",
        }
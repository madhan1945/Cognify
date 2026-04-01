"""
Quiz Generator Service
Handles rule-based and transformer-based question generation.
"""

import re
import random
from typing import List, Dict
import spacy
import nltk
from nltk.corpus import wordnet

nlp = spacy.load("en_core_web_sm")

_tokenizer = None
_model = None


def get_t5_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        from transformers import T5ForConditionalGeneration, T5Tokenizer
        print("Loading T5 model...")
        _tokenizer = T5Tokenizer.from_pretrained("t5-small")
        _model = T5ForConditionalGeneration.from_pretrained("t5-small")
        print("T5 model loaded!")
    return _tokenizer, _model


class QuizGenerator:

    @staticmethod
    def get_wordnet_distractors(word: str, num: int = 3) -> List[str]:
        """Get semantically related wrong answers using WordNet."""
        distractors = set()
        synsets = wordnet.synsets(word.replace(" ", "_"))

        for syn in synsets:
            # Hypernyms (broader terms)
            for hypernym in syn.hypernyms():
                for lemma in hypernym.lemmas():
                    candidate = lemma.name().replace("_", " ").lower()
                    if candidate != word.lower() and len(candidate) > 2:
                        distractors.add(candidate)

            # Hyponyms (narrower terms)
            for hyponym in syn.hyponyms():
                for lemma in hyponym.lemmas():
                    candidate = lemma.name().replace("_", " ").lower()
                    if candidate != word.lower() and len(candidate) > 2:
                        distractors.add(candidate)

            # Also siblings (same hypernym)
            for hypernym in syn.hypernyms():
                for hyponym in hypernym.hyponyms():
                    for lemma in hyponym.lemmas():
                        candidate = lemma.name().replace("_", " ").lower()
                        if candidate != word.lower() and len(candidate) > 2:
                            distractors.add(candidate)

        distractors = list(distractors)
        random.shuffle(distractors)
        return distractors[:num]

    @staticmethod
    def get_distractors(keyword: str, all_keywords: List[str], num: int = 3) -> List[str]:
        """
        Smart distractor selection:
        1. Try WordNet first
        2. Fall back to keywords from the same text
        """
        # Try WordNet
        wordnet_distractors = QuizGenerator.get_wordnet_distractors(keyword, num)
        if len(wordnet_distractors) >= num:
            return wordnet_distractors[:num]

        # Fall back to keywords filtered by similar length
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "in", "on",
            "at", "to", "of", "and", "or", "that", "this", "it", "its"
        }
        fallback = [
            k for k in all_keywords
            if k.lower() != keyword.lower()
            and k.lower() not in stopwords
            and len(k) > 4
            and abs(len(k) - len(keyword)) <= 8
            and len(k.split()) <= 2  # no long phrases
            and not any(sw in k.lower() for sw in ["the", "a ", "an ", "these", "this", "that"])
        ]
        random.shuffle(fallback)

        # Combine WordNet + fallback
        combined = wordnet_distractors + fallback
        seen = set()
        unique = []
        for d in combined:
            if d.lower() not in seen:
                seen.add(d.lower())
                unique.append(d)

        return unique[:num]

    @staticmethod
    def generate_mcq_rule_based(sentences: List[str], keywords: List[str]) -> List[Dict]:
        """Generate MCQs with smart WordNet-based distractors."""
        questions = []
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "in", "on",
            "at", "to", "of", "and", "or", "that", "this", "it", "its"
        }
        clean_keywords = [
            k for k in keywords
            if k.lower() not in stopwords and len(k) > 3
        ]

        for sentence in sentences:
            for keyword in clean_keywords:
                if keyword.lower() in sentence.lower() and len(sentence.split()) >= 8:
                    question_text = re.sub(
                        re.escape(keyword), "______", sentence,
                        flags=re.IGNORECASE, count=1
                    )

                    distractors = QuizGenerator.get_distractors(keyword, clean_keywords)

                    if len(distractors) < 3:
                        continue

                    options = distractors[:3] + [keyword]
                    random.shuffle(options)

                    questions.append({
                        "type": "mcq",
                        "question": f"Fill in the blank: {question_text}",
                        "options": options,
                        "answer": keyword,
                        "difficulty": QuizGenerator.estimate_difficulty(sentence),
                        "method": "rule-based",
                    })

                    if len(questions) >= 10:
                        return questions
                    break

        return questions

    @staticmethod
    def generate_truefalse(sentences: List[str]) -> List[Dict]:
        """Generate True/False questions."""
        questions = []

        for sentence in sentences:
            if len(sentence.split()) < 8:
                continue

            questions.append({
                "type": "true_false",
                "question": sentence,
                "answer": "True",
                "difficulty": QuizGenerator.estimate_difficulty(sentence),
                "method": "rule-based",
            })

            false_sentence = QuizGenerator.negate_sentence(sentence)
            if false_sentence:
                questions.append({
                    "type": "true_false",
                    "question": false_sentence,
                    "answer": "False",
                    "difficulty": QuizGenerator.estimate_difficulty(sentence),
                    "method": "rule-based",
                })

            if len(questions) >= 10:
                break

        return questions

    @staticmethod
    def generate_fill_blanks(sentences: List[str], keywords: List[str]) -> List[Dict]:
        """Generate fill-in-the-blank questions."""
        questions = []
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "in", "on",
            "at", "to", "of", "and", "or", "that", "this", "it", "its"
        }
        clean_keywords = [
            k for k in keywords
            if k.lower() not in stopwords and len(k) > 3
        ]

        for sentence in sentences:
            for keyword in clean_keywords:
                if keyword.lower() in sentence.lower() and len(sentence.split()) >= 8:
                    blanked = re.sub(
                        re.escape(keyword), "_____", sentence,
                        flags=re.IGNORECASE, count=1
                    )
                    questions.append({
                        "type": "fill_blank",
                        "question": blanked,
                        "answer": keyword,
                        "difficulty": QuizGenerator.estimate_difficulty(sentence),
                        "method": "rule-based",
                    })
                    break

            if len(questions) >= 10:
                break

        return questions

    @staticmethod
    def generate_questions_t5(paragraphs: List[str], num_questions: int = 5) -> List[Dict]:
        """Generate questions using T5 transformer model."""
        tokenizer, model = get_t5_model()
        questions = []

        for paragraph in paragraphs[:num_questions]:
            if len(paragraph.split()) < 20:
                continue

            input_text = f"generate question: {paragraph[:512]}"
            input_ids = tokenizer.encode(
                input_text, return_tensors="pt", max_length=512, truncation=True
            )

            outputs = model.generate(
                input_ids,
                max_length=64,
                num_beams=4,
                early_stopping=True,
            )

            question = tokenizer.decode(outputs[0], skip_special_tokens=True)

            questions.append({
                "type": "short_answer",
                "question": question,
                "context": paragraph[:300],
                "difficulty": QuizGenerator.estimate_difficulty(paragraph),
                "method": "t5-transformer",
            })

        return questions

    @staticmethod
    def negate_sentence(sentence: str) -> str:
        """Simple negation by inserting 'not' after first verb."""
        doc = nlp(sentence)
        for token in doc:
            if token.pos_ in ("AUX", "VERB"):
                return sentence.replace(token.text, token.text + " not", 1)
        return None

    @staticmethod
    def estimate_difficulty(text: str) -> str:
        """Estimate difficulty based on sentence length and complexity."""
        words = text.split()
        avg_word_len = sum(len(w) for w in words) / len(words) if words else 0

        if len(words) <= 10 and avg_word_len <= 5:
            return "easy"
        elif len(words) <= 20 and avg_word_len <= 7:
            return "medium"
        else:
            return "hard"

    @staticmethod
    def generate_all(processed_data: Dict) -> Dict:
        """Master method — generates all question types."""
        sentences = processed_data.get("sentences", [])
        paragraphs = processed_data.get("paragraphs", [])
        keywords = processed_data.get("keywords", [])

        mcqs = QuizGenerator.generate_mcq_rule_based(sentences, keywords)
        true_false = QuizGenerator.generate_truefalse(sentences)
        fill_blanks = QuizGenerator.generate_fill_blanks(sentences, keywords)
        t5_questions = QuizGenerator.generate_questions_t5(paragraphs)

        all_questions = mcqs + true_false + fill_blanks + t5_questions
        random.shuffle(all_questions)

        return {
            "total_questions": len(all_questions),
            "mcq_count": len(mcqs),
            "true_false_count": len(true_false),
            "fill_blank_count": len(fill_blanks),
            "t5_count": len(t5_questions),
            "questions": all_questions,
        }
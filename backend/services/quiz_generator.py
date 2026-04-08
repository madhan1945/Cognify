"""
Quiz Generator Service - Improved Version
Better True/False, smarter MCQ distractors, custom question counts.
"""

import re
import random
from typing import List, Dict
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import wordnet

nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt_tab', quiet=True)

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
        distractors = set()
        synsets = wordnet.synsets(word.replace(" ", "_"))
        for syn in synsets:
            for hypernym in syn.hypernyms():
                for lemma in hypernym.lemmas():
                    candidate = lemma.name().replace("_", " ").lower()
                    if candidate != word.lower() and len(candidate) > 2:
                        distractors.add(candidate)
            for hyponym in syn.hyponyms():
                for lemma in hyponym.lemmas():
                    candidate = lemma.name().replace("_", " ").lower()
                    if candidate != word.lower() and len(candidate) > 2:
                        distractors.add(candidate)
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
        wordnet_distractors = QuizGenerator.get_wordnet_distractors(keyword, num)
        if len(wordnet_distractors) >= num:
            return wordnet_distractors[:num]
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
            and len(k.split()) <= 2
            and not any(sw in k.lower() for sw in ["the", "a ", "an ", "these", "this", "that"])
        ]
        random.shuffle(fallback)
        combined = wordnet_distractors + fallback
        seen = set()
        unique = []
        for d in combined:
            if d.lower() not in seen:
                seen.add(d.lower())
                unique.append(d)
        return unique[:num]

    @staticmethod
    def generate_mcq_rule_based(sentences: List[str], keywords: List[str], count: int = 5) -> List[Dict]:
        questions = []
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "in", "on",
            "at", "to", "of", "and", "or", "that", "this", "it", "its"
        }
        clean_keywords = [k for k in keywords if k.lower() not in stopwords and len(k) > 3]
        for sentence in sentences:
            for keyword in clean_keywords:
                if keyword.lower() in sentence.lower() and len(sentence.split()) >= 8:
                    question_text = re.sub(re.escape(keyword), "______", sentence, flags=re.IGNORECASE, count=1)
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
                    if len(questions) >= count:
                        return questions
                    break
        return questions

    @staticmethod
    def make_false_statement(sentence: str) -> str:
        try:
            words = word_tokenize(sentence)
            tagged = pos_tag(words)
            candidates = [
                (word, tag) for word, tag in tagged
                if (tag.startswith('NN') or tag.startswith('JJ'))
                and len(word) > 3
                and word.isalpha()
            ]
            random.shuffle(candidates)
            for word, tag in candidates:
                antonyms = []
                for syn in wordnet.synsets(word):
                    for lemma in syn.lemmas():
                        for ant in lemma.antonyms():
                            name = ant.name().replace("_", " ")
                            if name.isalpha() and len(name) > 2:
                                antonyms.append(name)
                if antonyms:
                    replacement = random.choice(antonyms)
                    return sentence.replace(word, replacement, 1)
                for syn in wordnet.synsets(word)[:2]:
                    for hypernym in syn.hypernyms():
                        siblings = []
                        for hypo in hypernym.hyponyms():
                            for lemma in hypo.lemmas():
                                name = lemma.name().replace("_", " ")
                                if name.lower() != word.lower() and name.isalpha() and len(name) > 3:
                                    siblings.append(name)
                        if siblings:
                            replacement = random.choice(siblings)
                            return sentence.replace(word, replacement, 1)
        except Exception:
            pass
        return None

    @staticmethod
    def generate_truefalse(sentences: List[str], count: int = 5) -> List[Dict]:
        true_questions = []
        false_questions = []
        for sentence in sentences:
            if len(sentence.split()) < 8:
                continue
            true_questions.append({
                "type": "true_false",
                "question": sentence,
                "answer": "True",
                "difficulty": QuizGenerator.estimate_difficulty(sentence),
                "method": "rule-based",
            })
            false_sentence = QuizGenerator.make_false_statement(sentence)
            if false_sentence and false_sentence != sentence:
                false_questions.append({
                    "type": "true_false",
                    "question": false_sentence,
                    "answer": "False",
                    "difficulty": QuizGenerator.estimate_difficulty(sentence),
                    "method": "rule-based",
                })
        half = count // 2
        selected_true = true_questions[:half]
        selected_false = false_questions[:count - half]
        combined = selected_true + selected_false
        random.shuffle(combined)
        return combined[:count]

    @staticmethod
    def generate_fill_blanks(sentences: List[str], keywords: List[str], count: int = 5) -> List[Dict]:
        questions = []
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "in", "on",
            "at", "to", "of", "and", "or", "that", "this", "it", "its"
        }
        clean_keywords = [k for k in keywords if k.lower() not in stopwords and len(k) > 3]
        for sentence in sentences:
            for keyword in clean_keywords:
                if keyword.lower() in sentence.lower() and len(sentence.split()) >= 8:
                    blanked = re.sub(re.escape(keyword), "_____", sentence, flags=re.IGNORECASE, count=1)
                    questions.append({
                        "type": "fill_blank",
                        "question": blanked,
                        "answer": keyword,
                        "difficulty": QuizGenerator.estimate_difficulty(sentence),
                        "method": "rule-based",
                    })
                    break
            if len(questions) >= count:
                break
        return questions

    @staticmethod
    def generate_questions_t5(paragraphs: List[str], num_questions: int = 5) -> List[Dict]:
        tokenizer, model = get_t5_model()
        questions = []
        for paragraph in paragraphs[:num_questions]:
            if len(paragraph.split()) < 20:
                continue
            input_text = f"generate question: {paragraph[:512]}"
            input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
            outputs = model.generate(input_ids, max_length=64, num_beams=4, early_stopping=True)
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
        try:
            words = word_tokenize(sentence)
            tagged = pos_tag(words)
            for i, (word, tag) in enumerate(tagged):
                if tag.startswith('VB') or tag == 'MD':
                    return sentence.replace(word, word + " not", 1)
        except Exception:
            pass
        return None

    @staticmethod
    def estimate_difficulty(text: str) -> str:
        words = text.split()
        avg_word_len = sum(len(w) for w in words) / len(words) if words else 0
        if len(words) <= 10 and avg_word_len <= 5:
            return "easy"
        elif len(words) <= 20 and avg_word_len <= 7:
            return "medium"
        else:
            return "hard"

    @staticmethod
    def generate_all(processed_data: Dict, mcq_count: int = 5,
                     tf_count: int = 5, fill_count: int = 5) -> Dict:
        sentences = processed_data.get("sentences", [])
        keywords = processed_data.get("keywords", [])

        random.shuffle(sentences)
        third = max(1, len(sentences) // 3)
        mcq_sentences = sentences[:third]
        tf_sentences = sentences[third:third * 2]
        fill_sentences = sentences[third * 2:]

        mcqs = QuizGenerator.generate_mcq_rule_based(mcq_sentences, keywords, mcq_count)
        true_false = QuizGenerator.generate_truefalse(tf_sentences, tf_count)
        fill_blanks = QuizGenerator.generate_fill_blanks(fill_sentences, keywords, fill_count)

        all_questions = mcqs + true_false + fill_blanks
        random.shuffle(all_questions)

        return {
            "total_questions": len(all_questions),
            "mcq_count": len(mcqs),
            "true_false_count": len(true_false),
            "fill_blank_count": len(fill_blanks),
            "t5_count": 0,
            "questions": all_questions,
        }
"""
Text Preprocessing Pipeline
"""

import re
import spacy
from nltk.tokenize import sent_tokenize
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

nlp = spacy.load("en_core_web_sm")


class TextPreprocessor:

    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r"Page\s+\d+\s*(of\s*\d+)?", "", text, flags=re.IGNORECASE)
        text = re.sub(r"[-–]\s*\d+\s*[-–]", "", text)
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"[^\x20-\x7E\n]", " ", text)
        return text.strip()

    @staticmethod
    def segment_sentences(text: str) -> List[str]:
        sentences = sent_tokenize(text)
        return [s.strip() for s in sentences if len(s.split()) >= 5]

    @staticmethod
    def segment_paragraphs(text: str) -> List[str]:
        paragraphs = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paragraphs if len(p.split()) >= 20]

    @staticmethod
    def extract_keywords(text: str, top_n: int = 15) -> List[str]:
        """Extract keywords using spaCy — fast, no external model needed."""
        try:
            doc = nlp(text[:50000])
            # Extract noun chunks and named entities as keywords
            keywords = []
            seen = set()

            # Named entities first
            for ent in doc.ents:
                kw = ent.text.lower().strip()
                if kw not in seen and len(kw.split()) <= 3 and len(kw) > 2:
                    keywords.append(kw)
                    seen.add(kw)

            # Noun chunks
            for chunk in doc.noun_chunks:
                kw = chunk.text.lower().strip()
                if kw not in seen and len(kw.split()) <= 3 and len(kw) > 2:
                    keywords.append(kw)
                    seen.add(kw)

            return keywords[:top_n]
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []

    @staticmethod
    def detect_topics(text: str) -> List[str]:
        doc = nlp(text[:50000])
        entities = [ent.text for ent in doc.ents if len(ent.text.split()) <= 4]
        noun_chunks = [
            chunk.text.lower()
            for chunk in doc.noun_chunks
            if len(chunk.text.split()) >= 2
        ]
        all_topics = list(set(entities + noun_chunks))
        from collections import Counter
        topic_counts = Counter(
            word.lower()
            for word in all_topics
            for topic in all_topics
            if word.lower() in topic.lower()
        )
        return [topic for topic, _ in topic_counts.most_common(10)]

    @staticmethod
    def process(raw_text: str) -> Dict:
        cleaned = TextPreprocessor.clean_text(raw_text)
        sentences = TextPreprocessor.segment_sentences(cleaned)
        paragraphs = TextPreprocessor.segment_paragraphs(cleaned)
        keywords = TextPreprocessor.extract_keywords(cleaned)
        topics = TextPreprocessor.detect_topics(cleaned)

        return {
            "cleaned_text": cleaned,
            "sentences": sentences,
            "paragraphs": paragraphs,
            "keywords": keywords,
            "topics": topics,
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs),
        }
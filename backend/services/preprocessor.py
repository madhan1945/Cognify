"""
Text Preprocessing Pipeline
Handles cleaning, segmentation, keyword extraction, and topic detection.
"""

import re
import spacy
from keybert import KeyBERT
from nltk.tokenize import sent_tokenize
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Load models once at module level
nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()


class TextPreprocessor:

    @staticmethod
    def clean_text(text: str) -> str:
        """Remove noise: headers, footers, excessive whitespace, special chars."""
        text = re.sub(r"Page\s+\d+\s*(of\s*\d+)?", "", text, flags=re.IGNORECASE)
        text = re.sub(r"[-–]\s*\d+\s*[-–]", "", text)
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"[^\x20-\x7E\n]", " ", text)
        return text.strip()

    @staticmethod
    def segment_sentences(text: str) -> List[str]:
        """Split text into clean, meaningful sentences."""
        sentences = sent_tokenize(text)
        return [s.strip() for s in sentences if len(s.split()) >= 5]

    @staticmethod
    def segment_paragraphs(text: str) -> List[str]:
        """Split text into paragraphs."""
        paragraphs = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paragraphs if len(p.split()) >= 20]

    @staticmethod
    def extract_keywords(text: str, top_n: int = 15) -> List[str]:
        """Extract key terms using KeyBERT."""
        try:
            keywords = kw_model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                top_n=top_n,
                use_maxsum=True,
                nr_candidates=30,
            )
            return [kw[0] for kw in keywords]
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []

    @staticmethod
    def detect_topics(text: str) -> List[str]:
        """Detect high-level topics using spaCy."""
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
        """Full preprocessing pipeline."""
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
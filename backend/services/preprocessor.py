"""
Text Preprocessing Pipeline
Uses NLTK instead of spaCy to avoid Windows DLL issues.
"""

import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('maxent_ne_chunker_tab', quiet=True)
nltk.download('words', quiet=True)
nltk.download('punkt_tab', quiet=True)

STOPWORDS = set(stopwords.words('english'))


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
        """Extract keywords using NLTK POS tagging."""
        try:
            words = word_tokenize(text[:10000])
            tagged = pos_tag(words)

            keywords = []
            seen = set()

            # Extract nouns and noun phrases
            for i, (word, tag) in enumerate(tagged):
                if tag.startswith('NN') and word.lower() not in STOPWORDS and len(word) > 3:
                    kw = word.lower()
                    if kw not in seen:
                        keywords.append(kw)
                        seen.add(kw)

                # Bigrams (two consecutive nouns)
                if i < len(tagged) - 1:
                    word2, tag2 = tagged[i + 1]
                    if tag.startswith('NN') and tag2.startswith('NN'):
                        bigram = f"{word.lower()} {word2.lower()}"
                        if bigram not in seen:
                            keywords.append(bigram)
                            seen.add(bigram)

            return keywords[:top_n]
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []

    @staticmethod
    def detect_topics(text: str) -> List[str]:
        """Detect topics using NLTK named entity chunking."""
        try:
            sentences = sent_tokenize(text[:10000])
            topics = []
            seen = set()

            for sentence in sentences[:20]:
                words = word_tokenize(sentence)
                tagged = pos_tag(words)
                chunks = ne_chunk(tagged)

                for chunk in chunks:
                    if hasattr(chunk, 'label'):
                        topic = ' '.join(c[0] for c in chunk).lower()
                        if topic not in seen and len(topic) > 2:
                            topics.append(topic)
                            seen.add(topic)

            return topics[:10]
        except Exception as e:
            logger.error(f"Topic detection failed: {e}")
            return []

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
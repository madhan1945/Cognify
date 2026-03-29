"""
File Parser Service
Handles PDF, DOCX, and plain text extraction.
"""

import pdfplumber
from docx import Document
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class FileParser:

    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        text_parts = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text.strip())
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise

    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX files."""
        doc = Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    @staticmethod
    def extract_from_txt(file_path: str) -> str:
        """Read plain text files."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    @staticmethod
    def parse(file_path: str, file_extension: str) -> dict:
        """
        Main entry point. Detects file type and extracts text.
        """
        ext = file_extension.lower().strip(".")

        if ext == "pdf":
            raw_text = FileParser.extract_from_pdf(file_path)
        elif ext == "docx":
            raw_text = FileParser.extract_from_docx(file_path)
        elif ext in ("txt", "md"):
            raw_text = FileParser.extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        return {
            "raw_text": raw_text,
            "char_count": len(raw_text),
            "word_count": len(raw_text.split()),
            "file_type": ext,
        }
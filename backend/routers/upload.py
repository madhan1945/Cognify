"""
Upload Router
Handles file uploads and raw text input.
"""

import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from backend.services.file_parser import FileParser
from backend.services.preprocessor import TextPreprocessor

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def validate_file(file: UploadFile):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Allowed: {ALLOWED_EXTENSIONS}",
        )
    return ext


@router.post("/upload/file")
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF, DOCX, or TXT file and return preprocessed content."""
    ext = validate_file(file)

    file_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{file_id}.{ext}"

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        parsed = FileParser.parse(str(save_path), ext)

        if parsed["word_count"] < 50:
            raise HTTPException(
                status_code=422,
                detail="File content too short. Please upload a document with at least 50 words.",
            )

        processed = TextPreprocessor.process(parsed["raw_text"])

        return JSONResponse(
            content={
                "file_id": file_id,
                "filename": file.filename,
                "file_type": ext,
                "word_count": parsed["word_count"],
                "sentence_count": processed["sentence_count"],
                "paragraph_count": processed["paragraph_count"],
                "keywords": processed["keywords"],
                "topics": processed["topics"],
                "preview": processed["cleaned_text"][:500] + "...",
                "status": "processed",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        if save_path.exists():
            os.remove(save_path)


@router.post("/upload/text")
async def upload_text(content: str = Form(..., min_length=100)):
    """Accept raw text input and return preprocessed content."""
    try:
        processed = TextPreprocessor.process(content)

        return JSONResponse(
            content={
                "file_id": str(uuid.uuid4()),
                "file_type": "text",
                "word_count": len(content.split()),
                "sentence_count": processed["sentence_count"],
                "paragraph_count": processed["paragraph_count"],
                "keywords": processed["keywords"],
                "topics": processed["topics"],
                "preview": processed["cleaned_text"][:500] + "...",
                "status": "processed",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
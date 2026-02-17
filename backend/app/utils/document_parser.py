"""Document Parser - PDF and DOCX extraction"""
from typing import Optional
from app.core.logging import get_logger
logger = get_logger("document_parser")


def extract_text_from_pdf(filepath: str) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        logger.error("pdf_extraction_failed", error=str(e))
        return ""


def extract_text_from_docx(filepath: str) -> str:
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        logger.error("docx_extraction_failed", error=str(e))
        return ""


def extract_text(filepath: str) -> str:
    if filepath.endswith(".pdf"):
        return extract_text_from_pdf(filepath)
    elif filepath.endswith(".docx"):
        return extract_text_from_docx(filepath)
    elif filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

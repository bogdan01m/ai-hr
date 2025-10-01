"""PDF processing utility for company information extraction."""

from pathlib import Path
from typing import Optional, Tuple

import tiktoken
from pypdf import PdfReader

from .logger_config import log_pdf_operation


def process_pdf_file(pdf_path: str) -> Tuple[Optional[str], str]:
    """
    Process PDF file and validate token count.
    Based on the original user code.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Tuple of (extracted_text or None, status_message)
    """
    try:
        # Initialize tokenizer
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")

        # Create PDF reader object
        reader = PdfReader(pdf_path)

        # Extract text from all pages
        texts = []
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            text = page.extract_text() or ""  # важно: не добавляем None
            texts.append(text)

        # Join all texts
        full_text = "\n\n".join(texts)

        # Check token count
        token_count = len(encoding.encode(full_text))
        is_within_limit = token_count <= 100000

        log_pdf_operation(
            "process_pdf",
            success=is_within_limit,
            pdf_path=pdf_path,
            token_count=token_count,
        )

        if not is_within_limit:
            error_msg = f"Извините, но PDF слишком большой ({token_count:,} токенов). Максимум разрешено 100,000 токенов."
            return None, error_msg

        success_msg = f"PDF успешно обработан ({token_count:,} токенов)"
        return full_text, success_msg

    except Exception as e:
        error_msg = f"Ошибка при обработке PDF: {str(e)}"
        log_pdf_operation(
            "process_pdf", success=False, pdf_path=pdf_path, error=error_msg
        )
        return None, error_msg


class PDFProcessor:
    """Simple wrapper for backward compatibility."""

    def process_pdf(self, pdf_path: Path) -> Tuple[Optional[str], str]:
        return process_pdf_file(str(pdf_path))

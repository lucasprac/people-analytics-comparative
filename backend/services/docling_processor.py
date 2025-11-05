import os
from typing import Dict, Any

DOCLING_ENABLED = os.getenv('DOCLING_ENABLED', 'false').lower() == 'true'

try:
    if DOCLING_ENABLED:
        from docling.document_converter import DocumentConverter  # type: ignore
    else:
        DocumentConverter = None  # type: ignore
except Exception:
    DocumentConverter = None  # type: ignore

class DoclingDisabledError(RuntimeError):
    pass

class HRDoclingProcessor:
    """Hermetic Docling processor (BETA)
    - Disabled by default via feature flag
    - Only structured extraction from PDF/DOCX
    - No audio, no sentiment analysis
    - No public endpoints; to be called by internal jobs only
    """

    def __init__(self) -> None:
        if not DOCLING_ENABLED or DocumentConverter is None:
            raise DoclingDisabledError("Docling is disabled or not installed.")
        self.converter = DocumentConverter()

    def extract_structured(self, file_content: bytes) -> Dict[str, Any]:
        """Extracts structured information from PDF/DOCX using Docling.
        Returns a dict that callers can map to staging tables.
        """
        result = self.converter.convert(file_content)
        # Export to an expressive intermediate format (JSON/Markdown)
        text_md = result.document.export_to_markdown()
        json_lossless = result.document.export_to_dict()
        return {
            "markdown": text_md,
            "json": json_lossless,
            "meta": {
                "pages": getattr(result.document, 'page_count', None)
            }
        }

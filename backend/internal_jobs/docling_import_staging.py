from sqlalchemy import create_engine, text
import os, hashlib
from .services.docling_processor import HRDoclingProcessor, DoclingDisabledError

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@localhost:5432/people_analytics')
engine = create_engine(DATABASE_URL)

"""
INTERNAL JOB (BETA / HERMETIC)
- Reads a local file (PDF/DOCX), processes with Docling (if enabled),
  and stores outputs in a staging table without touching production tables.
- Not exposed as API; to be run manually or via internal scheduler.
"""

def import_document_to_staging(path: str, quarter: str, created_by: str = 'system'):
    try:
        processor = HRDoclingProcessor()
    except DoclingDisabledError as e:
        print(f"Docling disabled: {e}")
        return

    with open(path, 'rb') as f:
        content = f.read()

    extracted = processor.extract_structured(content)
    sha = hashlib.sha256(content).hexdigest()

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO docling_documents_staging
            (quarter, source_name, source_hash, content_markdown, content_json, meta, created_by)
            VALUES (:q, :name, :hash, :md, :json, :meta, :by)
        """), {
            'q': quarter,
            'name': os.path.basename(path),
            'hash': sha,
            'md': extracted['markdown'],
            'json': extracted['json'],
            'meta': extracted['meta'],
            'by': created_by,
        })
        conn.commit()
    print(f"Stored in staging: {path} ({sha[:8]}...) for {quarter}")

if __name__ == '__main__':
    # Example (won't run if DOCLING_ENABLED=false)
    # import_document_to_staging('docs/sample.pdf', '2025-Q4')
    pass

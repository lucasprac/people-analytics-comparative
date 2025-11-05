-- Staging table for Docling-extracted content (kept isolated)
CREATE TABLE IF NOT EXISTS docling_documents_staging (
    id SERIAL PRIMARY KEY,
    quarter VARCHAR(10) NOT NULL,
    source_name TEXT,
    source_hash VARCHAR(128),
    content_markdown TEXT,
    content_json JSONB,
    meta JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

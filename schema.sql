-- IOEVERSE database schema
-- Run with: psql $DATABASE_URL -f schema.sql
-- All statements are idempotent (IF NOT EXISTS).

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table (may already exist)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Documents table — one row per ingested file
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    subject TEXT NOT NULL,
    chapter TEXT NOT NULL,
    source_filename TEXT UNIQUE,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document chunks — individual text chunks with embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    chapter TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(3072),
    page INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast filtering and similarity search
CREATE INDEX IF NOT EXISTS idx_chunks_subject_chapter
    ON document_chunks(subject, chapter);

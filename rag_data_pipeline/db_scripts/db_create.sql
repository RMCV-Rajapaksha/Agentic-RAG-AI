-- 1. Create a new database for your RAG project.
CREATE DATABASE agentic_rag_db;

-- 2. Connect to your newly created database.
\c agentic_rag_db

-- 3. Enable the pgvector extension (CRITICAL STEP).
CREATE EXTENSION IF NOT EXISTS vector;

-- 4. Create the table as per your schema requirements.
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    vector VECTOR(1536) NOT NULL, -- IMPORTANT: Adjust 1536 to your embedding model's dimension size. (e.g., OpenAI ada-002 is 1536)
    chunked_text TEXT NOT NULL,
    metadata JSONB,
    source TEXT
);

-- 5. (Optional) Verify that the table was created correctly.
\dt

-- 6. Exit the psql shell.
\q
CREATE SCHEMA IF NOT EXISTS ragmaster;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE
  ragmaster.claim_chunks (
    id UUID NOT NULL,
    text TEXT NOT NULL
  );

CREATE TABLE
  ragmaster.claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    claim_chunk_id UUID NOT NULL,
    text TEXT NOT NULL,
    embedding VECTOR (1024) NOT NULL
  );


CREATE INDEX ON ragmaster.claims USING hnsw (embedding vector_cosine_ops);
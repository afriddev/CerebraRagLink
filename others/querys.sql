CREATE SCHEMA IF NOT EXISTS grag;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE grag.chunks (
  id UUID NOT NULL,
  text TEXT NOT NULL,
  text_vector VECTOR(1024) NOT NULL,
  entities TEXT[] NOT NULL
);

CREATE TABLE grag.chunk_questions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  chunk_id UUID NOT NULL,
  question_text TEXT NOT NULL,
  question_vector VECTOR(1024) NOT NULL
);

CREATE TABLE grag.chunk_images (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  chunk_id UUID NOT NULL,
  image_url TEXT DEFAULT NULL,
  description TEXT NOT NULL
);


CREATE TABLE grag.chunk_relations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  chunk_id UUID NOT NULL,
  relation TEXT NOT NULL,
  relation_vector VECTOR(1024) NOT NULL,
  relation_entities TEXT[] NOT NULL
);


CREATE INDEX idx_chunks_vec_hnsw        ON grag.chunks          USING hnsw (text_vector      vector_cosine_ops)   WITH (m=16, ef_construction=300);
CREATE INDEX idx_chunkq_vec_hnsw        ON grag.chunk_questions USING hnsw (question_vector  vector_cosine_ops)   WITH (m=16, ef_construction=300);
CREATE INDEX idx_chunkrel_vec_hnsw      ON grag.chunk_relations USING hnsw (relation_vector  vector_cosine_ops)   WITH (m=16, ef_construction=300);

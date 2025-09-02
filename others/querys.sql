CREATE SCHEMA IF NOT EXISTS ragmaster;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE
  ragmaster.userman_cks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    text TEXT NOT NULL,
    embedding VECTOR (1024) NOT NULL
  );

CREATE TABLE
  ragmaster.userman_ck_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    chunk_id UUID NOT NULL,
    text TEXT NOT NULL,
    embedding VECTOR (1024) NOT NULL
  );

CREATE TABLE
  ragmaster.userman_ck_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    chunk_id UUID NOT NULL,
    image_url TEXT DEFAULT NULL,
    description TEXT NOT NULL
  );

CREATE TABLE
  ragmaster.userman_ck_relations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    chunk_id UUID NOT NULL,
    text TEXT NOT NULL,
    embedding VECTOR (1024) NOT NULL
  );

CREATE TABLE
  IF NOT EXISTS ragmaster.qa_answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    text TEXT NOT NULL
  );

CREATE TABLE
  IF NOT EXISTS ragmaster.qa_ques (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    answer_id UUID NOT NULL,
    text TEXT NOT NULL,
    embedding VECTOR (1024) NOT NULL
  );

CREATE INDEX ON ragmaster.userman_cks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX ON ragmaster.userman_ck_questions USING hnsw (embedding vector_cosine_ops);

CREATE INDEX ON ragmaster.userman_ck_relations USING hnsw (embedding vector_cosine_ops);

CREATE INDEX ON ragmaster.qa_ques USING hnsw (embedding vector_cosine_ops);
qa_embedding_texts_query = """
CREATE TABLE IF NOT EXISTS qa_embedding_texts (
    id UUID PRIMARY KEY,
    vector_id UUID NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    embedding_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

qa_embedding_vectors_query = """
CREATE TABLE IF NOT EXISTS qa_embedding_vectors (
    id UUID PRIMARY KEY,
    embedding_id UUID NOT NULL,  
    embedding_vector vector(1024) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

qa_embedding_vector_index_query = """
CREATE INDEX IF NOT EXISTS qa_embedding_vectors_embedding_idx
ON qa_embedding_vectors
USING hnsw (embedding_vector vector_cosine_ops);
"""



"""

CREATE TABLE IF NOT EXISTS qa_embedding_texts (
    id UUID PRIMARY KEY,
    vector_id UUID NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    embedding_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS qa_embedding_vectors (
    id UUID PRIMARY KEY,
    embedding_id UUID NOT NULL,  
    embedding_vector vector(1024) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS qa_embedding_vectors_embedding_idx
ON qa_embedding_vectors
USING hnsw (embedding_vector vector_cosine_ops);

"""
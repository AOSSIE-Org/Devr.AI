--Function to execute arbitrary SQL
CREATE OR REPLACE FUNCTION execute_sql(sql TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE sql;
END;
$$ LANGUAGE plpgsql;


-- Create embeddings table
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(384) -- 384-dimensional embedding from Hugging Face sentence transformer
);


-- Function to query a document in the embeddings table, this function will return the documents with the closest embedding to the query embedding
CREATE OR REPLACE FUNCTION match_documents(query_embedding VECTOR(384), result_limit INT DEFAULT 5)
RETURNS TABLE(id INT, content TEXT, distance FLOAT) AS $$
BEGIN
    RETURN QUERY
    SELECT e.id, e.content, l2_distance(e.embedding, query_embedding) AS distance
    FROM embeddings e
    ORDER BY distance
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;
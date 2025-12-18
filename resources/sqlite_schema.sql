-- This schema is for the local SQLite vector store.

-- Main table to store the text content and metadata of each chunk.
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    metadata TEXT, -- Storing metadata as a JSON string
    sparse_vector TEXT -- Storing sparse vector as a JSON string (e.g. BM25)
);

-- Virtual table using the sqlite-vss extension to store and index the vector embeddings.
-- It links back to the main chunks table via the 'rowid'.
CREATE VIRTUAL TABLE IF NOT EXISTS vss_chunks USING vss0(
    embedding(384) -- The dimension of our 'all-MiniLM-L6-v2' model is 384
);

import pytest
import sqlite3
import json
from pathlib import Path
from langchain_core.documents import Document
from textnexus.core.storage import SQLiteVectorStore
from textnexus.core.embedding import SentenceTransformerModel

class MockEmbeddingModel:
    """Mock model to avoid loading heavy transformers during this unit test."""
    def create_embeddings(self, texts):
        return [[0.1, 0.2] for _ in texts]

@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test_sparse.db"
    return str(db_path)

def test_schema_has_sparse_column(temp_db):
    """Test that the database schema includes the sparse_vector column."""
    store = SQLiteVectorStore(db_path=temp_db, embedding_model=MockEmbeddingModel())
    
    # Inspect schema directly
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(chunks)")
    columns = [info[1] for info in cursor.fetchall()]
    conn.close()
    
    assert "sparse_vector" in columns, "Column 'sparse_vector' missing from 'chunks' table"

def test_add_documents_with_sparse(temp_db):
    """Test adding documents with associated sparse vectors."""
    store = SQLiteVectorStore(db_path=temp_db, embedding_model=MockEmbeddingModel())
    
    docs = [
        Document(page_content="Doc 1", metadata={"id": 1}),
        Document(page_content="Doc 2", metadata={"id": 2})
    ]
    sparse_vectors = [
        {"token_1": 1.5, "token_2": 0.5},  # Sparse vector for Doc 1
        {"token_3": 2.0}                   # Sparse vector for Doc 2
    ]
    
    # This should fail if the argument isn't supported or logic isn't implemented
    store.add_documents(docs, sparse_vectors=sparse_vectors)
    
    # Verify data in DB
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT content, sparse_vector FROM chunks")
    rows = cursor.fetchall()
    conn.close()
    
    assert len(rows) == 2
    # Check first row
    content, sparse_json = rows[0]
    assert content == "Doc 1"
    assert sparse_json is not None
    loaded_sparse = json.loads(sparse_json)
    assert loaded_sparse == {"token_1": 1.5, "token_2": 0.5}

def test_add_documents_sparse_mismatch(temp_db):
    """Test that an error is raised if sparse vectors length doesn't match docs."""
    store = SQLiteVectorStore(db_path=temp_db, embedding_model=MockEmbeddingModel())
    docs = [Document(page_content="A"), Document(page_content="B")]
    sparse = [{"t": 1}] # Only 1 vector for 2 docs
    
    with pytest.raises(ValueError):
        store.add_documents(docs, sparse_vectors=sparse)

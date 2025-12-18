import pytest
from unittest.mock import MagicMock
import numpy as np
from langchain_core.documents import Document

from textnexus.core.embedding import BaseEmbeddingModel
from textnexus.core.storage import SQLiteVectorStore

# The dimension of the real model we are using
MODEL_DIMENSION = 384

@pytest.fixture
def mock_embedding_model():
    """Provides a mocked embedding model that returns predictable 384-dimensional vectors."""
    mock_model = MagicMock(spec=BaseEmbeddingModel)
    
    # --- THE FIX IS HERE: Use a dictionary for robust mapping ---
    # Define a mapping from specific texts to specific, unique vectors
    vec1 = [0.0] * MODEL_DIMENSION
    vec1[0] = 1.0
    vec2 = [0.0] * MODEL_DIMENSION
    vec2[1] = 1.0
    query_vec = [0.0] * MODEL_DIMENSION
    query_vec[0] = 0.9

    embedding_map = {
        "This is the first chunk.": vec1,
        "This is the second chunk.": vec2,
        "A query about the first chunk.": query_vec,
    }

    # This new side_effect function is much more robust
    def mock_create_embeddings(texts: list[str]):
        """Returns the pre-defined vector for each text in the input list."""
        # For generic batch tests, create simple vectors
        if texts[0].startswith("Doc "):
            return [[(i + 1) * 0.1] + [0.0] * (MODEL_DIMENSION - 1) for i in range(len(texts))]
        # For our specific query tests, use the map
        return [embedding_map.get(text, [0.0] * MODEL_DIMENSION) for text in texts]

    mock_model.create_embeddings.side_effect = mock_create_embeddings
    return mock_model

@pytest.fixture
def in_memory_vector_store(mock_embedding_model):
    """
    Provides an instance of SQLiteVectorStore using an in-memory database.
    """
    store = SQLiteVectorStore(db_path=":memory:", embedding_model=mock_embedding_model)
    return store

def test_add_single_document(in_memory_vector_store):
    """
    Tests that a single document can be added to the vector store correctly.
    """
    doc = Document(page_content="This is the first chunk.", metadata={"source": "doc1.pdf"})
    in_memory_vector_store.add_documents([doc])

    cursor = in_memory_vector_store.conn.cursor()
    cursor.execute("SELECT rowid, embedding FROM vss_chunks WHERE rowid = 1")
    vss_result = cursor.fetchone()
    assert vss_result is not None
    
    expected_vec = [0.0] * MODEL_DIMENSION
    expected_vec[0] = 1.0
    expected_bytes = np.array(expected_vec, dtype=np.float32).tobytes()
    assert vss_result[1] == expected_bytes


def test_query_returns_correct_document(in_memory_vector_store):
    """
    Tests that the query method returns the most similar document.
    """
    doc1 = Document(page_content="This is the first chunk.", metadata={"source": "doc1.pdf"})
    doc2 = Document(page_content="This is the second chunk.", metadata={"source": "doc2.pdf"})
    in_memory_vector_store.add_documents([doc1, doc2])

    query_embedding = in_memory_vector_store.embedding_model.create_embeddings(
        ["A query about the first chunk."]
    )[0]
    
    results = in_memory_vector_store.query(query_embedding, top_k=1)

    assert len(results) == 1
    assert results[0].page_content == "This is the first chunk."

def test_add_documents_batch_insertion(in_memory_vector_store):
    """
    Tests that multiple documents can be added in a single batch.
    """
    docs = [
        Document(page_content=f"Doc {i}", metadata={"source": f"doc{i}.pdf"})
        for i in range(5)
    ]
    in_memory_vector_store.add_documents(docs)

    cursor = in_memory_vector_store.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chunks")
    count = cursor.fetchone()[0]
    assert count == 5

# ... (the other tests for empty list and DB failure remain the same)
def test_add_documents_handles_empty_list(in_memory_vector_store):
    in_memory_vector_store.add_documents([])
    cursor = in_memory_vector_store.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chunks")
    count = cursor.fetchone()[0]
    assert count == 0

def test_add_documents_raises_error_on_db_failure(mock_embedding_model, mocker):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.lastrowid = 1
    mock_conn.commit.side_effect = Exception("DB commit failed!")
    
    mocker.patch("textnexus.core.storage.sqlite3.connect", return_value=mock_conn)
    mocker.patch("builtins.open", mocker.mock_open(read_data=""))
    mocker.patch("sqlite_vss.load")
    
    with pytest.raises(Exception, match="DB commit failed!"):
        store = SQLiteVectorStore(db_path="dummy.db", embedding_model=mock_embedding_model)
        docs = [Document(page_content="Test doc")]
        store.add_documents(docs)

    mock_conn.rollback.assert_called_once()


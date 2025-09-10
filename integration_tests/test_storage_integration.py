import pytest
from langchain_core.documents import Document

# Import the real components we want to test together
from auto_rag.core.embedding import SentenceTransformerModel
from auto_rag.core.storage import SQLiteVectorStore

@pytest.mark.integration
def test_sqlite_vector_store_integration(tmp_path):
    """
    Performs an end-to-end integration test on the SQLiteVectorStore.

    This test verifies that the vector store can correctly integrate with a
    real embedding model and a file-based database to add, store,
    and retrieve documents.

    Args:
        tmp_path: A pytest fixture that provides a temporary directory path.
    """
    # 1. Setup: Define the path for our temporary database
    db_path = tmp_path / "test_vector_store.db"
    
    # Instantiate the real components
    embedding_model = SentenceTransformerModel()
    vector_store = SQLiteVectorStore(db_path=str(db_path), embedding_model=embedding_model)

    # 2. Add Documents: Add two distinct documents to the store
    doc1 = Document(page_content="The cat sat on the mat.", metadata={"source": "doc1.txt"})
    doc2 = Document(page_content="The dog chased the ball.", metadata={"source": "doc2.txt"})
    vector_store.add_documents([doc1, doc2])

    # 3. Create a Query: Create a query that is semantically similar to the first document
    query_text = "A feline was resting on the rug."
    query_embedding = embedding_model.create_embeddings([query_text])[0]

    # 4. Execute the Query: Search for the most similar document
    results = vector_store.query(query_embedding, top_k=1)

    # 5. Assertions: Verify that the correct document was retrieved
    assert len(results) == 1
    assert results[0].page_content == "The cat sat on the mat."
    assert results[0].metadata["source"] == "doc1.txt"

    print(f"\nIntegration test successful! Database was created at: {db_path}")

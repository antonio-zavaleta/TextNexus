import pytest
import sqlite3
import json
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from auto_rag.core.ingestion_pipeline import IngestionPipeline
from auto_rag.core.embedding import BaseEmbeddingModel
from auto_rag.core.storage import SQLiteVectorStore
from auto_rag.core.chunking import SemanticTextSplitter
from auto_rag.core.ingestion import BaseIngestion
from auto_rag import config

# Custom Loader for local files
class LocalFileLoader(BaseIngestion):
    def load(self, source: str) -> List[Document]:
        loader = PyPDFLoader(source)
        return loader.load()

# Mock Embedding Model to bypass heavy ML dependencies
class MockEmbeddingModel(BaseEmbeddingModel):
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Return dummy 384-dimensional vectors (standard size for MiniLM)
        return [[0.1] * 384 for _ in texts]

@pytest.mark.integration
def test_full_pipeline_ingestion_integration(tmp_path):
    """
    Integration test that runs the full IngestionPipeline with:
    - Real PDF loading (local)
    - Real Chunking (SemanticTextSplitter)
    - MOCK Embedding (to avoid external dependency issues)
    - Real SQLite Storage (Temporary DB)
    """
    # 1. Setup Resources
    db_path = tmp_path / "test_integration.db"
    
    # Initialize components
    embedding_model = MockEmbeddingModel()  # Use Mock!
    vector_store = SQLiteVectorStore(str(db_path), embedding_model)
    splitter = SemanticTextSplitter(embedding_model)
    loader = LocalFileLoader()
    
    # Initialize Pipeline
    pipeline = IngestionPipeline(loader, splitter, vector_store)
    
    # Path to our dummy PDF
    pdf_path = str(config.PROJECT_ROOT / "tests/data/20k_leagues.pdf")
    
    # 2. Execute Pipeline
    stats = pipeline.run(pdf_path)
    
    # 3. Verify Results
    
    # A. Check returned stats
    assert stats["documents_loaded"] > 0, "Should load at least 1 document"
    assert stats["chunks_created"] > 0, "Should create chunks"
    
    # B. Check Database Integrity
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check count
    cursor.execute("SELECT count(*) FROM chunks")
    count = cursor.fetchone()[0]
    assert count == stats["chunks_stored"]
    
    # Check content of one chunk to verify loading worked
    cursor.execute("SELECT content FROM chunks LIMIT 1")
    content = cursor.fetchone()[0]
    
    assert len(content) > 10
    assert "1866" in content or "Sea" in content or "monster" in content
    
    conn.close()

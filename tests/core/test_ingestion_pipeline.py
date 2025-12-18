import pytest
from unittest.mock import Mock, MagicMock

# FAILING IMPORT: This module does not exist yet
from textnexus.core.ingestion_pipeline import IngestionPipeline

def test_ingestion_pipeline_initialization():
    """Verify the pipeline initializes with required components."""
    mock_loader = Mock()
    mock_splitter = Mock()
    mock_vector_store = Mock()
    
    pipeline = IngestionPipeline(
        loader=mock_loader,
        splitter=mock_splitter,
        vector_store=mock_vector_store
    )
    
    assert pipeline.loader == mock_loader
    assert pipeline.splitter == mock_splitter
    assert pipeline.vector_store == mock_vector_store

def test_ingestion_pipeline_run_flow():
    """Verify the run method orchestrates load -> split -> store correctly."""
    # Arrange
    mock_loader = Mock()
    # Simulate loading 2 documents
    mock_loader.load.return_value = ["doc1", "doc2"]
    
    mock_splitter = Mock()
    # Simulate splitting into 3 chunks
    mock_splitter.split_documents.return_value = ["chunk1", "chunk2", "chunk3"]
    
    mock_vector_store = Mock()
    
    pipeline = IngestionPipeline(
        loader=mock_loader,
        splitter=mock_splitter,
        vector_store=mock_vector_store
    )
    
    # Act
    # We expect 'run' to return a dict with stats
    result = pipeline.run(source="test-prefix")
    
    # Assert
    # 1. Loader called with correct source
    mock_loader.load.assert_called_once_with("test-prefix")
    
    # 2. Splitter called with documents from loader
    mock_splitter.split_documents.assert_called_once_with(["doc1", "doc2"])
    
    # 3. Vector store called with chunks from splitter
    mock_vector_store.add_documents.assert_called_once_with(["chunk1", "chunk2", "chunk3"])
    
    # 4. Result contains expected stats
    assert result["documents_loaded"] == 2
    assert result["chunks_created"] == 3
    assert result["chunks_stored"] == 3

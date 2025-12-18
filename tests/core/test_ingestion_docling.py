import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from langchain_core.documents import Document
from textnexus.core.loaders import DoclingLoader

# Mock the entire docling library to avoid installation/download issues during unit tests
# and to verify our wrapper logic independently.
@pytest.fixture
def mock_docling_converter():
    with patch("textnexus.core.loaders.DocumentConverter") as mock:
        yield mock

def test_docling_loader_init():
    """Test that DoclingLoader initializes the converter."""
    # We need to patch where the class is defined/imported
    with patch("textnexus.core.loaders.DocumentConverter") as MockConverter:
        loader = DoclingLoader()
        MockConverter.assert_called_once()
        assert loader.converter is not None

def test_docling_loader_load_success(tmp_path):
    """Test loading a mock PDF successfully."""
    # Create a dummy file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("fake pdf content")
    
    # Mock the return value of converter.convert()
    mock_result = MagicMock()
    # Simulate the Docling document structure (simplified)
    mock_doc = MagicMock()
    mock_doc.export_to_markdown.return_value = "# Header\n\nSome text."
    mock_result.document = mock_doc
    
    with patch("textnexus.core.loaders.DocumentConverter") as MockConverter:
        instance = MockConverter.return_value
        instance.convert.return_value = mock_result
        
        loader = DoclingLoader()
        documents = loader.load(str(pdf_path))
        
        # Verify interactions
        instance.convert.assert_called_once_with(str(pdf_path))
        
        # Verify output
        assert len(documents) == 1
        assert isinstance(documents[0], Document)
        assert documents[0].page_content == "# Header\n\nSome text."
        assert documents[0].metadata["source"] == str(pdf_path)

def test_docling_loader_file_not_found():
    """Test that loader raises error if file does not exist."""
    loader = DoclingLoader()
    with pytest.raises(FileNotFoundError):
        loader.load("non_existent_file.pdf")

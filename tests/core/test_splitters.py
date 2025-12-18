
import pytest
from langchain_core.documents import Document
from textnexus.core.splitters import StructuredTextSplitter

class TestStructuredTextSplitter:

    @pytest.fixture
    def sample_markdown(self):
        return """
# Header 1
Content under header 1.

## Header 2
Content under header 2.

### Header 3
Content under header 3.
        """

    @pytest.fixture
    def sample_document(self, sample_markdown):
        return Document(
            page_content=sample_markdown,
            metadata={"source": "test.pdf", "page": 1}
        )

    def test_split_documents_basic(self, sample_document):
        splitter = StructuredTextSplitter()
        chunks = splitter.split_documents([sample_document])
        
        # Expecting 3 chunks due to H1, H2, H3
        # Depending on how logic handles hierarchy, H2 might inherit H1.
        # MarkdownHeaderTextSplitter logic:
        # Chunk 1: Header 1 (+ content)
        # Chunk 2: Header 1 > Header 2 (+ content)
        # Chunk 3: Header 1 > Header 2 > Header 3 (+ content)
        
        assert len(chunks) == 3
        
        # Check Content
        assert "Content under header 1" in chunks[0].page_content
        assert "Content under header 2" in chunks[1].page_content
        assert "Content under header 3" in chunks[2].page_content
        
        # Check Metadata preservation from original doc
        assert chunks[0].metadata["source"] == "test.pdf"
        assert chunks[0].metadata["page"] == 1
        
        # Check Metadata enrichment (headers)
        # Note: keys depend on default config of StructuredTextSplitter
        assert chunks[0].metadata.get("Header 1") == "Header 1"
        assert chunks[1].metadata.get("Header 2") == "Header 2"
        assert chunks[2].metadata.get("Header 3") == "Header 3"

    def test_split_documents_no_headers(self):
        doc = Document(page_content="Just some flat text.", metadata={"source": "flat.txt"})
        splitter = StructuredTextSplitter()
        chunks = splitter.split_documents([doc])
        
        assert len(chunks) == 1
        assert chunks[0].page_content == "Just some flat text."
        assert chunks[0].metadata["source"] == "flat.txt"

    def test_custom_headers(self):
        markdown = """
# Title
## Section
Text
        """
        doc = Document(page_content=markdown, metadata={})
        # Only split on H1
        splitter = StructuredTextSplitter(headers_to_split_on=[("#", "H1")])
        chunks = splitter.split_documents([doc])
        
        # With only H1 split, H2 should remain in the content of the H1 chunk
        assert len(chunks) == 1
        assert "## Section" in chunks[0].page_content
        assert chunks[0].metadata["H1"] == "Title"

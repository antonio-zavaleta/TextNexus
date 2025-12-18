from typing import List, Iterator, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    # Fallback or strict error depending on requirements. 
    # For now, we assume it's installed as per pyproject.toml
    DocumentConverter = None

class DoclingLoader(BaseLoader):
    """
    Loader that uses Docling to parse PDFs (and other formats) into LangChain Documents.
    It preserves rich structure (preserving tables/headers) better than standard PyPDF.
    """
    def __init__(self):
        if DocumentConverter is None:
            raise ImportError("Docling is not installed. Please run `poetry add docling`.")
        self.converter = DocumentConverter()

    def lazy_load(self) -> Iterator[Document]:
        """Lazy load is required by BaseLoader but we primarily use load()."""
        # We implementation load() directly below, but for BaseLoader compliance:
        raise NotImplementedError("lazy_load not implemented, use load()")

    def load(self, file_path: str) -> List[Document]:
        """
        Load a file using Docling and convert to LangChain Documents.
        
        Args:
            file_path: Path to the file to load.
            
        Returns:
            List[Document]: List of documents (currently 1 per file, containing full markdown).
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Convert the document
        result = self.converter.convert(str(path))
        
        # Export to markdown (simplest way to get text + structure)
        # Docling's export_to_markdown returns a string
        md_content = result.document.export_to_markdown()
        
        # Create a single LangChain Document for the whole file
        # In the future (A.2), we will split this intelligently using the structure.
        return [
            Document(
                page_content=md_content,
                metadata={
                    "source": str(path),
                    "loader": "docling",
                    "filename": path.name
                }
            )
        ]


from typing import List, Tuple, Any
from langchain_core.documents import Document
from langchain.text_splitter import MarkdownHeaderTextSplitter

class StructuredTextSplitter:
    """
    Splits Markdown documents based on their header structure.
    Preserves original metadata and enriches it with header info.
    """
    
    def __init__(self, headers_to_split_on: List[Tuple[str, str]] = None):
        """
        Args:
            headers_to_split_on: List of tuples (header_char, header_name).
                                 Defaults to splitting on H1, H2, H3.
        """
        if headers_to_split_on is None:
            self.headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        else:
            self.headers_to_split_on = headers_to_split_on
            
        self.internal_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False # Docling output might be cleaner if we keep headers in text too, or strip them. Let's strip=False default behavior usually strips. Wait, check defaults.
            # Default is strip_headers=True. Let's stick to default for now, but note that RAG might want context.
        )
        
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split a list of documents by headers.
        
        Args:
            documents: List of LangChain Documents (usually full pages).
            
        Returns:
            List of smaller Document chunks.
        """
        all_chunks = []
        
        for doc in documents:
            # 1. Split the text
            # split_text returns documents with 'page_content' and 'metadata' (from headers)
            splits = self.internal_splitter.split_text(doc.page_content)
            
            # 2. Merge metadata
            for split in splits:
                # Start with original doc metadata (e.g. source, page)
                combined_metadata = doc.metadata.copy()
                # Update with header metadata found by splitter
                combined_metadata.update(split.metadata)
                
                # Create new doc
                new_doc = Document(
                    page_content=split.page_content,
                    metadata=combined_metadata
                )
                all_chunks.append(new_doc)
                
        return all_chunks

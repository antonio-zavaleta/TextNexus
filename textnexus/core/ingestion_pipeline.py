import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class IngestionPipeline:
    """
    Orchestrates the document ingestion process: Loading -> Splitting -> Storing.
    """
    def __init__(self, loader, splitter, vector_store):
        """
        Initialize the pipeline with necessary components.
        
        Args:
            loader: Component responsible for loading documents (e.g., MinIOLoader).
            splitter: Component responsible for splitting documents into chunks.
            vector_store: Component responsible for storing chunks (e.g., SQLiteVectorStore).
        """
        self.loader = loader
        self.splitter = splitter
        self.vector_store = vector_store

    def run(self, source: str) -> Dict[str, Any]:
        """
        Run the ingestion pipeline for a specific source.
        
        Args:
            source: The source identifier (e.g., file prefix or path) to ingest from.
            
        Returns:
            Dict containing statistics about the ingestion process.
        """
        logger.info(f"Starting ingestion pipeline for source: {source}")
        
        # 1. Load Documents
        documents = self.loader.load(source)
        doc_count = len(documents) if documents else 0
        
        if not documents:
            logger.warning(f"No documents found for source: {source}")
            return {
                "documents_loaded": 0,
                "chunks_created": 0,
                "chunks_stored": 0
            }
        
        logger.info(f"Loaded {doc_count} documents.")

        # 2. Split Documents
        chunks = self.splitter.split_documents(documents)
        chunk_count = len(chunks) if chunks else 0
        logger.info(f"Created {chunk_count} chunks.")
        
        # 3. Store Chunks
        if chunks:
            self.vector_store.add_documents(chunks)
            logger.info(f"Stored {chunk_count} chunks in vector store.")
        
        return {
            "documents_loaded": doc_count,
            "chunks_created": chunk_count,
            "chunks_stored": chunk_count
        }

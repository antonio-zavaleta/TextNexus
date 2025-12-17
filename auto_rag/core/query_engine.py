import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class QueryEngine:
    """
    Core engine for performing retrieval-augmented generation (RAG) queries.
    Decouples the logic from the CLI to enable programmatic usage.
    """

    def __init__(self, vector_store: Any, embedding_model: Any):
        """
        Initialize the QueryEngine with necessary dependencies.

        Args:
            vector_store: The vector store instance (e.g., SQLiteVectorStore).
            embedding_model: The embedding model instance (e.g., SentenceTransformer).
        """
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def query(self, query_text: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Execute a semantic search query.

        Args:
            query_text (str): The user's query.
            top_k (int): Number of results to return.

        Returns:
            Dict[str, Any]: A structured dictionary containing the results.
                            Format: {'results': [{'content': str, 'metadata': dict}, ...]}
        """
        try:
            logger.debug(f"QueryEngine.query called with query_text='{query_text}', top_k={top_k}")
            
            logger.debug("Creating embedding for query.")
            # detailed logging is preserved from the original utility
            query_embedding = self.embedding_model.create_embeddings([query_text])[0]
            logger.debug("Query embedding created.")

            logger.info(f"Searching for top {top_k} most similar chunks...")
            documents = self.vector_store.query(query_embedding, top_k=top_k)
            logger.info(f"Found {len(documents)} results.")

            # Format results into a serializable/structured dictionary
            results = []
            for doc in documents:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })

            return {"results": results, "count": len(results)}

        except Exception as e:
            logger.error(f"Error during query execution: {e}", exc_info=True)
            raise RuntimeError(f"QueryEngine failed: {e}") from e

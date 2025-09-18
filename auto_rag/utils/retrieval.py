import logging
from typing import List
from langchain_core.documents import Document
import typer

logger = logging.getLogger(__name__)

def retrieve_relevant_chunks(
    ctx: typer.Context,
    query_text: str,
    top_k: int
) -> List[Document]:
    """Retrieve the most relevant document chunks from the knowledge base.

    Uses the embedding model and vector store from the Typer context to perform semantic search
    for the top-k most similar document chunks to the user's query.

    Args:
        ctx (typer.Context): The Typer context containing shared components.
        query_text (str): The user's question or prompt.
        top_k (int): The number of relevant chunks to retrieve.

    Returns:
        List[Document]: A list of retrieved document chunk objects.

    Raises:
        RuntimeError: If retrieval fails due to an error in embedding or vector search.
    """
    try:
        logger.debug(f"Retrieval called with query_text='{query_text}', top_k={top_k}")
        embedding_model = ctx.obj.embedding_model
        vector_store = ctx.obj.vector_store

        logger.debug("Creating embedding for query.")
        query_embedding = embedding_model.create_embeddings([query_text])[0]
        logger.debug("Query embedding created.")

        logger.info(f"Searching for top {top_k} most similar chunks...")
        results = vector_store.query(query_embedding, top_k=top_k)
        logger.info(f"Found {len(results)} results.")

        return results
    except Exception as e:
        logger.error(f"Retrieval error: {e}", exc_info=True)
        raise RuntimeError(f"Error during retrieval: {e}") from e
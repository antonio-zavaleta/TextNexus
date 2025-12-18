import logging
from abc import ABC, abstractmethod
from typing import List

import nltk
from langchain_core.documents import Document
from sklearn.metrics.pairwise import cosine_similarity

from textnexus.core.embedding import BaseEmbeddingModel

# Get a logger instance for this module
logger = logging.getLogger(__name__)

# --- NLTK Setup ---
# The first time this code is run, it will download the 'punkt' tokenizer models.
# This is a one-time download.
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.info("NLTK 'punkt' tokenizer not found. Downloading...")
    nltk.download('punkt', quiet=True)
    logger.info("'punkt' tokenizer downloaded successfully.")


class BaseTextSplitter(ABC):
    """
    Abstract base class for all text splitting/chunking strategies.
    """

    @abstractmethod
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits a list of large documents into smaller, processed documents (chunks).

        Args:
            documents (List[Document]): The documents to be split.

        Returns:
            List[Document]: A list of smaller chunked documents.
        """
        pass


class SemanticTextSplitter(BaseTextSplitter):
    """
    Splits text into chunks based on semantic similarity.

    This method groups consecutive sentences that are semantically similar,
    creating a new chunk when the meaning changes significantly.
    """

    def __init__(
        self,
        embedding_model: BaseEmbeddingModel,
        similarity_threshold: float = 0.85,
    ):
        """
        Initializes the SemanticTextSplitter.

        Args:
            embedding_model (BaseEmbeddingModel): The embedding model to use for
                                                  calculating sentence similarity.
            similarity_threshold (float): The cosine similarity threshold to use
                                          for creating a split. Defaults to 0.85.
        """
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        logger.info(f"SemanticTextSplitter initialized with threshold {self.similarity_threshold}.")

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits a list of documents into semantic chunks.

        Args:
            documents (List[Document]): The documents to split.

        Returns:
            List[Document]: The resulting list of smaller, contextually-grouped documents.
        """
        all_chunks = []
        for doc in documents:
            chunks = self._split_text_into_chunks(doc.page_content)
            
            # Create new Document objects for each chunk, preserving the original metadata
            for chunk_text in chunks:
                new_doc = Document(page_content=chunk_text, metadata=doc.metadata.copy())
                all_chunks.append(new_doc)
        
        logger.info(f"Split {len(documents)} documents into {len(all_chunks)} semantic chunks.")
        return all_chunks

    def _split_text_into_chunks(self, text: str) -> List[str]:
        """The core semantic chunking algorithm."""
        sentences = nltk.sent_tokenize(text)

        if not sentences:
            return []

        # Create embeddings for all sentences at once
        embeddings = self.embedding_model.create_embeddings(sentences)

        # Calculate cosine similarity between adjacent sentences
        similarities = [
            cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
            for i in range(len(embeddings) - 1)
        ]

        chunks = []
        current_chunk_start_index = 0
        for i in range(len(similarities)):
            # If similarity drops below the threshold, a semantic break has occurred
            if similarities[i] < self.similarity_threshold:
                # The current chunk ends at sentence i
                chunk = " ".join(sentences[current_chunk_start_index : i + 1])
                chunks.append(chunk)
                # The next chunk starts at sentence i+1
                current_chunk_start_index = i + 1

        # Add the final chunk (the remaining sentences)
        final_chunk = " ".join(sentences[current_chunk_start_index:])
        chunks.append(final_chunk)

        return chunks


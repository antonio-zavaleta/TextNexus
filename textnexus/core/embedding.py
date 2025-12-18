import logging
from abc import ABC, abstractmethod
from typing import List

# Get a logger instance for this module
logger = logging.getLogger(__name__)


class BaseEmbeddingModel(ABC):
    """
    Abstract base class for all embedding model strategies.

    This class defines a common interface for creating vector embeddings
    from text, ensuring that different models can be used interchangeably.
    """

    @abstractmethod
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Converts a list of texts into a list of vector embeddings.

        Args:
            texts (List[str]): A list of strings to be embedded.

        Returns:
            List[List[float]]: A list of vector embeddings, where each
                               embedding is a list of floats.
        """
        pass


class SentenceTransformerModel(BaseEmbeddingModel):
    """
    A concrete implementation for creating embeddings using a local
    Hugging Face SentenceTransformers model.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = None):
        """
        Initializes the SentenceTransformerModel.

        The actual model is loaded on the first call to create_embeddings
        to avoid loading it into memory if it's not used.

        Args:
            model_name (str): The name of the SentenceTransformers model
                              to use from Hugging Face.
            device (str): Device to run the model on ('cpu', 'cuda', etc.). 
                          If None, it will be automatically selected.
        """
        self.model_name = model_name
        self.device = device
        self.model = None  # Lazy load the model
        logger.info(f"SentenceTransformerModel initialized with model '{self.model_name}'.")

    def _lazy_load_model(self):
        """Loads the model into memory. This is done on the first use."""
        if self.model is None:
            try:
                logger.info(f"Lazy loading SentenceTransformers model: '{self.model_name}' on device '{self.device}'...")
                # The sentence_transformers library is heavy, so we import it here.
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name, device=self.device)
                logger.info("Model loaded successfully.")
            except ImportError:
                logger.error("The 'sentence-transformers' package is not installed. Please install it with 'poetry add sentence-transformers'.")
                raise
            except Exception as e:
                logger.error(f"Failed to load model '{self.model_name}': {e}")
                raise

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Creates embeddings for a list of texts using the loaded model.

        Args:
            texts (List[str]): The list of strings to embed.

        Returns:
            List[List[float]]: The list of vector embeddings.
        """
        self._lazy_load_model() # Ensure model is loaded
        
        logger.info(f"Creating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts, show_progress_bar=False).tolist()
        logger.info("Embeddings created successfully.")
        return embeddings

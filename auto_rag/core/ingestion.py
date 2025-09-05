import os
import tempfile
import logging
from abc import ABC, abstractmethod
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from minio import Minio

# Import our configuration from the config.py file
from auto_rag import config

# Get a logger instance for this module
logger = logging.getLogger(__name__)


class BaseIngestion(ABC):
    """
    Abstract base class for all document ingestion strategies.

    This class defines a common interface for loading documents from various
    sources, ensuring that they are returned in a standardized format.
    """

    @abstractmethod
    def load(self, source: str) -> List[Document]:
        """
        Loads documents from a given source.

        Args:
            source (str): The identifier for the data source. This could be
                          a file path, a bucket object name, a URL, etc.

        Returns:
            List[Document]: A list of LangChain Document objects, where each
                            object represents a piece of content from the source.
        """
        pass


class MinioPDFLoader(BaseIngestion):
    """
    A concrete implementation for ingesting PDF documents from a MinIO bucket.
    """
    def __init__(self, bucket_name: str = "raw-pdfs"):
        """
        Initializes the MinioPDFLoader.

        Args:
            bucket_name (str): The name of the MinIO bucket to interact with.
                               Defaults to "raw-pdfs".
        """
        self.bucket_name = bucket_name
        try:
            # Check if all necessary MinIO configurations are present
            if not all([config.MINIO_ENDPOINT, config.MINIO_ACCESS_KEY, config.MINIO_SECRET_KEY]):
                raise ValueError("MinIO configuration is missing. Please check your .env file.")

            self.minio_client = Minio(
                config.MINIO_ENDPOINT,
                access_key=config.MINIO_ACCESS_KEY,
                secret_key=config.MINIO_SECRET_KEY,
                secure=False  # Set to True if using HTTPS
            )
            logger.info("Successfully connected to MinIO server.")
        except Exception as e:
            logger.error(f"Failed to connect to MinIO: {e}")
            raise

    def load(self, source: str) -> List[Document]:
        """
        Loads a single PDF file from the MinIO bucket.

        Args:
            source (str): The object name (filename) of the PDF in the bucket.

        Returns:
            List[Document]: A list of Document objects, where each page of
                            the PDF is a separate Document.
        """
        # A temporary file is needed because PyPDFLoader works with local file paths.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            try:
                logger.info(f"Downloading '{source}' from bucket '{self.bucket_name}'...")
                # Download the PDF from MinIO to the temporary file
                response = self.minio_client.get_object(self.bucket_name, source)
                for d in response.stream(32*1024):
                    tmp_file.write(d)
                tmp_file.flush() # Ensure all data is written to the file
                logger.info(f"Successfully downloaded to temporary file: {tmp_file.name}")

                # Use LangChain's PyPDFLoader on the temporary local file
                loader = PyPDFLoader(tmp_file.name)
                documents = loader.load()
                logger.info(f"Successfully loaded {len(documents)} pages from '{source}'.")
                return documents

            except Exception as e:
                logger.error(f"An error occurred while processing '{source}': {e}")
                return []
            finally:
                # Clean up the temporary file if it was created
                if 'response' in locals() and response:
                    response.close()
                    response.release_conn()
                os.remove(tmp_file.name)
                logger.info(f"Cleaned up temporary file: {tmp_file.name}")


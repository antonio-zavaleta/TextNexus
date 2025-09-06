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
# Import our new preprocessor
from auto_rag.core.preprocessing import BasicTextCleaner


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
    A concrete implementation for ingesting and preprocessing PDF documents
    from a MinIO bucket.
    """
    def __init__(self, bucket_name: str = "raw-pdfs"):
        """
        Initializes the MinioPDFLoader.

        Args:
            bucket_name (str): The name of the MinIO bucket to interact with.
                               Defaults to "raw-pdfs".
        """
        self.bucket_name = bucket_name
        self.preprocessor = BasicTextCleaner() # Instantiate our cleaner
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
        Loads and preprocesses PDF files from the MinIO bucket based on a prefix.

        Args:
            source (str): The object name prefix. Can be a full filename to
                          load a single file, or a prefix (e.g., 'folder/')
                          to load multiple files.

        Returns:
            List[Document]: A list of cleaned Document objects.
        """
        all_documents = []
        logger.info(f"Listing objects in bucket '{self.bucket_name}' with prefix '{source}'...")
        
        objects_to_process = self.minio_client.list_objects(
            self.bucket_name, 
            prefix=source, 
            recursive=True
        )

        pdf_objects = [obj for obj in objects_to_process if obj.object_name.lower().endswith('.pdf')]

        if not pdf_objects:
            logger.warning(f"No PDF files found with prefix '{source}' in bucket '{self.bucket_name}'.")
            return []

        for obj in pdf_objects:
            # A temporary file is needed because PyPDFLoader works with local file paths.
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                try:
                    logger.info(f"Downloading '{obj.object_name}'...")
                    response = self.minio_client.get_object(self.bucket_name, obj.object_name)
                    for d in response.stream(32*1024):
                        tmp_file.write(d)
                    tmp_file.flush()
                    logger.info(f"Downloaded to temporary file: {tmp_file.name}")

                    # Use LangChain's PyPDFLoader on the temporary local file
                    loader = PyPDFLoader(tmp_file.name)
                    documents = loader.load()
                    logger.info(f"Loaded {len(documents)} pages from '{obj.object_name}'.")

                    # *** NEW STEP: Preprocess the loaded documents ***
                    cleaned_documents = self.preprocessor.clean(documents)
                    logger.info(f"Cleaned {len(cleaned_documents)} pages.")
                    all_documents.extend(cleaned_documents)

                except Exception as e:
                    logger.error(f"An error occurred while processing '{obj.object_name}': {e}")
                    # Continue to the next file
                finally:
                    # Clean up resources
                    if 'response' in locals() and response:
                        response.close()
                        response.release_conn()
                    os.remove(tmp_file.name)
                    logger.info(f"Cleaned up temporary file: {tmp_file.name}")

        logger.info(f"Total documents loaded and cleaned from all PDFs: {len(all_documents)}")
        return all_documents


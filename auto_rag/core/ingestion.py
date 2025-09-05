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

# ...existing code...

    def load(self, source: str) -> List[Document]:
        """
        Loads all PDF files from the MinIO bucket whose object names start with the given prefix.

        Args:
            source (str): The prefix to match PDF files in the bucket.

        Returns:
            List[Document]: A list of Document objects aggregated from all matching PDFs.
        """
        all_documents = []
        try:
            logger.info(f"Listing objects in bucket '{self.bucket_name}' with prefix '{source}'...")
            objects = self.minio_client.list_objects(self.bucket_name, prefix=source, recursive=True)
            pdf_objects = [obj for obj in objects if obj.object_name.lower().endswith(".pdf")]

            if not pdf_objects:
                logger.warning(f"No PDF files found with prefix '{source}' in bucket '{self.bucket_name}'.")
                return []

            for obj in pdf_objects:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    try:
                        logger.info(f"Downloading '{obj.object_name}' from bucket '{self.bucket_name}'...")
                        response = self.minio_client.get_object(self.bucket_name, obj.object_name)
                        for d in response.stream(32*1024):
                            tmp_file.write(d)
                        tmp_file.flush()
                        logger.info(f"Successfully downloaded to temporary file: {tmp_file.name}")

                        loader = PyPDFLoader(tmp_file.name)
                        documents = loader.load()
                        logger.info(f"Loaded {len(documents)} pages from '{obj.object_name}'.")
                        all_documents.extend(documents)
                    except Exception as e:
                        logger.error(f"Error processing '{obj.object_name}': {e}")
                    finally:
                        if 'response' in locals() and response:
                            response.close()
                            response.release_conn()
                        os.remove(tmp_file.name)
                        logger.info(f"Cleaned up temporary file: {tmp_file.name}")

            logger.info(f"Total documents loaded from all PDFs: {len(all_documents)}")
            return all_documents

        except Exception as e:
            logger.error(f"An error occurred during batch ingestion: {e}")
            return []
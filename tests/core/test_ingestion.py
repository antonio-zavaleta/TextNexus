import pytest
from unittest.mock import MagicMock, patch, ANY
from io import BytesIO

from langchain_core.documents import Document
from auto_rag.core.ingestion import MinioPDFLoader

# We need this to simulate the object returned by the real minio client
class MockMinioObject:
    def __init__(self, data):
        self._data = BytesIO(data)
    def stream(self, chunk_size):
        while True:
            chunk = self._data.read(chunk_size)
            if not chunk:
                break
            yield chunk
    def close(self):
        pass
    def release_conn(self):
        pass

@pytest.fixture
def mock_minio_client(mocker):
    """A pytest fixture to create a mocked MinIO client and config."""
    # --- FIX: Mock the config variables ---
    # This prevents the ValueError from being raised during initialization
    mocker.patch("auto_rag.config.MINIO_ENDPOINT", "mock-endpoint")
    mocker.patch("auto_rag.config.MINIO_ACCESS_KEY", "mock-access-key")
    mocker.patch("auto_rag.config.MINIO_SECRET_KEY", "mock-secret-key")

    # Create a mock instance of the Minio client
    mock_client = MagicMock()
    
    # Configure the mock's list_objects method to return a predefined list of objects
    mock_object = MagicMock()
    mock_object.object_name = "test.pdf"
    mock_client.list_objects.return_value = [mock_object]

    # Configure the mock's get_object method to return a mock file stream
    mock_pdf_data = b"This is fake PDF content."
    mock_client.get_object.return_value = MockMinioObject(mock_pdf_data)

    # Use mocker.patch to replace the real Minio class with our mock instance
    # whenever it's called within the 'auto_rag.core.ingestion' module.
    mocker.patch("auto_rag.core.ingestion.Minio", return_value=mock_client)
    return mock_client

@pytest.fixture
def mock_pypdf_loader(mocker):
    """A pytest fixture to mock the PyPDFLoader class."""
    # Create a mock instance that the class will return upon instantiation
    mock_instance = MagicMock()
    expected_docs = [
        Document(page_content="Page 1 content", metadata={"source": "test.pdf"}),
        Document(page_content="Page 2 content", metadata={"source": "test.pdf"})
    ]
    mock_instance.load.return_value = expected_docs

    # Patch the PyPDFLoader class itself. When called, it will return our mock_instance.
    mock_class = mocker.patch("auto_rag.core.ingestion.PyPDFLoader", return_value=mock_instance)
    
    # Return the mock *class* so we can make assertions on it.
    return mock_class

def test_minio_pdf_loader_success(mock_minio_client, mock_pypdf_loader):
    """
    Tests the successful loading and processing of a PDF from MinIO.
    This test uses mocks to isolate the loader from external services.
    """
    # 1. Setup: Instantiate our loader. The __init__ method will now receive
    #    the mocked Minio client thanks to our patch.
    loader = MinioPDFLoader(bucket_name="test-bucket")

    # 2. Execution: Call the load method.
    documents = loader.load(source="test.pdf")

    # 3. Assertions:
    
    # Verify that the MinIO client was called correctly
    mock_minio_client.list_objects.assert_called_once_with("test-bucket", prefix="test.pdf", recursive=True)
    mock_minio_client.get_object.assert_called_once_with("test-bucket", "test.pdf")

    # Verify that PyPDFLoader was initialized with the path to a temporary file.
    # The exact path is random, so we use ANY from unittest.mock to check that
    # it was called with any string argument.
    mock_pypdf_loader.assert_called_once_with(ANY)


    # Verify that the final output is the list of documents from our mocked PyPDFLoader
    assert len(documents) == 2
    assert documents[0].page_content == "Page 1 content"
    assert "source" in documents[0].metadata # Check that metadata is preserved

def test_minio_pdf_loader_no_files_found(mock_minio_client):
    """
    Tests that the loader returns an empty list when no PDF files are found.
    """
    # Override the mock for this specific test to return an empty list
    mock_minio_client.list_objects.return_value = []
    
    loader = MinioPDFLoader(bucket_name="test-bucket")
    documents = loader.load(source="nonexistent/")

    # Assert that an empty list is returned
    assert documents == []


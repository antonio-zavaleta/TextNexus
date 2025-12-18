import pytest
from unittest.mock import MagicMock
from langchain_core.documents import Document
from textnexus.core.embedding import BaseEmbeddingModel
from textnexus.core.chunking import SemanticTextSplitter

@pytest.fixture
def mock_embedding_model():
    """
    A pytest fixture that creates a mocked BaseEmbeddingModel.
    This mock will return predictable vectors for our tests.
    """
    mock_model = MagicMock(spec=BaseEmbeddingModel)
    
    # Define the fake vectors our mock model will return for the multi-sentence test.
    fake_embeddings = [
        [1.0, 0.0, 0.0],  # Sentence 1
        [0.9, 0.1, 0.0],  # Sentence 2 (similar to 1)
        [0.0, 1.0, 0.0],  # Sentence 3 (different from 2)
        [0.0, 0.9, 0.1],  # Sentence 4 (similar to 3)
        [0.1, 0.0, 0.9],  # Sentence 5 (different from 4)
    ]
    mock_model.create_embeddings.return_value = fake_embeddings
    
    return mock_model

def test_semantic_splitter_creates_correct_chunks(mock_embedding_model, mocker):
    """
    Tests the core logic of the semantic splitter.
    It verifies that a split is created where the cosine similarity
    between sentence embeddings drops below the threshold.
    """
    # 1. Setup
    splitter = SemanticTextSplitter(embedding_model=mock_embedding_model, similarity_threshold=0.8)
    
    text = "Sentence one. Sentence two. Sentence three is different. Sentence four is similar. Sentence five is the last one."
    doc = Document(page_content=text, metadata={"source": "test.pdf"})

    # Mock the nltk.sent_tokenize function for this test.
    mock_sentences = [
        "Sentence one.",
        "Sentence two.",
        "Sentence three is different.",
        "Sentence four is similar.",
        "Sentence five is the last one."
    ]
    mocker.patch("textnexus.core.chunking.nltk.sent_tokenize", return_value=mock_sentences)


    # 2. Execution
    chunks = splitter.split_documents([doc])

    # 3. Assertions
    # We expect three chunks based on our fake embeddings.
    assert len(chunks) == 3
    assert chunks[0].page_content == "Sentence one. Sentence two."
    assert chunks[1].page_content == "Sentence three is different. Sentence four is similar."
    assert chunks[2].page_content == "Sentence five is the last one."
    assert chunks[0].metadata["source"] == "test.pdf"

def test_semantic_splitter_handles_empty_document(mock_embedding_model, mocker):
    """Tests that the splitter handles an empty document without errors."""
    splitter = SemanticTextSplitter(embedding_model=mock_embedding_model)
    doc = Document(page_content="", metadata={"source": "empty.pdf"})
    
    # Mock the tokenizer to return an empty list for empty text
    mocker.patch("textnexus.core.chunking.nltk.sent_tokenize", return_value=[])
    
    chunks = splitter.split_documents([doc])
    
    assert len(chunks) == 0

def test_semantic_splitter_handles_single_sentence(mock_embedding_model, mocker):
    """Tests that a document with one sentence results in a single chunk."""
    splitter = SemanticTextSplitter(embedding_model=mock_embedding_model)
    doc = Document(page_content="This is a single sentence.", metadata={"source": "single.pdf"})
    
    # Mock the tokenizer to return a single sentence
    mocker.patch("textnexus.core.chunking.nltk.sent_tokenize", return_value=["This is a single sentence."])
    
    # --- THE FIX IS HERE ---
    # Explicitly re-configure the mock to return only one vector for this specific test.
    mock_embedding_model.create_embeddings.return_value = [[1.0, 0.0, 0.0]]
    
    chunks = splitter.split_documents([doc])
    
    assert len(chunks) == 1
    assert chunks[0].page_content == "This is a single sentence."


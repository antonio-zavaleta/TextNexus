import pytest
from textnexus.llm.llama_connector import Llama3Connector

@pytest.fixture(scope="module")
def connector() -> Llama3Connector:
    """Provides a Llama3Connector instance for testing.

    Returns:
        Llama3Connector: An instance of the connector.
    """
    return Llama3Connector()

def test_query_success(mocker, connector: Llama3Connector):
    """Test that Llama3Connector.query makes the correct API call and returns the expected response.

    Args:
        mocker: The pytest-mock fixture.
        connector: The Llama3Connector instance from the fixture.
    """
    mock_response = {"message": {"content": "Mocked Llama 3 response"}}
    mock_chat = mocker.patch('ollama.chat', return_value=mock_response)

    prompt = "What is RAG?"
    context = "Retrieval-Augmented Generation"
    expected_full_prompt = (
        "You are a helpful AI assistant. Use the provided context "
        "to answer the user's question. If you don't know the answer, "
        "just say that you don't know."
        f"\n\nContext: {context}"
    )

    result = connector.query(prompt=prompt, context=context)

    mock_chat.assert_called_once_with(
        model='llama3',
        messages=[
            {'role': 'system', 'content': expected_full_prompt},
            {'role': 'user', 'content': prompt}
        ]
    )
    assert result == "Mocked Llama 3 response"

def test_query_exception(mocker, connector: Llama3Connector):
    """Test that Llama3Connector.query raises RuntimeError when the Ollama API call fails.

    Args:
        mocker: The pytest-mock fixture.
        connector: The Llama3Connector instance from the fixture.
    """
    mocker.patch('ollama.chat', side_effect=Exception("Connection error"))

    with pytest.raises(RuntimeError) as exc_info:
        connector.query(prompt="What is RAG?", context="Retrieval-Augmented Generation")

    assert "Failed to query Llama 3 model" in str(exc_info.value)
    assert "Connection error" in str(exc_info.value)
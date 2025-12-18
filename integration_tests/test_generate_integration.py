import pytest
from typer.testing import CliRunner
from textnexus.cli import app

@pytest.fixture
def cli_runner():
    """Provides a Typer CliRunner instance for CLI integration testing."""
    return CliRunner()

def test_generate_command_success(mocker, cli_runner):
    """Test the 'generate' CLI command for successful LLM-based RAG generation.

    Mocks the Ollama API and the retrieval utility to simulate a successful
    end-to-end command execution.

    Args:
        mocker: The pytest-mock fixture.
        cli_runner: The Typer CliRunner fixture.
    """
    # Mock the return value of the retrieval utility function

    # Mock the QueryEngine.query method
    mocker.patch(
        "textnexus.core.query_engine.QueryEngine.query",
        return_value={
            "results": [
                {"content": "This is a relevant document chunk.", "metadata": {}},
                {"content": "This is another relevant chunk.", "metadata": {}},
            ],
            "count": 2
        }
    )

    # Mock the Ollama API response
    mock_ollama_chat = mocker.patch(
        "ollama.chat",
        return_value={"message": {"content": "Mocked LLM response"}}
    )
    
    # Invoke the CLI command
    result = cli_runner.invoke(
        app,
        ["generate", "What is RAG?", "--model", "llama3", "--top-k", "2"]
    )
    print(result.output)  # <-- Add here

    # Assertions
    assert result.exit_code == 0
    assert "Mocked LLM response" in result.output
    assert "RAG Generation" in result.output
    mock_ollama_chat.assert_called_once()

def test_generate_command_invalid_model(cli_runner):
    """Test the 'generate' CLI command with an unsupported model name.

    Verifies that the CLI command fails gracefully and outputs the correct error message.

    Args:
        cli_runner: The Typer CliRunner fixture.
    """
    result = cli_runner.invoke(
        app,
        ["generate", "What is RAG?", "--model", "unsupported_model"]
    )
    print(result.output)  # <-- Add here
    
    assert result.exit_code != 0
    assert "Error: Unsupported model 'unsupported_model'." in result.output
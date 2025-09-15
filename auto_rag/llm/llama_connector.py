from typing import Optional
import ollama
from .lm_connector import LLMConnector

class Llama3Connector(LLMConnector):
    """Concrete connector for interacting with a local Llama 3 model via the Ollama API.

    This class provides an implementation of the LLMConnector interface for
    querying a Llama 3 model running locally with Ollama.
    """

    def __init__(self, model_name: Optional[str] = "llama3"):
        """Initializes the Llama3Connector.

        Args:
            model_name: The name of the Llama 3 model to use with Ollama. Defaults to "llama3".
        """
        self.model_name = model_name

    def query(self, prompt: str, context: str) -> str:
        """Generates a response from the Llama 3 model using Ollama.

        Constructs a prompt that includes a system message, the provided context,
        and the user's prompt, then sends it to the local Llama 3 model.

        Args:
            prompt: The user's query or instruction.
            context: The retrieved context from the knowledge base to
                augment the prompt.

        Returns:
            The generated response from the Llama 3 model.

        Raises:
            RuntimeError: If the Ollama API call fails.
        """
        try:
            messages = [
                {"role": "system", "content": (
                    "You are a helpful AI assistant. Use the provided context "
                    "to answer the user's question. If you don't know the answer, "
                    "just say that you don't know."
                    f"\n\nContext: {context}"
                )},
                {"role": "user", "content": prompt}
            ]
            response = ollama.chat(
                model=self.model_name,
                messages=messages
            )
            return response["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Failed to query Llama 3 model: {e}") from e
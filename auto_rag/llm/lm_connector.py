from abc import ABC, abstractmethod


class LLMConnector(ABC):
    """Abstract base class for all LLM connectors.

    Defines the standard interface for interacting with different LLM providers,
    ensuring code portability and interchangeability.
    """

    @abstractmethod
    def query(self, prompt: str, context: str) -> str:
        """Generates a response from the LLM based on a prompt and context.

        Args:
            prompt: The user's query or instruction.
            context: The retrieved context from the knowledge base to
                augment the prompt.

        Returns:
            The generated response from the LLM.
        """
        pass
import re
from abc import ABC, abstractmethod
from typing import List

from langchain_core.documents import Document


class BasePreprocessor(ABC):
    """
    Abstract base class for all text preprocessing strategies.
    """

    @abstractmethod
    def clean(self, documents: List[Document]) -> List[Document]:
        """
        Cleans the text content of a list of Document objects.

        Args:
            documents (List[Document]): The documents to be cleaned.

        Returns:
            List[Document]: The cleaned documents.
        """
        pass


class BasicTextCleaner(BasePreprocessor):
    """
    A basic text cleaner that performs common preprocessing tasks on documents.
    """

    def clean(self, documents: List[Document]) -> List[Document]:
        """
        Applies a series of cleaning steps to the page_content of each document.

        Args:
            documents (List[Document]): The list of documents to clean.

        Returns:
            List[Document]: The list of documents with cleaned text.
        """
        cleaned_documents = []
        for doc in documents:
            cleaned_text = doc.page_content

            # 1. Merge words that are hyphenated across line breaks
            cleaned_text = self._merge_hyphenated_words(cleaned_text)
            
            # 2. Remove common PDF headers and footers
            cleaned_text = self._remove_headers_footers(cleaned_text)

            # 3. Normalize whitespace
            cleaned_text = self._normalize_whitespace(cleaned_text)

            # Create a new Document with the cleaned text, preserving metadata
            cleaned_doc = Document(page_content=cleaned_text, metadata=doc.metadata)
            cleaned_documents.append(cleaned_doc)

        return cleaned_documents

    def _merge_hyphenated_words(self, text: str) -> str:
        """
        Finds words split with a hyphen across a newline and merges them.
        Example: "state-of-the-\nart" becomes "state-of-the-art".
        """
        # THE FIX IS HERE: Changed r'\1\2' to r'\1-\2'
        return re.sub(r'(\w+)-\n(\w+)', r'\1-\2', text)

    def _remove_headers_footers(self, text: str) -> str:
        """
        Removes simple, common headers and footers like page numbers.
        This is a basic heuristic and may need to be improved for specific document layouts.
        Example: "Page 1 of 12"
        """
        # This regex removes lines that consist of 'Page', optional whitespace,
        # one or more digits, optional 'of', and more digits.
        # The `re.MULTILINE` flag allows `^` and `$` to match the start/end of lines.
        text = re.sub(r'^\s*Page\s*\d+\s*(of\s*\d+)?\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """
        Replaces multiple whitespace characters with a single space and
        removes leading/trailing whitespace.
        """
        # Replace multiple newlines with a single one, but only after cleaning headers/footers
        text = re.sub(r'\n\s*\n', '\n', text)
        # Replace multiple spaces/tabs with a single space
        text = re.sub(r'[ \t]+', ' ', text)
        # Remove leading/trailing whitespace from the whole text
        return text.strip()


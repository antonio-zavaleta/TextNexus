import pytest
from langchain_core.documents import Document
from textnexus.core.preprocessing import BasicTextCleaner

# A pytest fixture to create a reusable instance of our cleaner for tests
@pytest.fixture
def cleaner():
    """Provides a BasicTextCleaner instance for testing."""
    return BasicTextCleaner()

def test_merge_hyphenated_words(cleaner):
    """
    Tests that words hyphenated across a newline are correctly merged.
    """
    dirty_text = "This is a state-of-the-\nart example."
    expected_clean_text = "This is a state-of-the-art example."
    actual_clean_text = cleaner._merge_hyphenated_words(dirty_text)
    assert actual_clean_text == expected_clean_text

@pytest.mark.parametrize("dirty_text, expected_clean_text", [
    ("Page 5", ""),
    ("Some text\nPage 5 of 12\nSome more text", "Some text\n\nSome more text"),
    ("page 12", ""),
    ("Text without page numbers", "Text without page numbers"),
])
def test_remove_headers_footers(cleaner, dirty_text, expected_clean_text):
    """
    Tests the removal of common page number footers using parameterized inputs.
    """
    actual_clean_text = cleaner._remove_headers_footers(dirty_text)
    # We strip the result to handle cases where only whitespace might be left
    assert actual_clean_text.strip() == expected_clean_text.strip()

@pytest.mark.parametrize("dirty_text, expected_clean_text", [
    ("This has   too   many   spaces.", "This has too many spaces."),
    ("This has\n\n\nmultiple newlines.", "This has\nmultiple newlines."),
    ("\tLeading and trailing whitespace\t ", "Leading and trailing whitespace"),
])
def test_normalize_whitespace(cleaner, dirty_text, expected_clean_text):
    """
    Tests whitespace normalization using parameterized inputs.
    """
    actual_clean_text = cleaner._normalize_whitespace(dirty_text)
    assert actual_clean_text == expected_clean_text

def test_full_clean_integration(cleaner):
    """
    Tests that all cleaning steps are applied correctly in the main clean() method.
    """
    # Create a dummy Document object to test with
    dirty_doc = Document(
        page_content="Here is some hyphenated-\ncontent.\n\n   Lots of extra space.\n\nPage 1 of 1"
    )
    expected_clean_content = "Here is some hyphenated-content.\n Lots of extra space."

    # The clean method expects a list of documents
    cleaned_docs = cleaner.clean([dirty_doc])

    # Assert that we got one document back and its content is correct
    assert len(cleaned_docs) == 1
    assert cleaned_docs[0].page_content == expected_clean_content

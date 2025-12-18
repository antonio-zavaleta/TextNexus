import pytest
from unittest.mock import MagicMock
from langchain_core.documents import Document
from textnexus.evaluation.retrieval import RetrievalEvaluator

@pytest.fixture
def mock_query_engine():
    """Mock QueryEngine that returns controllable results."""
    return MagicMock()

def test_evaluator_perfect_scores(mock_query_engine):
    """Test case where all retrievals are perfect (rank 1)."""
    # 2 Questions
    dataset = [
        {"question": "Q1", "ground_truth_context_files": ["doc1.pdf"]},
        {"question": "Q2", "ground_truth_context_files": ["doc2.pdf"]}
    ]
    
    # Mock results: Rank 1 matches for both
    mock_query_engine.query.side_effect = [
        {"results": [{"content": "...", "metadata": {"source": "/path/to/doc1.pdf"}}]},
        {"results": [{"content": "...", "metadata": {"source": "/path/to/doc2.pdf"}}]}
    ]
    
    evaluator = RetrievalEvaluator(mock_query_engine)
    metrics = evaluator.evaluate(dataset, top_k=1)
    
    assert metrics["hit_rate"] == 1.0, "Hit Rate should be 1.0"
    assert metrics["mrr"] == 1.0, "MRR should be 1.0"

def test_evaluator_mixed_scores(mock_query_engine):
    """Test case with mixed results (1 hit at rank 2, 1 miss)."""
    # 2 Questions
    dataset = [
        {"question": "Q1", "ground_truth_context_files": ["doc1.pdf"]}, # Found at rank 2
        {"question": "Q2", "ground_truth_context_files": ["doc2.pdf"]}  # Not found
    ]
    
    # Mock results
    mock_query_engine.query.side_effect = [
        {"results": [
            {"content": "...", "metadata": {"source": "wrong.pdf"}},
            {"content": "...", "metadata": {"source": "doc1.pdf"}} # Rank 2
        ]},
        {"results": [
            {"content": "...", "metadata": {"source": "other.pdf"}} # Miss
        ]}
    ]
    
    evaluator = RetrievalEvaluator(mock_query_engine)
    metrics = evaluator.evaluate(dataset, top_k=2)
    
    # Hit Rate: 1 out of 2 found = 0.5
    assert metrics["hit_rate"] == 0.5
    
    # MRR: (1/2 + 0) / 2 = 0.25
    assert metrics["mrr"] == 0.25

def test_evaluator_partial_filename_match(mock_query_engine):
    """Test that it matches filename even if path is different."""
    dataset = [{"question": "Q1", "ground_truth_context_files": ["target.pdf"]}]
    
    mock_query_engine.query.return_value = {
        "results": [{"content": "...", "metadata": {"source": "/abs/path/to/target.pdf"}}]
    }
    
    evaluator = RetrievalEvaluator(mock_query_engine)
    metrics = evaluator.evaluate(dataset)
    assert metrics["hit_rate"] == 1.0

def test_evaluator_no_results(mock_query_engine):
    """Test handling of empty results."""
    dataset = [{"question": "Q1", "ground_truth_context_files": ["doc.pdf"]}]
    mock_query_engine.query.return_value = {"results": []}
    
    evaluator = RetrievalEvaluator(mock_query_engine)
    metrics = evaluator.evaluate(dataset)
    
    assert metrics["hit_rate"] == 0.0
    assert metrics["mrr"] == 0.0

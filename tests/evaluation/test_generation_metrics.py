
import pytest
from unittest.mock import Mock, MagicMock
from textnexus.evaluation.generation import GenerationEvaluator
from textnexus.evaluation.judges import BaseJudge

# Mocks
@pytest.fixture
def mock_query_engine():
    engine = Mock()
    # Setup default behavior or leave for individual tests
    return engine

@pytest.fixture
def mock_judge():
    judge = Mock(spec=BaseJudge)
    return judge

@pytest.fixture
def sample_dataset():
    return [
        {
            "question": "What is the capital of France?",
            "ground_truth_answer": "Paris",
            "type": "text"
        },
        {
            "question": "What is 2+2?",
            "ground_truth_answer": "4",
            "type": "text"
        }
    ]

def test_generation_evaluator_initialization(mock_query_engine, mock_judge):
    evaluator = GenerationEvaluator(query_engine=mock_query_engine, llm_judge=mock_judge)
    assert evaluator.query_engine == mock_query_engine
    assert evaluator.llm_judge == mock_judge

def test_evaluate_perfect_scores(mock_query_engine, mock_judge, sample_dataset):
    # Setup QueryEngine to return perfect answers
    mock_query_engine.query.side_effect = [
        ("Context about France", "Paris"), # Q1
        ("Context about math", "4")      # Q2
    ]
    
    # Setup Judge to return 1.0 for everything
    # We assume check_faithfulness and check_correctness return (score, reason) or just score.
    # Let's assume just score for now based on design doc: "Score (0-1)"
    mock_judge.check_faithfulness.return_value = 1.0
    mock_judge.check_correctness.return_value = 1.0
    
    evaluator = GenerationEvaluator(mock_query_engine, mock_judge)
    results = evaluator.evaluate(sample_dataset)
    
    assert results["faithfulness"] == 1.0
    assert results["answer_correctness"] == 1.0
    assert results["total_samples"] == 2
    
    # Verify calls
    assert mock_query_engine.query.call_count == 2
    assert mock_judge.check_faithfulness.call_count == 2
    assert mock_judge.check_correctness.call_count == 2

def test_evaluate_mixed_scores(mock_query_engine, mock_judge, sample_dataset):
    # Setup QueryEngine
    mock_query_engine.query.side_effect = [
        ("Context about France", "London"), # Q1: Wrong answer, maybe hallucinated?
        ("Context about math", "4")         # Q2: Correct
    ]
    
    # Setup Judge
    # Q1: Faithfulness=0.5 (hallucinated), Correctness=0.0 (wrong)
    # Q2: Faithfulness=1.0, Correctness=1.0
    mock_judge.check_faithfulness.side_effect = [0.5, 1.0]
    mock_judge.check_correctness.side_effect = [0.0, 1.0]
    
    evaluator = GenerationEvaluator(mock_query_engine, mock_judge)
    results = evaluator.evaluate(sample_dataset)
    
    # Avg Faithfulness: (0.5 + 1.0) / 2 = 0.75
    # Avg Correctness: (0.0 + 1.0) / 2 = 0.5
    assert results["faithfulness"] == 0.75
    assert results["answer_correctness"] == 0.5

def test_evaluate_empty_dataset(mock_query_engine, mock_judge):
    evaluator = GenerationEvaluator(mock_query_engine, mock_judge)
    results = evaluator.evaluate([])
    
    assert results["faithfulness"] == 0.0
    assert results["answer_correctness"] == 0.0
    assert results["total_samples"] == 0

# User Story C.2: Implement Retrieval Metric Tests

## Goal Description
Implement an automated mechanism to measure the performance of our retrieval system. We will calculate widely accepted information retrieval metrics:
- **Hit Rate**: % of queries where the correct document appears in the top-k results.
- **MRR (Mean Reciprocal Rank)**: Average of (1 / rank) of the first correct result.

## User Review Required
- **Metric Definitions**:
    - Hit Rate: Is the `ground_truth_context_files` present in the retrieved chunks' metadata?
- **Golden Dataset**: Uses the JSON we created in C.1.

## Proposed Changes

### Core Logic
#### [NEW] `textnexus/evaluation/__init__.py`
- Package initialization.

#### [NEW] [textnexus/evaluation/retrieval.py](file:///home/antonio/Documents/py-projects/TextNexus/textnexus/evaluation/retrieval.py)
- `RetrievalEvaluator` class.
    - `__init__(query_engine)`
    - `evaluate(dataset: List[dict], top_k=5) -> dict`
        - Iterates through the golden dataset.
        - Runs `query_engine.query(question)`.
        - Checks if any retrieved `source` matches `ground_truth_context_files`.
        - Returns `{"hit_rate": float, "mrr": float}`.

## Verification Plan
### Automated Tests
- **New Unit Test**: `tests/evaluation/test_retrieval_metrics.py`
    - Mock the Query Engine to return known results.
    - Verify metric calculations (e.g., if rank=1, MRR should be 1.0).

### Manual Verification
- **Script**: Run evaluation against the actual `attention_is_all_you_need.pdf` index.

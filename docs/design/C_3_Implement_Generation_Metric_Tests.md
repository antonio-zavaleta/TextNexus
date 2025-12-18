# User Story C.3: Implement Generation Metric Tests

## Goal Description
Implement "LLM-as-a-Judge" metrics to evaluate the quality of the generated answers. Evaluating generation is ensuring that the answer is:
1.  **Faithful**: derived *only* from the context (no hallucination).
2.  **Correct**: matches the `ground_truth_answer` in meaning.

## User Review Required
- **LLM Dependency**: This requires an LLM to act as the judge. We will design `GenerationEvaluator` to accept an `llm_judge`. The system will **default to Ollama** to ensure it works out-of-the-box for users without paid API keys, but will support OpenAI/Gemini if configured.
- **Metric Definitions**:
    - **Faithfulness**: (Context, Answer) -> Score (0-1).
    - **Answer Correctness**: (Answer, Ground Truth) -> Score (0-1).

## Proposed Changes

### Core Logic
#### [NEW] [textnexus/evaluation/generation.py](file:///home/antonio/Documents/py-projects/TextNexus/textnexus/evaluation/generation.py)
- `GenerationEvaluator` class.
    - `__init__(query_engine, llm_judge)`
    - `evaluate(dataset) -> dict`
        - For each Q in dataset:
            - context, answer = query_engine.query(Q)
            - score_faith = llm_judge.check_faithfulness(context, answer)
            - score_correct = llm_judge.check_correctness(answer, ground_truth)
        - Return average scores.

#### [NEW] [textnexus/evaluation/judges.py](file:///home/antonio/Documents/py-projects/TextNexus/textnexus/evaluation/judges.py)
- `BaseJudge` and `OllamaJudge` classes.
    - Encapsulate the prompt engineering for grading.

## Verification Plan
### Automated Tests
- **New Unit Test**: `tests/evaluation/test_generation_metrics.py`
    - Mock the LLM judge responses.
    - Verify score aggregation.

### Manual Verification
- **Script**: Run `verify_c_3_gen_eval.py` using Ollama (e.g. `llama3`) as the judge on our Golden Dataset.

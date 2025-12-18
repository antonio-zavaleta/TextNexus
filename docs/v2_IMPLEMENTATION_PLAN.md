# Phase 2: Implementation Plan & Sprint Schedule

## Goal
Implement "TextNexus V2.0: RAG 2.0 & Evaluation" with a focus on Robust Document Understanding, Hybrid Retrieval, and API Readiness.

## Modus Operandi
We will follow a strict **TDD by User Story** workflow for each item in the Sprint.

1.  **Branch**: Create a feature branch from `develop`.
    *   `git switch -c feature/<ID>-<short-desc> develop`
2.  **TDD Cycle**:
    *   **RED**: Write a failing unit test in `tests/`.
    *   **GREEN**: Write the minimal code to pass the test.
    *   **REFACTOR**: Clean up and optimize.
3.  **Commit**: Commit changes with a descriptive message.
    *   `git commit -m "feat: <description> (<ID>)"`
4.  **Push**: Push the feature branch to origin.
    *   `git push -u origin feature/...`
5.  **Review & Merge**: Stop and notify the User. The User will review and merge the PR on GitHub.
6.  **Sync**: Switch back to `develop` and pull the merged changes before starting the next story.
    *   `git switch develop && git pull origin develop`

7.  **Testing Hygiene**: For manual verification and integration tests, **always recreate the vector DB** to ensure test data matches the expected context and avoid stale embeddings.

## Sprint Schedule

### Sprint 1: API & Architecture (Refactoring)
**Focus**: Decoupling logic from the CLI to enable a programmatic API. This provides a clean foundation for the complex logic in subsequent sprints.
- [x] **[D.1] Refactor Ingestion Pipeline to API**
  - *Goal*: Extract `IngestionPipeline` as a reusable class.
  - *Dependencies*: None
- [x] **[D.2] Refactor Query Engine to API**
  - *Goal*: Extract `QueryEngine` as a reusable class.
  - *Dependencies*: None
- [x] **[D.3] Create Client Interface Package**
  - *Goal*: Create a top-level `textnexus` package and `init` file.
  - *Dependencies*: D.1, D.2

### Sprint 2: Foundation & Storage
**Focus**: Establishing test baselines and updating storage for sparse vectors.
- [x] **[C.1] Create Standardized Test Dataset** (High Risk)
  - *Goal*: Create a ground-truth dataset with table/image-specific questions.
  - *Dependencies*: None
- [x] **[B.1] Integrate Sparse Indexing with Storage**
  - *Goal*: Update SQLite schema for sparse vectors.
  - *Dependencies*: None

### Sprint 3: Ingestion Core & Metrics
**Focus**: Implementing the new visual-aware ingestion pipeline and setting up evaluation metrics.
- [x] **[A.1] Implement GraniteDoclingLoader** (High Risk)
  - *Goal*: Use Docling to ingest PDFs, converting visuals to text/markdown.
  - *Dependencies*: C.1 (Sprint 2)
- [x] **[C.2] Implement Retrieval Metric Tests**
  - *Goal*: Automated tests for retrieval quality (Hit Rate, MRR).
  - *Dependencies*: C.1 (Sprint 2)
- [x] **[C.3] Implement Generation Metric Tests**
  - *Goal*: Automated tests for answer quality using LLM-as-a-judge.
  - *Dependencies*: C.1 (Sprint 2)
  - *Note*: Gemini Judge temporarily disabled due to API errors (404). Ollama (default) and OpenAI are functional.

### Sprint 4: Advanced Ingestion
**Focus**: refining how we split documents and exposing options in the CLI.
- **[A.2] Create StructuredTextSplitter**
  - *Goal*: Smart chunking that preserves markdown tables and metadata.
  - *Dependencies*: A.1 (Sprint 3)
- **[A.3] Update index CLI for VLM Choice**
  - *Goal*: Allow users to select the new ingestion method via CLI.
  - *Dependencies*: A.1 (Sprint 3), A.2 (Sprint 4)

### Sprint 5: Hybrid Retrieval
**Focus**: Combining dense and sparse search for better results.
- **[B.2] Develop HybridRetriever**
  - *Goal*: Implement Reciprocal Rank Fusion (RRF) to merge search results.
  - *Dependencies*: B.1 (Sprint 2), A.3 (Sprint 4)
- **[B.3] Update query and generate CLIs**
  - *Goal*: Expose hybrid search options in the query/generate commands.
  - *Dependencies*: B.2 (Sprint 5)

### Sprint 6: Evaluation & Benchmarking
**Focus**: Objective comparison of system performance.
- **[E.1] Create Evaluation Pipeline**
  - *Goal*: Build a script to run RAGAS metrics (Faithfulness, Answer Relevance) against the Golden Dataset.
  - *Dependencies*: C.1 (Dataset)
- **[E.2] Comparative Benchmark (V1 vs V2)**
  - *Goal*: Run A/B test (PyPDF+Dense vs Docling+Hybrid) and report metric deltas.
  - *Dependencies*: E.1, A.1 (Docling), B.2 (Hybrid)

## Verification Plan

### Automated Tests
- **Unit Tests**:
  - `pytest tests/core/test_ingestion_pipeline.py` (New in Sprint 1)
  - `pytest tests/core/test_storage.py` (Verify B.1 sparse support)
  - `pytest tests/evaluation/` (New C.2/C.3 metric tests)
- **Integration Tests**:
  - `pytest integration_tests/` (Full pipeline runs)

### Manual Verification
- **API Usability**: Verify `import textnexus` works in a standalone python script (Sprint 1).
- **Docling Verification**: Visually inspect processed chunks from a complex PDF.

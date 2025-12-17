# User Story D.2: Refactor Query Engine to API

## Goal Description
Decouple the query logic from the CLI command (`auto_rag/commands/query.py`) into a reusable core class `QueryEngine`. This enables programmatic access to the retrieval engine (User Story D.1 & D.2) while maintaining existing CLI functionality.
This change also introduces a robust "Human-in-the-Loop" verification phase to prevent regressions.

## User Review Required
> [!IMPORTANT]
> **Verification Strategy**: We are introducing a manual "E2E" verification step.
> You will be asked to run `python scripts/verify_d_2_api.py` and specific CLI commands before we merge.

## Proposed Changes

### Core Logic
#### [NEW] [query_engine.py](file:///home/antonio/Documents/py-projects/TextNexus/auto_rag/core/query_engine.py)
- **Class**: `QueryEngine`
- **Methods**: 
    - `__init__(self, vector_store, embedding_model)`: Dependency injection.
    - `query(self, query_text: str, top_k: int) -> Dict`: Returns a structured result (e.g., `{"results": [...], "count": 3}`).
- Logic moved here from `utils/retrieval.py`.

### CLI Commands
#### [MODIFY] [query.py](file:///home/antonio/Documents/py-projects/TextNexus/auto_rag/commands/query.py)
- Instantiate `QueryEngine` from `ctx.obj`.
- Call `QueryEngine.query()`.
- Format the returned structured object for `rich` console output.

#### [MODIFY] [generate.py](file:///home/antonio/Documents/py-projects/TextNexus/auto_rag/commands/generate.py)
- Instantiate `QueryEngine`.
- Use `QueryEngine.query()` to fetch context for the LLM.

### Utilities
#### [DELETE] [retrieval.py](file:///home/antonio/Documents/py-projects/TextNexus/auto_rag/utils/retrieval.py)
- Function `retrieve_relevant_chunks` is deprecated/removed in favor of `QueryEngine`.

## Verification Plan

### Automated Tests
- **Unit Test**: `pytest tests/core/test_query_engine.py`
    - Verify `QueryEngine` initializes correctly.
    - Verify `query()` returns the expected dictionary structure.

### Manual Verification (Human-in-the-Loop)
- **API Script**: `python scripts/verify_d_2_api.py`
    - [NEW] Script created to import `textnexus` (or internal modules) and run a query programmatically.
- **CLI Check**: 
    - `textnexus query "test query" --top-k 1`
    - Verify output matches previous behavior (Rich table).

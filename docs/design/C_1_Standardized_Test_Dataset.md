# User Story D.3: Create Client Interface Package

## Goal Description
Transform the project into a proper Python package named `textnexus`. This involves renaming the existing `textnexus` directory to `textnexus` and exposing the high-level classes (`IngestionPipeline`, `QueryEngine`) in the top-level `__init__.py`. This enables external developers to simply `import textnexus` and use the core functionality programmatically.

## User Review Required
> [!WARNING]
> **Major Refactor**: This story involves renaming the core source directory (`textnexus` -> `textnexus`). This will touch potentially **every file** in the codebase to update imports.

## Proposed Changes

### Package Structure
#### [RENAME] `textnexus/` -> `textnexus/`
- The root source directory will be renamed to match the desired package name.

#### [MODIFY] [pyproject.toml](file:///home/antonio/Documents/py-projects/TextNexus/pyproject.toml)
- Update `name` to `textnexus`.
- Update `packages` to `[{include = "textnexus"}]`.
- Update `[tool.poetry.scripts]` to point to `textnexus.cli:app`.

#### [NEW] [__init__.py](file:///home/antonio/Documents/py-projects/TextNexus/textnexus/__init__.py) (will be `textnexus/__init__.py`)
- Import and expose:
    - `IngestionPipeline` (from `.core.ingestion_pipeline`)
    - `QueryEngine` (from `.core.query_engine`)

### Import Updates
- **Global**: Find and replace all occurrences of `from textnexus` with `from textnexus` and `import textnexus` with `import textnexus` in:
    - `tests/`
    - `textnexus/` (internal modules)
    - `scripts/`

## Verification Plan

### Automated Tests
- **Full Suite**: `pytest`
    - Must pass all existing tests after the rename.
- **Import Test**:
    - verify `pytest` can collect tests (requires correct package installed/linked).

### Manual Verification
- **Verification Script**: Create `scripts/verify_d_3_package.py`:
    ```python
    import textnexus
    print(f"TextNexus version: {textnexus.__version__}")
    
    pipeline = textnexus.IngestionPipeline(...)
    engine = textnexus.QueryEngine(...)
    print("Imports successful!")
    ```

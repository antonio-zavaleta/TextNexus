# User Story A.1: Implement Docling Ingestion

## Goal Description
Enhance the ingestion capabilities by integrating **Docling** (via `docling` library or Granite wrapper). This replaces or augments the simple `pypdf` loader, allowing for better extraction of **Tables** and **Document Structure** (headers, sections).

## User Review Required
- **Dependency**: We need to add `docling` or `docling-core` to `pyproject.toml`.
- **Loader Interface**: I will create a new class `DoclingLoader` that adheres to the langchain `BaseLoader` interface (or returns LangChain Documents) so it's plug-and-play with our pipeline.

## Proposed Changes

### Configuration
#### [MODIFY] [pyproject.toml](file:///home/antonio/Documents/py-projects/TextNexus/pyproject.toml)
- Add `docling = "^..."` (checking latest version).

### Core Logic
#### [NEW] [textnexus/core/loaders.py](file:///home/antonio/Documents/py-projects/TextNexus/textnexus/core/loaders.py)
- Create `DoclingLoader` class.
    - Method `load(file_path)` -> `List[Document]`.
    - Functionality: Parse PDF, converting Docling's rich structure into LangChain `Document` objects with metadata (e.g. `{"type": "table"}`).

#### [MODIFY] [textnexus/core/pipeline.py](file:///home/antonio/Documents/py-projects/TextNexus/textnexus/core/pipeline.py)
- Update `IngestionPipeline.__init__`:
    - Accept `loader_type: str = "pypdf"`.
    - If "docling", instantiate `DoclingLoader`.

## Verification Plan
### Automated Tests
- **New Unit Test**: `tests/core/test_ingestion_docling.py`
    - Mock `docling` to avoid slow model downloads during unit test.
    - Verify it produces Documents with correct metadata.

### Manual Verification
- **Script**: Run `textnexus ingest` (or script) on the Golden Dataset PDF using Docling loader. inspect output to see if tables are captured as text blocks.

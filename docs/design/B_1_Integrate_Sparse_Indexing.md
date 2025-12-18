# User Story B.1: Integrate Sparse Indexing with Storage

## Goal Description
Enable the `SQLiteVectorStore` to store **Sparse Vectors** (e.g., BM25 or Splade weights). This is a prerequisite for **Hybrid Search** (Sprint 5). We will update the database schema to store a JSON representation of sparse vectors alongside the text chunks and dense vectors.

## User Review Required
- **Storage Format**: Storing sparse vectors as a JSON text column (`{"token_id": weight, ...}`) in SQLite. This is simple and sufficient for MVP. Optimization (compression) can come later.

## Proposed Changes

### Database Schema
#### [MODIFY] [textnexus/core/storage.py](file:///home/antonio/Documents/py-projects/TextNexus/textnexus/core/storage.py)
- Update `_initialize_db`:
    - Add `sparse_vector TEXT` column to the `chunks` table.

### Code Changes
#### [MODIFY] [textnexus/core/storage.py](file:///home/antonio/Documents/py-projects/TextNexus/textnexus/core/storage.py)
- **`add_documents`**: Accept an optional list of `sparse_vectors`.
    - If provided, verify length matches `documents`.
    - Serialize to JSON and insert into the `chunks` table.
- **`query`**: (Preserve existing dense functionality, B.2 will add hybrid logic).

## Verification Plan
### Automated Tests
- **New Unit Test**: `tests/core/test_storage_sparse.py`
    - Verify creating a DB with the new schema.
    - Verify inserting a document *with* a dummy sparse vector (`{"foo": 1.5}`).
    - Verify retrieving that document allows access to the stored sparse vector.

### Manual Verification
- **Inspection**: Use `sqlite3` CLI or python script to inspect the `.db` file and see the JSON data in the new column.

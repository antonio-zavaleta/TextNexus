# Query Interface for Vector Store

## Purpose
The `query` method enables semantic search over the knowledge base, returning the most relevant document chunks for a given query embedding.

## Method Signature
```python
def query(self, embedding: list[float], top_k: int) -> list[Document]:
    """
    Returns the top_k most similar document chunks to the provided embedding.
    """
```

## Usage Example (Python)
```python
embedding = embedding_model.create_embeddings(["What is attention?"])[0]
results = vector_store.query(embedding, top_k=3)
for doc in results:
    print(doc.page_content, doc.metadata)
```

## Usage Example (CLI)
```bash
textnexus query "What is attention?" --top-k 3
```

## Output
Returns a list of `Document` objects, each with `page_content` and `metadata` (including source and page).

## Error Handling
- Raises an exception if the database is unavailable or the query fails.
- Returns an empty list if no relevant chunks are found.

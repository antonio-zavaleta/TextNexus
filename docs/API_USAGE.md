# TextNexus API Usage Guide

TextNexus exposes a clean Python API for building RAG applications programmatically.

## Quick Start
```python
import textnexus

print(f"TextNexus version: {textnexus.__version__}")
```

## 1. Querying (Retrieval)
Use the `QueryEngine` to search for relevant context.

```python
from textnexus import QueryEngine
from textnexus.core.embedding import SentenceTransformerModel
from textnexus.core.storage import SQLiteVectorStore
from textnexus import config

# 1. Setup components
embedding_model = SentenceTransformerModel(model_name="all-MiniLM-L6-v2")
vector_store = SQLiteVectorStore(
    db_path=str(config.DB_PATH),
    embedding_model=embedding_model
)

# 2. Initialize Engine
engine = QueryEngine(vector_store=vector_store, embedding_model=embedding_model)

# 3. Query
response = engine.query("What is the architecture of the transformer?", top_k=3)

# 4. Handle Results
print(f"Found {response['count']} results:")
for result in response['results']:
    print(f"- {result['content'][:100]}... (Source: {result['metadata'].get('source')})")
```

## 2. Ingestion
Use the `IngestionPipeline` to process documents.

```python
from textnexus import IngestionPipeline

pipeline = IngestionPipeline()
pipeline.run(source="path/to/documents/")
```

# AGENT INSTRUCTIONS FOR PROJECT: TextNexus

## 1. PROJECT_GOAL
Build a modular Python CLI tool to create and run Retrieval-Augmented Generation (RAG) pipelines for PDF documents. The user will ingest PDFs and query them via the CLI.

## 2. TECH_STACK
- **Language**: Python 3.9+
- **Dependency_Manager**: Poetry
- **LLM_Framework**: LangChain (`langchain-core`, LCEL)
- **LLM_Observability**: LangSmith
- **CLI_Framework**: Typer
- **Object_Storage_Local**: MinIO (S3 API)
- **Vector_DB_Local**: SQLite with `sqlite-vss` extension
- **Embedding_Model_Local**: Hugging Face SentenceTransformers (`all-MiniLM-L6-v2`)
- **GPU_Acceleration**: Required for local embedding via CUDA.
- **Cloud_Target**: GCP (GCS, BigQuery/Vertex Vector Search, Cloud Run)
- **Infrastructure_as_Code**: Terraform

## 3. KEY_ABSTRACTIONS
- **File**: `auto_rag/core/embedding.py`
  - **Abstract_Class**: `BaseEmbeddingModel`
  - **Initial_Implementation**: `SentenceTransformerModel`
- **File**: `auto_rag/core/chunking.py`
  - **Abstract_Class**: `BaseTextSplitter`
  - **Initial_Implementation**: LangChain's `RecursiveCharacterTextSplitter`

## 4. DEVELOPMENT_RULES
- **Rule_1 (Branching)**: Use GitFlow model. All new work must be on a `feature/` branch created from `develop`.
- **Rule_2 (Commits)**: All commit messages MUST follow the Conventional Commits specification (e.g., `feat:`, `fix:`, `docs:`).
- **Rule_3 (Docstrings)**: All public functions, classes, and methods MUST have Google-style Python docstrings.
- **Rule_4 (File_Structure)**: Adhere strictly to the file structure defined below.

## 5. FILE_STRUCTURE
```
TextNexus/
├── AGENTS.MD
├── LICENSE
├── pyproject.toml
├── poetry.lock
├── auto_rag/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   ├── chunking.py
│   │   ├── embedding.py
│   │   ├── storage.py
│   │   └── query.py
│   ├── pipelines/
│   │   ├── __init__.py
│   │
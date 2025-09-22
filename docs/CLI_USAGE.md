# TextNexus CLI Usage Guide

This document provides an overview of the TextNexus command-line interface and its core commands.

## Prerequisites

Before using any TextNexus commands, ensure your environment is properly set up:

1. **Start the MinIO Server**
   ```bash
   ./scripts/start_minio.sh
   ```
   MinIO is used for document storage and must be running before any operations.

2. **Organize and Upload PDF Files**
   - Files must be organized in "folders" (prefixes) in MinIO, like `transformers/`, `papers/`, etc.
   - Use the MinIO client (mc) to upload files:
     ```bash
     # Example: Upload a PDF to the transformers folder
     mc cp your-paper.pdf local/raw-pdfs/transformers/
     ```

3. **Verify Setup**
   - MinIO server is running and accessible
   - PDF files are properly organized in MinIO buckets
   - Vector store is configured (see [Local Vector Store Setup](LOCAL_VECTOR_STORE_SETUP.md))

For detailed setup instructions, see the [Local Setup Guide](LOCAL_SETUP.md).

## Getting Started

All TextNexus commands must be prefixed with `poetry run`. This ensures that the application runs inside the correct Python virtual environment with all necessary dependencies installed. The general format is:

```sh
poetry run python auto_rag/cli.py [COMMAND] [ARGUMENTS] [OPTIONS]
```

## Available Commands

### `index`
Index and process PDF documents for the RAG pipeline.

```sh
# Index a specific folder of PDFs
poetry run python auto_rag/cli.py index transformers/

# Index all PDFs in the bucket
poetry run python auto_rag/cli.py index --all
```

[Detailed Index Command Documentation](commands/INDEX_COMMAND.md)

### `query`
Search indexed documents using semantic search.

```sh
# Search with default parameters
poetry run python auto_rag/cli.py query "What is deep learning?"

# Search with custom chunk limit
poetry run python auto_rag/cli.py query "Explain transformers" --top-k 5
```

[Detailed Query Command Documentation](commands/QUERY_COMMAND.md)

### `generate`
Generate answers using LLM-powered RAG.

```sh
# Generate with default parameters
poetry run python auto_rag/cli.py generate "What is deep learning?"

# Generate with custom model and context size
poetry run python auto_rag/cli.py generate "Explain neural networks" --model llama2 --top-k 5
```

[Detailed Generate Command Documentation](commands/GENERATE_COMMAND.md)

## Common Options

Each command has its own specific options, but some common patterns include:
- `--help`: Display help information for any command
- `--top-k`: Specify the number of relevant chunks to retrieve (for query and generate)
- `-y/--yes`: Skip confirmation prompts (where applicable)

## Technical Documentation

For more detailed technical information about specific components:
- [Query Interface](technical/QUERY_INTERFACE.md)
- [Local Setup](LOCAL_SETUP.md)
- [Vector Store Setup](LOCAL_VECTOR_STORE_SETUP.md)

## Environment Configuration

Make sure you have completed the necessary setup steps:
1. Install all dependencies (`poetry install`)
2. Configure local services (MinIO, vector store)
3. Set up any required environment variables

For detailed setup instructions, see the [Local Setup Guide](LOCAL_SETUP.md).

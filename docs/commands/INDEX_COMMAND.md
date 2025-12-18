# Index Command

## Overview
The `index` command is a core component of TextNexus that processes and ingests PDF documents into the RAG pipeline. It handles document retrieval from MinIO storage, text extraction, chunking, and vector storage operations.

## Prerequisites and Setup

### 1. MinIO Server
Before using the index command, ensure MinIO is running:
```bash
# Start MinIO server
./scripts/start_minio.sh

# Verify MinIO is running
mc ls local
```

### 2. PDF Organization
Organize your PDF files in MinIO using "folders" (prefixes):
```bash
raw-pdfs/
├── transformers/          # AI/ML papers about transformers
│   ├── attention.pdf
│   └── bert-paper.pdf
├── papers/               # General research papers
│   └── deep-learning.pdf
└── documentation/        # Technical documentation
    └── user-guide.pdf
```

### 3. Upload Files
Use MinIO client to upload PDFs:
```bash
# Create a new "folder"
mc mb local/raw-pdfs/my-papers

# Upload PDFs
mc cp ./papers/*.pdf local/raw-pdfs/my-papers/
```

## Complete Workflow
1. Start MinIO server if not running
2. Organize and upload PDFs to desired prefix
3. Run index command on the prefix
4. Verify successful indexing
5. (Optional) Check vector store for indexed content

## Usage
```bash
poetry run python textnexus.cli.py index [SOURCE] [OPTIONS]
```

## Arguments
- `SOURCE` (Optional): A source identifier that acts as a prefix to filter objects in the MinIO bucket (e.g., `transformers/`).

## Options
- `--all`: Process all `.pdf` files in the entire bucket. Mutually exclusive with `SOURCE`.
- `-y, --yes`: Bypass confirmation prompt when using `--all`. Useful for automated scripts.

## Examples

### Index a Specific PDF File
```bash
poetry run python textnexus/cli.py index transformers/attention_is_all_you_need.pdf
```

### Index All PDFs in a "Folder"
```bash
poetry run python textnexus/cli.py index transformers/
```

### Index All PDFs in the Bucket (Interactive)
```bash
poetry run python textnexus/cli.py index --all
```

### Index All PDFs in the Bucket (Non-Interactive)
```bash
poetry run python textnexus/cli.py index --all -y
```

## How It Works
1. **Document Retrieval**: Fetches PDF documents from MinIO based on the specified source or pattern
2. **Text Extraction**: Processes PDFs to extract raw text
3. **Chunking**: Splits text into manageable chunks for efficient retrieval
4. **Vector Storage**: Embeds chunks and stores them in the vector database

## Error Handling
- Invalid source patterns will result in clear error messages
- Missing PDFs or access issues are reported with helpful context
- Processing errors for individual files won't stop the entire operation

## Tips
- Use folder-style indexing (`transformers/`) for batch processing related documents
- The `--all` flag is powerful but use with caution in production
- For automation, combine `--all` with `-y` in scripts

## Related Documentation
- [CLI Usage Guide](../CLI_USAGE.md) - General CLI documentation
- [Local Setup](../LOCAL_SETUP.md) - Environment setup for indexing
- [Vector Store Setup](../LOCAL_VECTOR_STORE_SETUP.md) - Vector database configuration
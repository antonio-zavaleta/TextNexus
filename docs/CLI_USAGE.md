# TextNexus CLI Usage Guide

This document provides detailed examples and explanations for using the TextNexus command-line interface.

## Executing Commands

All commands must be prefixed with `poetry run`. This ensures that the application runs inside the correct Python virtual environment with all the necessary dependencies installed. The general format is:

```sh
poetry run python auto_rag/cli.py [COMMAND] [ARGUMENTS] [OPTIONS]
```
## Core Commands

### `index`

The `index` command is used to ingest and process documents from a source, preparing them for the RAG pipeline.

#### Arguments & Options

* `SOURCE` (Optional): The source identifier, which acts as a **prefix** to filter objects in the MinIO bucket (e.g., `transformers/`).
* `--all` (Flag): A flag to process all `.pdf` files in the entire bucket. This is mutually exclusive with the `SOURCE` argument.
* `-y`, `--yes` (Flag): A flag to bypass the confirmation prompt when using `--all`. This is intended for use in automated scripts.

#### Usage Examples

**1. Index a single, specific PDF file:**

The `SOURCE` is the full object name.
```sh
poetry run python auto_rag/cli.py index transformers/attention_is_all_you_need.pdf
```


**2. Index all PDFs in a "folder" (prefix):**
```sh
poetry run python auto_rag/cli.py index transformers/
```

**3. Index all PDFs in the entire bucket (Interactive Mode)::**
Simply ommit the `SOURCE` argument.
```sh
poetry run python auto_rag/cli.py index --all
```
**4. Index all PDFs in the entire bucket (Script Mode):**
Using `--all` with `-y` will bypass the confirmation prompt, making it suitable for automated scripts.
```sh
poetry run python auto_rag/cli.py index --all -y
```

### `query` (Future Implementation)

The `query` command will be used to ask questions of the indexed documents.

*(This section will be updated as the feature is developed.)*

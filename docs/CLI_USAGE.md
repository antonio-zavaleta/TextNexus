# TextNexus CLI Usage Guide

This document provides detailed examples and explanations for using the TextNexus command-line interface.

## Executing Commands

All commands must be prefixed with `poetry run`. This ensures that the application runs inside the correct Python virtual environment with all the necessary dependencies installed. The general format is:

```sh
poetry run python auto_rag/cli.py [COMMAND] [ARGUMENTS] [OPTIONS]
```
## Core Commands

### `index`

The `index` command is used to ingest and process a source document, preparing it for the RAG pipeline.

#### Arguments

* `SOURCE` (Required): The identifier for the source document.

#### Usage

**Ingest a single PDF from the `raw-pdfs` MinIO bucket:**

```sh
poetry run python auto_rag/cli.py index attention_is_all_you_need.pdf
```
### `query` (Future Implementation)

The `query` command will be used to ask questions of the indexed documents.

*(This section will be updated as the feature is developed.)*

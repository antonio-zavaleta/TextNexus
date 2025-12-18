# TextNexus

A modular Python CLI tool to create and run Retrieval-Augmented Generation (RAG) pipelines for your PDFs.

The project is architected to be modular, scalable, and cloud-ready, with a focus on clear development practices and robust testing.

---

## 🚀 Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites

* Python 3.9+
* [Poetry](https://python-poetry.org/docs/#installation) for dependency management
* [Docker](https://docs.docker.com/engine/install/) for running local infrastructure
* MinIO for document storage (started via `scripts/start_minio.sh`)

Before using any commands, ensure:
1. MinIO server is running (`./scripts/start_minio.sh`)
2. Your PDF files are uploaded to MinIO in organized "folders" (e.g., `transformers/`, `papers/`)
### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/your-username/TextNexus.git](https://github.com/your-username/TextNexus.git)
    cd TextNexus
    ```

2.  **Install dependencies:**
    ```sh
    poetry install
    ```
3.  **Complete the one-time local environment setup:**
    * For detailed instructions on starting the local MinIO server and creating the necessary buckets, please follow the **[Local Development Setup Guide](docs/LOCAL_SETUP.md)**.
    * For an overview of the local vector database, see the **[Local Vector Store Setup Guide](docs/LOCAL_VECTOR_STORE_SETUP.md)**.

## 🚀 Quick Start

After installation and MinIO setup, try these commands to see TextNexus in action:

1. **Index your first documents:**
```sh
poetry run python textnexus/cli.py index artemis
```
```
Step 1: Ingestion complete. Found 85 pages.
Step 2: Chunking complete. Created 737 semantic chunks.
Step 3: Storage complete. Saved 737 chunks to the database.
```

2. **Query the knowledge base:**
```sh
poetry run python textnexus/cli.py query "What is Project Artemis?" --top-k 3
```
This will show relevant document chunks from your indexed files.

3. **Generate an answer using RAG:**
```sh
poetry run python textnexus/cli.py generate "Summarize the goals of Project Artemis." --top-k 10
```
The system will generate a contextual answer based on the indexed documents.

This example uses NASA's Artemis documents, but you can use any PDF documents organized in MinIO "folders". See the [CLI Usage Guide](docs/CLI_USAGE.md) for detailed instructions.

---

## 💡 Features
- Query the knowledge base for relevant document chunks using semantic search (`query` command). See [docs/commands/QUERY_COMMAND.md](docs/commands/QUERY_COMMAND.md) for details.
- Generate contextual answers using LLM-powered RAG pipelines (`generate` command). See [docs/commands/GENERATE_COMMAND.md](docs/commands/GENERATE_COMMAND.md) for details.
- Index and process your PDF documents (`index` command). See [docs/commands/INDEX_COMMAND.md](docs/commands/INDEX_COMMAND.md) for details.

## 💻 Basic Usage

The primary interface for TextNexus is through its command line, executed via `poetry run`.

**Index a "folder" of PDF files from your MinIO bucket:**
```sh
poetry run python textnexus/cli.py index transformers/
```

**Generate an answer using RAG:**
```sh
poetry run python textnexus/cli.py generate "What is deep learning?" --top-k 3
```

For more detailed examples and a full list of commands and options, please see the [**CLI Usage Guide**](docs/CLI_USAGE.md).


---

## 🏗️ Architecture & Development

For a complete overview of the project's architecture, long-term vision, technology stack, and development best practices, please see our detailed **[Project Plan](docs/PROJECT_PLAN.md)**.
# TextNexus

A modular Python CLI tool to create and run Retrieval-Augmented Generation (RAG) pipelines for your PDFs.

The project is architected to be modular, scalable, and cloud-ready, with a focus on clear development practices and robust testing.

---

## 🚀 Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites

* Python 3.9+
* [Poetry](https://python-poetry.org/docs/#installation) for dependency management.
* [Docker](https://docs.docker.com/engine/install/) for running local infrastructure.

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
    For detailed instructions on starting the local MinIO server and creating the necessary buckets, please follow the **[Local Development Setup Guide](docs/LOCAL_SETUP.md)**.

---

## 💻 Basic Usage

The primary interface for TextNexus is through its command line, executed via `poetry run`.

**Index a "folder" of PDF files from your MinIO bucket:**
```sh
poetry run python auto_rag/cli.py index transformers/
```
For more detailed examples and a full list of commands and options, please see the [**CLI Usage Guide**](docs/CLI_USAGE.md).


---

## 🏗️ Architecture & Development

For a complete overview of the project's architecture, long-term vision, technology stack, and development best practices, please see our detailed **[Project Plan](docs/PROJECT_PLAN.md)**.
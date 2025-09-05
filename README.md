# TextNexus

TextNexus is a Python-based command-line tool designed to automatically create and manage Retrieval-Augmented Generation (RAG) pipelines. It allows you to ingest PDF documents and ask questions about their content directly from your terminal.

The project is architected to be modular, scalable, and cloud-ready, with a focus on clear development practices and robust testing.

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing.

### Prerequisites

* Python 3.9+
* [Poetry](https://python-poetry.org/docs/#installation) for dependency management.

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/your-username/TextNexus.git](https://github.com/your-username/TextNexus.git)
    cd TextNexus
    ```

2.  **Install dependencies:**
    This project uses Poetry to manage dependencies. Run the following command to create a virtual environment and install the required packages.
    ```sh
    poetry install
    ```

---

## 💻 Basic Usage

The primary interface for TextNexus is through its command line, executed via `poetry run`.

**1. Index a PDF file from your MinIO bucket:**

```sh
poetry run python auto_rag/cli.py index your-file-name.pdf

```
For more detailed examples and a full list of commands and options, please see the [**CLI Usage Guide**](docs/CLI_USAGE.md).


---

## 🏗️ Architecture & Development

For a complete overview of the project's architecture, long-term vision, technology stack, and development best practices, please see our detailed **[Project Plan](docs/PROJECT_PLAN.md)**.
import logging
from pathlib import Path

import typer

# Import our core components
from auto_rag.core.embedding import SentenceTransformerModel
from auto_rag.core.storage import SQLiteVectorStore
from auto_rag.commands import index, query
from auto_rag import config

# Create the main Typer application instance
app = typer.Typer(
    name="TextNexus",
    help="A CLI tool to automatically build and run RAG pipelines for your PDFs.",
    add_completion=False,
)

# Add the sub-applications to the main app
app.add_typer(index.app, name="index", help="Ingest, chunk, embed, and store documents from a source.")
app.add_typer(query.app, name="query", help="Query the knowledge base for relevant document chunks.")

logger = logging.getLogger(__name__)

class AppState:
    """A simple state object to hold our shared components."""
    def __init__(self):
        self.embedding_model = None
        self.vector_store = None

@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
):
    """
    Main callback to configure logging and initialize shared components.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    logging.basicConfig(level=log_level, format=log_format)
    logger.info(f"Logging configured at level: {logging.getLevelName(log_level)}")

    # --- Dependency Injection ---
    # Create and attach the state object to the context
    ctx.obj = AppState()
    logger.info("Initializing shared components...")
    
    # Ensure the data directory exists for the database
    db_dir = Path(config.DB_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    ctx.obj.embedding_model = SentenceTransformerModel()
    ctx.obj.vector_store = SQLiteVectorStore(
        db_path=str(config.DB_PATH), 
        embedding_model=ctx.obj.embedding_model
    )
    logger.info("Shared components initialized and attached to context.")

if __name__ == "__main__":
    app()


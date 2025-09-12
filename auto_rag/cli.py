import logging
import typer

# Import the command "sub-apps" from our new directory
from auto_rag.commands import index, query

# Create the main Typer application instance
app = typer.Typer(
    name="TextNexus",
    help="A CLI tool to automatically build and run RAG pipelines for your PDFs.",
    add_completion=False,
)

# Add the sub-applications to the main app
app.add_typer(index.app, name="index", help="Ingest, chunk, embed, and store documents from a source.")
app.add_typer(query.app, name="query", help="Query the knowledge base for relevant document chunks.")

# Get a logger instance for this module
logger = logging.getLogger(__name__)


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """
    Main callback to configure the application state, like logging.
    This function runs before any command.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    logging.basicConfig(level=log_level, format=log_format)
    logger.info(f"Logging configured at level: {logging.getLevelName(log_level)}")


if __name__ == "__main__":
    app()


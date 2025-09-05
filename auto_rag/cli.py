import logging
import typer

# Import our MinioPDFLoader
from auto_rag.core.ingestion import MinioPDFLoader

# Create a Typer application instance
app = typer.Typer(
    name="TextNexus",
    help="A CLI tool to automatically build and run RAG pipelines for your PDFs.",
    add_completion=False,
)


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

    # This configuration will be inherited by all loggers in the 'auto_rag' package
    # because we configured the root logger.
    logging.getLogger("auto_rag").info(f"Logging configured at level: {logging.getLevelName(log_level)}")


@app.command()
def index(
    source: str = typer.Argument(..., help="The source to index. For now, a PDF filename in the 'raw-pdfs' bucket."),
):
    """
    Ingest and index a document from a source.
    """
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Starting ingestion for source: {source}")
        typer.echo(f"Starting ingestion for source: {source}")
        
        loader = MinioPDFLoader()
        documents = loader.load(source)

        if not documents:
            warning_message = f"No documents were loaded from '{source}'. The file might be empty, corrupted, or not found."
            logger.warning(warning_message)
            typer.secho(f"Warning: {warning_message}", fg=typer.colors.YELLOW)
            raise typer.Exit()

        success_message = f"Successfully loaded {len(documents)} pages from '{source}'."
        logger.info(success_message)
        typer.secho(success_message, fg=typer.colors.GREEN)
        # In a future step, we will pass these 'documents' to the chunking and embedding pipeline.

    except Exception as e:
        logger.error(f"An unhandled error occurred during ingestion: {e}", exc_info=True)
        typer.secho(f"Error during ingestion: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

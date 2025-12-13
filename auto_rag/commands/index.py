import logging
from typing import Optional

import typer
from rich.console import Console

# Import our core components
from auto_rag.core.embedding import SentenceTransformerModel
from auto_rag.core.chunking import SemanticTextSplitter
from auto_rag.core.ingestion import MinioPDFLoader
from auto_rag.core.ingestion_pipeline import IngestionPipeline
from auto_rag.core.storage import SQLiteVectorStore
from auto_rag import config

# Each command file has its own Typer app instance.
app = typer.Typer()
logger = logging.getLogger(__name__)
console = Console()

@app.callback(invoke_without_command=True)
def index(
    ctx: typer.Context, # The context now holds our shared components
    source: Optional[str] = typer.Argument(None, help="The source prefix to index (e.g., 'transformers/')."),
    all_files: bool = typer.Option(False, "--all", help="Process all PDF files in the entire bucket."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Bypass confirmation prompts."),
):
    """
    Ingest, chunk, embed, and store documents from a source.
    """
    # --- Input Validation ---
    if not source and not all_files:
        typer.secho("Error: You must specify a SOURCE prefix or use the --all flag.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if source and all_files:
        typer.secho("Error: The SOURCE argument and the --all flag are mutually exclusive.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    target_prefix = "" if all_files else source

    # --- Pre-computation and Confirmation (using a separate loader instance) ---
    try:
        temp_loader = MinioPDFLoader()
        if all_files and not yes:
            objects_to_process = list(temp_loader.minio_client.list_objects(temp_loader.bucket_name, prefix=target_prefix, recursive=True))
            pdf_count = sum(1 for obj in objects_to_process if obj.object_name.lower().endswith('.pdf'))
            if not typer.confirm(f"Found {pdf_count} PDFs. Are you sure you want to process all of them?"):
                typer.echo("Aborting.")
                raise typer.Exit()
    except typer.Exit:
        raise
    except Exception as e:
        logger.error(f"An error occurred during pre-computation: {e}", exc_info=True)
        typer.secho(f"Error during setup: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    # --- Main Pipeline Logic ---
    try:
        console.rule("[bold green]Starting Indexing Pipeline[/bold green]")
        
        # --- Use components from the context ---
        embedding_model = ctx.obj.embedding_model
        vector_store = ctx.obj.vector_store

        # Initialize components
        loader = MinioPDFLoader()
        splitter = SemanticTextSplitter(embedding_model=embedding_model)
        
        # Initialize and Run Pipeline
        pipeline = IngestionPipeline(loader, splitter, vector_store)
        stats = pipeline.run(target_prefix)
        
        # Check results
        if stats["documents_loaded"] == 0:
            warning_message = f"No documents were loaded from prefix '{target_prefix}'."
            logger.warning(warning_message)
            typer.secho(f"Warning: {warning_message}", fg=typer.colors.YELLOW)
            raise typer.Exit()

        # Log completion stats
        console.log(f"Step 1: Ingestion complete. Found {stats['documents_loaded']} pages.")
        console.log(f"Step 2: Chunking complete. Created {stats['chunks_created']} semantic chunks.")
        console.log(f"Step 3: Storage complete. Saved {stats['chunks_stored']} chunks to the database.")

        console.rule("[bold green]Pipeline Finished Successfully[/bold green]")
        success_message = f"Successfully processed source '{target_prefix if target_prefix else 'ENTIRE BUCKET'}' and stored {len(chunks)} chunks in the knowledge base."
        logger.info(success_message)
        typer.secho(success_message, fg=typer.colors.GREEN)

    except typer.Exit:
        raise
    except Exception as e:
        logger.error(f"An unhandled error occurred during the pipeline: {e}", exc_info=True)
        typer.secho(f"Error during pipeline execution: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


import logging
import typer
from rich.console import Console
from rich.table import Table

# Each command file has its own Typer app instance.
app = typer.Typer()
logger = logging.getLogger(__name__)
console = Console()


@app.callback(invoke_without_command=True)
def query(
    ctx: typer.Context, # This context now holds our shared components
    query_text: str = typer.Argument(..., help="The question to ask the knowledge base."),
    top_k: int = typer.Option(3, "--top-k", "-k", help="The number of relevant chunks to retrieve."),
):
    """
    Query the knowledge base for relevant document chunks.
    """

    try:
        console.rule(f"[bold green]Executing Query: '{query_text}'[/bold green]")
        
        # --- Use components from the context (Dependency Injection) ---
        # We no longer create instances here; we receive them from cli.py
        embedding_model = ctx.obj.embedding_model
        vector_store = ctx.obj.vector_store
        logger.info("Shared components received from context.")

        # 2. Create Query Embedding
        logger.info(f"Creating embedding for query: '{query_text}'")
        query_embedding = embedding_model.create_embeddings([query_text])[0]
        logger.info("Query embedding created.")

        # 3. Search the Vector Store
        logger.info(f"Searching for top {top_k} most similar chunks...")
        results = vector_store.query(query_embedding, top_k=top_k)
        logger.info(f"Found {len(results)} results.")

        # 4. Display Results
        if not results:
            console.print("[bold yellow]Could not find any relevant documents for your query.[/bold yellow]")
            raise typer.Exit(code=0)

        console.log(f"Found {len(results)} relevant chunks:")
        table = Table(title="Query Results", show_lines=True)
        table.add_column("Source", style="cyan", no_wrap=True)
        table.add_column("Page", style="green", justify="right")
        table.add_column("Content", style="magenta")

        for doc in results:
            source = doc.metadata.get('source', 'N/A')
            page = str(doc.metadata.get('page', 'N/A'))
            content = " ".join(doc.page_content.strip().split())
            table.add_row(source, page, content)
        
        console.print(table)

    except Exception as e:
        logger.error(f"An unhandled error occurred during query: {e}", exc_info=True)
        typer.secho(f"Error during query execution: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


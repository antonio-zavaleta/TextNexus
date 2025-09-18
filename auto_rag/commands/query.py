import logging
import typer
from rich.console import Console
from rich.table import Table
from auto_rag.utils.retrieval import retrieve_relevant_chunks

app = typer.Typer()
logger = logging.getLogger(__name__)
console = Console()

@app.command()
def query(
    ctx: typer.Context,
    query_text: str = typer.Argument(..., help="The question to ask the knowledge base."),
    top_k: int = typer.Option(3, "--top-k", "-k", help="The number of relevant chunks to retrieve."),
) -> None:
    """
    Query the knowledge base for relevant document chunks.

    This command orchestrates the retrieval process by calling a shared utility
    function to find the most relevant document chunks based on the user's query.

    Args:
        ctx (typer.Context): Typer context containing shared components.
        query_text (str): The user's question or prompt.
        top_k (int): Number of relevant chunks to retrieve.

    Returns:
        None. Prints the results to the console.
    """
    try:
        logger.info(f"Query called with query_text='{query_text}', top_k={top_k}")
        console.rule(f"[bold green]Executing Query: '{query_text}'[/bold green]")
        
        results = retrieve_relevant_chunks(ctx, query_text, top_k)
        
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

    except RuntimeError as e:
        logger.error(f"Retrieval error: {e}", exc_info=True)
        typer.secho(f"Error during retrieval: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"An unhandled error occurred during query: {e}", exc_info=True)
        typer.secho(f"Error during query execution: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    
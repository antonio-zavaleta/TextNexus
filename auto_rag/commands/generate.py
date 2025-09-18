import typer
from rich.console import Console
from auto_rag.llm.connector_registry import LLM_CONNECTORS
from auto_rag.utils.retrieval import retrieve_relevant_chunks
import logging


app = typer.Typer()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = Console()

@app.command()
def generate(
    ctx: typer.Context,
    query_text: str = typer.Argument(..., help="The question to ask the LLM-powered RAG pipeline."),
    model: str = typer.Option("llama3", "--model", "-m", help="The LLM model to use for generation."),
    top_k: int = typer.Option(3, "--top-k", "-k", help="Number of relevant chunks to retrieve for context."),
) -> None:
    """
    Generate an answer using a selected language model and Retrieval-Augmented Generation (RAG).

    This command orchestrates the entire Retrieval-Augmented Generation (RAG)
    pipeline to provide answers grounded in your documents.

    Args:
        ctx: The Typer context object for dependency injection.
        query_text: The user's question or prompt.
        model: The name of the language model to use for generation.
        top_k: The number of top relevant document chunks to retrieve.

    Returns:
        None. Prints the generated response to the console.
    """
    try:
        console.rule(f"[bold green]RAG Generation: '{query_text}'[/bold green]")

        connector_class = LLM_CONNECTORS.get(model)
        if connector_class is None:
            console.print(f"[bold red]Error: Unsupported model '{model}'. Available models: {list(LLM_CONNECTORS.keys())}[/bold red]")
            logger.warning(f"Unsupported model requested: {model}")
            raise typer.Exit(code=1)

        context_docs = retrieve_relevant_chunks(ctx=ctx, query_text=query_text, top_k=top_k)
        context = "\n\n".join([doc.page_content.strip() for doc in context_docs]) if context_docs else ""
        if not context:
            console.print("[bold yellow]Warning: No relevant documents found. Generating a general response.[/bold yellow]")
            logger.info("No relevant documents found for context.")

        connector = connector_class()
        response = connector.query(prompt=query_text, context=context)

        console.print("\n[bold cyan]Answer:[/bold cyan]")
        console.print(response)

    except Exception as e:
        logger.error(f"An unhandled error occurred: {e}", exc_info=True)
        console.print(f"[bold red]Error during RAG generation: {e}[/bold red]")
        raise typer.Exit(code=1)
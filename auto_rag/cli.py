import typer
from rich.console import Console
from auto_rag.commands.index import app as index_app
from auto_rag.commands.query import query
from auto_rag.commands.generate import generate
from auto_rag.core.embedding import SentenceTransformerModel
from auto_rag.core.storage import SQLiteVectorStore
from auto_rag import config

app = typer.Typer()
console = Console()

class AppState:
    def __init__(self):
        self.embedding_model = SentenceTransformerModel()
        self.vector_store = SQLiteVectorStore(
            db_path=str(config.DB_PATH),
            embedding_model=self.embedding_model
        )

@app.callback()
def main(ctx: typer.Context):
    """
    Main callback to initialize shared components for dependency injection.
    """
    ctx.obj = AppState()

app.add_typer(index_app, name="index")
app.command()(query)
app.command()(generate)

if __name__ == "__main__":
    app()
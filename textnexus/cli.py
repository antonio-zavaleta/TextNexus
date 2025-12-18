import typer
from rich.console import Console
from textnexus.commands.index import app as index_app
from textnexus.commands.query import query
from textnexus.commands.generate import generate
from textnexus.core.embedding import SentenceTransformerModel
from textnexus.core.storage import SQLiteVectorStore
from textnexus import config

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
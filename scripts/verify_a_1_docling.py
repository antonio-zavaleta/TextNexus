import sys
import logging
from pathlib import Path
import json

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from textnexus.core.ingestion_pipeline import IngestionPipeline
from textnexus.core.loaders import DoclingLoader
from textnexus.core.storage import SQLiteVectorStore
from textnexus.core.embedding import SentenceTransformerModel
from textnexus.core.chunking import SemanticTextSplitter
from langchain_core.documents import Document

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockEmbeddingModel:
    """Mock to avoid loading heavy model."""
    def create_embeddings(self, texts):
        return [[0.1] * 384 for _ in texts]

def main():
    print("Starting Docling Ingestion Verification...")
    
    # 1. Setup Paths
    base_dir = Path(__file__).parent.parent
    pdf_path = base_dir / "tests/data/golden_dataset/documents/attention_is_all_you_need.pdf"
    
    if not pdf_path.exists():
        print(f"❌ Test PDF not found at {pdf_path}")
        exit(1)
        
    db_path = "verify_docling.db"
    Path(db_path).unlink(missing_ok=True) # Clean up
    
    # 2. Initialize Components
    loader = DoclingLoader()
    # Use Mock embedding model for speed, assuming 384 dim (MiniLM)
    # But wait, SemanticTextSplitter might need real embeddings if it does semantic splitting?
    # If SemanticTextSplitter uses the model solely for embeddings, Mock is fine.
    # If it uses it for clustering (Breakpoints), Mock might produce weird results (all same), 
    # but for verification of FLOW, it's acceptable.
    model = MockEmbeddingModel()
    splitter = SemanticTextSplitter(embedding_model=model)
    store = SQLiteVectorStore(db_path=db_path, embedding_model=model)
    
    pipeline = IngestionPipeline(loader, splitter, store)
    
    # 3. Run Pipeline
    try:
        stats = pipeline.run(str(pdf_path))
        print(f"Pipeline Stats: {json.dumps(stats, indent=2)}")
        
        if stats["documents_loaded"] != 1:
            raise ValueError(f"Expected 1 document, got {stats['documents_loaded']}")
        if stats["chunks_stored"] == 0:
            raise ValueError("No chunks stored!")
            
        print("✅ Pipeline ran successfully.")
        
        # 4. Inspect content
        # We want to see if Markdown is preserved (e.g., look for '#' headers)
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM chunks LIMIT 1")
        row = cursor.fetchone()
        if row:
            content = row[0]
            print("\nSample Chunk Content (First 200 chars):")
            print("-" * 40)
            print(content[:200])
            print("-" * 40)
            
            if "#" not in content and "Attention" not in content:
                print("⚠️ Warning: Content doesn't look like Markdown or text.")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ Verification Failed: {e}")
        # Print full traceback
        import traceback
        traceback.print_exc()
        exit(1)
    finally:
        Path(db_path).unlink(missing_ok=True)

if __name__ == "__main__":
    main()

import sys
from pathlib import Path
import json
import sqlite3

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from textnexus.core.storage import SQLiteVectorStore
from langchain_core.documents import Document

class MockEmbeddingModel:
    def create_embeddings(self, texts):
        # Return 2D embeddings for simplicity
        return [[0.1, 0.2] for _ in texts]

def main():
    db_path = "verify_sparse.db"
    
    # 1. Initialize Store
    print(f"Initializing SQLiteVectorStore at {db_path}...")
    # Clean up previous run
    Path(db_path).unlink(missing_ok=True)
    
    store = SQLiteVectorStore(db_path=db_path, embedding_model=MockEmbeddingModel())
    
    # 2. Add Documents with Sparse Vectors
    print("Adding documents with sparse vectors...")
    docs = [
        Document(page_content="Apple Pie", metadata={"category": "food"}),
        Document(page_content="Linear Algebra", metadata={"category": "math"})
    ]
    sparse_vectors = [
        {"apple": 1.0, "pie": 0.8},
        {"linear": 0.9, "algebra": 0.9}
    ]
    
    store.add_documents(docs, sparse_vectors=sparse_vectors)
    
    # 3. Verify Storage via Raw SQL
    print("Verifying storage...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT content, sparse_vector FROM chunks")
        rows = cursor.fetchall()
        
        print(f"\nFound {len(rows)} rows:")
        for content, sparse_str in rows:
            print(f"- Content: '{content}'")
            print(f"  Sparse Vector: {sparse_str}")
            
            # Additional constraint check
            if content == "Apple Pie":
                vec = json.loads(sparse_str)
                if vec.get("apple") != 1.0:
                    raise ValueError("Incorrect sparse vector value for Apple Pie")
        
        print("\n✅ Verification Successful: Sparse vectors stored correctly.")
        
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        exit(1)
    finally:
        if 'conn' in locals():
            conn.close()
        # Cleanup
        Path(db_path).unlink(missing_ok=True)

if __name__ == "__main__":
    main()

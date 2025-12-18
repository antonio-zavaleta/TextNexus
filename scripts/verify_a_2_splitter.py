
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from textnexus.core.loaders import DoclingLoader
from textnexus.core.splitters import StructuredTextSplitter

def main():
    pdf_path = "tests/data/golden_dataset/documents/attention_is_all_you_need.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return

    print(">>> 1. Loading PDF with DoclingLoader...")
    loader = DoclingLoader()
    docs = loader.load(file_path=pdf_path)
    print(f">>> Loaded {len(docs)} full-page documents.")
    
    # Print sample of first doc
    print("\n--- Doc 1 Content Preview (First 500 chars) ---")
    print(docs[0].page_content[:500])
    print("-----------------------------------------------")

    print("\n>>> 2. Splitting with StructuredTextSplitter...")
    splitter = StructuredTextSplitter()
    chunks = splitter.split_documents(docs)
    print(f">>> Created {len(chunks)} chunks.")

    print("\n>>> 3. Inspecting Chunks...")
    
    # Count Header Levels
    h1_count = sum(1 for c in chunks if "Header 1" in c.metadata)
    h2_count = sum(1 for c in chunks if "Header 2" in c.metadata)
    h3_count = sum(1 for c in chunks if "Header 3" in c.metadata)
    
    print(f"Chunks with H1: {h1_count}")
    print(f"Chunks with H2: {h2_count}")
    print(f"Chunks with H3: {h3_count}")

    # Inspect a chunk with a table if possible (looking for "Table" string)
    table_chunks = [c for c in chunks if "Table" in c.page_content]
    if table_chunks:
        print(f"\n>>> Found {len(table_chunks)} chunks potentially containing tables.")
        print("--- Table Chunk Preview ---")
        print(table_chunks[0].page_content[:500])
        print("--- Metadata ---")
        print(table_chunks[0].metadata)
    else:
        print("\n>>> No specific 'Table' keyword found in chunks (might be normal depending on OCR content).")

if __name__ == "__main__":
    main()

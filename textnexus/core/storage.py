import sqlite3
import json
import logging
from abc import ABC, abstractmethod
from typing import List
import numpy as np

from langchain_core.documents import Document

from textnexus.core.embedding import BaseEmbeddingModel
from textnexus import config

logger = logging.getLogger(__name__)

class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        pass

    @abstractmethod
    def query(self, query_embedding: List[float], top_k: int) -> List[Document]:
        pass

class SQLiteVectorStore(BaseVectorStore):
    def __init__(self, db_path: str, embedding_model: BaseEmbeddingModel):
        self.db_path = db_path
        self.embedding_model = embedding_model
        self.conn = None
        self._initialize_database()

    def _initialize_database(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.enable_load_extension(True)
            import sqlite_vss
            sqlite_vss.load(self.conn)
            
            schema_path = config.PROJECT_ROOT / "resources" / "sqlite_schema.sql"
            with open(schema_path, 'r') as f:
                schema = f.read()
            self.conn.executescript(schema)
            self.conn.commit()
            logger.info(f"Successfully connected to and initialized database at '{self.db_path}'.")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite database: {e}")
            if self.conn:
                self.conn.rollback()
            raise

    def add_documents(self, documents: List[Document], sparse_vectors: List[dict] = None) -> None:
        if not documents:
            return

        # Validation: Check if sparse_vectors length matches documents
        if sparse_vectors is not None:
            if len(sparse_vectors) != len(documents):
                raise ValueError(f"Number of sparse vectors ({len(sparse_vectors)}) does not match number of documents ({len(documents)}).")
        else:
            # If no sparse vectors provided, fill with None/Null
            sparse_vectors = [None] * len(documents)

        texts_to_embed = [doc.page_content for doc in documents]
        embeddings = self.embedding_model.create_embeddings(texts_to_embed)

        cursor = self.conn.cursor()
        try:
            for doc, embedding, sparse in zip(documents, embeddings, sparse_vectors):
                # Serialize sparse vector to JSON if present
                sparse_json = json.dumps(sparse) if sparse is not None else None
                
                cursor.execute(
                    "INSERT INTO chunks (content, metadata, sparse_vector) VALUES (?, ?, ?)",
                    (doc.page_content, json.dumps(doc.metadata), sparse_json)
                )
                chunk_id = cursor.lastrowid
                
                # FIX: Convert embedding to a numpy array and then to bytes
                embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
                
                cursor.execute(
                    "INSERT INTO vss_chunks (rowid, embedding) VALUES (?, ?)",
                    (chunk_id, embedding_bytes)
                )
            self.conn.commit()
            logger.info(f"Successfully added {len(documents)} documents.")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            self.conn.rollback()
            raise

    def query(self, query_embedding: List[float], top_k: int) -> List[Document]:
        cursor = self.conn.cursor()
        sql_query = """
            SELECT c.content, c.metadata
            FROM chunks c
            JOIN (
                SELECT rowid
                FROM vss_chunks
                WHERE vss_search(embedding, ?)
                LIMIT ?
            ) AS vss ON c.id = vss.rowid
        """
        # FIX: Convert query embedding to bytes for the search
        query_embedding_bytes = np.array(query_embedding, dtype=np.float32).tobytes()
        params = (query_embedding_bytes, top_k)
        
        try:
            cursor.execute(sql_query, params)
            results = cursor.fetchall()
            found_documents = [
                Document(page_content=row[0], metadata=json.loads(row[1])) for row in results
            ]
            logger.info(f"Found {len(found_documents)} similar documents.")
            return found_documents
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            return []

    def __del__(self):
        if self.conn:
            self.conn.close()


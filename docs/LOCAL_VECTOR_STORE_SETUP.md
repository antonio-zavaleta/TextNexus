# Local Vector Store Setup Guide

This document provides a technical overview of the local vector storage component used in the TextNexus project. Unlike the MinIO server, the vector store does not require manual setup; it is created and managed automatically by the application.

## Overview

For local development, TextNexus uses an `SQLiteVectorStore` class that leverages a standard SQLite database file. This provides a lightweight, serverless, and file-based vector database that is perfect for local testing and development.

The default database file will be created at `data/vector_store.db` within the project root when the `index` command is run.

## Key Components

### 1. `sqlite-vss` Extension

The core of our local vector search capability comes from the `sqlite-vss` Python package. This is a third-party extension for SQLite that adds functions for storing and efficiently searching high-dimensional vector embeddings.

When the `SQLiteVectorStore` is initialized, it programmatically loads this extension into the SQLite connection, enabling the use of specialized functions like `vss_search()`.

### 2. Database Schema (`resources/sqlite_schema.sql`)

The structure of our vector database is defined in the `resources/sqlite_schema.sql` file. This is a standard practice that separates our database schema from our application code. The script creates two main tables:

* **`chunks`**: A standard SQL table that stores the raw text `content` of each chunk and its associated `metadata` (as a JSON string). Each chunk is given a unique integer ID.

* **`vss_chunks`**: This is a **virtual table** controlled by the `sqlite-vss` extension. It is specifically designed to create an efficient index for vector similarity searches. It stores the `embedding` for each chunk as a raw binary `BLOB` and links back to the main `chunks` table using the chunk's ID. The `embedding(384)` definition is critical, as it tells the index that our vectors have 384 dimensions, matching the output of our `all-MiniLM-L6-v2` embedding model.

This setup allows for efficient storage and retrieval. We can perform a fast similarity search on the indexed vectors in `vss_chunks` and then use the resulting IDs to retrieve the full text content and metadata from the main `chunks` table.
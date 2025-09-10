import os
from pathlib import Path
from dotenv import load_dotenv

# --- Project Root Path ---
# This gives us a reliable, absolute path to the project's root directory.
# It finds the directory where this config.py file lives and goes up one level.
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from a .env file in the project root
load_dotenv(PROJECT_ROOT / ".env")


# --- MinIO Configuration ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

# --- LangSmith Configuration ---
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")


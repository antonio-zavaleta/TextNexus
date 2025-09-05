import os
from dotenv import load_dotenv

# Find the .env file in the project root and load its variables
# into the environment for this process.
load_dotenv()

# --- MinIO Configuration ---
# Retrieve the loaded environment variables. os.getenv will return None
# if the variable is not found, preventing the app from crashing.
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")


# --- Future Configurations ---
# We can add other configurations here as the project grows.
# For example:
# LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")


#!/bin/bash

# A script to start a local MinIO server using Docker for development.

# --- Configuration ---
# These values should match what's in your .env file
MINIO_ROOT_USER="minioadmin"
MINIO_ROOT_PASSWORD="minioadmin"
MINIO_PORT_API="9000"
MINIO_PORT_CONSOLE="9001"
# Create a data directory in the project root, which is ignored by git
MINIO_DATA_DIR="$PWD/data/minio"

# --- Script Logic ---
echo "Attempting to start MinIO server..."

# Ensure the data directory exists
mkdir -p "$MINIO_DATA_DIR"

# Check if a MinIO container is already running
if [ "$(docker ps -q -f name=minio_server)" ]; then
    echo "MinIO server is already running."
    echo "API is available at: http://localhost:${MINIO_PORT_API}"
    echo "Console is available at: http://localhost:${MINIO_PORT_CONSOLE}"
    exit 0
fi

# Check if a stopped MinIO container exists
if [ "$(docker ps -aq -f status=exited -f name=minio_server)" ]; then
    echo "Restarting existing stopped MinIO container..."
    docker start minio_server
else
    echo "Starting new MinIO container..."
    docker run -d \
        -p ${MINIO_PORT_API}:${MINIO_PORT_API} \
        -p ${MINIO_PORT_CONSOLE}:${MINIO_PORT_CONSOLE} \
        --name minio_server \
        -v "${MINIO_DATA_DIR}:/data" \
        -e "MINIO_ROOT_USER=${MINIO_ROOT_USER}" \
        -e "MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}" \
        minio/minio server /data --console-address ":${MINIO_PORT_CONSOLE}"
fi

echo "MinIO server started successfully."
echo "API is available at: http://localhost:${MINIO_PORT_API}"
echo "Console is available at: http://localhost:${MINIO_PORT_CONSOLE}"

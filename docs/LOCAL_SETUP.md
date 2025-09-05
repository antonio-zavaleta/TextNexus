# Local Development Setup Guide

This guide provides step-by-step instructions for setting up the local development environment for TextNexus, which relies on a MinIO object storage server running in Docker.

## 1. Start the MinIO Server

This project uses a Docker container to run a local, S3-compatible MinIO server.

First, ensure the startup script is executable (this only needs to be done once):
```sh
chmod +x ./scripts/start_minio.sh
```

Now, run the script to start the server:
```sh
./scripts/start_minio.sh
```
This will start the MinIO server and a web console.
* **API Endpoint:** `http://localhost:9000`
* **Web Console:** `http://localhost:9001`
* **Credentials:** `minioadmin` / `minioadmin`

## 2. Configure the MinIO Client & Create a Bucket

To create the necessary storage bucket for your PDFs, you'll need the MinIO Client (`mc`).

### A. Install the Client

If you don't have it installed, use your system's package manager.

```sh
# For Debian/Ubuntu
sudo apt update && sudo apt install minio-client

# For macOS with Homebrew
# brew install minio-mc
```

### B. Create a Shortcut (Debian/Ubuntu Users)

**Important:** The Debian `apt` package installs the command as `minio-client` instead of the standard `mc`. To make the command consistent with this guide and most online tutorials, it is highly recommended to create a symbolic link (a shortcut).

Run the following command to create the `mc` shortcut:
```sh
sudo ln -s /usr/bin/minio-client /usr/local/bin/mc
```
After running this, you can use the `mc` command as expected.

### C. Configure the Local Server Alias

This command creates a "shortcut" named `local` that tells `mc` how to connect to your local server.

```sh
mc alias set local http://localhost:9000 minioadmin minioadmin
```

### D. Create the Bucket

Finally, create the `raw-pdfs` bucket where the application will look for source files.

```sh
mc mb local/raw-pdfs
```
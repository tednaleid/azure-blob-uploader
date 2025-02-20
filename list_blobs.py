#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "azure-storage-blob",
# ]
# ///
import os
from azure.storage.blob import BlobServiceClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_blobs():
    connection_string = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1;"
    container_name = "testcontainer"
    
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service.get_container_client(container_name)
    
    logger.info(f"Listing blobs in container {container_name}:")
    blob_count = 0
    for blob in container_client.list_blobs():
        blob_count += 1
        if blob_count <= 5:  # Only show first 5 blobs
            logger.info(f"  {blob.name} (size: {blob.size} bytes)")
        elif blob_count == 6:
            logger.info("  ...")
    
    logger.info(f"\nTotal blobs: {blob_count}")

if __name__ == "__main__":
    list_blobs()

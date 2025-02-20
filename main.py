#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "psycopg2-binary",
#     "azure-storage-blob",
#     "python-dotenv",
# ]
# ///
import os
import threading
import time
from queue import Queue
from azure.storage.blob import BlobServiceClient
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Iterator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlobUploader:
    def __init__(self, connection_string: str, container_name: str, num_workers: int = 5):
        self.blob_service = BlobServiceClient.from_connection_string(connection_string)
        self.container = self.blob_service.get_container_client(container_name)
        self.work_queue = Queue()
        self.num_workers = num_workers
        self.workers = []
        
        # Create container if it doesn't exist
        if not self.container.exists():
            logger.info(f"Creating container {container_name}")
            self.container.create_container()

    def upload_worker(self):
        """Worker thread that processes items from the queue"""
        while True:
            try:
                # Get work item from queue
                work_item = self.work_queue.get()
                if work_item is None:  # Poison pill
                    break

                blob_name, xml_content = work_item
                
                # Upload to Azure
                blob_client = self.container.get_blob_client(blob_name)
                blob_client.upload_blob(xml_content, overwrite=True)
                
                logger.info(f"Successfully uploaded {blob_name}")
                
            except Exception as e:
                logger.error(f"Error processing {blob_name}: {str(e)}")
            finally:
                self.work_queue.task_done()

    def start_workers(self):
        """Start the worker threads"""
        self.workers = []
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self.upload_worker)
            worker.start()
            self.workers.append(worker)

    def stop_workers(self):
        """Stop all workers gracefully"""
        # Put poison pills in queue
        for _ in range(self.num_workers):
            self.work_queue.put(None)
        
        # Wait for all workers to finish
        for worker in self.workers:
            worker.join()

    def process_rows(self, row_iterator: Iterator[tuple]):
        """Process rows from database and queue them for upload"""
        try:
            self.start_workers()
            
            for row_id, xml_content in row_iterator:
                blob_name = f"{row_id}.xml"
                self.work_queue.put((blob_name, xml_content))
            
            # Wait for queue to be empty
            self.work_queue.join()
            
        finally:
            self.stop_workers()

def get_db_connection(max_retries=5, retry_delay=5):
    """Get database connection with retry mechanism"""
    retries = 0
    last_error = None
    
    while retries < max_retries:
        try:
            return psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                cursor_factory=RealDictCursor
            )
        except psycopg2.OperationalError as e:
            last_error = e
            retries += 1
            if retries < max_retries:
                logger.warning(f"Failed to connect to database (attempt {retries}/{max_retries}). Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            
    logger.error(f"Failed to connect to database after {max_retries} attempts")
    raise last_error

def get_rows() -> Iterator[tuple]:
    """Generator function to fetch rows from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    batch_size = 100
    offset = 0
    
    try:
        while True:
            cursor.execute("""
                SELECT id, xml_content 
                FROM test_files 
                ORDER BY id 
                LIMIT %s OFFSET %s
            """, (batch_size, offset))
            
            batch = cursor.fetchall()
            if not batch:
                break
                
            for row in batch:
                yield (row['id'], row['xml_content'])
                
            offset += batch_size
            
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Initialize container in Azurite
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_CONTAINER_NAME")
    
    uploader = BlobUploader(connection_string, container_name, num_workers=5)
    logger.info("Starting upload process with 5 workers...")
    uploader.process_rows(get_rows())
    logger.info("Upload process completed!")
__module_name__ = "vector_db"


from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings
import os
import shutil
import tempfile
import asyncio
import threading

# Global constant for vector database directory
VECTOR_DB_DIR = "backend/vectorstore/index"

def get_vectorstore(embedding_model: Embeddings, clear_existing: bool = False) -> Chroma:
    """
    Get a Chroma vectorstore instance with proper error handling.
    
    Args:
        embedding_model: The embedding model to use
        clear_existing: If True, clears any existing vector database
    """
    global VECTOR_DB_DIR  # Explicitly reference the global variable
    
    # Handle event loop issues
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running, this is fine for ChromaDB
        pass
    
    # Use a working directory variable to avoid scope issues
    working_dir = VECTOR_DB_DIR
    
    # Clear existing database if requested or if there are permission issues
    if clear_existing and os.path.exists(working_dir):
        try:
            shutil.rmtree(working_dir)
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not remove existing vector database: {e}")
            # Create a temporary directory as fallback
            working_dir = tempfile.mkdtemp(prefix="chroma_temp_")
            print(f"Using temporary directory: {working_dir}")
    
    # Create directory with proper permissions
    try:
        os.makedirs(working_dir, mode=0o755, exist_ok=True)
    except (PermissionError, OSError) as e:
        print(f"Warning: Could not create directory {working_dir}: {e}")
        # Use temporary directory as fallback
        working_dir = tempfile.mkdtemp(prefix="chroma_temp_")
        print(f"Using temporary directory: {working_dir}")
    
    # Initialize ChromaDB with error handling
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return Chroma(
                persist_directory=working_dir,
                embedding_function=embedding_model,
                collection_metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"ChromaDB initialization attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                # Last attempt - try with a guaranteed writable temporary directory
                temp_dir = tempfile.mkdtemp(prefix="chroma_fallback_")
                print(f"Using fallback temporary directory: {temp_dir}")
                return Chroma(
                    persist_directory=temp_dir,
                    embedding_function=embedding_model,
                    collection_metadata={"hnsw:space": "cosine"}
                )
            # Wait before retry
            import time
            time.sleep(1)

def clear_vectorstore() -> None:
    """Clear the entire vector database with error handling."""
    global VECTOR_DB_DIR
    try:
        if os.path.exists(VECTOR_DB_DIR):
            shutil.rmtree(VECTOR_DB_DIR)
    except (PermissionError, OSError) as e:
        print(f"Warning: Could not clear vectorstore: {e}")

def store_embeddings(vectorstore: Chroma, chunks: list) -> None:
    """Store embeddings with error handling."""
    if not chunks:
        print("Warning: No chunks to store")
        return
    
    try:
        vectorstore.add_documents(chunks)
        # Try to persist if the method exists
        if hasattr(vectorstore, 'persist'):
            vectorstore.persist()
    except Exception as e:
        print(f"Error storing embeddings: {e}")
        # Try without persistence as fallback
        try:
            vectorstore.add_documents(chunks)
        except Exception as e2:
            raise RuntimeError(f"Failed to store embeddings even without persistence: {e2}")
        
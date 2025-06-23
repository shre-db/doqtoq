"""
Vector database module for DoqToq.

This module provides a unified interface for different vector database implementations.
Currently supports Chroma with Qdrant support planned for Phase 2.
"""

from .base import VectorDatabaseInterface
from .config import (
    VectorDBConfig, 
    VectorDBProvider, 
    QdrantConfig, 
    ChromaConfig,
    get_vector_db_config
)
from .factory import (
    VectorDatabaseFactory, 
    get_vector_database,
    get_available_providers
)
from .chroma_db import ChromaVectorDB

# Backward compatibility - maintain the original API
from .vector_db import (
    get_vectorstore, 
    clear_vectorstore, 
    store_embeddings,
    get_vectorstore_info,
    is_vectorstore_initialized
)

__all__ = [
    # New modular API
    "VectorDatabaseInterface",
    "VectorDBConfig",
    "VectorDBProvider", 
    "QdrantConfig",
    "ChromaConfig",
    "get_vector_db_config",
    "VectorDatabaseFactory",
    "get_vector_database",
    "get_available_providers",
    "ChromaVectorDB",
    
    # Backward compatibility API
    "get_vectorstore",
    "clear_vectorstore", 
    "store_embeddings",
    "get_vectorstore_info",
    "is_vectorstore_initialized"
]

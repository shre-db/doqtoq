"""
Qdrant vector database implementation.
This module implements the VectorDatabaseInterface for Qdrant.
"""

import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from langchain_qdrant import QdrantVectorStore
from langchain.embeddings.base import Embeddings
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse

from .base import VectorDatabaseInterface
from .config import QdrantConfig, create_data_directory


class QdrantVectorDB(VectorDatabaseInterface):
    """Qdrant implementation of the vector database interface."""
    
    def __init__(self, embedding_model: Embeddings, config: QdrantConfig):
        """
        Initialize Qdrant vector database.
        
        Args:
            embedding_model: The embedding model to use
            config: Qdrant-specific configuration
        """
        super().__init__(embedding_model, config)
        self.config: QdrantConfig = config
        self._vectorstore: Optional[QdrantVectorStore] = None
        self._client: Optional[QdrantClient] = None
        
        # Map string distance to Qdrant Distance enum
        self._distance_map = {
            "Cosine": Distance.COSINE,
            "Euclid": Distance.EUCLID,
            "Dot": Distance.DOT
        }
    
    def _get_client(self) -> QdrantClient:
        """Get or create Qdrant client."""
        if self._client is None:
            if self.config.mode == "local":
                # Ensure data directory exists
                create_data_directory(self.config.path)
                self._client = QdrantClient(path=self.config.path)
                print(f"Connected to local Qdrant at: {self.config.path}")
            else:  # server mode
                client_kwargs = {
                    "url": self.config.url,
                    "prefer_grpc": self.config.prefer_grpc,
                    "timeout": self.config.timeout
                }
                
                if self.config.api_key:
                    client_kwargs["api_key"] = self.config.api_key
                
                self._client = QdrantClient(**client_kwargs)
                print(f"Connected to Qdrant server at: {self.config.url}")
        
        return self._client
    
    def _ensure_collection_exists(self) -> None:
        """Ensure the collection exists with proper configuration."""
        client = self._get_client()
        
        try:
            # Check if collection exists
            collections = client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.config.collection_name not in collection_names:
                # Create collection
                client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=VectorParams(
                        size=self.config.vector_size,
                        distance=self._distance_map[self.config.distance]
                    )
                )
                print(f"Created Qdrant collection: {self.config.collection_name}")
            else:
                print(f"Using existing Qdrant collection: {self.config.collection_name}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to ensure collection exists: {e}")
    
    def initialize(self, clear_existing: bool = False) -> None:
        """
        Initialize the Qdrant database.
        
        Args:
            clear_existing: If True, clear any existing data
        """
        try:
            # Clear existing data if requested
            if clear_existing:
                self.clear()
            
            # Ensure collection exists
            self._ensure_collection_exists()
            
            # Initialize LangChain QdrantVectorStore
            client = self._get_client()
            
            self._vectorstore = QdrantVectorStore(
                client=client,
                collection_name=self.config.collection_name,
                embeddings=self.embedding_model
            )
            
            print(f"Qdrant vector database initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Qdrant: {e}")
            raise RuntimeError(f"Failed to initialize Qdrant: {e}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to Qdrant.
        
        Args:
            documents: List of documents to add
        """
        if not documents:
            print("Warning: No documents to store")
            return
        
        if self._vectorstore is None:
            raise RuntimeError("Vector database not initialized. Call initialize() first.")
        
        try:
            # Add documents using LangChain interface
            ids = self._vectorstore.add_documents(documents)
            print(f"Added {len(documents)} documents to Qdrant with IDs: {len(ids)} generated")
            
        except Exception as e:
            print(f"Error storing documents in Qdrant: {e}")
            raise RuntimeError(f"Failed to add documents to Qdrant: {e}")
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Perform similarity search in Qdrant.
        
        Args:
            query: Query string to search for
            k: Number of similar documents to return
            
        Returns:
            List of similar documents
        """
        if self._vectorstore is None:
            raise RuntimeError("Vector database not initialized. Call initialize() first.")
        
        try:
            return self._vectorstore.similarity_search(query, k=k)
        except Exception as e:
            print(f"Error performing similarity search: {e}")
            raise RuntimeError(f"Similarity search failed: {e}")
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[tuple]:
        """
        Perform similarity search with relevance scores.
        
        Args:
            query: Query string to search for
            k: Number of similar documents to return
            
        Returns:
            List of tuples (document, score)
        """
        if self._vectorstore is None:
            raise RuntimeError("Vector database not initialized. Call initialize() first.")
        
        try:
            return self._vectorstore.similarity_search_with_score(query, k=k)
        except Exception as e:
            print(f"Error performing similarity search with score: {e}")
            raise RuntimeError(f"Similarity search with score failed: {e}")
    
    def clear(self) -> None:
        """Clear all data from Qdrant."""
        try:
            client = self._get_client()
            
            # Check if collection exists before trying to delete
            collections = client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.config.collection_name in collection_names:
                # Delete the collection
                client.delete_collection(self.config.collection_name)
                print(f"Cleared Qdrant collection: {self.config.collection_name}")
            else:
                print(f"Collection {self.config.collection_name} does not exist, nothing to clear")
            
            # Reset vectorstore
            self._vectorstore = None
            
        except Exception as e:
            print(f"Warning: Could not clear Qdrant collection: {e}")
    
    def persist(self) -> None:
        """
        Persist Qdrant to storage.
        
        Note: Qdrant automatically persists data, so this is mostly a no-op.
        """
        try:
            if self._client and self.config.mode == "local":
                # For local mode, data is automatically persisted
                print("Qdrant data automatically persisted to local storage")
            elif self._client and self.config.mode == "server":
                # For server mode, data is managed by the server
                print("Qdrant data managed by server")
            else:
                print("No Qdrant client to persist")
                
        except Exception as e:
            print(f"Warning: Error during Qdrant persist: {e}")
    
    def get_retriever(self, k: int = 4, **kwargs) -> Any:
        """
        Get a retriever object for Qdrant.
        
        Args:
            k: Number of documents to retrieve
            **kwargs: Additional retriever-specific parameters
            
        Returns:
            Qdrant retriever object
        """
        if self._vectorstore is None:
            raise RuntimeError("Vector database not initialized. Call initialize() first.")
        
        return self._vectorstore.as_retriever(
            search_kwargs={"k": k, **kwargs}
        )
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the Qdrant collection.
        
        Returns:
            Dictionary containing collection information
        """
        if self._client is None:
            return {"status": "not_initialized"}
        
        try:
            client = self._get_client()
            collections = client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.config.collection_name not in collection_names:
                return {
                    "provider": "qdrant",
                    "collection_name": self.config.collection_name,
                    "status": "collection_not_found",
                    "mode": self.config.mode,
                    "path": self.config.path if self.config.mode == "local" else self.config.url
                }
            
            # Get collection info
            collection_info = client.get_collection(self.config.collection_name)
            
            return {
                "provider": "qdrant",
                "collection_name": self.config.collection_name,
                "status": collection_info.status,
                "vector_count": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance.name,
                "mode": self.config.mode,
                "path": self.config.path if self.config.mode == "local" else self.config.url,
                "indexed_vectors_count": collection_info.indexed_vectors_count
            }
            
        except Exception as e:
            return {
                "provider": "qdrant",
                "collection_name": self.config.collection_name,
                "error": str(e),
                "mode": self.config.mode,
                "path": self.config.path if self.config.mode == "local" else self.config.url
            }
    
    def get_vector_count(self) -> int:
        """
        Get the number of vectors in the collection.
        
        Returns:
            Number of vectors stored
        """
        try:
            if self._client is None:
                return 0
            
            client = self._get_client()
            collection_info = client.get_collection(self.config.collection_name)
            return collection_info.points_count or 0
            
        except Exception as e:
            print(f"Error getting vector count: {e}")
            return 0
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the Qdrant connection.
        
        Returns:
            Health check results
        """
        try:
            client = self._get_client()
            
            # Basic connectivity test
            collections = client.get_collections()
            
            return {
                "status": "healthy",
                "mode": self.config.mode,
                "collections_count": len(collections.collections),
                "target_collection_exists": self.config.collection_name in [c.name for c in collections.collections]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "mode": self.config.mode
            }

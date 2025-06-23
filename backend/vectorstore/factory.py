"""
Factory for creating vector database instances.
This module provides a unified interface for creating different vector database implementations.
"""

from typing import Type
from langchain.embeddings.base import Embeddings

from .base import VectorDatabaseInterface
from .config import VectorDBConfig, VectorDBProvider, get_vector_db_config
from .chroma_db import ChromaVectorDB


class VectorDatabaseFactory:
    """Factory class for creating vector database instances."""
    
    # Registry of available vector database implementations
    _providers = {
        "chroma": ChromaVectorDB,
        # "qdrant": QdrantVectorDB,  # Will be added in Phase 2
    }
    
    @classmethod
    def create(
        cls,
        embedding_model: Embeddings,
        provider: VectorDBProvider = None,
        config: VectorDBConfig = None
    ) -> VectorDatabaseInterface:
        """
        Create a vector database instance.
        
        Args:
            embedding_model: The embedding model to use
            provider: Vector database provider ("qdrant" or "chroma")
            config: Configuration object (optional, will load from env if not provided)
            
        Returns:
            Vector database instance implementing VectorDatabaseInterface
            
        Raises:
            ValueError: If provider is not supported
            RuntimeError: If provider implementation is not available
        """
        # Load config if not provided
        if config is None:
            config = get_vector_db_config()
        
        # Use provider from config if not specified
        if provider is None:
            provider = config.provider
        
        # Validate provider
        if provider not in cls._providers:
            available = ", ".join(cls._providers.keys())
            if provider == "qdrant":
                raise RuntimeError(
                    f"Qdrant provider not yet implemented. "
                    f"Available providers: {available}. "
                    f"Qdrant support will be added in Phase 2."
                )
            else:
                raise ValueError(
                    f"Unsupported vector database provider: {provider}. "
                    f"Available providers: {available}"
                )
        
        # Get the provider class
        provider_class = cls._providers[provider]
        
        # Get provider-specific config
        if provider == "chroma":
            provider_config = config.chroma
        elif provider == "qdrant":
            provider_config = config.qdrant
        else:
            raise ValueError(f"No configuration found for provider: {provider}")
        
        # Create and return the instance
        print(f"Creating {provider} vector database...")
        return provider_class(embedding_model, provider_config)
    
    @classmethod
    def register_provider(
        cls,
        name: str,
        provider_class: Type[VectorDatabaseInterface]
    ) -> None:
        """
        Register a new vector database provider.
        
        Args:
            name: Provider name
            provider_class: Provider implementation class
        """
        if not issubclass(provider_class, VectorDatabaseInterface):
            raise ValueError(
                f"Provider class must implement VectorDatabaseInterface"
            )
        
        cls._providers[name] = provider_class
        print(f"Registered vector database provider: {name}")
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """
        Get list of available vector database providers.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def is_provider_available(cls, provider: str) -> bool:
        """
        Check if a provider is available.
        
        Args:
            provider: Provider name to check
            
        Returns:
            True if provider is available, False otherwise
        """
        return provider in cls._providers


# Convenience functions for backward compatibility and ease of use

def get_vector_database(
    embedding_model: Embeddings,
    provider: VectorDBProvider = None,
    clear_existing: bool = False
) -> VectorDatabaseInterface:
    """
    Get a vector database instance (convenience function).
    
    Args:
        embedding_model: The embedding model to use
        provider: Vector database provider ("qdrant" or "chroma")
        clear_existing: If True, clear any existing data
        
    Returns:
        Initialized vector database instance
    """
    # Create the database instance
    db = VectorDatabaseFactory.create(embedding_model, provider)
    
    # Initialize it
    db.initialize(clear_existing=clear_existing)
    
    return db

def get_available_providers() -> list[str]:
    """Get list of available vector database providers."""
    return VectorDatabaseFactory.get_available_providers()
